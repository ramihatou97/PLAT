"""Configuration management for PLAT system."""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database Configuration
    database_url: str = Field(default="sqlite:///./data/plat.db")
    
    # AI Provider API Keys
    openai_api_key: Optional[str] = Field(default=None)
    google_api_key: Optional[str] = Field(default=None)
    anthropic_api_key: Optional[str] = Field(default=None)
    
    # PubMed Configuration
    pubmed_email: Optional[str] = Field(default=None)
    pubmed_api_key: Optional[str] = Field(default=None)
    
    # Vector Database Configuration
    chromadb_path: str = Field(default="./data/chromadb")
    
    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379/0")
    
    # Application Configuration
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")
    max_concepts: int = Field(default=427)
    update_frequency_hours: int = Field(default=24)
    
    # Content Sources Configuration
    enable_textbook_scraping: bool = Field(default=True)
    enable_research_papers: bool = Field(default=True)
    enable_ai_generation: bool = Field(default=True)
    
    # Confidence Scoring Configuration
    min_confidence_score: float = Field(default=0.7)
    max_results_per_query: int = Field(default=50)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()