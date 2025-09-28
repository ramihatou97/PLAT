"""Main FastAPI application for PLAT neurosurgical encyclopedia."""

from fastapi import FastAPI, Depends, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from ..core.config import settings
from ..services.ai_providers import ai_manager
from ..services.pubmed_service import pubmed_service
from ..services.search_service import search_service
from .schemas import (
    ConceptResponse, ConceptCreate, ConceptUpdate,
    SearchRequest, SearchResponse,
    PubMedPaper, GenerateContentRequest
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="PLAT - Neurosurgical Encyclopedia API",
    description="Personal AI-Driven Neurosurgical Knowledge Management System",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Starting PLAT API server...")
    
    # Initialize services
    try:
        # Verify AI providers
        available_providers = ai_manager.get_available_providers()
        logger.info(f"Available AI providers: {available_providers}")
        
        # Get search statistics
        search_stats = await search_service.get_search_statistics()
        logger.info(f"Search index statistics: {search_stats}")
        
        logger.info("PLAT API server started successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")


@app.get("/", response_model=Dict[str, Any])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "PLAT - Neurosurgical Encyclopedia API",
        "version": "0.1.0",
        "description": "Personal AI-Driven Neurosurgical Knowledge Management System",
        "features": [
            "Semantic search across 427+ neurosurgical concepts",
            "AI-powered content generation (GPT-4, Gemini, Claude)",
            "Auto-updating from PubMed research",
            "Evidence-based protocols and guidelines",
            "Real-time searchable medical reference"
        ],
        "endpoints": {
            "search": "/search",
            "concepts": "/concepts",
            "generate": "/generate",
            "pubmed": "/pubmed",
            "stats": "/stats"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "ai_providers": len(ai_manager.get_available_providers()),
            "search_service": "active",
            "pubmed_service": "active"
        }
    }


@app.post("/search", response_model=SearchResponse)
async def search_concepts(request: SearchRequest):
    """Search for neurosurgical concepts using semantic similarity."""
    try:
        logger.info(f"Search request: '{request.query}'")
        
        # Perform semantic search
        results = await search_service.search_concepts(
            query=request.query,
            max_results=request.max_results,
            filters=request.filters,
            min_confidence=request.min_confidence
        )
        
        return SearchResponse(
            query=request.query,
            results=results,
            total_results=len(results),
            search_time_ms=0,  # Would be calculated in real implementation
            semantic_search_used=True
        )
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail="Search operation failed")


@app.get("/search/similar/{concept_id}")
async def find_similar_concepts(
    concept_id: int,
    max_results: int = Query(default=10, ge=1, le=50)
):
    """Find concepts similar to a given concept."""
    try:
        similar_concepts = await search_service.search_similar_concepts(
            concept_id=concept_id,
            max_results=max_results
        )
        
        return {
            "concept_id": concept_id,
            "similar_concepts": similar_concepts,
            "count": len(similar_concepts)
        }
        
    except Exception as e:
        logger.error(f"Similar concept search failed: {e}")
        raise HTTPException(status_code=500, detail="Similar concept search failed")


@app.post("/generate", response_model=Dict[str, Any])
async def generate_content(request: GenerateContentRequest):
    """Generate neurosurgical content using AI providers."""
    try:
        logger.info(f"Content generation request: '{request.prompt[:100]}...'")
        
        # Generate content using AI providers
        content, confidence = await ai_manager.generate_consensus_content(
            prompt=request.prompt,
            context=request.context,
            providers=request.providers
        )
        
        if not content:
            raise HTTPException(
                status_code=500, 
                detail="Failed to generate content from available providers"
            )
        
        return {
            "generated_content": content,
            "confidence_score": confidence,
            "providers_used": request.providers or ai_manager.get_available_providers(),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Content generation failed: {e}")
        raise HTTPException(status_code=500, detail="Content generation failed")


@app.get("/pubmed/recent", response_model=List[PubMedPaper])
async def get_recent_papers(
    days_back: int = Query(default=30, ge=1, le=365),
    max_results: int = Query(default=50, ge=1, le=200)
):
    """Get recent neurosurgical papers from PubMed."""
    try:
        logger.info(f"Fetching recent papers: {days_back} days, max {max_results}")
        
        papers = await pubmed_service.search_recent_papers(
            days_back=days_back,
            max_results=max_results
        )
        
        return [PubMedPaper(**paper) for paper in papers]
        
    except Exception as e:
        logger.error(f"PubMed search failed: {e}")
        raise HTTPException(status_code=500, detail="PubMed search failed")


@app.get("/pubmed/concept/{concept}")
async def search_concept_papers(
    concept: str,
    max_results: int = Query(default=20, ge=1, le=100)
):
    """Search for papers related to a specific neurosurgical concept."""
    try:
        papers = await pubmed_service.search_concept_papers(
            concept=concept,
            max_results=max_results
        )
        
        return {
            "concept": concept,
            "papers": papers,
            "count": len(papers)
        }
        
    except Exception as e:
        logger.error(f"Concept paper search failed: {e}")
        raise HTTPException(status_code=500, detail="Concept paper search failed")


@app.post("/update/pubmed")
async def trigger_pubmed_update(background_tasks: BackgroundTasks):
    """Trigger background update from PubMed."""
    try:
        # Add background task to update content from PubMed
        background_tasks.add_task(update_from_pubmed)
        
        return {
            "message": "PubMed update task started",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to trigger PubMed update: {e}")
        raise HTTPException(status_code=500, detail="Failed to trigger update")


@app.get("/stats")
async def get_system_statistics():
    """Get system statistics and metrics."""
    try:
        search_stats = await search_service.get_search_statistics()
        
        return {
            "system_info": {
                "version": "0.1.0",
                "uptime": "N/A",  # Would calculate actual uptime
                "last_update": datetime.now().isoformat()
            },
            "search_index": search_stats,
            "ai_providers": {
                "available": ai_manager.get_available_providers(),
                "total": len(ai_manager.get_available_providers())
            },
            "configuration": {
                "max_concepts": settings.max_concepts,
                "update_frequency_hours": settings.update_frequency_hours,
                "min_confidence_score": settings.min_confidence_score
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")


@app.get("/concepts/types")
async def get_content_types():
    """Get available content types and categories."""
    return {
        "content_types": [
            "protocol",
            "surgical_technique", 
            "clinical_guideline",
            "concept",
            "definition",
            "case_study"
        ],
        "neurosurgical_categories": [
            "Brain Tumors",
            "Vascular Neurosurgery",
            "Spinal Surgery",
            "Functional Neurosurgery",
            "Pediatric Neurosurgery",
            "Trauma",
            "Stereotactic Radiosurgery",
            "Endoscopic Surgery",
            "Pain Management",
            "Epilepsy Surgery"
        ]
    }


async def update_from_pubmed():
    """Background task to update content from PubMed."""
    try:
        logger.info("Starting PubMed update task...")
        
        # Fetch recent papers
        papers = await pubmed_service.search_recent_papers(
            days_back=7,  # Weekly updates
            max_results=100
        )
        
        logger.info(f"Retrieved {len(papers)} papers from PubMed")
        
        # Process and add high-confidence papers to the knowledge base
        # This would involve:
        # 1. Converting papers to concepts
        # 2. Adding to database
        # 3. Updating search index
        # Implementation would depend on specific requirements
        
        logger.info("PubMed update task completed")
        
    except Exception as e:
        logger.error(f"PubMed update task failed: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.plat.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )