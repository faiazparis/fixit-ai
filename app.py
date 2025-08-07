"""
iFixit Repair Guide System - FastAPI Backend
A REST API for searching and retrieving repair guides from iFixit.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Union
import uvicorn
import logging
from datetime import datetime
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from fastapi_ifixit import IFixitRepairGuide
from fastapi_utils import clean_content, extract_tools_and_parts, extract_steps
from deepseek_summarizer import DeepSeekSummarizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
DEFAULT_PORT = 8000
DEFAULT_HOST = "127.0.0.1"
DEFAULT_MAX_RESULTS = 10
MAX_RESULTS_LIMIT = 50
API_VERSION = "1.0.0"

# Initialize FastAPI app
app = FastAPI(
    title="iFixit Repair Guide API",
    description="A REST API for searching and retrieving repair guides from iFixit",
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Initialize the repair guide system
repair_system = IFixitRepairGuide()

# Initialize DeepSeek summarizer
try:
    deepseek_summarizer = DeepSeekSummarizer()
    logger.info("DeepSeek summarizer initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize DeepSeek summarizer: {e}")
    deepseek_summarizer = None

# Pydantic models for request/response
class SearchRequest(BaseModel):
    """Request model for device search."""
    query: str = Field(
        ..., 
        description="Device name or model to search for", 
        example="iPhone 14",
        min_length=1,
        max_length=100
    )
    max_results: Optional[int] = Field(
        DEFAULT_MAX_RESULTS, 
        description="Maximum number of results to return", 
        ge=1, 
        le=MAX_RESULTS_LIMIT
    )

    @field_validator('query')
    def validate_query(cls, v):
        """Validate search query."""
        if not v.strip():
            raise ValueError('Query cannot be empty or whitespace only')
        return v.strip()

class DeviceInfo(BaseModel):
    """Device information model."""
    title: str = Field(..., description="Device title")
    source: str = Field(..., description="Source URL")
    content: str = Field(..., description="Device description")
    relevance_score: Optional[int] = Field(None, description="Relevance score (0-100)")

class RepairGuide(BaseModel):
    """Repair guide model."""
    title: str = Field(..., description="Guide title")
    source: str = Field(..., description="Guide source URL")
    content: str = Field(..., description="Guide content")
    tools: List[str] = Field(default_factory=list, description="Required tools")
    parts: List[str] = Field(default_factory=list, description="Required parts")
    steps: List[Dict[str, str]] = Field(default_factory=list, description="Repair steps")

class SearchResponse(BaseModel):
    """Search response model."""
    query: str = Field(..., description="Original search query")
    total_results: int = Field(..., description="Total number of results")
    devices: List[DeviceInfo] = Field(..., description="List of devices")
    timestamp: datetime = Field(..., description="Response timestamp")

class GuideResponse(BaseModel):
    """Guide response model."""
    device_url: str = Field(..., description="Device URL")
    guides: List[RepairGuide] = Field(..., description="Repair guides")
    teardowns: List[RepairGuide] = Field(..., description="Teardown guides")
    answers: List[RepairGuide] = Field(..., description="Community answers")
    timestamp: datetime = Field(..., description="Response timestamp")

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(..., description="Check timestamp")
    version: str = Field(..., description="API version")

class DeepSeekSummaryRequest(BaseModel):
    """DeepSeek summary request model."""
    device_url: str = Field(
        ..., 
        description="iFixit device URL to summarize",
        pattern=r"^https://www\.ifixit\.com/.*$"
    )
    summary_type: Optional[str] = Field(
        "beginner", 
        description="Type of summary: beginner, intermediate, expert"
    )

    @field_validator('summary_type')
    def validate_summary_type(cls, v):
        """Validate summary type."""
        valid_types = ["beginner", "intermediate", "expert"]
        if v not in valid_types:
            raise ValueError(f'Summary type must be one of: {", ".join(valid_types)}')
        return v

class DeepSeekSummaryResponse(BaseModel):
    """DeepSeek summary response model."""
    device_url: str = Field(..., description="Device URL")
    original_title: str = Field(..., description="Original guide title")
    summary: str = Field(..., description="AI-generated summary")
    difficulty: str = Field(..., description="Repair difficulty level")
    time_estimate: str = Field(..., description="Estimated repair time")
    success_rate: str = Field(..., description="Success rate estimate")
    available: bool = Field(..., description="Summary availability")
    timestamp: datetime = Field(..., description="Response timestamp")

# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """Health check endpoint to verify API status."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version=API_VERSION
    )

# Search devices endpoint
@app.post("/search", response_model=SearchResponse, tags=["Search"])
async def search_devices(request: SearchRequest) -> SearchResponse:
    """
    Search for devices using the iFixit API.
    
    Args:
        request: SearchRequest containing query and max_results
        
    Returns:
        SearchResponse with device information
        
    Raises:
        HTTPException: If search fails
    """
    try:
        logger.info(f"Searching for devices with query: '{request.query}' (max_results: {request.max_results})")
        
        # Search for devices
        devices = repair_system.search_device(request.query, request.max_results)
        
        # Convert to response format
        device_infos = []
        for device in devices:
            device_info = DeviceInfo(
                title=device.metadata.get('title', 'Unknown Device'),
                source=device.metadata.get('source', ''),
                content=clean_content(device.page_content),
                relevance_score=device.metadata.get('relevance_score', 0)
            )
            device_infos.append(device_info)
        
        logger.info(f"Found {len(device_infos)} devices for query '{request.query}'")
        
        return SearchResponse(
            query=request.query,
            total_results=len(device_infos),
            devices=device_infos,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error searching devices: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

# Get guides endpoint
@app.get("/guides/{device_url:path}", response_model=GuideResponse, tags=["Guides"])
async def get_guides(device_url: str) -> GuideResponse:
    """
    Get repair guides, teardowns, and community answers for a specific device.
    
    Args:
        device_url: URL of the device page
        
    Returns:
        GuideResponse with guides, teardowns, and answers
        
    Raises:
        HTTPException: If guides cannot be retrieved
    """
    try:
        logger.info(f"Getting guides for device: {device_url}")
        
        # Get repair guides
        guides = repair_system.get_repair_guides(device_url)
        guide_responses = []
        for guide in guides:
            tools, parts = extract_tools_and_parts(guide.page_content)
            steps = extract_steps(guide.page_content)
            
            guide_response = RepairGuide(
                title=guide.metadata.get('title', 'Untitled Guide'),
                source=guide.metadata.get('source', ''),
                content=clean_content(guide.page_content),
                tools=tools,
                parts=parts,
                steps=[{"title": step[0], "content": step[1]} for step in steps]
            )
            guide_responses.append(guide_response)
        
        # Get teardowns
        teardowns = repair_system.get_teardowns(device_url)
        teardown_responses = []
        for teardown in teardowns:
            tools, parts = extract_tools_and_parts(teardown.page_content)
            steps = extract_steps(teardown.page_content)
            
            teardown_response = RepairGuide(
                title=teardown.metadata.get('title', 'Untitled Teardown'),
                source=teardown.metadata.get('source', ''),
                content=clean_content(teardown.page_content),
                tools=tools,
                parts=parts,
                steps=[{"title": step[0], "content": step[1]} for step in steps]
            )
            teardown_responses.append(teardown_response)
        
        # Get community answers
        answers = repair_system.get_answers(device_url)
        answer_responses = []
        for answer in answers:
            tools, parts = extract_tools_and_parts(answer.page_content)
            steps = extract_steps(answer.page_content)
            
            answer_response = RepairGuide(
                title=answer.metadata.get('title', 'Untitled Answer'),
                source=answer.metadata.get('source', ''),
                content=clean_content(answer.page_content),
                tools=tools,
                parts=parts,
                steps=[{"title": step[0], "content": step[1]} for step in steps]
            )
            answer_responses.append(answer_response)
        
        logger.info(f"Retrieved {len(guide_responses)} guides, {len(teardown_responses)} teardowns, {len(answer_responses)} answers")
        
        return GuideResponse(
            device_url=device_url,
            guides=guide_responses,
            teardowns=teardown_responses,
            answers=answer_responses,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error getting guides: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get guides: {str(e)}")

# DeepSeek summary endpoint
@app.post("/summarize", response_model=DeepSeekSummaryResponse, tags=["AI Summary"])
async def summarize_repair_guide(request: DeepSeekSummaryRequest) -> DeepSeekSummaryResponse:
    """
    Generate a beginner-friendly summary of a repair guide using DeepSeek AI.
    
    Args:
        request: DeepSeekSummaryRequest containing device URL and summary type
        
    Returns:
        DeepSeekSummaryResponse with AI-generated summary
        
    Raises:
        HTTPException: If summary generation fails
    """
    try:
        logger.info(f"Generating summary for device: {request.device_url} (type: {request.summary_type})")
        
        # Get the repair guide content
        guides = repair_system.get_repair_guides(request.device_url)
        if not guides:
            raise HTTPException(status_code=404, detail="No repair guides found for this device")
        
        # Use the first guide for summarization
        guide = guides[0]
        guide_content = clean_content(guide.page_content)
        guide_title = guide.metadata.get('title', 'Unknown Repair Guide')
        
        # Extract device name and repair type from title
        device_name = guide_title.split()[0] if guide_title else "Device"
        repair_type = " ".join(guide_title.split()[1:]) if len(guide_title.split()) > 1 else "repair"
        
        # Generate summary using DeepSeek
        summary_result = deepseek_summarizer.summarize_repair_guide(
            device_name=device_name,
            repair_type=repair_type,
            guide_content=guide_content
        )
        
        logger.info(f"Successfully generated summary for {device_name} {repair_type}")
        
        return DeepSeekSummaryResponse(
            device_url=request.device_url,
            original_title=guide_title,
            summary=summary_result["summary"],
            difficulty=summary_result["difficulty"],
            time_estimate=summary_result["time_estimate"],
            success_rate=summary_result["success_rate"],
            available=summary_result["available"],
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")

# Quick search endpoint (GET method for easier testing)
@app.get("/search", response_model=SearchResponse, tags=["Search"])
async def quick_search(
    q: str = Query(
        ..., 
        description="Device name or model to search for", 
        examples=["iPhone 14"],
        min_length=1,
        max_length=100
    ),
    max_results: int = Query(
        DEFAULT_MAX_RESULTS, 
        description="Maximum number of results to return", 
        ge=1, 
        le=MAX_RESULTS_LIMIT
    )
) -> SearchResponse:
    """
    Quick search endpoint using GET method.
    
    Args:
        q: Search query
        max_results: Maximum number of results
        
    Returns:
        SearchResponse with device information
    """
    request = SearchRequest(query=q, max_results=max_results)
    return await search_devices(request)

# Get popular devices endpoint
@app.get("/popular", tags=["Info"])
async def get_popular_devices() -> Dict[str, Any]:
    """Get list of popular devices for suggestions."""
    popular_devices = {
        "smartphones": [
            "iPhone 14", "iPhone 13", "iPhone 12",
            "Samsung Galaxy S23", "Samsung Galaxy S22",
            "Google Pixel 8", "Google Pixel 7"
        ],
        "laptops": [
            "MacBook Pro", "MacBook Air", "MacBook",
            "Dell XPS", "Lenovo ThinkPad", "HP Spectre"
        ],
        "gaming": [
            "PlayStation 5", "Xbox Series X", "Nintendo Switch",
            "PlayStation 4", "Xbox One"
        ],
        "tablets": [
            "iPad", "iPad Pro", "iPad Air",
            "Samsung Galaxy Tab", "Microsoft Surface"
        ]
    }
    
    return {
        "categories": popular_devices,
        "timestamp": datetime.utcnow()
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors."""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Root endpoint - API information
@app.get("/", tags=["Info"])
async def root() -> Dict[str, Any]:
    """API root endpoint with basic information."""
    return {
        "message": "iFixit Repair Guide API",
        "version": API_VERSION,
        "description": "A REST API for searching and retrieving repair guides from iFixit",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "search": "/search",
            "guides": "/guides/{device_url}",
            "summarize": "/summarize",
            "popular": "/popular"
        }
    }

if __name__ == "__main__":
    # Set USER_AGENT to fix the warning
    os.environ["USER_AGENT"] = "iFixit-Repair-Guide-API/1.0.0"
    
    # Run the application with performance optimizations
    port = int(os.getenv("PORT", DEFAULT_PORT))
    host = os.getenv("HOST", DEFAULT_HOST)
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=True,
        log_level="info",
        workers=1,  # Single worker for development
        access_log=True,
        timeout_keep_alive=30,  # Reduce keep-alive timeout
        timeout_graceful_shutdown=10
    ) 