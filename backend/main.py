import os
import sys
import logging
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import the existing pipeline logic
from backend.run_all import main as run_pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Myntra AI Insights API")

# Allow CORS for the frontend (Vercel or localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, change this to your Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScrapeResponse(BaseModel):
    message: str
    status: str

@app.get("/")
def health_check():
    return {"status": "Backend is running!"}

@app.post("/api/scrape", response_model=ScrapeResponse)
def trigger_scrape(background_tasks: BackgroundTasks):
    """
    Triggers the scraping pipeline in the background so the HTTP request
    doesn't timeout while waiting for Apify, Play Store, and AI analysis.
    """
    logger.info("Received request to trigger scraping pipeline.")
    
    # Add the pipeline to background tasks
    background_tasks.add_task(run_pipeline)
    
    return {
        "message": "Scraping pipeline successfully started in the background. Data will appear in the database shortly.",
        "status": "processing"
    }

if __name__ == "__main__":
    import uvicorn
    # This allows running locally via: python backend/main.py
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
