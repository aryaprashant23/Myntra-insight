import sys
import os
import logging
from google_play_scraper import Sort, reviews

# Add the parent directory to the path so we can import the database module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import supabase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

APP_ID = "com.myntra.android"

def fetch_playstore_reviews(count: int = 100):
    """
    Fetches reviews from the Google Play Store for the Myntra app and stores them in Supabase.
    """
    logger.info(f"Fetching {count} recent reviews from Google Play Store...")
    
    try:
        result, _ = reviews(
            APP_ID,
            lang='en', 
            country='in', # India, since it's Myntra
            sort=Sort.NEWEST, 
            count=count 
        )
        
        records_to_insert = []
        for review in result:
            # Skip reviews without text content
            if not review.get('content'):
                continue
                
            record = {
                "source": "play_store",
                "raw_text": review['content'],
                "metadata": {
                    "review_id": review.get('reviewId'),
                    "user_name": review.get('userName'),
                    "score": review.get('score'),
                    "thumbs_up_count": review.get('thumbsUpCount'),
                    "at": review.get('at').isoformat() if review.get('at') else None
                }
            }
            records_to_insert.append(record)
            
        if not records_to_insert:
            logger.info("No text reviews found in this batch.")
            return []
            
        # Insert into Supabase
        logger.info(f"Inserting {len(records_to_insert)} reviews into Supabase 'raw_reviews' table...")
        response = supabase.table("raw_reviews").insert(records_to_insert).execute()
        
        logger.info(f"Successfully inserted {len(response.data)} records.")
        return response.data
        
    except Exception as e:
        logger.error(f"Error fetching/inserting Play Store reviews: {e}")
        return None

if __name__ == "__main__":
    fetch_playstore_reviews(10) # Test run with 10 reviews
