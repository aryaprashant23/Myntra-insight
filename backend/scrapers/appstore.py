import sys
import os
import logging
from apify_client import ApifyClient

# Add the parent directory to the path so we can import the database module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import supabase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Myntra's Apple App Store ID
APP_ID = "412812508"
APIFY_API_TOKEN = os.environ.get("APIFY_API_TOKEN")

def fetch_appstore_reviews(app_id: str = APP_ID, max_reviews: int = 100):
    """
    Fetches recent reviews from the Apple App Store for Myntra using Apify's managed
    App Store scraper (epctex/app-store-scraper).
    """
    if not APIFY_API_TOKEN or APIFY_API_TOKEN.startswith("your_"):
        logger.error("APIFY_API_TOKEN is missing or invalid in .env file.")
        return None

    logger.info(f"Triggering Apify App Store Scraper for App ID: '{app_id}'...")
    
    try:
        client = ApifyClient(APIFY_API_TOKEN)
        
        # Prepare the Actor input
        run_input = {
            "appId": app_id,
            "maxReviews": max_reviews,
            "country": "in"
        }
        
        # Run the Actor and wait for it to finish
        logger.info("Running Apify Actor 'easyapi/app-store-reviews-scraper'. This might take a minute...")
        run = client.actor("easyapi/app-store-reviews-scraper").call(run_input=run_input)
        
        logger.info("Apify run finished. Fetching results from the dataset...")
        
        records_to_insert = []
        dataset_id = run["defaultDatasetId"] if isinstance(run, dict) else getattr(run, "defaultDatasetId", getattr(run, "default_dataset_id", None))
        for item in client.dataset(dataset_id).iterate_items():
            if not item.get('text'):
                continue
                
            record = {
                "source": "app_store",
                "raw_text": item['text'],
                "metadata": {
                    "user_name": item.get('userName'),
                    "score": item.get('rating'),
                    "title": item.get('title'),
                    "date": item.get('date')
                }
            }
            records_to_insert.append(record)
            
        if not records_to_insert:
            logger.info("No App Store reviews found.")
            return []
            
        # Insert into Supabase
        logger.info(f"Inserting {len(records_to_insert)} App Store reviews into Supabase 'raw_reviews' table...")
        response = supabase.table("raw_reviews").insert(records_to_insert).execute()
        
        logger.info(f"Successfully inserted {len(response.data)} records.")
        return response.data
        
    except Exception as e:
        logger.error(f"Error fetching/inserting App Store reviews via Apify: {e}")
        return None

if __name__ == "__main__":
    fetch_appstore_reviews(max_reviews=20)
