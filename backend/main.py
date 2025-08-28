from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import logging
import os

from rag_service_simple import RAGService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AOG Family Devotional RAG API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (frontend)
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path, html=True), name="static")
else:
    # Fallback for production - try relative path
    import pathlib
    current_dir = pathlib.Path(__file__).parent.parent
    frontend_fallback = current_dir / "frontend"
    if frontend_fallback.exists():
        app.mount("/static", StaticFiles(directory=str(frontend_fallback), html=True), name="static")

rag_service = RAGService()

class DevotionalRequest(BaseModel):
    age_group: str
    topic: Optional[str] = None

class DevotionalResponse(BaseModel):
    title: str
    question_of_day: str
    listen_scripture: str
    listen_content: str
    learn_content: str
    live_content: str
    prayer: str
    age_group: str
    topic: Optional[str] = None

@app.get("/")
async def serve_frontend():
    # Try main path first
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "index.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path, media_type="text/html")
    
    # Fallback for production
    import pathlib
    current_dir = pathlib.Path(__file__).parent.parent
    frontend_fallback = current_dir / "frontend" / "index.html"
    if frontend_fallback.exists():
        return FileResponse(str(frontend_fallback), media_type="text/html")
    
    return {"message": "AOG Family Devotional RAG API"}

@app.get("/api")
async def root():
    return {"message": "AOG Family Devotional RAG API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/generate-devotional", response_model=DevotionalResponse)
async def generate_devotional(request: DevotionalRequest):
    try:
        logger.info(f"Generating devotional for age group: {request.age_group}, topic: {request.topic}")
        
        if request.age_group not in ["children", "teens", "young_adults", "adults"]:
            raise HTTPException(
                status_code=400,
                detail="Age group must be one of: children, teens, young_adults, adults"
            )
        
        devotional = await rag_service.generate_devotional(
            age_group=request.age_group,
            topic=request.topic
        )
        
        return devotional
        
    except Exception as e:
        logger.error(f"Error generating devotional: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate devotional")

@app.get("/topics")
async def get_suggested_topics():
    return {
        "topics": [
            "Faith and Trust",
            "Love and Kindness",
            "Prayer and Worship",
            "Forgiveness",
            "Patience",
            "Gratitude",
            "Courage",
            "Family",
            "Friendship",
            "Service to Others"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)