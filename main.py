#!/usr/bin/env python3
"""
PLAT - Personal AI-Driven Neurosurgical Knowledge Management System
Main application entry point.
"""

import sys
import os
import logging
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from plat.core.config import settings
from plat.api.main import app

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("plat.log") if not settings.debug else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main application entry point."""
    logger.info("Starting PLAT Neurosurgical Encyclopedia System")
    
    # Create necessary directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # Import and start the FastAPI application
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=True
    )

if __name__ == "__main__":
    main()