import sys
import os
import re
import logging
import hashlib

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import supabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Regex Patterns for PII Masking
EMAIL_REGEX = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
URL_REGEX = r'https?://[^\s]+'
PHONE_REGEX = r'\b\d{10}\b|\+91[-.\s]?\d{10}'

def mask_pii(text: str) -> str:
    """Masks emails, URLs, and phone numbers in text."""
    text = re.sub(EMAIL_REGEX, '[EMAIL]', text)
    text = re.sub(URL_REGEX, '[URL]', text)
    text = re.sub(PHONE_REGEX, '[PHONE]', text)
    return text

def is_valid_text(text: str) -> bool:
    """Filters out comments < 8 words or mostly gibberish/emoji."""
    words = text.split()
    if len(words) < 8:
        return False
        
    # Check if mostly emoji/gibberish (must contain at least some alphabetic characters)
    alpha_count = sum(c.isalpha() for c in text)
    if alpha_count < 5:
        return False
        
    return True

def clean_and_process():
    logger.info("Fetching raw reviews from Supabase...")
    
    # 1. Fetch raw reviews
    raw_response = supabase.table("raw_reviews").select("*").execute()
    raw_reviews = raw_response.data
    
    if not raw_reviews:
        logger.info("No raw reviews found in database.")
        return
        
    # 2. Fetch already processed review IDs to avoid reprocessing
    processed_response = supabase.table("processed_reviews").select("raw_review_id").execute()
    processed_ids = {record['raw_review_id'] for record in processed_response.data}
    
    reviews_to_process = [r for r in raw_reviews if r['id'] not in processed_ids]
    
    if not reviews_to_process:
        logger.info("All raw reviews have already been processed.")
        return
        
    logger.info(f"Found {len(reviews_to_process)} new reviews to process.")
    
    records_to_insert = []
    seen_hashes = set()
    
    # Pre-populate seen hashes with existing processed valid reviews for cross-batch deduplication
    existing_valid_response = supabase.table("processed_reviews").select("cleaned_text").eq("is_valid", True).execute()
    for row in existing_valid_response.data:
        text_hash = hashlib.md5(row['cleaned_text'].encode('utf-8')).hexdigest()
        seen_hashes.add(text_hash)
    
    for review in reviews_to_process:
        raw_text = review.get('raw_text', '')
        if not raw_text:
            continue
            
        # PII Masking
        cleaned = mask_pii(raw_text)
        
        # Validation (word count, gibberish)
        valid = is_valid_text(cleaned)
        
        # Deduplication
        if valid:
            text_hash = hashlib.md5(cleaned.encode('utf-8')).hexdigest()
            if text_hash in seen_hashes:
                valid = False # It's a duplicate
                logger.debug("Duplicate found, marking invalid.")
            else:
                seen_hashes.add(text_hash)
                
        record = {
            "raw_review_id": review['id'],
            "cleaned_text": cleaned,
            "is_valid": valid
        }
        records_to_insert.append(record)
        
    # 3. Batch insert into processed_reviews
    if records_to_insert:
        valid_count = sum(1 for r in records_to_insert if r['is_valid'])
        logger.info(f"Inserting {len(records_to_insert)} processed records ({valid_count} valid, {len(records_to_insert) - valid_count} invalid)...")
        
        # Insert in chunks of 100 to avoid request size limits
        chunk_size = 100
        for i in range(0, len(records_to_insert), chunk_size):
            chunk = records_to_insert[i:i+chunk_size]
            supabase.table("processed_reviews").insert(chunk).execute()
            
        logger.info("Data Cleaning & Processing complete!")
    else:
        logger.info("No records to insert.")

if __name__ == "__main__":
    clean_and_process()
