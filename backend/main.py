import os
import sys
import logging
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load .env from the backend folder
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Fix import path: add backend directory to sys.path
sys.path.insert(0, os.path.dirname(__file__))
from run_all import main as run_pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Myntra AI Insights API")

# Allow CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    background_tasks.add_task(run_pipeline)
    return {
        "message": "Scraping pipeline successfully started in the background. Data will appear in the database shortly.",
        "status": "processing"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
