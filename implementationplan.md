# Detailed Implementation Plan: Myntra Wishlist Hesitation

This document provides a detailed, phase-by-phase implementation plan tailored to the requested technology stack:
- **Database**: Supabase (PostgreSQL)
- **Backend**: Render (Python FastAPI / Node.js)
- **AI Inference**: Groq (High-speed LLMs)
- **Frontend**: Vercel (Next.js/React)

---

## Phase 1: Architecture & Infrastructure Setup
**Goal:** Initialize the environments, define the database schemas, and connect the core services.

- [x] **1.1 Set up Supabase (Database layer)**
  - Create a new project in the Supabase dashboard.
  - Define the SQL schema for three primary tables:
    - `raw_reviews` (id, source, raw_text, metadata, created_at)
    - `processed_reviews` (id, raw_review_id, cleaned_text, is_valid)
    - `analysis_results` (id, processed_review_id, hesitation_tag, extracted_quote)
  - Obtain connection strings and API keys for the backend/frontend.
- [x] **1.2 Initialize Backend Repository (Deploying to Render)**
  - Initialize a Python project (e.g., using FastAPI) as it has excellent ecosystem support for scraping and AI.
  - Set up a virtual environment and install dependencies (`fastapi`, `supabase`, `groq`, `google-play-scraper`, `praw`, `google-api-python-client`).
  - Configure `.env` variables (`SUPABASE_URL`, `SUPABASE_KEY`, `GROQ_API_KEY`, etc.).
  - Prepare deployment configurations (`requirements.txt`, `Procfile`, or `render.yaml`) for seamless Render deployment.
- [ ] **1.3 Initialize Frontend Repository (Deploying to Vercel)**
  - Initialize a Next.js project (`npx create-next-app@latest`).
  - Install frontend dependencies (Tailwind CSS, charting library like Recharts, `@supabase/supabase-js`).
  - Link the repository to Vercel for continuous deployment (CI/CD).

---

## Phase 2: Data Collection API (Backend)
**Goal:** Build the scraping and collection modules in the backend to pull data from all four sources.

- [x] **2.1 App Store Scraper Module**
  - *Status:* Implemented using Apify, but currently blocked due to Apple throwing 500 Internal Errors against cloud scrapers.
  - Format the incoming data and insert it into the `raw_reviews` table via the Supabase client.
- [x] **2.2 Play Store Scraper Module**
  - Use the `google-play-scraper` library to pull recent reviews.
  - Format and push records to `raw_reviews`.
- [x] **2.3 Reddit API Module**
  - *Status:* Implemented using Apify (`scrapers_lat/reddit-scraper`) instead of PRAW due to API restrictions. Fetched specific "myntra wishlist" related posts.
  - Extract relevant posts/comments and insert them into `raw_reviews`.
- [x] **2.4 YouTube Comments Module**
  - Integrate the YouTube Data API v3.
  - Pull comments from specified fashion haul/styling videos and push to `raw_reviews`.
- [ ] **2.5 Automation / Schedulers**
  - Create FastAPI endpoints or background workers (like Celery/APScheduler) to trigger these collection jobs periodically on Render.

---

## Phase 3: Data Cleaning & Processing (Backend)
**Goal:** Prepare the raw text for AI analysis by removing noise, spam, and PII.

- [x] **3.1 Basic Filtering Engine**
  - Build a pipeline that queries unprocessed records from `raw_reviews`.
  - Drop comments containing fewer than 8 words.
  - Drop emoji-only strings and gibberish.
- [x] **3.2 PII Masking & Deduplication**
  - Implement regex patterns to mask or strip emails, phone numbers, and URLs.
  - Apply a hashing or similarity check to flag and remove duplicate comments.
- [x] **3.3 Processed Storage**
  - Insert the cleaned, ready-to-analyze records into the `processed_reviews` table.

---

## Phase 4: AI Analysis Pipeline (Backend using Groq)
**Goal:** Use Groq's high-speed inference to tag hesitation reasons and extract quotes.

- [x] **4.1 Groq Client Integration**
  - Instantiate the Groq client in the backend using the `GROQ_API_KEY`.
- [x] **4.2 Prompt Engineering & Structured Output**
  - Define the system prompt mapping to the business requirements (Size/Fit, Price, Styling, Occasion, Comparing, Window Shopping).
  - Instruct the model (e.g., using `llama3-70b-8192` or `mixtral-8x7b-32768`) to return data in a strict JSON schema: `{ "tag": "Reason", "quote": "Exact user quote" }`.
- [x] **4.3 Batch Inference Logic**
  - Fetch batches of unanalyzed text from the `processed_reviews` table.
  - Send requests to the Groq API (taking advantage of its high speed for fast batch processing).
  - Parse the JSON responses, handle any rate limits, and insert the final `tag` and `quote` into the `analysis_results` table in Supabase.

---

## Phase 5: Measurement & Frontend Dashboard (Vercel)
**Goal:** Expose the insights through a fast, shareable UI.

- [ ] **5.1 Backend Aggregation Endpoints**
  - Create a FastAPI endpoint (e.g., `/api/metrics`) that runs SQL queries against Supabase to calculate the percentage distribution of each hesitation tag.
  - Create an endpoint (e.g., `/api/quotes/{tag}`) to fetch the real, verbatim quotes for a specific tag.
- [ ] **5.2 Next.js UI Implementation**
  - Build the main Dashboard page.
  - Fetch the aggregated data from the backend (or use the Supabase client directly in Next.js Server Components).
  - Display the ranked list of reasons visually using a bar or pie chart (e.g., Recharts).
  - Build a drill-down feature: clicking on a "Size/Fit" bar reveals a list of actual user quotes backing that metric.
- [ ] **5.3 Final Deployment & Testing**
  - Verify the backend APIs are running stably on Render.
  - Verify the Next.js frontend is deployed successfully on Vercel.
  - Test the end-to-end flow and share the live Vercel link with the product team.
