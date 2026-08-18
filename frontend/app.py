import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
from supabase import create_client

# ──────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Myntra Scraper · Precision Data Intelligence",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────
BACKEND_API_URL = st.secrets.get("BACKEND_API_URL", "https://myntra-insight-production.up.railway.app")
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://lmvwdvueptvglihzhebp.supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")


@st.cache_resource
def get_supabase_client():
    return create_client(SUPABASE_URL, SUPABASE_KEY)


# ──────────────────────────────────────────────
# CUSTOM CSS
# ──────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Geist:wght@400;500&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

    .stApp {
        background: #0b0e14 !important;
        color: #e1e2eb !important;
        font-family: 'Inter', sans-serif !important;
    }
    header[data-testid="stHeader"] { background: transparent !important; }
    .block-container { padding-top: 0.5rem !important; max-width: 1440px !important; }
    div[data-testid="stToolbar"] { display: none !important; }
    footer { display: none !important; }
    .stDeployButton { display: none !important; }

    /* ── Navbar ── */
    .navbar {
        background: rgba(16, 19, 26, 0.85);
        backdrop-filter: blur(16px);
        border-bottom: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.15);
        padding: 0.8rem 2.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-radius: 0 0 12px 12px;
        margin-bottom: 1rem;
    }
    .navbar .brand {
        font-size: 1.6rem; font-weight: 800; color: #00f0ff;
        letter-spacing: -0.5px;
    }
    .navbar .nav-links { display: flex; gap: 2rem; }
    .navbar .nav-links a {
        font-size: 15px; color: #a3adc0; text-decoration: none;
        transition: color 0.3s;
    }
    .navbar .nav-links a:hover, .navbar .nav-links a.active { color: #00f0ff; }

    /* ── Hero Section ── */
    .hero {
        text-align: center;
        padding: 3rem 2rem 2rem;
        background: radial-gradient(ellipse at center, rgba(0,240,255,0.04) 0%, transparent 70%);
    }
    .hero-badge {
        display: inline-flex; align-items: center; gap: 0.5rem;
        padding: 0.4rem 1rem; border-radius: 9999px;
        border: 1px solid rgba(57,255,20,0.25);
        background: rgba(57,255,20,0.06);
        margin-bottom: 1rem;
    }
    .hero-badge .dot {
        width: 8px; height: 8px; border-radius: 50%;
        background: #39ff14; animation: pulse 2s infinite;
    }
    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
    .hero-badge .text {
        font-size: 11px; text-transform: uppercase;
        letter-spacing: 0.06em; font-weight: 500; color: #39ff14;
    }
    .hero h1 {
        font-size: 48px; line-height: 1.1; font-weight: 800;
        letter-spacing: -0.02em; color: #e1e2eb;
        max-width: 800px; margin: 0 auto 1rem;
    }
    .hero .gradient-text {
        background: linear-gradient(to right, #00f0ff, #39ff14, #0088ff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .hero .subtitle {
        font-size: 16px; line-height: 1.6; color: #a3adc0;
        max-width: 600px; margin: 0 auto;
    }

    /* ── Glass Panel ── */
    .glass-panel {
        background: rgba(25, 28, 34, 0.4);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.05);
        border-top-color: rgba(255,255,255,0.1);
        border-radius: 1rem;
        padding: 1.5rem;
        margin-top: 1rem;
        position: relative;
        box-shadow: 0 25px 50px rgba(0,0,0,0.4);
    }
    .glass-panel .ambient-light {
        position: absolute; top: 0; left: 25%; right: 25%; height: 1px;
        background: linear-gradient(to right, transparent, #00f0ff, transparent);
        opacity: 0.5;
    }
    .dashboard-title {
        font-size: 22px; font-weight: 600; color: #e1e2eb;
        display: flex; align-items: center; gap: 0.5rem;
        margin-bottom: 0.25rem;
    }
    .dashboard-title .material-symbols-outlined { color: #00f0ff; }
    .dashboard-subtitle {
        font-size: 11px; text-transform: uppercase;
        letter-spacing: 0.05em; color: #a3adc0; margin-bottom: 1rem;
    }

    /* ── Source Column ── */
    .source-col {
        background: rgba(25, 28, 34, 0.5);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 1rem;
        height: 100%;
        transition: border-color 0.3s;
    }
    .source-col:hover { border-color: rgba(0,240,255,0.2); }
    .source-header {
        display: flex; align-items: center; gap: 0.5rem;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        padding-bottom: 0.5rem; margin-bottom: 0.75rem;
    }
    .source-header .material-symbols-outlined { font-size: 20px; }
    .source-header.reddit .material-symbols-outlined { color: #00f0ff; }
    .source-header.playstore .material-symbols-outlined { color: #39ff14; }
    .source-header.youtube .material-symbols-outlined { color: #0088ff; }
    .source-header h3 {
        font-family: 'Geist', monospace;
        font-size: 11px; text-transform: uppercase;
        letter-spacing: 0.06em; font-weight: 500;
        color: #a3adc0; margin: 0;
    }

    /* ── Scrollable reviews container ── */
    .reviews-scroll {
        max-height: 360px;
        overflow-y: auto;
        padding-right: 4px;
    }
    .reviews-scroll::-webkit-scrollbar { width: 3px; }
    .reviews-scroll::-webkit-scrollbar-track { background: transparent; }
    .reviews-scroll::-webkit-scrollbar-thumb {
        background: rgba(255,255,255,0.1); border-radius: 4px;
    }

    /* ── Review Card ── */
    .review-card {
        background: rgba(29, 32, 38, 0.45);
        border: 1px solid rgba(255,255,255,0.04);
        border-radius: 8px;
        padding: 0.7rem 0.8rem;
        margin-bottom: 0.5rem;
        transition: all 0.2s;
    }
    .review-card:hover {
        background: rgba(29, 32, 38, 0.75);
        border-color: rgba(255,255,255,0.1);
    }
    .review-card .quote {
        font-family: 'Geist', monospace;
        font-size: 13px; line-height: 1.5; color: #e1e2eb;
        margin-bottom: 0.35rem;
    }
    .tag-badge {
        font-family: 'Geist', monospace;
        font-size: 10px; text-transform: uppercase;
        letter-spacing: 0.04em; font-weight: 500;
        padding: 2px 8px; border-radius: 9999px;
        display: inline-block;
    }
    .tag-size   { color: #ffb4ab; background: rgba(255,180,171,0.1); }
    .tag-price  { color: #39ff14; background: rgba(57,255,20,0.1); }
    .tag-trust  { color: #60a5fa; background: rgba(96,165,250,0.1); }
    .tag-style  { color: #cdbdff; background: rgba(205,189,255,0.1); }
    .tag-default{ color: #a3adc0; background: rgba(163,173,192,0.08); }

    /* ── Summary Section ── */
    .summary-section {
        background: rgba(25, 28, 34, 0.8);
        border: 1px solid rgba(57,255,20,0.2);
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1.5rem;
        position: relative; overflow: hidden;
        box-shadow: 0 0 20px rgba(57,255,20,0.08);
    }
    .summary-section .glow {
        position: absolute; right: -30px; top: -30px;
        width: 200px; height: 200px;
        background: rgba(57,255,20,0.08);
        filter: blur(60px); border-radius: 50%;
        pointer-events: none;
    }
    .summary-section h3 {
        font-size: 18px; font-weight: 600; color: #e1e2eb;
        display: flex; align-items: center; gap: 0.5rem;
        margin-bottom: 1rem;
    }
    .summary-section h3 .material-symbols-outlined { color: #39ff14; }
    .summary-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1rem;
    }
    .summary-item {
        background: rgba(29, 32, 38, 0.6);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 8px; padding: 1rem;
    }
    .summary-item .label {
        font-size: 11px; text-transform: uppercase;
        letter-spacing: 0.05em; font-weight: 600;
        display: flex; align-items: center; gap: 0.4rem;
        margin-bottom: 0.5rem;
    }
    .summary-item .label.green { color: #39ff14; }
    .summary-item .label.cyan  { color: #00f0ff; }
    .summary-item .body { font-size: 15px; color: #e1e2eb; line-height: 1.5; }
    .summary-item .meta {
        font-size: 11px; color: #a3adc0;
        text-align: right; margin-top: 0.5rem;
    }

    /* ── Stat Cards ── */
    .stat-row { display: flex; gap: 1rem; margin-bottom: 1.25rem; flex-wrap: wrap; }
    .stat-card {
        flex: 1; min-width: 120px;
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 10px; padding: 1rem; text-align: center;
    }
    .stat-card .value {
        font-size: 1.8rem; font-weight: 700; color: #00f0ff;
    }
    .stat-card .label {
        font-size: 0.7rem; color: #a3adc0;
        text-transform: uppercase; letter-spacing: 1px; margin-top: 2px;
    }

    /* ── Button overrides ── */
    .stButton > button {
        background: linear-gradient(135deg, #00f0ff, #39ff14) !important;
        color: #0b0e14 !important;
        border: none !important;
        border-radius: 9999px !important;
        padding: 0.55rem 1.8rem !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.04em !important;
        box-shadow: 0 0 18px rgba(0,240,255,0.25) !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    }
    .stButton > button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 0 28px rgba(0,240,255,0.4) !important;
    }
    .stButton > button:active { transform: scale(0.95) !important; }

    /* ── Selectbox ── */
    div[data-baseweb="select"] {
        background: rgba(25,28,34,0.6) !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
    }

    /* ── Footer ── */
    .custom-footer {
        background: #10131a;
        border-top: 1px solid rgba(255,255,255,0.05);
        padding: 2rem 2.5rem;
        display: flex; justify-content: space-between;
        align-items: center; flex-wrap: wrap; gap: 1rem;
        margin-top: 3rem; border-radius: 12px 12px 0 0;
    }
    .custom-footer .brand { font-size: 20px; font-weight: 600; color: #00f0ff; }
    .custom-footer .copy { font-family: 'Geist', monospace; font-size: 13px; color: #a3adc0; }
    .custom-footer .links { display: flex; gap: 1.5rem; }
    .custom-footer .links a {
        font-family: 'Geist', monospace; font-size: 13px; color: #a3adc0;
        text-decoration: none; transition: color 0.3s;
    }
    .custom-footer .links a:hover { color: #39ff14; }

    .no-data { text-align: center; padding: 2rem; color: rgba(255,255,255,0.25); }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────
def get_tag_class(tag: str) -> str:
    t = tag.lower()
    if "size" in t or "fit" in t:      return "tag-size"
    if "price" in t or "cost" in t:    return "tag-price"
    if "trust" in t or "quality" in t: return "tag-trust"
    if "style" in t or "occasion" in t or "fashion" in t: return "tag-style"
    return "tag-default"


def build_review_cards_html(df, source_type):
    """Build the HTML for all review cards in a scrollable container."""
    if df.empty:
        return '<div class="no-data">No data in this time range</div>'

    cards = []
    for _, row in df.iterrows():
        tag_class = get_tag_class(row["hesitation_tag"])
        cards.append(f"""
        <div class="review-card">
            <div class="quote">"{row["extracted_quote"]}"</div>
            <span class="tag-badge {tag_class}">{row["hesitation_tag"]}</span>
        </div>""")

    return '<div class="reviews-scroll">' + "\n".join(cards) + '</div>'


@st.cache_data(ttl=60)
def fetch_data(days: int):
    client = get_supabase_client()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

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

    pr_ids = list({r["processed_review_id"] for r in analysis_data if r.get("processed_review_id")})
    source_map = {}
    if pr_ids:
        pr_resp = client.table("processed_reviews").select("id, raw_review_id").in_("id", pr_ids).execute()
        pr_data = pr_resp.data or []
        raw_ids = list({r["raw_review_id"] for r in pr_data if r.get("raw_review_id")})
        pr_to_raw = {r["id"]: r["raw_review_id"] for r in pr_data}
        if raw_ids:
            raw_resp = client.table("raw_reviews").select("id, source").in_("id", raw_ids).execute()
            raw_data = raw_resp.data or []
            raw_to_source = {r["id"]: r["source"] for r in raw_data}
            for pr_id, raw_id in pr_to_raw.items():
                source_map[pr_id] = raw_to_source.get(raw_id, "unknown")

    for row in analysis_data:
        row["source"] = source_map.get(row.get("processed_review_id"), "unknown")

    df = pd.DataFrame(analysis_data)
    reddit_df = df[df["source"].str.contains("reddit", case=False, na=False)]
    playstore_df = df[df["source"].str.contains("play", case=False, na=False)]
    youtube_df = df[df["source"].str.contains("youtube", case=False, na=False)]
    return df, reddit_df, playstore_df, youtube_df


# ═══════════════════════════════════════════════
#                    LAYOUT
# ═══════════════════════════════════════════════

# ── Navbar ──
st.markdown("""
<div class="navbar">
    <div class="brand">Myntra Scraper</div>
    <div class="nav-links">
        <a href="#" class="active">Dashboard</a>
        <a href="#">Documentation</a>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Hero ──
st.markdown("""
<div class="hero">
    <div class="hero-badge">
        <div class="dot"></div>
        <span class="text">AI Engine v2.4 Active</span>
    </div>
    <h1>
        Command the Flow of<br>
        <span class="gradient-text">Consumer Intelligence</span>
    </h1>
    <p class="subtitle">
        Deploy hyper-scale scrapers across fashion networks.
        Synthesize behavioral data into actionable foresight instantly.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Controls Row: Scrape Button + Time Filter + Refresh ──
st.markdown("")  # spacer
c1, c2, c3 = st.columns([1.5, 1, 1])
with c1:
    scrape_clicked = st.button("⚡  SCRAPE DATA", use_container_width=True)
with c2:
    time_filter = st.selectbox(
        "Time", [7, 15, 30],
        format_func=lambda x: f"📅 Last {x} Days",
        index=2, label_visibility="collapsed",
    )
with c3:
    refresh_clicked = st.button("🔄  REFRESH", use_container_width=True)


# ── Handle Scrape ──
if scrape_clicked:
    with st.status("⚡ Triggering scrape pipeline on Railway...", expanded=True) as status:
        st.write("Sending POST to Railway backend...")
        try:
            resp = requests.post(
                f"{BACKEND_API_URL}/api/scrape",
                json={"source": "all"},
                timeout=30
            )
            if resp.status_code == 200:
                status.update(label="✅ Pipeline triggered! Data will appear in ~2 minutes.", state="complete")
                st.toast("Scraping started in background. Click Refresh shortly!", icon="🎉")
            else:
                status.update(label=f"⚠️ Backend returned {resp.status_code}", state="error")
                st.error(f"Response: {resp.text}")
        except requests.exceptions.ConnectionError:
            status.update(label="❌ Cannot reach Railway backend", state="error")
            st.error(f"Could not connect to {BACKEND_API_URL}. Check if Railway is running.")
        except Exception as e:
            status.update(label="❌ Request failed", state="error")
            st.error(str(e))

if refresh_clicked:
    st.cache_data.clear()
    st.rerun()

# ── Fetch Data ──
df_all, df_reddit, df_playstore, df_youtube = fetch_data(time_filter)

# ── Glass Panel Dashboard ──
st.markdown("""
<div class="glass-panel">
    <div class="ambient-light"></div>
    <div class="dashboard-title">
        <span class="material-symbols-outlined">dashboard</span>
        Analytics Console
    </div>
    <div class="dashboard-subtitle">Real-time data stream visualization</div>
""", unsafe_allow_html=True)

if not df_all.empty:
    # ── Stat Cards ──
    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-card">
            <div class="value">{len(df_all)}</div>
            <div class="label">Total Insights</div>
        </div>
        <div class="stat-card">
            <div class="value">{len(df_reddit)}</div>
            <div class="label">Reddit</div>
        </div>
        <div class="stat-card">
            <div class="value">{len(df_playstore)}</div>
            <div class="label">Play Store</div>
        </div>
        <div class="stat-card">
            <div class="value">{len(df_youtube)}</div>
            <div class="label">YouTube</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Three Columns with Scrollable Review Boxes ──
    col_r, col_p, col_y = st.columns(3)

    with col_r:
        reddit_html = build_review_cards_html(df_reddit, "reddit")
        st.markdown(f"""
        <div class="source-col">
            <div class="source-header reddit">
                <span class="material-symbols-outlined">forum</span>
                <h3>Reddit Sentiment ({len(df_reddit)})</h3>
            </div>
            {reddit_html}
        </div>
        """, unsafe_allow_html=True)

    with col_p:
        playstore_html = build_review_cards_html(df_playstore, "playstore")
        st.markdown(f"""
        <div class="source-col">
            <div class="source-header playstore">
                <span class="material-symbols-outlined">shop</span>
                <h3>Play Store Reviews ({len(df_playstore)})</h3>
            </div>
            {playstore_html}
        </div>
        """, unsafe_allow_html=True)

    with col_y:
        youtube_html = build_review_cards_html(df_youtube, "youtube")
        st.markdown(f"""
        <div class="source-col">
            <div class="source-header youtube">
                <span class="material-symbols-outlined">smart_display</span>
                <h3>YouTube Comments ({len(df_youtube)})</h3>
            </div>
            {youtube_html}
        </div>
        """, unsafe_allow_html=True)

    # ── Summary Section ──
    tag_counts = df_all["hesitation_tag"].value_counts()
    total = len(df_all)

    items_html = ""
    colors = ["green", "cyan", "green", "cyan"]
    icons = ["trending_up", "notifications_active", "insights", "query_stats"]
    for i, (tag, count) in enumerate(tag_counts.head(4).items()):
        pct = round(count / total * 100, 1)
        color = colors[i % len(colors)]
        icon = icons[i % len(icons)]
        sample = df_all[df_all["hesitation_tag"] == tag].iloc[0]["extracted_quote"]
        items_html += f"""
        <div class="summary-item">
            <div class="label {color}">
                <span class="material-symbols-outlined" style="font-size:16px;">{icon}</span>
                {tag} · {pct}%
            </div>
            <div class="body">"{sample}"</div>
            <div class="meta">{count} mentions</div>
        </div>"""

    st.markdown(f"""
    <div class="summary-section">
        <div class="glow"></div>
        <h3>
            <span class="material-symbols-outlined">insights</span>
            Summary: Top Hesitation Reasons
        </h3>
        <div class="summary-grid">
            {items_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div style="text-align:center; padding: 3rem;">
        <p style="font-size: 3rem; margin-bottom: 0.5rem;">🔍</p>
        <h2 style="color: rgba(255,255,255,0.35); font-size: 1.3rem;">No data found</h2>
        <p style="color: rgba(255,255,255,0.2); font-size: 0.9rem;">
            Click <strong>⚡ SCRAPE DATA</strong> above to trigger the pipeline, or adjust the time range.
        </p>
    </div>
    """, unsafe_allow_html=True)

# Close glass panel
st.markdown('</div>', unsafe_allow_html=True)

# ── Footer ──
st.markdown("""
<div class="custom-footer">
    <div style="display:flex; align-items:center; gap:1.5rem;">
        <div class="brand">Myntra Scraper</div>
        <div class="copy">© 2024 Myntra Scraper AI. Precision Data Intelligence.</div>
    </div>
    <div class="links">
        <a href="#">Privacy Policy</a>
        <a href="#">Terms of Service</a>
        <a href="#">API Docs</a>
        <a href="#">Contact</a>
    </div>
</div>
""", unsafe_allow_html=True)
