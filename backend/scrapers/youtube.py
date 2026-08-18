import sys
import os
import logging
from googleapiclient.discovery import build

# Add the parent directory to the path so we can import the database module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import supabase

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")

# Myntra-specific fashion haul / review video IDs
# These are real Indian fashion YouTuber videos about Myntra hauls & reviews
MYNTRA_VIDEO_IDS = [
    # Search for "Myntra haul" or "Myntra review" on YouTube and paste the video ID
    # (the part after ?v= in the URL)
]

# Search queries to auto-discover Myntra videos
MYNTRA_SEARCH_QUERIES = [
    "Myntra haul 2024",
    "Myntra wishlist try on",
    "Myntra shopping review",
    "Myntra sale haul",
    "Myntra fashion haul India",
]


def search_myntra_videos(youtube, max_videos_per_query: int = 5):
    """
    Search YouTube for Myntra-related videos and return their video IDs.
    """
    video_ids = set()

    for query in MYNTRA_SEARCH_QUERIES:
        logger.info(f"Searching YouTube for: '{query}'")
        try:
            search_response = youtube.search().list(
                q=query,
                part="id",
                type="video",
                maxResults=max_videos_per_query,
                order="date",
                relevanceLanguage="en",
                regionCode="IN",
            ).execute()

            for item in search_response.get("items", []):
                vid = item["id"].get("videoId")
                if vid:
                    video_ids.add(vid)
        except Exception as e:
            logger.warning(f"Search failed for '{query}': {e}")

    logger.info(f"Found {len(video_ids)} unique Myntra-related videos.")
    return list(video_ids)


def fetch_youtube_comments(video_id: str, youtube, max_results: int = 50):
    """
    Fetches top-level comments from a specific YouTube video and stores them in Supabase.
    Only keeps comments that mention Myntra or are clearly about Myntra products.
    """
    logger.info(f"Fetching up to {max_results} comments from YouTube video '{video_id}'...")

    try:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=max_results,
            textFormat="plainText"
        )
        response = request.execute()

        records_to_insert = []
        myntra_keywords = [
            "myntra", "wishlist", "haul", "try on", "size", "fit",
            "delivery", "return", "refund", "quality", "price",
            "sale", "coupon", "order", "app", "buy", "bought",
            "cart", "checkout", "brand", "outfit", "dress", "kurta",
            "jeans", "shirt", "fashion", "style", "review"
        ]

        for item in response.get("items", []):
            comment = item["snippet"]["topLevelComment"]["snippet"]
            text = comment.get("textDisplay", "")

            if not text:
                continue

            # Filter: keep only comments relevant to Myntra / fashion shopping
            text_lower = text.lower()
            is_relevant = any(kw in text_lower for kw in myntra_keywords)

            if not is_relevant:
                continue

            record = {
                "source": "youtube",
                "raw_text": text,
                "metadata": {
                    "video_id": video_id,
                    "comment_id": item["id"],
                    "user_name": comment.get("authorDisplayName"),
                    "like_count": comment.get("likeCount"),
                    "published_at": comment.get("publishedAt"),
                }
            }
            records_to_insert.append(record)

        if not records_to_insert:
            logger.info(f"No relevant Myntra comments found for video {video_id}.")
            return []

        # Insert into Supabase
        logger.info(f"Inserting {len(records_to_insert)} YouTube comments into Supabase...")
        db_response = supabase.table("raw_reviews").insert(records_to_insert).execute()

        logger.info(f"Successfully inserted {len(db_response.data)} records.")
        return db_response.data

    except Exception as e:
        logger.error(f"Error fetching comments for video {video_id}: {e}")
        return None


def main():
    if not YOUTUBE_API_KEY or YOUTUBE_API_KEY.startswith("your_"):
        logger.error("YOUTUBE_API_KEY is missing or invalid in .env file.")
        return

    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    # Combine hardcoded video IDs with auto-discovered ones
    all_video_ids = list(MYNTRA_VIDEO_IDS)

    # Search for fresh Myntra videos
    discovered_ids = search_myntra_videos(youtube, max_videos_per_query=3)
    all_video_ids.extend(discovered_ids)

    # Deduplicate
    all_video_ids = list(set(all_video_ids))

    if not all_video_ids:
        logger.warning("No Myntra video IDs found. Skipping YouTube scraping.")
        return

    logger.info(f"Scraping comments from {len(all_video_ids)} Myntra videos...")
    total_inserted = 0
    for vid in all_video_ids:
        result = fetch_youtube_comments(vid, youtube, max_results=50)
        if result:
            total_inserted += len(result)

    logger.info(f"YouTube scraping complete. Total comments inserted: {total_inserted}")


if __name__ == "__main__":
    main()
