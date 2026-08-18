# Context: Myntra Wishlist Hesitation Analysis

## 1. The Problem
Millions of people save clothes and accessories to their Myntra wishlist, but very few actually purchase those items. The company wants to increase the conversion rate of these saved items into real purchases without relying on discounts or cashback. 

To solve this, we need to uncover the hidden reasons for user hesitation. These reasons are often buried in casual online conversations: app reviews, Reddit posts, and YouTube comments. This project aims to build an AI system that reads these conversations and extracts the real reasons for hesitation into a clear, ranked list.

## 2. System Overview
The system acts as an automated, fast, and patient research assistant. It follows a four-step pipeline:

1. **Collect**: Gathers public comments about online fashion shopping from four sources: App Store reviews, Play Store reviews, Reddit (fashion forums), and YouTube comments.
2. **Clean**: Filters the raw text to remove spam, one-word junk, emoji-only comments, and personally identifiable information (PII).
3. **Understand**: Utilizes AI to analyze each cleaned comment and tag the underlying reason for hesitation (e.g., size/fit, price, styling, occasion).
4. **Measure**: Aggregates the tags to produce a ranked report of the top hesitation reasons, backed by real user quotes.

The final output is a shareable report that team members can easily consume in five minutes without reading raw reviews.

## 3. Detailed Workflow

### Step 1 — Collect
The system collects data from public sources without requiring special access:
- **App Store reviews**: Accessed via Apple's free, public feed of recent reviews.
- **Play Store reviews**: Scraped using a free, publicly available tool from the listing page.
- **Reddit**: Posts and comments from fashion/shopping communities are pulled using Reddit's free API.
- **YouTube comments**: Comments from fashion haul and review videos are pulled using YouTube's free API.

### Step 2 — Clean
To prepare the text for AI analysis, the system removes:
- Very short comments (under 8 words).
- Emoji-only or spam-like comments.
- Personally identifiable information (usernames, emails,V device IDs).
- Duplicate or near-duplicate comments.

### Step 3 — Understand (AI Analysis)
Each cleaned comment is processed by an AI model that tags the reason for hesitation based on a predefined list, such as:
- Uncertainty about size or fit.
- Waiting for a price drop or sale.
- Uncertainty about styling or pairing with other clothes.
- Saving for a future occasion (wedding, festival, trip).
- Comparing with similar items on other apps.
- Just "window shopping" with no intent to buy.

The AI also records the original quote so that every finding in the final report is backed by real user sentiment.

### Step 4 — Measure
The tagged comments are aggregated to generate a clear ranking (e.g., "38% of hesitation comments are about fit and size, 24% are about price-waiting"). This ranking helps the product team focus on the most impactful solutions.
