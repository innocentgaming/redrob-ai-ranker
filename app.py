import os
import json
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Ensure directories are in path
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.ranking_engine import RankingEngine
from src.explainability import ExplainabilityEngine
from src.validator import SubmissionValidator
from src.evaluate import RankEvaluator
from src.job_analyzer import JobAnalyzer

# ==========================================
# 1. PAGE CONFIGURATION & THEME STATE
# ==========================================
st.set_page_config(
    page_title="Redrob AI Recruiter",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"

IS_DARK = st.session_state.theme == "dark"

# ==========================================
# 2. CUSTOM CSS DESIGN SYSTEM
# ==========================================
bg = "#09090b" if IS_DARK else "#ffffff"
bg_subtle = "#0c0c0f" if IS_DARK else "#f9fafb"
card = "#0c0c0f" if IS_DARK else "#ffffff"
border = "#1e1e24" if IS_DARK else "#e4e4e7"
border_subtle = "#16161a" if IS_DARK else "#f0f0f2"
text = "#fafafa" if IS_DARK else "#09090b"
text_muted = "#71717a"
text_dim = "#52525b" if IS_DARK else "#a1a1aa"
accent = "#2563eb"
green = "#22c55e" if IS_DARK else "#16a34a"
green_muted = "rgba(34,197,94,0.12)" if IS_DARK else "rgba(22,163,74,0.08)"
red = "#ef4444" if IS_DARK else "#dc2626"
red_muted = "rgba(239,68,68,0.12)" if IS_DARK else "rgba(220,38,38,0.08)"
amber = "#f59e0b" if IS_DARK else "#d97706"
amber_muted = "rgba(245,158,11,0.12)" if IS_DARK else "rgba(217,119,6,0.08)"
shadow = "none" if IS_DARK else "0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.03)"

css = f"""
<style>
    /* Hide Streamlit chrome */
    header[data-testid="stHeader"], #MainMenu, footer, [data-testid="stToolbar"],
    [data-testid="stDecoration"], [data-testid="stStatusWidget"], .stDeployButton,
    div[data-testid="stSidebarCollapsedControl"] {{
        display: none !important;
    }}
    
    /* Global App Styling */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .main, .block-container, section[data-testid="stMain"] {{
        background-color: {bg} !important;
        color: {text} !important;
        font-family: 'DM Sans', -apple-system, sans-serif !important;
    }}
    .block-container {{
        padding: 1.5rem 2rem 2rem !important;
        max-width: 1360px !important;
    }}
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {{
        background-color: {bg_subtle} !important;
        border-right: 1px solid {border} !important;
    }}
    [data-testid="stSidebar"] .block-container {{
        padding: 1.5rem 1rem !important;
    }}
    
    /* Tabs (pill-style) */
    button[data-baseweb="tab"] {{
        background: transparent !important;
        color: {text_muted} !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        padding: 0.6rem 1.2rem !important;
        border: 1px solid transparent !important;
        border-radius: 7px !important;
        transition: all 0.2s ease !important;
    }}
    button[data-baseweb="tab"]:hover {{
        color: {text} !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: {text} !important;
        background: {card} !important;
        border-color: {border} !important;
        box-shadow: {shadow} !important;
    }}
    [data-baseweb="tab-highlight"], [data-baseweb="tab-border"] {{
        display: none !important;
    }}
    [data-baseweb="tab-list"] {{
        gap: 6px !important;
        background: {bg_subtle} !important;
        border: 1px solid {border} !important;
        border-radius: 10px !important;
        padding: 4px;
        margin-bottom: 1.5rem !important;
    }}
    
    /* KPI Cards */
    .metric-card {{
        background: {card};
        border: 1px solid {border};
        border-radius: 10px;
        padding: 1.2rem 1.4rem;
        box-shadow: {shadow};
        transition: all 0.2s ease;
    }}
    .metric-card:hover {{
        border-color: {accent};
    }}
    .metric-label {{
        font-size: 0.78rem;
        color: {text_muted};
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    .metric-value {{
        font-size: 1.8rem;
        font-weight: 700;
        color: {text};
        letter-spacing: -0.02em;
        margin-top: 0.2rem;
    }}
    .metric-delta {{
        font-size: 0.75rem;
        font-weight: 500;
        margin-top: 0.4rem;
        padding: 2px 8px;
        border-radius: 6px;
        display: inline-flex;
        align-items: center;
        gap: 3px;
    }}
    .delta-up {{ color: {green}; background: {green_muted}; }}
    .delta-down {{ color: {red}; background: {red_muted}; }}
    .delta-warn {{ color: {amber}; background: {amber_muted}; }}
    
    /* Chart Containers */
    .chart-wrap {{
        background: {card};
        border: 1px solid {border};
        border-radius: 10px;
        padding: 1.2rem;
        box-shadow: {shadow};
        margin-bottom: 1.25rem;
    }}
    .chart-title {{
        font-size: 0.85rem;
        font-weight: 600;
        color: {text};
        margin-bottom: 0.2rem;
    }}
    .chart-subtitle {{
        font-size: 0.72rem;
        color: {text_muted};
        margin-bottom: 1rem;
    }}
    
    /* HTML Data Tables */
    .data-table {{
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        font-size: 0.82rem;
        margin-top: 0.5rem;
    }}
    .data-table th {{
        text-align: left;
        padding: 0.75rem 0.9rem;
        color: {text_muted};
        font-weight: 600;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        border-bottom: 1px solid {border};
        background-color: {bg_subtle};
    }}
    .data-table td {{
        padding: 0.8rem 0.9rem;
        color: {text};
        border-bottom: 1px solid {border_subtle};
        vertical-align: middle;
    }}
    .data-table tr:hover td {{
        background-color: {bg_subtle};
    }}
    .data-table tr:last-child td {{
        border-bottom: none;
    }}
    
    /* Badges */
    .badge {{
        display: inline-block;
        padding: 3px 9px;
        border-radius: 6px;
        font-size: 0.72rem;
        font-weight: 600;
    }}
    .badge-green {{ color: {green}; background: {green_muted}; border: 1px solid rgba(34,197,94,0.2); }}
    .badge-red {{ color: {red}; background: {red_muted}; border: 1px solid rgba(239,68,68,0.2); }}
    .badge-amber {{ color: {amber}; background: {amber_muted}; border: 1px solid rgba(245,158,11,0.2); }}
    .badge-blue {{ color: {accent}; background: rgba(37,99,235,0.1); border: 1px solid rgba(37,99,235,0.2); }}
    
    /* Custom Timeline */
    .timeline {{
        position: relative;
        padding-left: 1.5rem;
        margin: 1rem 0;
        border-left: 2px solid {border};
    }}
    .timeline-item {{
        position: relative;
        margin-bottom: 1.5rem;
    }}
    .timeline-item::before {{
        content: "";
        position: absolute;
        left: -1.95rem;
        top: 0.25rem;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background-color: {accent};
        border: 2px solid {bg};
    }}
    .timeline-date {{
        font-size: 0.72rem;
        color: {text_muted};
        font-weight: 500;
        margin-bottom: 0.15rem;
    }}
    .timeline-title {{
        font-size: 0.85rem;
        font-weight: 600;
        color: {text};
    }}
    .timeline-company {{
        font-size: 0.78rem;
        color: {text_muted};
        margin-bottom: 0.4rem;
        font-weight: 500;
    }}
    .timeline-desc {{
        font-size: 0.78rem;
        color: {text_dim};
        line-height: 1.4;
    }}
    
    /* Brand Header */
    .brand-container {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 1.2rem;
        border-bottom: 1px solid {border};
        margin-bottom: 1.5rem;
    }}
    .brand-title {{
        font-size: 1.25rem;
        font-weight: 700;
        color: {text};
        letter-spacing: -0.02em;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .brand-icon {{
        color: {accent};
        font-weight: 800;
    }}
    
    /* Row columns gap */
    [data-testid="stHorizontalBlock"] {{
        gap: 1.25rem !important;
    }}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# ==========================================
# 3. HELPER FUNCTIONS & METRIC CARDS
# ==========================================
def metric_card(label, value, delta=None, delta_type="up"):
    cls = f"delta-{delta_type}"
    arrow = "↑" if delta_type == "up" else ("↓" if delta_type == "down" else "⚠")
    delta_html = f'<div class="metric-delta {cls}">{arrow} {delta}</div>' if delta else ""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

# Plotly Global Theme Layout
PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color="#71717a" if not IS_DARK else "#a1a1aa", size=11),
    margin=dict(l=40, r=20, t=20, b=30),
    xaxis=dict(
        gridcolor="rgba(0,0,0,0.05)" if not IS_DARK else "rgba(255,255,255,0.05)",
        zerolinecolor="rgba(0,0,0,0.05)" if not IS_DARK else "rgba(255,255,255,0.05)",
        tickfont=dict(size=10, color="#71717a"),
    ),
    yaxis=dict(
        gridcolor="rgba(0,0,0,0.05)" if not IS_DARK else "rgba(255,255,255,0.05)",
        zerolinecolor="rgba(0,0,0,0.05)" if not IS_DARK else "rgba(255,255,255,0.05)",
        tickfont=dict(size=10, color="#71717a"),
    ),
)

# ==========================================
# 4. LOAD DATASETS
# ==========================================
@st.cache_data
def load_data():
    # If files don't exist, we must generate them
    if not os.path.exists("data/candidates.jsonl") or not os.path.exists("data/jobs.csv"):
        # We call generate data
        from src.generate_data import generate_candidates, generate_jobs
        import src.generate_data as gd
        gd.UNIVERSITIES = ["IIT Bombay", "IIT Delhi", "IIT Madras", "BITS Pilani", "IIIT Hyderabad", "Delhi Technological University", "Anna University", "VIT University", "Stanford University", "MIT", "Carnegie Mellon University"]
        gd.DEGREES = ["B.Tech in Computer Science", "Dual Degree (B.Tech + M.Tech) in CS", "M.Tech in Artificial Intelligence", "B.E. in Information Technology", "M.S. in Computer Science", "B.Tech in Civil Engineering", "MBA in HR Management"]
        generate_candidates()
        generate_jobs()
        
    candidates = []
    with open("data/candidates.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                candidates.append(json.loads(line))
                
    jobs_df = pd.read_csv("data/jobs.csv")
    return candidates, jobs_df

try:
    candidates, jobs_df = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Initialize session state for custom candidates
if "custom_candidates" not in st.session_state:
    st.session_state.custom_candidates = []

# Merge base candidates with custom uploaded/manually added candidates
all_candidates = candidates + st.session_state.custom_candidates

# ==========================================
# 5. SIDEBAR CONTROLS
# ==========================================
with st.sidebar:
    # Brand Header
    st.markdown(f"""
    <div class="brand-container">
        <div class="brand-title">
            <span class="brand-icon">◆</span>
            <span>Redrob Ranker</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Theme Toggle
    theme_btn_label = "☀️ Light Theme" if IS_DARK else "🌙 Dark Theme"
    st.button(theme_btn_label, on_click=toggle_theme, use_container_width=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.subheader("1. Job Requirements")
    
    # Preset Selector
    preset_titles = list(jobs_df["title"].unique()) + ["+ Paste Custom Job Description"]
    selected_preset = st.selectbox("Choose a Job Profile", preset_titles)
    
    custom_jd_text = ""
    if selected_preset == "+ Paste Custom Job Description":
        custom_jd_text = st.text_area(
            "Paste Job Description Here",
            height=200,
            value="Looking for a Python Developer with ML experience, FastAPI knowledge, AWS deployment experience and 3+ years experience"
        )
        jd_text = custom_jd_text
    else:
        preset_row = jobs_df[jobs_df["title"] == selected_preset].iloc[0]
        jd_text = preset_row["description"]
        # Show preset details
        st.markdown(f"""
        <div style="background:{card}; border:1px solid {border}; border-radius:8px; padding:10px; margin-top:8px; font-size:0.75rem;">
            <b>Department:</b> {preset_row['department']}<br>
            <b>Experience:</b> {preset_row['experience_min']} - {preset_row['experience_max']} years<br>
            <b>Location:</b> {preset_row['location_preference']}
        </div>
        """, unsafe_allow_html=True)
        
    st.subheader("2. Scoring Weightages")
    st.caption("Adjust weight distributions (must sum to 100%)")
    
    w_sem = st.slider("Semantic Fit (%)", 0, 100, 40)
    w_skl = st.slider("Skills Match (%)", 0, 100, 25)
    w_exp = st.slider("Experience Match (%)", 0, 100, 15)
    w_beh = st.slider("Behavioral Signals (%)", 0, 100, 10)
    w_gro = st.slider("Growth Potential (%)", 0, 100, 10)
    
    # Normalize weights
    total_w = w_sem + w_skl + w_exp + w_beh + w_gro
    if total_w == 0:
        total_w = 1e-9
    weights = {
        "semantic": w_sem / total_w,
        "skills": w_skl / total_w,
        "experience": w_exp / total_w,
        "behavioral": w_beh / total_w,
        "growth": w_gro / total_w
    }
    
    if total_w != 100:
        st.warning(f"Weights sum to {total_w}%. Automatically normalized to 100%.")
        
    st.subheader("3. Hard Filtering Toggles")
    filter_honeypot = st.checkbox("Block Honeypot Resumes", value=True)
    filter_domain = st.checkbox("Block Wrong Domains", value=True)
    filter_experience = st.checkbox("Strict Experience Bounds", value=True)

# ==========================================
# 6. RUN ENGINE AND SCORE CANDIDATES
# ==========================================
@st.cache_data
def get_scored_candidates(candidates_data, jd, w, f_hp, f_dom, f_exp):
    # Initialize ranking engine
    engine = RankingEngine()
    
    # Extract structural info for summary
    jd_struct = JobAnalyzer.analyze_job_description(jd)
    
    # Compute ranked candidates
    ranked = engine.rank_candidates(
        candidates_data, 
        jd, 
        weights=w,
        apply_honeypot=f_hp, 
        apply_domain=f_dom, 
        apply_experience_filter=f_exp
    )
    return ranked, jd_struct

scored_candidates, jd_struct = get_scored_candidates(
    all_candidates, 
    jd_text, 
    weights, 
    filter_honeypot, 
    filter_domain, 
    filter_experience
)

# Calculate stats
total_pool = len(all_candidates)
scored_count = len(scored_candidates)
flagged_honeypots = sum(1 for c in all_candidates if RankingEngine.is_honeypot(c))
avg_score = np.mean([sc["final_score"] for sc in scored_candidates]) if scored_count > 0 else 0.0

# ==========================================
# 7. EXECUTIVE TABS
# ==========================================
tab_dash, tab_rank, tab_detail, tab_eval, tab_add = st.tabs([
    "📊 Executive Dashboard", 
    "🏆 Candidate shortlists", 
    "👤 Deep-Dive Profile",
    "🧪 Evaluation & Benchmark",
    "➕ Add External Candidates"
])

# ------------------------------------------
# TAB 1: EXECUTIVE DASHBOARD
# ------------------------------------------
with tab_dash:
    # KPI metrics row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Total Candidate Pool", total_pool, "Global Resumes")
    with c2:
        metric_card("Scored & Filtered", scored_count, f"{total_pool - scored_count} Filtered out", "down" if (total_pool - scored_count) > 0 else "up")
    with c3:
        metric_card("Avg Matching Score", f"{avg_score * 100:.1f}%", "Overall pool fit")
    with c4:
        # Honeypots flagged
        metric_card("Flagged Honeypots", flagged_honeypots, "Fraudulent Resumes", "warn" if flagged_honeypots > 0 else "up")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Charts Row 1
    col_ch1, col_ch2 = st.columns(2)
    
    with col_ch1:
        st.markdown("""
        <div class="chart-wrap">
            <div class="chart-title">Matching Score Distribution</div>
            <div class="chart-subtitle">Distribution of final matching scores among qualified candidates</div>
        """, unsafe_allow_html=True)
        
        if scored_count > 0:
            scores_df = pd.DataFrame([sc["final_score"] * 100 for sc in scored_candidates], columns=["Score"])
            fig_hist = px.histogram(
                scores_df, 
                x="Score", 
                nbins=12,
                color_discrete_sequence=[accent]
            )
            fig_hist.update_layout(
                **PLOT_LAYOUT,
                xaxis_title="Final Match Score (%)",
                yaxis_title="Count of Candidates",
                showlegend=False
            )
            st.plotly_chart(fig_hist, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No candidates qualified after filters.")
            
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_ch2:
        st.markdown("""
        <div class="chart-wrap">
            <div class="chart-title">Top 8 Candidate Comparison</div>
            <div class="chart-subtitle">Direct comparison of top-scoring candidates across core dimensions</div>
        """, unsafe_allow_html=True)
        
        if scored_count > 0:
            top8 = scored_candidates[:8]
            top8_data = []
            for sc in top8:
                c_name = sc["candidate"]["profile"]["name"]
                top8_data.append({"Candidate": c_name, "Dimension": "Semantic Fit", "Score": sc["semantic_score"] * 100})
                top8_data.append({"Candidate": c_name, "Dimension": "Skills Match", "Score": sc["skills_score"] * 100})
                top8_data.append({"Candidate": c_name, "Dimension": "Experience Match", "Score": sc["experience_score"] * 100})
                top8_data.append({"Candidate": c_name, "Dimension": "Behavioral", "Score": sc["behavior_score"] * 100})
                top8_data.append({"Candidate": c_name, "Dimension": "Growth Potential", "Score": sc["growth_score"] * 100})
                
            top8_df = pd.DataFrame(top8_data)
            fig_bar = px.bar(
                top8_df,
                x="Candidate",
                y="Score",
                color="Dimension",
                barmode="group",
                color_discrete_sequence=[accent, "#10b981", "#f59e0b", "#8b5cf6", "#ec4899"]
            )
            fig_bar.update_layout(
                **PLOT_LAYOUT,
                xaxis_title="Candidates",
                yaxis_title="Dimension Score (%)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No candidates qualified after filters.")
            
        st.markdown("</div>", unsafe_allow_html=True)

    # Job Extraction Insights Card
    st.markdown(f"""
    <div class="chart-wrap">
        <div class="chart-title">AI Job Analysis Extraction Summary</div>
        <div class="chart-subtitle">Structured requirements parsed from the Job Description</div>
        <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:15px; font-size:0.8rem; margin-top:10px;">
            <div style="background:{bg_subtle}; padding:10px; border-radius:6px; border:1px solid {border};">
                <span style="color:{text_muted}; font-size:0.7rem; text-transform:uppercase;">Extracted Title</span><br>
                <b>{jd_struct['title']}</b>
            </div>
            <div style="background:{bg_subtle}; padding:10px; border-radius:6px; border:1px solid {border};">
                <span style="color:{text_muted}; font-size:0.7rem; text-transform:uppercase;">Industry Domain</span><br>
                <b>{jd_struct['domain']}</b>
            </div>
            <div style="background:{bg_subtle}; padding:10px; border-radius:6px; border:1px solid {border};">
                <span style="color:{text_muted}; font-size:0.7rem; text-transform:uppercase;">Experience Target</span><br>
                <b>{jd_struct['experience_min']} - {jd_struct['experience_max']} Years</b>
            </div>
            <div style="background:{bg_subtle}; padding:10px; border-radius:6px; border:1px solid {border};">
                <span style="color:{text_muted}; font-size:0.7rem; text-transform:uppercase;">Preferred Locations</span><br>
                <b>{', '.join(jd_struct['location_preference']) if jd_struct['location_preference'] else 'Any Location'}</b>
            </div>
        </div>
        <div style="margin-top:15px; font-size:0.8rem;">
            <b>Must-Have Core Skills:</b><br>
            {" ".join([f'<span class="badge badge-blue" style="margin:2px 4px 2px 0;">{s}</span>' for s in jd_struct['required_skills']]) if jd_struct['required_skills'] else 'None extracted'}<br><br>
            <b>Preferred Nice-To-Have Skills:</b><br>
            {" ".join([f'<span class="badge badge-green" style="margin:2px 4px 2px 0;">{s}</span>' for s in jd_struct['preferred_skills']]) if jd_struct['preferred_skills'] else 'None extracted'}
        </div>
    </div>
    """, unsafe_allow_html=True)

# ------------------------------------------
# TAB 2: CANDIDATE SHORTLISTS (RANKING)
# ------------------------------------------
with tab_rank:
    # Controls for tabular shortlist
    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([4, 3, 3])
    with col_ctrl1:
        search_query = st.text_input("Search by Name or Skills", placeholder="e.g. Python, Candidate AI...")
    with col_ctrl2:
        min_score_filter = st.slider("Minimum Fitness Score (%)", 0, 100, 40)
    with col_ctrl3:
        location_filter = st.selectbox("Filter by Location", ["All Locations"] + list(np.unique([c["profile"]["current_location"] for c in candidates])))
        
    # Apply filtering
    filtered_list = []
    for sc in scored_candidates:
        c = sc["candidate"]
        prof = c["profile"]
        skills_str = ", ".join([s["name"] for s in c["skills"]]).lower()
        
        # Text Search
        if search_query:
            q = search_query.lower()
            if q not in prof["name"].lower() and q not in skills_str and q not in prof["current_title"].lower():
                continue
                
        # Score Filter
        if sc["final_score"] * 100 < min_score_filter:
            continue
            
        # Location Filter
        if location_filter != "All Locations" and prof["current_location"] != location_filter:
            continue
            
        filtered_list.append(sc)
        
    # Table Action buttons
    act_col1, act_col2 = st.columns([8, 2])
    with act_col2:
        # Export Shortlist Button
        export_btn = st.button("💾 Export & Validate Shortlist", use_container_width=True)
        
    if export_btn:
        if len(filtered_list) > 0:
            # Generate the submission file
            submission_rows = []
            for sc in filtered_list[:100]: # Cap at 100
                xai_profile = ExplainabilityEngine.generate_candidate_explanation(sc)
                submission_rows.append({
                    "candidate_id": sc["candidate_id"],
                    "rank": sc["rank"],
                    "final_score": sc["final_score"],
                    "skill_score": sc["skills_score"],
                    "experience_score": sc["experience_score"],
                    "semantic_score": sc["semantic_score"],
                    "recommendation": xai_profile["recommendation"]
                })
            df_sub = pd.DataFrame(submission_rows)
            df_sub.to_csv("submission.csv", index=False)
            df_sub.to_csv("outputs/submission.csv", index=False)
            
            st.success("✓ shortlist saved to outputs/submission.csv!")
            
            # Run validator on the file
            report = SubmissionValidator.validate_submission("submission.csv")
            if report["valid"]:
                st.markdown(f"""
                <div class="badge badge-green" style="font-size:0.8rem; padding:8px 15px; display:block; text-align:center; width:100%; margin-top:10px;">
                    ✓ CSV INTEGRITY VALIDATION PASSED: {report['candidate_count']} candidates formatted successfully. No duplicates or null values found.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="badge badge-red" style="font-size:0.8rem; padding:8px 15px; display:block; text-align:center; width:100%; margin-top:10px;">
                    ❌ CSV INTEGRITY VALIDATION FAILED: {", ".join(report['errors'])}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error("No candidates in the shortlist to export.")
            
    # Render table
    if len(filtered_list) > 0:
        rows_html = ""
        for sc in filtered_list:
            c = sc["candidate"]
            prof = c["profile"]
            
            # Recommendation category badge
            final_pct = sc["final_score"] * 100
            if final_pct >= 78:
                rec_badge = '<span class="badge badge-green">STRONG HIRE</span>'
            elif final_pct >= 60:
                rec_badge = '<span class="badge badge-amber">CONSIDER</span>'
            else:
                rec_badge = '<span class="badge badge-red">PASS</span>'
                
            # Quick short description
            skills_names = [s["name"] for s in c["skills"][:4]]
            skills_badges = " ".join([f'<span class="badge badge-blue" style="font-size:0.65rem; padding:1px 5px; margin:1px;">{s}</span>' for s in skills_names])
            
            rows_html += f"""
            <tr>
                <td><b>#{sc['rank']}</b></td>
                <td>
                    <b>{prof['name']}</b><br>
                    <small style="color:{text_muted}">{prof['current_title']} at {c['career_history'][0]['company'] if c['career_history'] else 'Freelancer'}</small>
                </td>
                <td><b style="color:{accent}; font-size:0.9rem;">{final_pct:.1f}%</b></td>
                <td>{skills_badges}</td>
                <td>{prof['years_of_experience']} Years</td>
                <td>{prof['current_location']}</td>
                <td>{rec_badge}</td>
            </tr>
            """
            
        table_html = f"""
        <div style="background:{card}; border:1px solid {border}; border-radius:10px; padding:1rem; box-shadow:{shadow}; overflow-x:auto;">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Candidate Profile</th>
                        <th>Match Score</th>
                        <th>Top Skills</th>
                        <th>Experience</th>
                        <th>Location</th>
                        <th>AI Recommendation</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
        """
        st.html(table_html)
    else:
        st.info("No candidates match your filters. Try adjusting the score slider or weights.")

# ------------------------------------------
# TAB 3: CANDIDATE DEEP-DIVE
# ------------------------------------------
with tab_detail:
    if len(scored_candidates) > 0:
        # Dropdown to select candidate
        cand_map = {f"#{sc['rank']} - {sc['candidate']['profile']['name']} ({sc['final_score']*100:.1f}%)": sc for sc in scored_candidates}
        selected_cand_label = st.selectbox("Select a Candidate to Inspect", list(cand_map.keys()))
        
        sc = cand_map[selected_cand_label]
        c = sc["candidate"]
        prof = c["profile"]
        sigs = c["redrob_signals"]
        
        # Generate XAI explanation
        xai = ExplainabilityEngine.generate_candidate_explanation(sc)
        
        # Candidate Header Row
        h_prob = xai["hiring_probability"]
        h_rating = xai["rating"]
        if h_rating == "Strong Hire":
            rating_badge = '<span class="badge badge-green" style="font-size:0.9rem; padding:4px 12px;">STRONG HIRE</span>'
        elif h_rating == "Consider":
            rating_badge = '<span class="badge badge-amber" style="font-size:0.9rem; padding:4px 12px;">CONSIDER</span>'
        else:
            rating_badge = '<span class="badge badge-red" style="font-size:0.9rem; padding:4px 12px;">PASS</span>'
            
        st.markdown(f"""
        <div style="background:{card}; border:1px solid {border}; border-radius:10px; padding:1.5rem; box-shadow:{shadow}; margin-bottom:1.5rem;">
            <div style="display:flex; justify-content:between; align-items:start; flex-wrap:wrap; gap:15px;">
                <div style="flex:1; min-width:250px;">
                    <span class="badge badge-blue">RANK #{sc['rank']}</span>
                    <h2 style="margin:4px 0 2px 0; color:{text}">{prof['name']}</h2>
                    <p style="margin:0 0 8px 0; color:{text_muted}; font-size:0.9rem;">{prof['headline']}</p>
                    <p style="font-size:0.82rem; color:{text_dim}; line-height:1.4; max-width:750px;">{prof['summary']}</p>
                </div>
                <div style="text-align:right; min-width:150px; display:flex; flex-direction:column; align-items:end; gap:5px;">
                    <span style="font-size:0.75rem; color:{text_muted}; text-transform:uppercase; font-weight:600;">Fitness Rating</span>
                    {rating_badge}
                    <h1 style="margin:5px 0 0 0; color:{accent}; font-size:2.4rem; font-weight:800; letter-spacing:-0.04em;">{h_prob:.1f}%</h1>
                    <span style="font-size:0.7rem; color:{text_muted};">Hiring Probability</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Grid details
        col_det1, col_det2 = st.columns([6, 4])
        
        with col_det1:
            # 1. Timeline Card
            st.markdown("""
            <div class="chart-wrap">
                <div class="chart-title">Career History & Timeline</div>
                <div class="chart-subtitle">Chronological progression of previous professional engagements</div>
                <div class="timeline">
            """, unsafe_allow_html=True)
            
            timeline_html = ""
            for job in c.get("career_history", []):
                start = job.get("start_date", "")[:7]
                end = job.get("end_date", "")[:7] if job.get("end_date") != "Present" else "Present"
                timeline_html += f"""
                <div class="timeline-item">
                    <div class="timeline-date">{start} - {end}</div>
                    <div class="timeline-title">{job.get('title')}</div>
                    <div class="timeline-company">{job.get('company')}</div>
                    <div class="timeline-desc">{job.get('description')}</div>
                </div>
                """
            st.markdown(timeline_html + "</div></div>", unsafe_allow_html=True)
            
            # 2. Projects & Certifications
            st.markdown(f"""
            <div class="chart-wrap">
                <div class="chart-title">Engineering Projects & Certifications</div>
                <div class="chart-subtitle">Detailed portfolio review and verified external certifications</div>
            """, unsafe_allow_html=True)
            
            if c.get("projects"):
                for p in c["projects"]:
                    p_techs = "".join([f'<span class="badge badge-blue" style="font-size:0.65rem; padding:1px 5px; margin:2px 2px 2px 0;">{t}</span>' for t in p.get("tech_used", [])])
                    st.markdown(f"""
                    <div style="border-bottom:1px solid {border_subtle}; padding-bottom:10px; margin-bottom:10px;">
                        <div style="font-size:0.85rem; font-weight:600;">{p.get('title')}</div>
                        <div style="font-size:0.78rem; color:{text_dim}; line-height:1.4; margin:3px 0 5px 0;">{p.get('description')}</div>
                        <div>{p_techs}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.caption("No custom projects listed.")
                
            if sigs.get("recent_certifications"):
                st.markdown("<br><b>Verified Certifications:</b>", unsafe_allow_html=True)
                certs_html = "".join([f'<div style="font-size:0.78rem; color:{green}; margin:4px 0;"><span style="font-size:1rem; margin-right:5px;">✓</span> {cert}</div>' for cert in sigs.get("recent_certifications", [])])
                st.markdown(certs_html, unsafe_allow_html=True)
                
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col_det2:
            # 0. Skills Fit Radar Chart
            jd_req_skills = jd_struct.get("required_skills", [])
            jd_pref_skills = jd_struct.get("preferred_skills", [])

            categories = list(set([s.lower() for s in jd_req_skills] + [s.lower() for s in jd_pref_skills] + [s["name"].lower() for s in c.get("skills", [])[:4]]))
            categories = [cat for cat in categories if cat.strip()][:8]

            if len(categories) >= 3:
                cand_skill_map = {s["name"].lower(): s for s in c.get("skills", [])}
                
                cand_scores = []
                jd_scores = []
                for cat in categories:
                    matched_skill = None
                    for c_skill in cand_skill_map:
                        if cat in c_skill or c_skill in cat:
                            matched_skill = cand_skill_map[c_skill]
                            break
                    if matched_skill:
                        prof_skill = matched_skill.get("proficiency", "intermediate").lower()
                        if prof_skill == "expert":
                            cand_scores.append(100)
                        elif prof_skill in ["advanced", "senior"]:
                            cand_scores.append(85)
                        elif prof_skill == "intermediate":
                            cand_scores.append(65)
                        else:
                            cand_scores.append(45)
                    else:
                        cand_scores.append(15)
                        
                    if cat in [s.lower() for s in jd_req_skills]:
                        jd_scores.append(100)
                    elif cat in [s.lower() for s in jd_pref_skills]:
                        jd_scores.append(70)
                    else:
                        jd_scores.append(30)
                        
                categories_closed = categories + [categories[0]]
                cand_scores_closed = cand_scores + [cand_scores[0]]
                jd_scores_closed = jd_scores + [jd_scores[0]]
                
                fig_radar = go.Figure()
                
                fig_radar.add_trace(go.Scatterpolar(
                    r=jd_scores_closed,
                    theta=categories_closed,
                    fill='toself',
                    name='Job Requirements',
                    fillcolor='rgba(37, 99, 235, 0.08)',
                    line=dict(color='rgba(37, 99, 235, 0.5)', width=2)
                ))
                
                fig_radar.add_trace(go.Scatterpolar(
                    r=cand_scores_closed,
                    theta=categories_closed,
                    fill='toself',
                    name=prof['name'],
                    fillcolor='rgba(34, 197, 94, 0.15)',
                    line=dict(color='#22c55e', width=2)
                ))
                
                radar_layout = PLOT_LAYOUT.copy()
                radar_layout["margin"] = dict(l=50, r=50, t=25, b=25)
                radar_layout["polar"] = dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100],
                        gridcolor="rgba(255,255,255,0.05)" if IS_DARK else "rgba(0,0,0,0.05)",
                        angle=0,
                        tickfont=dict(size=8, color=text_muted)
                    ),
                    angularaxis=dict(
                        gridcolor="rgba(255,255,255,0.05)" if IS_DARK else "rgba(0,0,0,0.05)",
                        tickfont=dict(size=9, color=text)
                    ),
                    bgcolor="rgba(0,0,0,0)"
                )
                fig_radar.update_layout(**radar_layout)
                
                st.markdown("""
                <div class="chart-wrap">
                    <div class="chart-title">Skills Fit Radar Analysis</div>
                    <div class="chart-subtitle">Direct comparison of candidate proficiencies vs Job Description requirements</div>
                """, unsafe_allow_html=True)
                st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False})
                st.markdown("</div>", unsafe_allow_html=True)

            # 1. Feature Attribution Chart (SHAP-inspired breakdown)
            st.markdown("""
            <div class="chart-wrap">
                <div class="chart-title">AI Component Attribution</div>
                <div class="chart-subtitle">SHAP-inspired score contribution from each core recruitment dimension</div>
            """, unsafe_allow_html=True)
            
            attribs = xai["feature_attributions"]
            fig_pie = go.Figure(go.Bar(
                x=list(attribs.values()),
                y=list(attribs.keys()),
                orientation='h',
                marker=dict(color=[accent, "#10b981", "#f59e0b", "#8b5cf6", "#ec4899"]),
                text=[f"{v}%" for v in attribs.values()],
                textposition='inside',
                textfont=dict(color='white')
            ))
            pie_layout = PLOT_LAYOUT.copy()
            pie_layout["margin"] = dict(l=110, r=20, t=10, b=20)
            # Safely merge yaxis settings
            pie_yaxis = pie_layout.get("yaxis", {}).copy()
            pie_yaxis["autorange"] = "reversed"
            pie_layout["yaxis"] = pie_yaxis
            
            fig_pie.update_layout(
                **pie_layout,
                xaxis_title="Score Contribution (%)"
            )
            st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # 2. Strengths and Gaps
            st.markdown(f"""
            <div class="chart-wrap">
                <div class="chart-title">AI Core Recruiter Evaluation</div>
                <div class="chart-subtitle">Automatic audit of candidate strengths and potential hiring gaps</div>
                <div style="margin-bottom:15px;">
                    <b style="color:{green}; font-size:0.8rem;">✓ Key Strengths</b>
                    {"".join([f'<div style="font-size:0.78rem; display:flex; align-items:start; gap:6px; margin:5px 0;"><span style="color:{green};">●</span><span>{s}</span></div>' for s in xai['strengths']]) if xai['strengths'] else '<div style="font-size:0.75rem; color:#71717a;">No major strengths flagged.</div>'}
                </div>
                <div>
                    <b style="color:{amber}; font-size:0.8rem;">⚠ Potential Gaps</b>
                    {"".join([f'<div style="font-size:0.78rem; display:flex; align-items:start; gap:6px; margin:5px 0;"><span style="color:{amber};">●</span><span>{w}</span></div>' for w in xai['weaknesses']]) if xai['weaknesses'] else '<div style="font-size:0.75rem; color:#71717a; margin-top:5px;">✓ No major gaps or risks flagged. Excellent!</div>'}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 3. Behavioral signals card
            st.markdown(f"""
            <div class="chart-wrap">
                <div class="chart-title">Behavioral Signals Audit</div>
                <div class="chart-subtitle">Engagement, availability and learning agility indexes</div>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; font-size:0.78rem; margin-top:8px;">
                    <div style="background:{bg_subtle}; padding:8px; border-radius:5px; border:1px solid {border};">
                        <span style="color:{text_muted}; font-size:0.65rem;">GITHUB COMMITS</span><br>
                        <b>{sigs['github_contributions_commits']} Commits</b>
                    </div>
                    <div style="background:{bg_subtle}; padding:8px; border-radius:5px; border:1px solid {border};">
                        <span style="color:{text_muted}; font-size:0.65rem;">NOTICE PERIOD</span><br>
                        <b>{sigs['notice_period_days']} Days</b>
                    </div>
                    <div style="background:{bg_subtle}; padding:8px; border-radius:5px; border:1px solid {border};">
                        <span style="color:{text_muted}; font-size:0.65rem;">RECRUITER RESPONSE</span><br>
                        <b>{sigs['recruiter_response_rate']*100:.0f}%</b>
                    </div>
                    <div style="background:{bg_subtle}; padding:8px; border-radius:5px; border:1px solid {border};">
                        <span style="color:{text_muted}; font-size:0.65rem;">LEARNING ADOPTION</span><br>
                        <b>{sigs['technology_adoption_index']*100:.0f}% AGILITY</b>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No candidates available for deep-dive.")

# ------------------------------------------
# TAB 4: EVALUATION & BENCHMARK
# ------------------------------------------
with tab_eval:
    st.markdown("""
    <div class="chart-wrap">
        <div class="chart-title">AI Hybrid Ranker vs Baseline Keyword ATS</div>
        <div class="chart-subtitle">Scientific validation and benchmarking against traditional keyword search engines</div>
    """, unsafe_allow_html=True)
    
    # Run evaluation
    try:
        metrics = RankEvaluator.run_evaluation(candidates, jd_text)
        
        st.markdown(f"""
        <p style="font-size:0.82rem; color:{text_dim}; line-height:1.4;">
            To validate the accuracy of our <b>Hybrid AI Ranker</b>, we set up a scientific evaluation pipeline. 
            We define a <b>Ground Truth Suitability</b> for each of the {metrics['total_candidates']} candidates based on strict domain, 
            experience targets, and core skill requirements. We then compare our hybrid model against a 
            <b>Baseline Keyword-Matching ATS</b> (which simply counts keyword frequencies in resumes).
        </p>
        <p style="font-size:0.8rem;">
            <b>Total High-Suitability Candidates in Pool (Ground Truth):</b> <span class="badge badge-blue">{metrics['total_relevant']}</span>
        </p>
        """, unsafe_allow_html=True)
        
        # Build comparison table
        eval_rows = ""
        for k in [5, 10, 20]:
            h_nd = metrics[f"hybrid_k{k}"]["ndcg"]
            b_nd = metrics[f"baseline_k{k}"]["ndcg"]
            nd_lift = ((h_nd - b_nd) / (b_nd + 1e-9)) * 100
            
            h_pr = metrics[f"hybrid_k{k}"]["precision"]
            b_pr = metrics[f"baseline_k{k}"]["precision"]
            pr_lift = ((h_pr - b_pr) / (b_pr + 1e-9)) * 100
            
            h_rc = metrics[f"hybrid_k{k}"]["recall"]
            b_rc = metrics[f"baseline_k{k}"]["recall"]
            rc_lift = ((h_rc - b_rc) / (b_rc + 1e-9)) * 100
            
            eval_rows += f"""
            <tr>
                <td><b>NDCG@{k}</b> (Ranking Quality)</td>
                <td>{b_nd:.4f}</td>
                <td><b style="color:{green};">{h_nd:.4f}</b></td>
                <td><span class="badge badge-green">{nd_lift:+.1f}%</span></td>
            </tr>
            <tr>
                <td><b>Precision@{k}</b> (Shortlist Accuracy)</td>
                <td>{b_pr:.4f}</td>
                <td><b style="color:{green};">{h_pr:.4f}</b></td>
                <td><span class="badge badge-green">{pr_lift:+.1f}%</span></td>
            </tr>
            <tr>
                <td><b>Recall@{k}</b> (Talent Retrieval)</td>
                <td>{b_rc:.4f}</td>
                <td><b style="color:{green};">{h_rc:.4f}</b></td>
                <td><span class="badge badge-green">{rc_lift:+.1f}%</span></td>
            </tr>
            <tr style="background-color:transparent;"><td colspan="4" style="border:none; padding:5px;"></td></tr>
            """
            
        eval_table_html = f"""
        <table class="data-table" style="margin-top:10px;">
            <thead>
                <tr>
                    <th>Evaluation Metric</th>
                    <th>Keyword-Matching ATS (Baseline)</th>
                    <th>Hybrid AI Recruiter (Our Platform)</th>
                    <th>Performance Lift</th>
                </tr>
            </thead>
            <tbody>
                {eval_rows}
            </tbody>
        </table>
        """
        st.html(eval_table_html)
        
        st.markdown(f"""
        <br>
        <div style="background:{bg_subtle}; border:1px dashed {border}; border-radius:8px; padding:15px; font-size:0.8rem; line-height:1.5;">
            <b>Why does the Hybrid AI Ranker outperform traditional ATS?</b><br>
            1. <b>Contextual Semantics (NDCG Boost):</b> Embeddings understand that "Deep Learning" is closely related to "Neural Networks" and "PyTorch", whereas a keyword ATS would fail if the exact string wasn't found.<br>
            2. <b>Honeypot Suppression (Precision Boost):</b> Traditional ATS is easily fooled by "keyword stuffing" (listing expert skills with 0 months experience or inflating timelines). The Hybrid AI engine identifies these contradictions and filters them out.<br>
            3. <b>Seniority Alignment (Recall Boost):</b> Parabolic experience penalties ensure that candidates are neither too junior nor too senior, ensuring high quality on the final shortlist.
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error running evaluation: {e}")
        
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------
# TAB 5: ADD EXTERNAL CANDIDATES
# ------------------------------------------
with tab_add:
    st.markdown(f"""
    <div class="chart-wrap">
        <div class="chart-title">Import Candidate Data from External Sources</div>
        <div class="chart-subtitle">Upload file formats like CSV, Excel (.xlsx), JSON, or JSONL to add them to the ranking pool.</div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Upload candidates file", type=["jsonl", "json", "csv", "xlsx", "pdf"])
    
    if uploaded_file is not None:
        try:
            new_candidates = []
            file_name = uploaded_file.name
            
            if file_name.endswith(".jsonl"):
                for line in uploaded_file:
                    line = line.decode("utf-8").strip()
                    if line:
                        new_candidates.append(json.loads(line))
            elif file_name.endswith(".json"):
                data = json.load(uploaded_file)
                if isinstance(data, list):
                    new_candidates.extend(data)
                else:
                    new_candidates.append(data)
            elif file_name.endswith(".pdf"):
                from src.pdf_parser import PDFResumeParser
                cand_dict = PDFResumeParser.parse_pdf(uploaded_file)
                new_candidates.append(cand_dict)
            elif file_name.endswith(".csv") or file_name.endswith(".xlsx"):
                if file_name.endswith(".csv"):
                    df_upload = pd.read_csv(uploaded_file)
                else:
                    df_upload = pd.read_excel(uploaded_file)
                
                # Convert DataFrame rows to candidate dicts
                for _, row in df_upload.iterrows():
                    cid = str(row.get("candidate_id", f"custom_{np.random.randint(1000, 9999)}"))
                    name = str(row.get("name", row.get("candidate_name", "Unnamed Candidate")))
                    title = str(row.get("current_title", row.get("title", "Software Engineer")))
                    
                    # Safe float conversion for experience
                    try:
                        yoe = float(row.get("years_of_experience", row.get("experience", row.get("yoe", 0))))
                    except (ValueError, TypeError):
                        yoe = 0.0
                        
                    location = str(row.get("current_location", row.get("location", "Unknown")))
                    education = str(row.get("education", ""))
                    headline = str(row.get("headline", f"{title} with {yoe} years of experience"))
                    summary = str(row.get("summary", ""))
                    industry = str(row.get("current_industry", row.get("industry", "Technology")))
                    
                    # Parse skills (could be comma-separated string or list)
                    skills_raw = row.get("skills", "")
                    skills_list = []
                    if isinstance(skills_raw, str) and skills_raw.strip():
                        for s in skills_raw.split(","):
                            s_name = s.strip()
                            if s_name:
                                skills_list.append({"name": s_name, "proficiency": "advanced", "duration_months": int(yoe * 12)})
                    
                    # Parse signals
                    open_to_work = bool(row.get("open_to_work_flag", row.get("open_to_work", True)))
                    notice = int(row.get("notice_period_days", row.get("notice_period", 30)))
                    commits = int(row.get("github_contributions_commits", row.get("github_commits", 100)))
                    relocate = bool(row.get("willing_to_relocate", row.get("relocate", True)))
                    
                    cand_dict = {
                        "candidate_id": cid,
                        "profile": {
                            "name": name,
                            "headline": headline,
                            "summary": summary,
                            "current_title": title,
                            "current_industry": industry,
                            "years_of_experience": yoe,
                            "current_location": location,
                            "education": education
                        },
                        "skills": skills_list,
                        "career_history": [
                            {"company": "Previous Company", "title": title, "description": summary, "start_date": "2020-01-01", "end_date": "Present"}
                        ],
                        "projects": [],
                        "redrob_signals": {
                            "open_to_work_flag": open_to_work,
                            "notice_period_days": notice,
                            "recruiter_response_rate": 0.8,
                            "willing_to_relocate": relocate,
                            "github_contributions_commits": commits,
                            "recent_certifications": [],
                            "project_frequency_count": 0,
                            "technology_adoption_index": 0.7
                        }
                    }
                    new_candidates.append(cand_dict)
            
            if new_candidates:
                st.session_state.custom_candidates.extend(new_candidates)
                st.success(f"Successfully imported {len(new_candidates)} candidates from {file_name}!")
                st.rerun()
            else:
                st.warning("No valid candidates found in the uploaded file.")
        except Exception as e:
            st.error(f"Error parsing file: {e}")
            
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="chart-wrap">
        <div class="chart-title">Add Candidate Manually</div>
        <div class="chart-subtitle">Directly enter candidate details to add them to the pool.</div>
    """, unsafe_allow_html=True)
    
    with st.form("add_candidate_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name", placeholder="e.g. Jane Doe")
            title = st.text_input("Current Job Title", placeholder="e.g. Senior AI Engineer")
            yoe = st.number_input("Years of Experience", min_value=0.0, max_value=40.0, value=5.0, step=0.5)
            location = st.text_input("Location", placeholder="e.g. Noida")
            education = st.text_input("Education / University", placeholder="e.g. B.Tech from IIT Delhi")
            headline = st.text_input("Profile Headline", placeholder="e.g. AI Specialist in NLP & RAG")
            summary = st.text_area("Profile Summary / Bio", placeholder="Write a short summary of the candidate...")
            
        with col2:
            skills_input = st.text_input("Skills (comma-separated)", placeholder="e.g. Python, RAG systems, LLMs, Pinecone")
            notice = st.number_input("Notice Period (Days)", min_value=0, max_value=180, value=30)
            commits = st.number_input("GitHub Contributions (Commits)", min_value=0, max_value=5000, value=150)
            open_to_work = st.checkbox("Open to Work (Actively Looking)", value=True)
            relocate = st.checkbox("Willing to Relocate", value=True)
            
        submitted = st.form_submit_button("Add Candidate to Pool")
        if submitted:
            if not name.strip() or not title.strip():
                st.error("Name and Job Title are required.")
            else:
                skills_list = []
                if skills_input.strip():
                    for s in skills_input.split(","):
                        s_name = s.strip()
                        if s_name:
                            skills_list.append({
                                "name": s_name,
                                "proficiency": "advanced",
                                "duration_months": int(yoe * 12)
                            })
                
                custom_id = f"custom_{np.random.randint(10000, 99999)}"
                new_cand = {
                    "candidate_id": custom_id,
                    "profile": {
                        "name": name.strip(),
                        "headline": headline.strip() if headline.strip() else f"{title.strip()} with {yoe} years of experience",
                        "summary": summary.strip(),
                        "current_title": title.strip(),
                        "current_industry": "Technology",
                        "years_of_experience": yoe,
                        "current_location": location.strip(),
                        "education": education.strip()
                    },
                    "skills": skills_list,
                    "career_history": [
                        {
                            "company": "Current/Previous Company",
                            "title": title.strip(),
                            "description": summary.strip(),
                            "start_date": "2021-01-01",
                            "end_date": "Present"
                        }
                    ],
                    "projects": [],
                    "redrob_signals": {
                        "open_to_work_flag": open_to_work,
                        "notice_period_days": notice,
                        "recruiter_response_rate": 0.8,
                        "willing_to_relocate": relocate,
                        "github_contributions_commits": commits,
                        "recent_certifications": [],
                        "project_frequency_count": 0,
                        "technology_adoption_index": 0.8
                    }
                }
                
                st.session_state.custom_candidates.append(new_cand)
                st.success(f"Successfully added candidate {name.strip()} ({custom_id}) to the pool!")
                st.rerun()
                
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="chart-wrap">
        <div class="chart-title">Manage Custom Candidates</div>
        <div class="chart-subtitle">Perform actions on your imported/manually added candidate list.</div>
    """, unsafe_allow_html=True)
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        if st.button("🗑️ Clear All Custom Candidates", use_container_width=True):
            st.session_state.custom_candidates = []
            st.success("Cleared all custom candidates!")
            st.rerun()
            
    with col_m2:
        if st.button("💾 Save Custom Candidates to Disk", use_container_width=True):
            if not st.session_state.custom_candidates:
                st.warning("No custom candidates to save.")
            else:
                try:
                    # Append custom candidates to data/candidates.jsonl
                    with open("data/candidates.jsonl", "a", encoding="utf-8") as f:
                        for c in st.session_state.custom_candidates:
                            f.write(json.dumps(c) + "\n")
                    
                    # Clear session state custom candidates since they are now on disk
                    st.session_state.custom_candidates = []
                    st.success("Successfully saved custom candidates to data/candidates.jsonl!")
                    
                    # Clear the streamlit cache to reload the new candidates from disk
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to save to disk: {e}")
                    
    st.markdown("</div>", unsafe_allow_html=True)
