"""Pydantic schemas for API request/response models."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from ..models.content import ContentType, ContentSource


class ConceptBase(BaseModel):
    """Base concept schema."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    content: str = Field(..., min_length=1)
    content_type: ContentType
    category: Optional[str] = None
    subcategory: Optional[str] = None
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence_level: Optional[str] = None
    peer_reviewed: bool = False


class ConceptCreate(ConceptBase):
    """Schema for creating new concepts."""
    pass


class ConceptUpdate(BaseModel):
    """Schema for updating existing concepts."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    content: Optional[str] = Field(None, min_length=1)
    content_type: Optional[ContentType] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    evidence_level: Optional[str] = None
    peer_reviewed: Optional[bool] = None


class ConceptResponse(ConceptBase):
    """Schema for concept responses."""
    id: int
    version: int
    created_at: datetime
    updated_at: datetime
    last_updated: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SearchRequest(BaseModel):
    """Schema for search requests."""
    query: str = Field(..., min_length=1, max_length=500)
    max_results: int = Field(default=20, ge=1, le=100)
    filters: Optional[Dict[str, Any]] = None
    min_confidence: Optional[float] = Field(default=0.0, ge=0.0, le=1.0)


class SearchResult(BaseModel):
    """Schema for individual search results."""
    concept_id: int
    title: str
    content_type: str
    category: str
    subcategory: str
    confidence_score: float
    evidence_level: str
    peer_reviewed: bool
    similarity_score: float
    content_preview: str


class SearchResponse(BaseModel):
    """Schema for search responses."""
    query: str
    results: List[SearchResult]
    total_results: int
    search_time_ms: float
    semantic_search_used: bool
    filters_applied: Optional[Dict[str, Any]] = None


class GenerateContentRequest(BaseModel):
    """Schema for AI content generation requests."""
    prompt: str = Field(..., min_length=1, max_length=2000)
    context: Optional[str] = Field(None, max_length=5000)
    providers: Optional[List[str]] = None
    max_tokens: int = Field(default=2000, ge=100, le=4000)
    content_type: Optional[ContentType] = None


class GenerateContentResponse(BaseModel):
    """Schema for AI content generation responses."""
    generated_content: str
    confidence_score: float
    providers_used: List[str]
    content_type: Optional[ContentType] = None
    timestamp: datetime


class PubMedPaper(BaseModel):
    """Schema for PubMed paper information."""
    pmid: Optional[str] = None
    title: str
    abstract: str
    authors: List[str]
    journal: str
    publication_date: Optional[datetime] = None
    doi: Optional[str] = None
    confidence_score: float
    source_type: ContentSource
    content_type: ContentType
    url: Optional[str] = None


class ContentSourceInfo(BaseModel):
    """Schema for content source information."""
    source_type: ContentSource
    source_url: Optional[str] = None
    source_title: Optional[str] = None
    authors: Optional[str] = None
    publication_date: Optional[datetime] = None
    doi: Optional[str] = None
    pmid: Optional[str] = None
    citation_count: Optional[int] = None
    impact_factor: Optional[float] = None
    source_confidence: float


class TagInfo(BaseModel):
    """Schema for tag information."""
    id: int
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    
    class Config:
        from_attributes = True


class UpdateLogEntry(BaseModel):
    """Schema for update log entries."""
    id: int
    source_type: ContentSource
    operation: str
    concept_id: Optional[int] = None
    summary: Optional[str] = None
    success: bool
    error_message: Optional[str] = None
    processing_time_ms: Optional[float] = None
    concepts_processed: int
    concepts_updated: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class SystemStats(BaseModel):
    """Schema for system statistics."""
    total_concepts: int
    total_sources: int
    total_tags: int
    search_index_size: int
    last_update: datetime
    available_providers: List[str]
    update_frequency_hours: int


class HealthStatus(BaseModel):
    """Schema for health check response."""
    status: str
    timestamp: datetime
    services: Dict[str, Any]
    version: str


class ConceptSimilarity(BaseModel):
    """Schema for concept similarity results."""
    concept_id: int
    title: str
    content_type: str
    category: str
    similarity_score: float
    content_preview: str


class SimilarConceptsResponse(BaseModel):
    """Schema for similar concepts response."""
    concept_id: int
    similar_concepts: List[ConceptSimilarity]
    count: int


class ContentTypeInfo(BaseModel):
    """Schema for content type information."""
    content_types: List[str]
    neurosurgical_categories: List[str]


class PubMedSearchResponse(BaseModel):
    """Schema for PubMed search response."""
    concept: str
    papers: List[PubMedPaper]
    count: int


class UpdateTriggerResponse(BaseModel):
    """Schema for update trigger response."""
    message: str
    timestamp: datetime
    task_id: Optional[str] = None


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    error: str
    detail: str
    timestamp: datetime
    status_code: int


# Additional schemas for more advanced features

class ConceptVersion(BaseModel):
    """Schema for concept version information."""
    id: int
    concept_id: int
    version: int
    content: str
    changes_summary: Optional[str] = None
    created_at: datetime
    created_by: Optional[str] = None


class SearchAnalytics(BaseModel):
    """Schema for search analytics."""
    query: str
    frequency: int
    avg_results: float
    avg_response_time_ms: float
    last_searched: datetime


class ConceptRelationship(BaseModel):
    """Schema for concept relationships."""
    from_concept_id: int
    to_concept_id: int
    relationship_type: str  # "related_to", "part_of", "contraindicated_with", etc.
    strength: float = Field(ge=0.0, le=1.0)
    created_at: datetime


class EvidenceSource(BaseModel):
    """Schema for evidence sources."""
    source_id: int
    source_name: str
    evidence_level: str
    quality_score: float
    last_updated: datetime
    url: Optional[str] = None