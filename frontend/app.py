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
# FULL CUSTOM CSS — matching code.html design
# ──────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Import fonts ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Geist:wght@400;500&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

    /* ── Reset Streamlit defaults ── */
    .stApp {
        background: #0b0e14 !important;
        color: #e1e2eb !important;
        font-family: 'Inter', sans-serif !important;
    }
    header[data-testid="stHeader"] { background: transparent !important; }
    .block-container { padding-top: 1rem !important; max-width: 1440px !important; }
    div[data-testid="stToolbar"] { display: none !important; }
    footer { display: none !important; }
    .stDeployButton { display: none !important; }

    /* ── Navbar ── */
    .navbar {
        background: rgba(16, 19, 26, 0.8);
        backdrop-filter: blur(16px);
        border-bottom: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.15);
        padding: 1rem 2.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: -1rem -1rem 0 -1rem;
        position: sticky;
        top: 0;
        z-index: 50;
    }
    .navbar .brand {
        font-family: 'Inter', sans-serif;
        font-size: 2rem;
        font-weight: 800;
        color: #00f0ff;
        letter-spacing: -0.5px;
    }
    .navbar .nav-links {
        display: flex;
        gap: 2rem;
        align-items: center;
    }
    .navbar .nav-links a {
        font-size: 16px;
        color: #a3adc0;
        text-decoration: none;
        transition: color 0.3s;
    }
    .navbar .nav-links a:hover { color: #00f0ff; }
    .navbar .nav-links a.active {
        color: #00f0ff;
        border-bottom: 2px solid #00f0ff;
        padding-bottom: 4px;
    }
    .nav-buttons { display: flex; gap: 1rem; align-items: center; }
    .btn-login {
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 500;
        color: #39ff14;
        border: 1px solid rgba(57,255,20,0.5);
        border-radius: 9999px;
        padding: 0.5rem 1.5rem;
        background: transparent;
        cursor: pointer;
    }
    .btn-launch {
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 500;
        background: #00f0ff;
        color: #003322;
        border-radius: 9999px;
        padding: 0.5rem 1.5rem;
        border: none;
        box-shadow: 0 0 20px rgba(0,240,255,0.3);
        cursor: pointer;
    }

    /* ── Hero Section ── */
    .hero {
        position: relative;
        min-height: 70vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 6rem 2rem 8rem;
        overflow: hidden;
        background: radial-gradient(circle at center, transparent 0%, rgba(11,14,20,0.95) 100%),
                    linear-gradient(135deg, rgba(0,240,255,0.05), rgba(57,255,20,0.05));
    }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 9999px;
        border: 1px solid rgba(57,255,20,0.2);
        background: rgba(57,255,20,0.05);
        backdrop-filter: blur(8px);
        margin-bottom: 1.5rem;
    }
    .hero-badge .dot {
        width: 8px; height: 8px;
        border-radius: 50%;
        background: #39ff14;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.4; }
    }
    .hero-badge span.text {
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 500;
        color: #39ff14;
    }
    .hero h1 {
        font-family: 'Inter', sans-serif;
        font-size: 72px;
        line-height: 1.05;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: #e1e2eb;
        max-width: 900px;
        margin: 0 auto 1.5rem;
    }
    .hero h1 .gradient-text {
        background: linear-gradient(to right, #00f0ff, #39ff14, #0088ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .hero .subtitle {
        font-size: 18px;
        line-height: 1.6;
        color: #a3adc0;
        max-width: 640px;
        margin: 0 auto;
    }

    /* ── Glass Panel (Dashboard Container) ── */
    .glass-panel {
        background: rgba(25, 28, 34, 0.4);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.05);
        border-top-color: rgba(255,255,255,0.1);
        border-left-color: rgba(255,255,255,0.1);
        border-radius: 1rem;
        padding: 1.5rem;
        margin-top: -4rem;
        position: relative;
        box-shadow: 0 25px 50px rgba(0,0,0,0.5);
    }
    .glass-panel .ambient-light {
        position: absolute;
        top: 0; left: 25%; right: 25%; height: 1px;
        background: linear-gradient(to right, transparent, #00f0ff, transparent);
        opacity: 0.5;
    }
    .dashboard-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
        flex-wrap: wrap;
        gap: 1rem;
    }
    .dashboard-header h2 {
        font-size: 24px; font-weight: 600;
        color: #e1e2eb;
        display: flex; align-items: center; gap: 0.5rem;
    }
    .dashboard-header h2 .material-symbols-outlined { color: #00f0ff; }
    .dashboard-header .subtitle {
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #a3adc0;
        margin-top: 4px;
    }

    /* ── Source Column ── */
    .source-column {
        background: rgba(25, 28, 34, 0.5);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 1rem;
        transition: border-color 0.3s;
        display: flex;
        flex-direction: column;
    }
    .source-column:hover { border-color: rgba(0,240,255,0.3); }
    .source-column.reddit:hover { border-color: rgba(0,240,255,0.3); }
    .source-column.playstore:hover { border-color: rgba(57,255,20,0.3); }
    .source-column.youtube:hover { border-color: rgba(0,136,255,0.3); }

    .source-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 1rem;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        padding-bottom: 0.5rem;
    }
    .source-header .material-symbols-outlined { font-size: 20px; }
    .source-header.reddit .material-symbols-outlined { color: #00f0ff; }
    .source-header.playstore .material-symbols-outlined { color: #39ff14; }
    .source-header.youtube .material-symbols-outlined { color: #0088ff; }
    .source-header h3 {
        font-family: 'Geist', monospace;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 500;
        color: #a3adc0;
        margin: 0;
    }

    /* ── Review Card ── */
    .review-card {
        background: rgba(29, 32, 38, 0.4);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 8px;
        padding: 0.75rem;
        margin-bottom: 0.5rem;
        transition: background 0.2s, border-color 0.2s;
    }
    .review-card:hover {
        background: rgba(29, 32, 38, 0.7);
        border-color: rgba(255,255,255,0.1);
    }
    .review-card .quote {
        font-family: 'Geist', monospace;
        font-size: 13px;
        line-height: 1.5;
        color: #e1e2eb;
        margin-bottom: 0.4rem;
    }
    .review-card .tag-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .tag-badge {
        font-family: 'Geist', monospace;
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 2px 8px;
        border-radius: 9999px;
    }
    .tag-negative, .tag-size { color: #ffb4ab; }
    .tag-positive, .tag-price { color: #39ff14; }
    .tag-neutral, .tag-trust { color: #a3adc0; }
    .tag-style { color: #cdbdff; }
    .tag-default { color: #a3adc0; }

    /* ── Summary Section ── */
    .summary-section {
        background: rgba(25, 28, 34, 0.8);
        border: 1px solid rgba(57,255,20,0.2);
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1.5rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 0 20px rgba(57,255,20,0.1);
    }
    .summary-section .glow {
        position: absolute;
        right: 0; top: 0;
        width: 256px; height: 256px;
        background: rgba(57,255,20,0.1);
        filter: blur(48px);
        border-radius: 50%;
        pointer-events: none;
    }
    .summary-section h3 {
        font-size: 20px; font-weight: 600;
        color: #e1e2eb;
        display: flex; align-items: center; gap: 0.5rem;
        margin-bottom: 1rem;
    }
    .summary-section h3 .material-symbols-outlined { color: #39ff14; }
    .summary-item {
        background: rgba(29, 32, 38, 0.6);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 8px;
        padding: 1rem;
    }
    .summary-item .label {
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 500;
        display: flex; align-items: center; gap: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .summary-item .label.trending { color: #39ff14; }
    .summary-item .label.alert { color: #00f0ff; }
    .summary-item .body { font-size: 16px; color: #e1e2eb; line-height: 1.5; }
    .summary-item .meta {
        font-size: 12px; color: #a3adc0;
        text-align: right;
        margin-top: 0.5rem;
    }

    /* ── Footer ── */
    .custom-footer {
        background: #10131a;
        border-top: 1px solid rgba(255,255,255,0.05);
        padding: 3rem 2.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 1rem;
        margin: 4rem -1rem -1rem -1rem;
    }
    .custom-footer .brand { font-size: 24px; font-weight: 600; color: #00f0ff; }
    .custom-footer .copy { font-family: 'Geist', monospace; font-size: 14px; color: #a3adc0; }
    .custom-footer .links { display: flex; gap: 1.5rem; }
    .custom-footer .links a {
        font-family: 'Geist', monospace;
        font-size: 14px; color: #a3adc0;
        text-decoration: none;
        transition: color 0.3s;
    }
    .custom-footer .links a:hover { color: #39ff14; }

    /* ── Streamlit widget overrides ── */
    .stSelectbox label, .stButton > button { font-family: 'Inter', sans-serif !important; }
    div[data-baseweb="select"] { background: rgba(25,28,34,0.6) !important; border-radius: 8px !important; border: 1px solid rgba(255,255,255,0.1) !important; }
    .stButton > button {
        background: linear-gradient(to right, #00f0ff, #39ff14) !important;
        color: #0b0e14 !important;
        border: none !important;
        border-radius: 9999px !important;
        padding: 0.6rem 2rem !important;
        font-weight: 600 !important;
        font-size: 12px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        box-shadow: 0 0 20px rgba(0,240,255,0.3) !important;
        transition: transform 0.15s ease !important;
    }
    .stButton > button:hover {
        transform: scale(1.05) !important;
    }
    .stButton > button:active {
        transform: scale(0.95) !important;
    }
    div[data-testid="stMetricValue"] { color: #00f0ff !important; font-family: 'Inter', sans-serif !important; }
    div[data-testid="stMetricLabel"] { color: #a3adc0 !important; }
    div[data-testid="stMetricDelta"] { color: #39ff14 !important; }

    /* ── Scrollbar ── */
    .reviews-scroll {
        max-height: 300px;
        overflow-y: auto;
        padding-right: 0.5rem;
    }
    .reviews-scroll::-webkit-scrollbar { width: 4px; }
    .reviews-scroll::-webkit-scrollbar-track { background: transparent; }
    .reviews-scroll::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 4px; }

    /* ── Empty state ── */
    .empty-state {
        text-align: center; padding: 4rem 2rem;
    }
    .empty-state h2 { color: rgba(255,255,255,0.3); font-size: 1.5rem; }
    .empty-state p { color: rgba(255,255,255,0.15); margin-top: 0.5rem; }
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


# ──────────────────────────────────────────────
# NAVBAR
# ──────────────────────────────────────────────
st.markdown("""
<div class="navbar">
    <div class="brand">Myntra Scraper</div>
    <div class="nav-links">
        <a href="#" class="active">Features</a>
        <a href="#">Pricing</a>
        <a href="#">Documentation</a>
    </div>
    <div class="nav-buttons">
        <button class="btn-login">Login</button>
        <button class="btn-launch">Launch App</button>
    </div>
</div>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# HERO SECTION
# ──────────────────────────────────────────────
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
        Deploy hyper-scale scrapers across fashion networks. Synthesize behavioral data into actionable foresight instantly. Built for the modern data vanguard.
    </p>
</div>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# CONTROLS (inside the glass panel)
# ──────────────────────────────────────────────
ctrl1, ctrl2, ctrl3 = st.columns([2, 1, 1])
with ctrl1:
    time_filter = st.selectbox(
        "Time Range",
        options=[7, 15, 30],
        format_func=lambda x: f"📅 Last {x} Days",
        index=2,
        label_visibility="collapsed",
    )
with ctrl2:
    scrape_clicked = st.button("⚡ Scrape Data", use_container_width=True)
with ctrl3:
    refresh_clicked = st.button("🔄 Refresh", use_container_width=True)


# ──────────────────────────────────────────────
# HANDLE SCRAPE
# ──────────────────────────────────────────────
if scrape_clicked:
    with st.status("⚡ Triggering scrape pipeline on Railway...", expanded=True) as status:
        st.write("Sending request to backend...")
        try:
            resp = requests.post(f"{BACKEND_API_URL}/api/scrape", json={"source": "all"}, timeout=30)
            if resp.status_code == 200:
                status.update(label="✅ Scrape pipeline triggered! Data will appear shortly.", state="complete")
                st.toast("Pipeline is running in the background. Click Refresh in ~2 min.", icon="🎉")
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
# GLASS PANEL — DASHBOARD
# ──────────────────────────────────────────────
df_all, df_reddit, df_playstore, df_youtube = fetch_data(time_filter)

st.markdown("""
<div class="glass-panel">
    <div class="ambient-light"></div>
    <div class="dashboard-header">
        <div>
            <h2><span class="material-symbols-outlined">dashboard</span> Analytics Console</h2>
            <div class="subtitle">Real-time data stream visualization</div>
        </div>
    </div>
""", unsafe_allow_html=True)

if not df_all.empty:
    # ── Three-column bento grid ──
    col_r, col_p, col_y = st.columns(3)

    with col_r:
        st.markdown("""
        <div class="source-column reddit">
            <div class="source-header reddit">
                <span class="material-symbols-outlined">forum</span>
                <h3>Reddit Sentiment</h3>
            </div>
        """, unsafe_allow_html=True)
        if df_reddit.empty:
            st.caption("No Reddit data in this time range.")
        else:
            st.markdown('<div class="reviews-scroll">', unsafe_allow_html=True)
            for _, row in df_reddit.iterrows():
                tag_class = get_tag_class(row["hesitation_tag"])
                st.markdown(f"""
                <div class="review-card">
                    <div class="quote">"{row["extracted_quote"]}"</div>
                    <div class="tag-row">
                        <span class="tag-badge {tag_class}">{row["hesitation_tag"]}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_p:
        st.markdown("""
        <div class="source-column playstore">
            <div class="source-header playstore">
                <span class="material-symbols-outlined">shop</span>
                <h3>Play Store Reviews</h3>
            </div>
        """, unsafe_allow_html=True)
        if df_playstore.empty:
            st.caption("No Play Store data in this time range.")
        else:
            st.markdown('<div class="reviews-scroll">', unsafe_allow_html=True)
            for _, row in df_playstore.iterrows():
                tag_class = get_tag_class(row["hesitation_tag"])
                st.markdown(f"""
                <div class="review-card">
                    <div class="quote">"{row["extracted_quote"]}"</div>
                    <div class="tag-row">
                        <span class="tag-badge {tag_class}">{row["hesitation_tag"]}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_y:
        st.markdown("""
        <div class="source-column youtube">
            <div class="source-header youtube">
                <span class="material-symbols-outlined">smart_display</span>
                <h3>YouTube Comments</h3>
            </div>
        """, unsafe_allow_html=True)
        if df_youtube.empty:
            st.caption("No YouTube data in this time range.")
        else:
            st.markdown('<div class="reviews-scroll">', unsafe_allow_html=True)
            for _, row in df_youtube.iterrows():
                tag_class = get_tag_class(row["hesitation_tag"])
                st.markdown(f"""
                <div class="review-card">
                    <div class="quote">"{row["extracted_quote"]}"</div>
                    <div class="tag-row">
                        <span class="tag-badge {tag_class}">{row["hesitation_tag"]}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Summary Section ──
    tag_counts = df_all["hesitation_tag"].value_counts()
    total = len(df_all)
    top_tag = tag_counts.index[0] if len(tag_counts) > 0 else "N/A"
    top_count = tag_counts.iloc[0] if len(tag_counts) > 0 else 0
    second_tag = tag_counts.index[1] if len(tag_counts) > 1 else "N/A"
    second_count = tag_counts.iloc[1] if len(tag_counts) > 1 else 0

    # Get example quotes for top tags
    top_quote = df_all[df_all["hesitation_tag"] == top_tag].iloc[0]["extracted_quote"] if top_tag != "N/A" else ""
    second_quote = df_all[df_all["hesitation_tag"] == second_tag].iloc[0]["extracted_quote"] if second_tag != "N/A" and not df_all[df_all["hesitation_tag"] == second_tag].empty else ""

    st.markdown(f"""
    <div class="summary-section">
        <div class="glow"></div>
        <h3><span class="material-symbols-outlined">insights</span> Summary: Top Hesitations</h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div class="summary-item">
                <div class="label trending">
                    <span class="material-symbols-outlined" style="font-size:16px;">trending_up</span>
                    #{1} Hesitation · {round(top_count/total*100, 1)}%
                </div>
                <div class="body">"{top_quote}"</div>
                <div class="meta">{top_tag} · {top_count} mentions</div>
            </div>
            <div class="summary-item">
                <div class="label alert">
                    <span class="material-symbols-outlined" style="font-size:16px;">notifications_active</span>
                    #{2} Hesitation · {round(second_count/total*100, 1)}%
                </div>
                <div class="body">"{second_quote}"</div>
                <div class="meta">{second_tag} · {second_count} mentions</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div class="empty-state">
        <h2>No data found</h2>
        <p>Click <strong>⚡ Scrape Data</strong> to trigger the pipeline, or adjust the time range.</p>
    </div>
    """, unsafe_allow_html=True)

# Close glass panel
st.markdown('</div>', unsafe_allow_html=True)


# ──────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────
st.markdown("""
<div class="custom-footer">
    <div style="display:flex; align-items:center; gap:2rem;">
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
