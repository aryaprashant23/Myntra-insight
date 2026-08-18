# Edge Cases & Corner Scenarios

This document outlines potential edge cases, corner scenarios, and failure points for the Myntra Wishlist Hesitation Analysis system, organized by architectural phase. Addressing these ensures the system remains robust in production.

## 1. Data Collection Phase
*   **API Rate Limiting & IP Bans**: 
    *   *Scenario*: Pulling data too aggressively from Reddit, YouTube, or Google Play results in HTTP 429 (Too Many Requests) or IP bans.
    *   *Mitigation*: Implement exponential backoff, respect API rate limit headers, and utilize proxies for the scraper modules if necessary.
*   **Data Structure Changes**: 
    *   *Scenario*: Apple changes their public RSS feed format or Google Play updates their DOM, breaking the `google-play-scraper`.
    *   *Mitigation*: Implement try/catch blocks that trigger alerts (e.g., via Slack/Email) when parsing fails, rather than silently failing or inserting `null` records into Supabase.
*   **Traffic Spikes (Sale Events)**: 
    *   *Scenario*: During Myntra's Big Fashion Festival, the volume of reviews and comments spikes by 10x, overwhelming the Render backend.
    *   *Mitigation*: Process collection in paginated chunks and utilize background workers (e.g., Celery) to queue jobs so the main API doesn't time out.

## 2. Data Cleaning Phase
*   **Mixed Languages & "Hinglish"**: 
    *   *Scenario*: A user writes a comment in a mix of Hindi and English (e.g., "Size fit nahi hua"). 
    *   *Mitigation*: Ensure the LLM prompt explicitly supports understanding Hinglish, or add a pre-processing step that translates or drops non-English text if the LLM struggles with it.
*   **Aggressive PII Masking**: 
    *   *Scenario*: The regex for phone numbers accidentally redacts valid product serial numbers, or email regex redacts a specific styling term.
    *   *Mitigation*: Use strict, well-tested Regex boundaries and consider using Named Entity Recognition (NER) libraries instead of blind Regex.
*   **Extremely Long Reviews**: 
    *   *Scenario*: A user writes a 2000-word essay about their shopping experience, which exceeds the context window or slows down the AI inference.
    *   *Mitigation*: Truncate reviews to a sensible character limit (e.g., 1000 characters) before inserting them into the `processed_reviews` table.

## 3. AI Understanding Phase (Groq)
*   **Multiple Hesitation Reasons**: 
    *   *Scenario*: A user writes, "I wasn't sure if the size would fit, plus it's too expensive right now." Which category should it fall under?
    *   *Mitigation*: Instruct the LLM in the prompt to either (a) pick the *primary* (first mentioned or most emphasized) reason, or (b) allow the schema to return an array of tags `["Size/Fit", "Price"]` and handle the multi-tag logic in the frontend.
*   **LLM Hallucination / Invalid JSON**: 
    *   *Scenario*: Groq returns a tag that is not in our predefined list (e.g., "Delivery Issue"), or the JSON is malformed due to a stray quote mark.
    *   *Mitigation*: Use a schema validation library (like Pydantic in Python) to validate the Groq response. If it fails, retry the prompt or flag the record as `analysis_failed` in Supabase.
*   **Sarcasm & Contradictions**: 
    *   *Scenario*: "I love paying 3000 rupees for a shirt that looks like a potato sack."
    *   *Mitigation*: The prompt should explicitly ask the LLM to identify the underlying sentiment/hesitation (Price & Styling) rather than taking positive words at face value.
*   **Irrelevant Complaints**: 
    *   *Scenario*: A review complains about the delivery boy being late or the app crashing, which has nothing to do with wishlist hesitation.
    *   *Mitigation*: Add an "Irrelevant / Unrelated" category to the predefined tag list so the LLM can safely discard these.

## 4. Measurement & Dashboard Phase (Vercel)
*   **Empty States (Zero Data)**: 
    *   *Scenario*: The database is fresh, or a specific category has exactly 0 records. The UI attempts to calculate a percentage and throws a "Divide by Zero" error.
    *   *Mitigation*: Implement empty state UI components and mathematical fallbacks in the Next.js frontend.
*   **Database Timeouts**: 
    *   *Scenario*: Querying millions of records to calculate metrics slows down the API, causing Vercel's serverless functions to time out (usually 10s or 50s limit).
    *   *Mitigation*: Instead of computing aggregations on the fly, use Supabase materialized views or run a daily cron job on Render to pre-calculate the metrics into a `daily_metrics` table.
