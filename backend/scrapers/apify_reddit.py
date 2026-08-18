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

APIFY_API_TOKEN = os.environ.get("APIFY_API_TOKEN")

# Competitor keywords to filter OUT
COMPETITOR_KEYWORDS = ["flipkart", "amazon", "ajio", "meesho", "nykaa", "tata cliq", "snapdeal", "shein"]

def is_myntra_relevant(text: str) -> bool:
    """Check if text is primarily about Myntra, not competitors."""
    text_lower = text.lower()
    # If it mentions a competitor more prominently than Myntra, skip it
    for comp in COMPETITOR_KEYWORDS:
        if comp in text_lower and "myntra" not in text_lower:
            return False
    return True

def fetch_reddit_data(search_term: str = "myntra", max_posts: int = 50, max_comments_per_post: int = 15):
    """
    Fetches Reddit posts and comments using Apify's managed Reddit Scraper 
    (lekole/reddit-scraper or trudax/reddit-scraper).
    """
    if not APIFY_API_TOKEN or APIFY_API_TOKEN.startswith("your_"):
        logger.error("APIFY_API_TOKEN is missing or invalid in .env file.")
        return None

    logger.info(f"Triggering Apify Reddit Scraper for search term: '{search_term}'...")
    
    try:
        client = ApifyClient(APIFY_API_TOKEN)
        
        # Prepare the Actor input
        run_input = {
            "searchQuery": search_term,
            "subreddits": ["IndianFashionAddicts", "india", "IndianStreetFashion", "Myntra"],
            "resultsLimit": max_posts,
            "sort": "new"
        }
        
        # Run the Actor and wait for it to finish
        logger.info("Running Apify Actor 'scrapers_lat/reddit-scraper'. This might take a minute...")
        run = client.actor("scrapers_lat/reddit-scraper").call(run_input=run_input)
        
        logger.info("Apify run finished. Fetching results from the dataset...")
        
        records_to_insert = []
        dataset_id = run["defaultDatasetId"] if isinstance(run, dict) else getattr(run, "defaultDatasetId", getattr(run, "default_dataset_id", None))
        
        # Iterate over the scraped items
        for item in client.dataset(dataset_id).iterate_items():
            # Sometimes actors return comments directly, sometimes posts with nested comments
            text = item.get('text') or item.get('body') or item.get('title')
            
            if not text:
                continue
            
            # Filter: only keep Myntra-relevant content
            if not is_myntra_relevant(text):
                logger.info(f"Skipping non-Myntra content: {text[:60]}...")
                continue
                
            record = {
                "source": "reddit",
                "raw_text": text,
                "metadata": {
                    "id": item.get('id'),
                    "url": item.get('url'),
                    "author": item.get('author'),
                    "upvotes": item.get('upvotes'),
                    "createdAt": item.get('createdAt')
                }
            }
            records_to_insert.append(record)
            
        if not records_to_insert:
            logger.info("No Reddit posts/comments found.")
            return []
            
        # Insert into Supabase
        logger.info(f"Inserting {len(records_to_insert)} Reddit items into Supabase 'raw_reviews' table...")
        response = supabase.table("raw_reviews").insert(records_to_insert).execute()
        
        logger.info(f"Successfully inserted {len(response.data)} records.")
        return response.data
        
    except Exception as e:
        logger.error(f"Error fetching/inserting Reddit data via Apify: {e}")
        return None

if __name__ == "__main__":
    fetch_reddit_data()
