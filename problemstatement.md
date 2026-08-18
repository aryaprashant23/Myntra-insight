# Problem Statement: Myntra Wishlist Hesitation

## 1. The Problem, In One Paragraph
Millions of people save clothes and accessories to their Myntra wishlist — but very few of them actually come back and buy those items. The company wants more of those saved items to turn into real purchases, without offering discounts or cashback. 

Before we can fix this, we first need to find out why people save something but then hesitate — and that reason is not written down anywhere. It's hidden inside thousands of casual conversations people are already having online: app reviews, Reddit posts, YouTube comments. This project builds an AI system that reads all of that for us and tells us the real reasons, in a clear, ranked list.

## 2. What This System Actually Does (End to End)
Think of it as a very fast, very patient research assistant. It does four things, in order:

1. **Collects** public comments about online fashion shopping from four places: App Store reviews, Play Store reviews, Reddit/fashion forums, and YouTube comments.
2. **Cleans** that raw text — throws away spam, one-word junk, emoji-only comments, and anything that could identify a real person.
3. **Uses AI to Understand** and read each comment, tagging WHY the person seems to be hesitating — is it about size and fit? Price? Not sure how to style it? Waiting for an occasion?
4. **Measures** and counts up all those tags and produces a simple ranked report — "this is the #1 reason people don't buy what they wishlist, this is #2," and so on — backed by real quotes.

The end output is a shareable link: a report anyone on the team can open and understand in five minutes, without reading a single raw review themselves.

## 3. How It Works — Visual Flow
*(See architecture for the visual flow of data from collection to reporting.)*

## 4. Each Step, Explained Simply

### Step 1 — Collect
We don't need to "hack" anything or ask anyone for special access. All four sources are public:
- **App Store reviews:** Apple provides a free, public feed of recent reviews (no login needed).
- **Play Store reviews:** A free, publicly available tool reads reviews straight off the Play Store listing page.
- **Reddit:** Reddit's free API lets us pull posts and comments from fashion/shopping communities.
- **YouTube comments:** YouTube's free API lets us pull comments from fashion haul and review videos.

### Step 2 — Clean
Raw internet text is messy. Before the AI looks at anything, we strip out:
- Very short comments (under 8 words) — usually too vague to be useful.
- Emoji-only or spam-like comments.
- Anything that could identify a real person — usernames, emails, device IDs.
- Duplicate or near-duplicate comments.

### Step 3 — Understand (This is the AI part)
This is the core of the system. Each cleaned comment is passed to an AI model, which reads it the way a researcher would and tags it against a fixed list of possible reasons, for example:
- Not sure about size or fit
- Waiting for a price drop or sale
- Not sure how to style it / pair it with other clothes
- Saving it for a future occasion (wedding, festival, trip)
- Comparing it with similar items on other apps
- Just "window shopping" — never really intended to buy

The AI also notes which real quote it came from, so nothing in the final report is made up — every finding is backed by an actual sentence someone wrote.

### Step 4 — Measure
Once every comment has a tag, we simply count them. This turns hundreds of scattered opinions into one clear ranking — e.g., "38% of hesitation comments are about fit and size, 24% are about price-waiting," and so on. This ranking is what tells us where to focus the actual product solution.
