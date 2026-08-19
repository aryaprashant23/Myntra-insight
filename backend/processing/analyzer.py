import sys
import os
import json
import logging
from typing import List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import supabase

from groq import Groq
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Explicitly load .env from the backend folder
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key":
    logger.error("Invalid GROQ_API_KEY in .env")
    sys.exit(1)

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """You are an expert e-commerce data analyst specifically for Myntra (the Indian fashion e-commerce platform).
Your task is to analyze user comments and determine if the user is hesitating to make a purchase ON MYNTRA.

CRITICAL RULES:
- ONLY analyze comments that are about Myntra, Myntra's app, or shopping on Myntra.
- If the comment is primarily about a COMPETITOR (Flipkart, Amazon, Ajio, Meesho, Nykaa, Tata Cliq, Snapdeal, Shein) and NOT about Myntra, return {"hesitation": false}.
- If the comment is a generic fashion opinion with no mention of Myntra or online shopping hesitation, return {"hesitation": false}.

If the user IS hesitating about a Myntra purchase, categorize the primary reason into one of these tags:
- Size/Fit
- Price
- Styling
- Occasion
- Comparing
- Window Shopping
- Delivery/Logistics
- Trust/Quality
- Other

You MUST output ONLY valid JSON in the following format:
{
  "hesitation": true/false,
  "tag": "one of the tags above" (only if hesitation is true),
  "quote": "extract the exact sub-sentence/quote backing the reason" (only if hesitation is true)
}
"""

def analyze_reviews():
    logger.info("Fetching unanalyzed processed reviews...")
    
    # 1. Fetch valid processed reviews
    processed_res = supabase.table("processed_reviews").select("id, cleaned_text").eq("is_valid", True).execute()
    valid_reviews = processed_res.data
    
    if not valid_reviews:
        logger.info("No valid processed reviews found.")
        return
        
    # 2. Fetch already analyzed review IDs to avoid duplicate API calls
    analyzed_res = supabase.table("analysis_results").select("processed_review_id").execute()
    analyzed_ids = {record["processed_review_id"] for record in analyzed_res.data}
    
    reviews_to_analyze = [r for r in valid_reviews if r["id"] not in analyzed_ids]
    
    if not reviews_to_analyze:
        logger.info("All valid reviews have already been analyzed.")
        return
        
    logger.info(f"Found {len(reviews_to_analyze)} reviews to analyze with Groq.")
    
    results_to_insert = []
    
    for review in reviews_to_analyze:
        text = review["cleaned_text"]
        logger.info(f"Analyzing review {review['id']}...")
        
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Analyze this comment:\n{text}"}
                ],
                model="openai/gpt-oss-120b",
                response_format={"type": "json_object"},
                temperature=0.0
            )
            
            response_content = chat_completion.choices[0].message.content
            response_json = json.loads(response_content)
            
            if response_json.get("hesitation"):
                tag = response_json.get("tag", "Other")
                quote = response_json.get("quote", text[:100] + "...")
                
                results_to_insert.append({
                    "processed_review_id": review["id"],
                    "hesitation_tag": tag,
                    "extracted_quote": quote
                })
                logger.info(f" -> Found hesitation: {tag}")
            else:
                logger.info(" -> No hesitation found.")
                
        except Exception as e:
            logger.error(f"Error analyzing review {review['id']}: {e}")
            
    # 3. Batch insert the findings into Supabase
    if results_to_insert:
        logger.info(f"Inserting {len(results_to_insert)} analysis results into Supabase...")
        chunk_size = 100
        for i in range(0, len(results_to_insert), chunk_size):
            chunk = results_to_insert[i:i+chunk_size]
            supabase.table("analysis_results").insert(chunk).execute()
        logger.info("Analysis complete!")
    else:
        logger.info("No hesitations found to insert.")

if __name__ == "__main__":
    analyze_reviews()
