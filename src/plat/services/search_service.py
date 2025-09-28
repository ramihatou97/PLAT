"""Semantic search service using ChromaDB for neurosurgical content."""

import logging
from typing import Dict, List, Optional, Tuple
import uuid
from datetime import datetime

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import numpy as np

from ..core.config import settings
from ..models.content import Concept, SearchQuery

logger = logging.getLogger(__name__)


class SemanticSearchService:
    """Service for semantic search functionality using ChromaDB."""
    
    def __init__(self):
        self.chroma_client = None
        self.collection = None
        self.embedding_model = None
        self._initialize_chromadb()
        self._initialize_embedding_model()
    
    def _initialize_chromadb(self):
        """Initialize ChromaDB client and collection."""
        try:
            # Initialize ChromaDB client
            self.chroma_client = chromadb.PersistentClient(
                path=settings.chromadb_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection for neurosurgical concepts
            self.collection = self.chroma_client.get_or_create_collection(
                name="neurosurgical_concepts",
                metadata={
                    "description": "Neurosurgical concepts and content for semantic search",
                    "created_at": datetime.now().isoformat()
                }
            )
            
            logger.info("ChromaDB initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise
    
    def _initialize_embedding_model(self):
        """Initialize sentence transformer model for embeddings."""
        try:
            # Use a model optimized for medical/scientific text
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            self.embedding_model = SentenceTransformer(model_name)
            logger.info(f"Embedding model {model_name} loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    async def add_concept(self, concept: Concept) -> bool:
        """Add a concept to the search index."""
        try:
            # Prepare content for embedding
            content_text = self._prepare_concept_content(concept)
            
            # Generate embedding
            embedding = self.embedding_model.encode(content_text).tolist()
            
            # Prepare metadata
            metadata = {
                "concept_id": concept.id,
                "title": concept.title,
                "content_type": concept.content_type.value,
                "category": concept.category or "",
                "subcategory": concept.subcategory or "",
                "confidence_score": concept.confidence_score,
                "evidence_level": concept.evidence_level or "",
                "peer_reviewed": concept.peer_reviewed,
                "version": concept.version,
                "created_at": concept.created_at.isoformat(),
                "updated_at": concept.updated_at.isoformat()
            }
            
            # Add to ChromaDB
            self.collection.add(
                embeddings=[embedding],
                documents=[content_text],
                metadatas=[metadata],
                ids=[f"concept_{concept.id}"]
            )
            
            logger.info(f"Added concept {concept.id} to search index")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add concept {concept.id} to search index: {e}")
            return False
    
    def _prepare_concept_content(self, concept: Concept) -> str:
        """Prepare concept content for embedding."""
        # Combine title, description, and content for better search
        content_parts = [concept.title]
        
        if concept.description:
            content_parts.append(concept.description)
        
        content_parts.append(concept.content)
        
        if concept.category:
            content_parts.append(f"Category: {concept.category}")
        
        if concept.subcategory:
            content_parts.append(f"Subcategory: {concept.subcategory}")
        
        return " | ".join(filter(None, content_parts))
    
    async def search_concepts(
        self, 
        query: str, 
        max_results: int = None,
        filters: Optional[Dict] = None,
        min_confidence: Optional[float] = None
    ) -> List[Dict]:
        """Search for concepts using semantic similarity."""
        try:
            start_time = datetime.now()
            
            if max_results is None:
                max_results = settings.max_results_per_query
            
            if min_confidence is None:
                min_confidence = settings.min_confidence_score
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Build where clause for filtering
            where_clause = {}
            if filters:
                if "content_type" in filters:
                    where_clause["content_type"] = filters["content_type"]
                if "category" in filters:
                    where_clause["category"] = filters["category"]
                if "peer_reviewed" in filters:
                    where_clause["peer_reviewed"] = filters["peer_reviewed"]
            
            # Add confidence filter
            if min_confidence > 0:
                where_clause["confidence_score"] = {"$gte": min_confidence}
            
            # Perform semantic search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=max_results,
                where=where_clause if where_clause else None,
                include=["metadatas", "documents", "distances"]
            )
            
            # Process results
            search_results = []
            if results["ids"] and results["ids"][0]:
                for i, concept_id in enumerate(results["ids"][0]):
                    metadata = results["metadatas"][0][i]
                    document = results["documents"][0][i]
                    distance = results["distances"][0][i]
                    
                    # Convert distance to similarity score (0-1)
                    similarity_score = max(0, 1 - distance)
                    
                    search_results.append({
                        "concept_id": metadata["concept_id"],
                        "title": metadata["title"],
                        "content_type": metadata["content_type"],
                        "category": metadata["category"],
                        "subcategory": metadata["subcategory"],
                        "confidence_score": metadata["confidence_score"],
                        "evidence_level": metadata["evidence_level"],
                        "peer_reviewed": metadata["peer_reviewed"],
                        "similarity_score": similarity_score,
                        "content_preview": document[:200] + "..." if len(document) > 200 else document
                    })
            
            # Log search query
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds() * 1000
            
            await self._log_search_query(
                query, 
                len(search_results), 
                response_time, 
                filters,
                semantic_similarity_used=True
            )
            
            return search_results
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []
    
    async def search_similar_concepts(
        self, 
        concept_id: int, 
        max_results: int = 10
    ) -> List[Dict]:
        """Find concepts similar to a given concept."""
        try:
            # Get the concept's embedding from ChromaDB
            concept_result = self.collection.get(
                ids=[f"concept_{concept_id}"],
                include=["embeddings", "metadatas"]
            )
            
            if not concept_result["ids"]:
                logger.warning(f"Concept {concept_id} not found in search index")
                return []
            
            concept_embedding = concept_result["embeddings"][0]
            
            # Search for similar concepts
            results = self.collection.query(
                query_embeddings=[concept_embedding],
                n_results=max_results + 1,  # +1 to exclude the concept itself
                include=["metadatas", "documents", "distances"]
            )
            
            # Process results (exclude the original concept)
            similar_concepts = []
            if results["ids"] and results["ids"][0]:
                for i, result_id in enumerate(results["ids"][0]):
                    if result_id != f"concept_{concept_id}":  # Skip the original concept
                        metadata = results["metadatas"][0][i]
                        document = results["documents"][0][i]
                        distance = results["distances"][0][i]
                        
                        similarity_score = max(0, 1 - distance)
                        
                        similar_concepts.append({
                            "concept_id": metadata["concept_id"],
                            "title": metadata["title"],
                            "content_type": metadata["content_type"],
                            "category": metadata["category"],
                            "similarity_score": similarity_score,
                            "content_preview": document[:200] + "..." if len(document) > 200 else document
                        })
            
            return similar_concepts[:max_results]
            
        except Exception as e:
            logger.error(f"Similar concept search failed for concept {concept_id}: {e}")
            return []
    
    async def update_concept(self, concept: Concept) -> bool:
        """Update a concept in the search index."""
        try:
            # Remove existing concept
            await self.remove_concept(concept.id)
            
            # Add updated concept
            return await self.add_concept(concept)
            
        except Exception as e:
            logger.error(f"Failed to update concept {concept.id} in search index: {e}")
            return False
    
    async def remove_concept(self, concept_id: int) -> bool:
        """Remove a concept from the search index."""
        try:
            self.collection.delete(ids=[f"concept_{concept_id}"])
            logger.info(f"Removed concept {concept_id} from search index")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove concept {concept_id} from search index: {e}")
            return False
    
    async def get_search_statistics(self) -> Dict:
        """Get search index statistics."""
        try:
            collection_count = self.collection.count()
            
            return {
                "total_concepts": collection_count,
                "collection_created": self.collection.metadata.get("created_at"),
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
                "chromadb_version": chromadb.__version__
            }
            
        except Exception as e:
            logger.error(f"Failed to get search statistics: {e}")
            return {}
    
    async def rebuild_index(self, concepts: List[Concept]) -> bool:
        """Rebuild the entire search index from scratch."""
        try:
            logger.info("Starting search index rebuild...")
            
            # Clear existing collection
            self.chroma_client.delete_collection("neurosurgical_concepts")
            
            # Recreate collection
            self.collection = self.chroma_client.create_collection(
                name="neurosurgical_concepts",
                metadata={
                    "description": "Neurosurgical concepts and content for semantic search",
                    "created_at": datetime.now().isoformat()
                }
            )
            
            # Add all concepts
            success_count = 0
            for concept in concepts:
                if await self.add_concept(concept):
                    success_count += 1
            
            logger.info(f"Search index rebuild completed: {success_count}/{len(concepts)} concepts indexed")
            return success_count == len(concepts)
            
        except Exception as e:
            logger.error(f"Failed to rebuild search index: {e}")
            return False
    
    async def _log_search_query(
        self, 
        query: str, 
        results_count: int, 
        response_time: float,
        filters: Optional[Dict] = None,
        semantic_similarity_used: bool = False
    ):
        """Log search query for analytics (would integrate with database)."""
        # In a full implementation, this would save to the SearchQuery model
        logger.info(
            f"Search query logged: '{query}' -> {results_count} results "
            f"in {response_time:.2f}ms (semantic: {semantic_similarity_used})"
        )


# Global semantic search service instance
search_service = SemanticSearchService()