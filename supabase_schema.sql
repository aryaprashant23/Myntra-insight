-- Supabase SQL Schema for Myntra Wishlist Hesitation Analysis

-- 1. raw_reviews table
-- Stores the original text collected from the scrapers/APIs before any cleaning.
CREATE TABLE raw_reviews (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    source VARCHAR(50) NOT NULL, -- e.g., 'app_store', 'play_store', 'reddit', 'youtube'
    raw_text TEXT NOT NULL,
    metadata JSONB, -- Optional metadata (e.g., author username, URL, video_id)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. processed_reviews table
-- Stores the text after basic filtering and PII masking.
CREATE TABLE processed_reviews (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    raw_review_id UUID REFERENCES raw_reviews(id) ON DELETE CASCADE,
    cleaned_text TEXT NOT NULL,
    is_valid BOOLEAN DEFAULT TRUE, -- False if it failed deduplication or was too short
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. analysis_results table
-- Stores the output from the Groq AI model.
CREATE TABLE analysis_results (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    processed_review_id UUID REFERENCES processed_reviews(id) ON DELETE CASCADE,
    hesitation_tag VARCHAR(100) NOT NULL, -- e.g., 'Size/Fit', 'Price', 'Occasion'
    extracted_quote TEXT NOT NULL, -- The specific substring backing the reason
    analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Optional: Create indexes for faster aggregation and querying
CREATE INDEX idx_raw_source ON raw_reviews(source);
CREATE INDEX idx_analysis_tag ON analysis_results(hesitation_tag);
