import os
import sys
import logging
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from backend.database import supabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_tables():
    logger.info("Checking raw_reviews...")
    try:
        res = supabase.table("raw_reviews").select("*").limit(1).execute()
        logger.info(f"raw_reviews fetch success. Rows: {len(res.data)}")
    except Exception as e:
        logger.error(f"Error fetching raw_reviews: {e}")

    logger.info("Checking processed_reviews...")
    try:
        res = supabase.table("processed_reviews").select("*").limit(1).execute()
        logger.info(f"processed_reviews fetch success. Rows: {len(res.data)}")
    except Exception as e:
        logger.error(f"Error fetching processed_reviews: {e}")

if __name__ == "__main__":
    check_tables()
