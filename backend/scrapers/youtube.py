import sys
import os
import logging
from googleapiclient.discovery import build

# Add the parent directory to the path so we can import the database module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import supabase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")

def fetch_youtube_comments(video_id: str, max_results: int = 100):
    """
    Fetches top-level comments from a specific YouTube video and stores them in Supabase.
    """
    if not YOUTUBE_API_KEY or YOUTUBE_API_KEY.startswith("your_"):
        logger.error("YOUTUBE_API_KEY is missing or invalid in .env file.")
        return None

    logger.info(f"Fetching up to {max_results} comments from YouTube video '{video_id}'...")
    
    try:
        # Build the YouTube client
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        
        # Call the commentThreads API
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=max_results,
            textFormat="plainText"
        )
        response = request.execute()
        
        records_to_insert = []
        for item in response.get('items', []):
            comment = item['snippet']['topLevelComment']['snippet']
            
            # Skip empty comments
            if not comment.get('textDisplay'):
                continue
                
            record = {
                "source": "youtube",
                "raw_text": comment['textDisplay'],
                "metadata": {
                    "video_id": video_id,
                    "comment_id": item['id'],
                    "user_name": comment.get('authorDisplayName'),
                    "like_count": comment.get('likeCount'),
                    "published_at": comment.get('publishedAt')
                }
            }
            records_to_insert.append(record)
            
        if not records_to_insert:
            logger.info("No comments found for this video.")
            return []
            
        # Insert into Supabase
        logger.info(f"Inserting {len(records_to_insert)} YouTube comments into Supabase 'raw_reviews' table...")
        db_response = supabase.table("raw_reviews").insert(records_to_insert).execute()
        
        logger.info(f"Successfully inserted {len(db_response.data)} records.")
        return db_response.data
        
    except Exception as e:
        logger.error(f"Error fetching/inserting YouTube comments: {e}")
        return None

if __name__ == "__main__":
    # Test with a highly commented video (Rick Astley - Never Gonna Give You Up) just to prove it works!
    # You can change this to a Myntra haul video ID (e.g., the part after 'v=' in the URL)
    TEST_VIDEO_ID = "dQw4w9WgXcQ" 
    fetch_youtube_comments(TEST_VIDEO_ID, max_results=10)
