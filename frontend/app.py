import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
from supabase import create_client

# ──────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Myntra Insight · Hesitation Dashboard",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────
# CONFIGURATION (secrets managed by Streamlit)
# ──────────────────────────────────────────────
BACKEND_API_URL = st.secrets.get("BACKEND_API_URL", "https://myntra-insight-production.up.railway.app")
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://lmvwdvueptvglihzhebp.supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")


@st.cache_resource
def get_supabase_client():
    """Create a cached Supabase client."""
    return create_client(SUPABASE_URL, SUPABASE_KEY)


# ──────────────────────────────────────────────
# CUSTOM CSS  –  dark, premium aesthetic
# ──────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Global overrides ── */
    .stApp {
        background: linear-gradient(145deg, #0a0a0f 0%, #111118 50%, #0d0d14 100%);
    }
    header[data-testid="stHeader"] {
        background: transparent;
    }

    /* ── Hero banner ── */
    .hero-banner {
        background: linear-gradient(135deg, #6c3baa 0%, #3b82f6 50%, #06b6d4 100%);
        border-radius: 16px;
        padding: 2.5rem 2rem;
        margin-bottom: 1.5rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(108, 59, 170, 0.3);
    }
    .hero-banner h1 {
        color: white;
        font-size: 2.4rem;
        font-weight: 800;
        margin: 0 0 0.4rem 0;
        letter-spacing: -0.5px;
    }
    .hero-banner p {
        color: rgba(255,255,255,0.85);
        font-size: 1.05rem;
        margin: 0;
    }

    /* ── Stat cards ── */
    .stat-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 1.2rem 1rem;
        text-align: center;
        backdrop-filter: blur(12px);
    }
    .stat-card .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #a78bfa;
    }
    .stat-card .stat-label {
        font-size: 0.8rem;
        color: rgba(255,255,255,0.5);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.25rem;
    }

    /* ── Column headers ── */
    .column-header {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        text-align: center;
    }
    .column-header h3 {
        margin: 0;
        font-size: 1.1rem;
        font-weight: 600;
    }

    /* ── Review cards ── */
    .review-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.6rem;
        transition: background 0.2s ease, border-color 0.2s ease;
    }
    .review-card:hover {
        background: rgba(255,255,255,0.06);
        border-color: rgba(167,139,250,0.3);
    }
    .review-card .quote {
        font-size: 0.88rem;
        color: rgba(255,255,255,0.85);
        line-height: 1.5;
        margin-bottom: 0.5rem;
        font-style: italic;
    }
    .review-card .tag {
        display: inline-block;
        font-size: 0.68rem;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        padding: 3px 10px;
        border-radius: 20px;
        font-weight: 600;
    }
    .tag-size   { background: rgba(239,68,68,0.15); color: #f87171; }
    .tag-price  { background: rgba(234,179,8,0.15);  color: #facc15; }
    .tag-trust  { background: rgba(59,130,246,0.15); color: #60a5fa; }
    .tag-style  { background: rgba(168,85,247,0.15); color: #c084fc; }
    .tag-other  { background: rgba(255,255,255,0.08); color: rgba(255,255,255,0.6); }

    /* ── Summary box ── */
    .summary-box {
        background: linear-gradient(135deg, rgba(108,59,170,0.1), rgba(59,130,246,0.1));
        border: 1px solid rgba(167,139,250,0.2);
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1rem;
    }

    /* ── Button overrides ── */
    .stButton > button {
        background: linear-gradient(135deg, #7c3aed, #3b82f6) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 2rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(124,58,237,0.4) !important;
    }

    /* ── Selectbox style ── */
    div[data-baseweb="select"] {
        background: rgba(255,255,255,0.04) !important;
        border-radius: 10px !important;
    }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# HELPER FUNCTIONS
# ──────────────────────────────────────────────

def get_tag_class(tag: str) -> str:
    """Map a hesitation tag to a CSS class."""
    t = tag.lower()
    if "size" in t or "fit" in t:
        return "tag-size"
    if "price" in t or "money" in t or "cost" in t:
        return "tag-price"
    if "trust" in t or "quality" in t:
        return "tag-trust"
    if "style" in t or "fashion" in t or "occasion" in t:
        return "tag-style"
    return "tag-other"


def render_review_card(quote: str, tag: str):
    """Render a single review card as HTML."""
    tag_class = get_tag_class(tag)
    st.markdown(f"""
    <div class="review-card">
        <div class="quote">"{quote}"</div>
        <span class="tag {tag_class}">{tag}</span>
    </div>
    """, unsafe_allow_html=True)


@st.cache_data(ttl=60)
def fetch_data(days: int):
    """Fetch analysis results joined with raw_reviews from Supabase."""
    client = get_supabase_client()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

    # Fetch analysis results
    analysis_resp = (
        client.table("analysis_results")
        .select("id, hesitation_tag, extracted_quote, processed_review_id, analyzed_at")
        .gte("analyzed_at", cutoff)
        .order("analyzed_at", desc=True)
        .execute()
    )
    analysis_data = analysis_resp.data or []

    if not analysis_data:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    # Get processed_review_ids to look up the raw source
    pr_ids = list({r["processed_review_id"] for r in analysis_data if r.get("processed_review_id")})

    source_map = {}
    if pr_ids:
        # Fetch processed_reviews to get raw_review_ids
        pr_resp = (
            client.table("processed_reviews")
            .select("id, raw_review_id")
            .in_("id", pr_ids)
            .execute()
        )
        pr_data = pr_resp.data or []
        raw_ids = list({r["raw_review_id"] for r in pr_data if r.get("raw_review_id")})
        pr_to_raw = {r["id"]: r["raw_review_id"] for r in pr_data}

        if raw_ids:
            # Fetch raw_reviews to get source
            raw_resp = (
                client.table("raw_reviews")
                .select("id, source")
                .in_("id", raw_ids)
                .execute()
            )
            raw_data = raw_resp.data or []
            raw_to_source = {r["id"]: r["source"] for r in raw_data}

            # Build final mapping: processed_review_id -> source
            for pr_id, raw_id in pr_to_raw.items():
                source_map[pr_id] = raw_to_source.get(raw_id, "unknown")

    # Attach source to each analysis row
    for row in analysis_data:
        row["source"] = source_map.get(row.get("processed_review_id"), "unknown")

    df = pd.DataFrame(analysis_data)

    # Split by source
    reddit_df = df[df["source"].str.contains("reddit", case=False, na=False)]
    playstore_df = df[df["source"].str.contains("play", case=False, na=False)]
    youtube_df = df[df["source"].str.contains("youtube", case=False, na=False)]

    return df, reddit_df, playstore_df, youtube_df


# ──────────────────────────────────────────────
# HERO BANNER
# ──────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
    <h1>🔍 Myntra Insight</h1>
    <p>Real-time AI analysis of why users hesitate to buy from their Myntra wishlists</p>
</div>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# CONTROLS ROW
# ──────────────────────────────────────────────
ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([2, 1, 1])

with ctrl_col1:
    time_filter = st.selectbox(
        "📅 Time Range",
        options=[7, 15, 30],
        format_func=lambda x: f"Last {x} days",
        index=0,
        label_visibility="collapsed",
    )

with ctrl_col2:
    scrape_clicked = st.button("🚀 Scrape Data", use_container_width=True)

with ctrl_col3:
    refresh_clicked = st.button("🔄 Refresh", use_container_width=True)


# ──────────────────────────────────────────────
# HANDLE SCRAPE BUTTON
# ──────────────────────────────────────────────
if scrape_clicked:
    with st.status("⚡ Triggering scrape pipeline on Railway...", expanded=True) as status:
        st.write("Sending request to backend...")
        try:
            resp = requests.post(f"{BACKEND_API_URL}/api/scrape", json={"source": "all"}, timeout=30)
            if resp.status_code == 200:
                status.update(label="✅ Scrape pipeline triggered successfully!", state="complete")
                st.toast("Pipeline is running in the background. Data will appear shortly!", icon="🎉")
            else:
                status.update(label=f"⚠️ Backend returned status {resp.status_code}", state="error")
                st.error(f"Response: {resp.text}")
        except requests.exceptions.ConnectionError:
            status.update(label="❌ Cannot reach Railway backend", state="error")
            st.error("Make sure your Railway service is running and the URL is correct.")
        except Exception as e:
            status.update(label="❌ Request failed", state="error")
            st.error(str(e))

if refresh_clicked:
    st.cache_data.clear()


# ──────────────────────────────────────────────
# FETCH & DISPLAY DATA
# ──────────────────────────────────────────────
df_all, df_reddit, df_playstore, df_youtube = fetch_data(time_filter)

# ── Stat Cards ──
if not df_all.empty:
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{len(df_all)}</div>
            <div class="stat-label">Total Insights</div>
        </div>
        """, unsafe_allow_html=True)
    with s2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{len(df_reddit)}</div>
            <div class="stat-label">Reddit</div>
        </div>
        """, unsafe_allow_html=True)
    with s3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{len(df_playstore)}</div>
            <div class="stat-label">Play Store</div>
        </div>
        """, unsafe_allow_html=True)
    with s4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{len(df_youtube)}</div>
            <div class="stat-label">YouTube</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Three-column layout ──
    col_reddit, col_playstore, col_youtube = st.columns(3)

    with col_reddit:
        st.markdown("""
        <div class="column-header">
            <h3>🟠 Reddit Hesitations</h3>
        </div>
        """, unsafe_allow_html=True)
        if df_reddit.empty:
            st.caption("No Reddit data in this time range.")
        else:
            for _, row in df_reddit.iterrows():
                render_review_card(row["extracted_quote"], row["hesitation_tag"])

    with col_playstore:
        st.markdown("""
        <div class="column-header">
            <h3>🟢 Play Store Hesitations</h3>
        </div>
        """, unsafe_allow_html=True)
        if df_playstore.empty:
            st.caption("No Play Store data in this time range.")
        else:
            for _, row in df_playstore.iterrows():
                render_review_card(row["extracted_quote"], row["hesitation_tag"])

    with col_youtube:
        st.markdown("""
        <div class="column-header">
            <h3>🔴 YouTube Hesitations</h3>
        </div>
        """, unsafe_allow_html=True)
        if df_youtube.empty:
            st.caption("No YouTube data in this time range.")
        else:
            for _, row in df_youtube.iterrows():
                render_review_card(row["extracted_quote"], row["hesitation_tag"])

    # ── Summary Section ──
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="summary-box">', unsafe_allow_html=True)
    st.markdown("### 📊 Summary: Top Hesitation Reasons")

    tag_counts = df_all["hesitation_tag"].value_counts()
    total = len(df_all)

    summary_cols = st.columns(min(len(tag_counts), 4))
    for i, (tag, count) in enumerate(tag_counts.head(4).items()):
        with summary_cols[i]:
            pct = round(count / total * 100, 1)
            st.metric(label=tag, value=f"{pct}%", delta=f"{count} mentions")

    st.markdown('</div>', unsafe_allow_html=True)

else:
    # ── Empty state ──
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center; padding: 3rem;">
        <h2 style="color: rgba(255,255,255,0.4);">No data found</h2>
        <p style="color: rgba(255,255,255,0.25);">
            Click <strong>🚀 Scrape Data</strong> to trigger the pipeline, or adjust the time range.
        </p>
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────
st.markdown("---")
st.caption("Built with Streamlit · Data from Supabase · AI by Groq · Scraping via Railway")
