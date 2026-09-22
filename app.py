"""AI Interview Coach - Streamlit Application.
Main entrypoint and stage routing (setup -> analysis -> interview -> report).
Premium dark-mode UI/UX with enterprise-grade styling.
"""

import streamlit as st
import pandas as pd
from config import (
    MODES,
    DIFFICULTY_LEVELS,
    DEFAULT_QUESTIONS,
    MIN_QUESTIONS,
    MAX_QUESTIONS,
    validate_config,
)
from utils import (
    extract_text_from_pdf,
    truncate_text,
    compute_aggregate_scores,
)
from samples import (
    SAMPLE_RESUME,
    SAMPLE_JD,
    DEMO_QUESTIONS,
    DEMO_ANSWERS,
)
from analysis import (
    analyze_gap,
    get_next_question,
    score_answer,
    generate_report,
)
from charts import make_radar_chart
from exporter import build_markdown, build_pdf

# Set page config
st.set_page_config(
    page_title="AI Interview Coach",
    page_icon="IC",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================
# PREMIUM DARK-MODE CSS INJECTION
# ==========================================
st.markdown(
    """
    <style>
    /* ========== GOOGLE FONTS ========== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Plus+Jakarta+Sans:wght@600;700&display=swap');

    /* ========== ROOT VARIABLES ========== */
    :root {
        --surface: #0a122a;
        --surface-container-lowest: #050d25;
        --surface-container-low: #131a33;
        --surface-container: #171e37;
        --surface-container-high: #212942;
        --surface-container-highest: #2c344d;
        --surface-bright: #313852;
        --on-surface: #dbe1ff;
        --on-surface-variant: #c0c7d4;
        --primary: #a3c9ff;
        --primary-container: #0078d4;
        --on-primary: #00315c;
        --on-primary-container: #ffffff;
        --secondary: #4edea3;
        --secondary-container: #00a572;
        --on-secondary: #003824;
        --tertiary: #ffb95f;
        --tertiary-container: #a66900;
        --error: #ffb4ab;
        --error-container: #93000a;
        --outline: #8a919e;
        --outline-variant: #404752;
    }

    /* ========== GLOBAL OVERRIDES ========== */
    .stApp, [data-testid="stAppViewContainer"] {
        background-color: var(--surface) !important;
        color: var(--on-surface) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    [data-testid="stHeader"] {
        background-color: rgba(10, 18, 42, 0.85) !important;
        backdrop-filter: blur(16px) !important;
        border-bottom: 1px solid var(--outline-variant) !important;
    }

    /* Hide default Streamlit top bar decorations */
    header[data-testid="stHeader"] .stDeployButton,
    #MainMenu, footer {
        display: none !important;
    }

    /* ========== SIDEBAR ========== */
    [data-testid="stSidebar"] {
        background-color: var(--surface-container-low) !important;
        border-right: 1px solid var(--outline-variant) !important;
        box-shadow: 0 1px 8px rgba(0,0,0,0.4) !important;
    }

    [data-testid="stSidebar"] * {
        color: var(--on-surface) !important;
    }

    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown span {
        color: var(--on-surface-variant) !important;
        font-size: 0.85rem !important;
    }

    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: var(--on-surface) !important;
    }

    [data-testid="stSidebar"] hr {
        border-color: var(--outline-variant) !important;
        opacity: 0.4 !important;
    }

    /* ========== TYPOGRAPHY ========== */
    h1, h2, h3, h4, h5, h6 {
        color: var(--on-surface) !important;
        font-family: 'Plus Jakarta Sans', 'Inter', sans-serif !important;
    }

    p, span, label, div {
        color: var(--on-surface) !important;
    }

    /* ========== BUTTONS ========== */
    .stButton > button {
        background-color: var(--surface-container-high) !important;
        color: var(--on-surface) !important;
        border: 1px solid var(--outline-variant) !important;
        border-radius: 10px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        padding: 0.55rem 1.2rem !important;
        transition: all 0.2s ease !important;
        letter-spacing: 0.01em !important;
    }

    .stButton > button:hover {
        background-color: var(--surface-bright) !important;
        border-color: var(--primary) !important;
        box-shadow: 0 0 12px rgba(0, 120, 212, 0.25) !important;
        transform: translateY(-1px) !important;
    }

    .stButton > button[kind="primary"],
    .stButton > button[data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, var(--primary-container) 0%, #005aa0 100%) !important;
        color: var(--on-primary-container) !important;
        border: 1px solid rgba(163, 201, 255, 0.3) !important;
        box-shadow: 0 2px 12px rgba(0, 120, 212, 0.3) !important;
        font-weight: 700 !important;
    }

    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="stBaseButton-primary"]:hover {
        background: linear-gradient(135deg, #0088ff 0%, var(--primary-container) 100%) !important;
        box-shadow: 0 4px 20px rgba(0, 120, 212, 0.45) !important;
        transform: translateY(-2px) !important;
    }

    /* Catch all for secondary / default buttons to ensure they aren't white */
    button[kind="secondary"],
    [data-testid="baseButton-secondary"],
    div[data-testid="stButton"] button {
        background-color: var(--surface-container-high) !important;
        color: var(--on-surface) !important;
        border: 1px solid var(--outline-variant) !important;
    }


    /* ========== TEXT INPUTS & TEXT AREAS ========== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stTextInput input,
    .stTextArea textarea,
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea {
        background-color: var(--surface-container-low) !important;
        color: var(--on-surface) !important;
        border: 1px solid var(--outline-variant) !important;
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
        caret-color: var(--primary) !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 2px rgba(163, 201, 255, 0.2) !important;
    }

    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: var(--outline) !important;
        opacity: 0.6 !important;
    }

    /* Force dark on all label elements */
    .stTextInput label,
    .stTextArea label,
    .stSelectbox label,
    .stSlider label,
    .stCheckbox label,
    .stFileUploader label,
    [data-testid="stWidgetLabel"] {
        color: var(--on-surface-variant) !important;
    }

    /* ========== SELECT BOXES ========== */
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background-color: var(--surface-container-low) !important;
        color: var(--on-surface) !important;
        border-color: var(--outline-variant) !important;
        border-radius: 8px !important;
    }

    [data-baseweb="select"],
    [data-baseweb="select"] > div {
        background-color: var(--surface-container-low) !important;
    }

    [data-baseweb="select"] * {
        color: var(--on-surface) !important;
    }

    [data-baseweb="popover"],
    [data-baseweb="popover"] > div {
        background-color: var(--surface-container-high) !important;
        border: 1px solid var(--outline-variant) !important;
    }

    [data-baseweb="popover"] li,
    [data-baseweb="popover"] ul li {
        background-color: var(--surface-container-high) !important;
        color: var(--on-surface) !important;
    }

    [data-baseweb="popover"] li:hover {
        background-color: var(--surface-bright) !important;
    }

    /* ========== SLIDER ========== */
    .stSlider > div > div > div > div {
        background-color: transparent !important;
    }

    .stSlider [data-baseweb="slider"] div {
        color: var(--on-surface) !important;
    }

    [data-baseweb="slider"] [data-testid="stTickBarMin"],
    [data-baseweb="slider"] [data-testid="stTickBarMax"] {
        background-color: transparent !important;
        color: var(--on-surface-variant) !important;
    }

    [data-baseweb="slider"] div[role="slider"] > div {
        background-color: var(--surface-container-highest) !important;
        color: var(--on-surface) !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
    }

    /* ========== FILE UPLOADER ========== */
    [data-testid="stFileUploader"],
    [data-testid="stFileUploadDropzone"],
    .stFileUploader > div {
        background-color: var(--surface-container) !important;
        border: 1px dashed var(--outline-variant) !important;
        border-radius: 10px !important;
    }

    [data-testid="stFileUploader"]:hover,
    [data-testid="stFileUploadDropzone"]:hover {
        border-color: var(--primary) !important;
        background-color: var(--surface-container-high) !important;
    }

    /* Deep override for file uploader internals */
    [data-testid="stFileUploader"] *,
    [data-testid="stFileUploadDropzone"] *,
    [data-testid="stFileUploader"] section,
    [data-testid="stFileUploader"] section > * {
        color: var(--on-surface-variant) !important;
        background-color: transparent !important;
    }

    [data-testid="stFileUploader"] button,
    [data-testid="stFileUploadDropzone"] button {
        background-color: var(--surface-container-high) !important;
        color: var(--on-surface) !important;
        border: 1px solid var(--outline-variant) !important;
        border-radius: 8px !important;
    }

    [data-testid="stFileUploader"] button:hover {
        background-color: var(--surface-bright) !important;
        border-color: var(--primary) !important;
    }

    /* File uploader drop zone area */
    [data-testid="stFileUploader"] section[data-testid="stFileUploadDropzone"] {
        background-color: var(--surface-container-low) !important;
        border: 1px dashed var(--outline-variant) !important;
        border-radius: 8px !important;
    }

    /* Override any white/light backgrounds on all nested Streamlit containers */
    .stApp div[data-testid] {
        background-color: transparent;
    }

    /* Catch-all for remaining white inputs */
    input, textarea, select {
        background-color: var(--surface-container-low) !important;
        color: var(--on-surface) !important;
        border-color: var(--outline-variant) !important;
    }

    /* ========== CHECKBOX ========== */
    .stCheckbox label span {
        color: var(--on-surface) !important;
    }

    /* ========== METRICS ========== */
    [data-testid="stMetric"] {
        background-color: var(--surface-container) !important;
        border: 1px solid var(--outline-variant) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2) !important;
    }

    [data-testid="stMetric"] label {
        color: var(--on-surface-variant) !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.8rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.04em !important;
    }

    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: var(--primary) !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 700 !important;
    }

    /* ========== PROGRESS BAR ========== */
    .stProgress > div > div > div {
        background-color: var(--surface-container-lowest) !important;
        border-radius: 10px !important;
    }

    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--primary-container) 0%, var(--primary) 100%) !important;
        border-radius: 10px !important;
    }

    /* ========== CHAT MESSAGES ========== */
    [data-testid="stChatMessage"] {
        background-color: var(--surface-container) !important;
        border: 1px solid var(--outline-variant) !important;
        border-radius: 12px !important;
        padding: 1rem 1.2rem !important;
        margin-bottom: 0.8rem !important;
    }

    [data-testid="stChatMessage"][data-testid*="assistant"],
    .stChatMessage:nth-child(odd) {
        border-left: 3px solid var(--primary-container) !important;
    }

    /* ========== CHAT INPUT ========== */
    [data-testid="stBottom"],
    [data-testid="stBottom"] > div,
    [data-testid="stBottomBlockContainer"] {
        background-color: var(--surface) !important;
    }

    [data-testid="stChatInput"],
    [data-testid="stChatInput"] > div,
    [data-testid="stChatInput"] > div > div {
        background-color: var(--surface-container-lowest) !important;
        border-color: var(--outline-variant) !important;
    }

    [data-testid="stChatInput"] textarea {
        background-color: transparent !important;
        color: var(--on-surface) !important;
        font-family: 'Inter', sans-serif !important;
        -webkit-text-fill-color: var(--on-surface) !important;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: var(--outline) !important;
        -webkit-text-fill-color: var(--outline) !important;
    }

    [data-testid="stChatInput"] button {
        background-color: var(--primary-container) !important;
        color: var(--on-primary-container) !important;
    }

    /* ========== DATAFRAME / TABLE ========== */
    .stDataFrame, [data-testid="stDataFrame"] {
        background-color: var(--surface-container) !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }

    .stDataFrame th {
        background-color: var(--surface-container-high) !important;
        color: var(--on-surface) !important;
        font-weight: 600 !important;
        border-bottom: 2px solid var(--outline-variant) !important;
    }

    .stDataFrame td {
        color: var(--on-surface) !important;
        border-bottom: 1px solid var(--outline-variant) !important;
    }

    /* ========== EXPANDER ========== */
    [data-testid="stExpander"] {
        background-color: var(--surface-container) !important;
        border: 1px solid var(--outline-variant) !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }

    [data-testid="stExpander"] details summary,
    [data-testid="stExpander"] details summary:hover,
    [data-testid="stExpander"] details summary * {
        background-color: var(--surface-container-high) !important;
        color: var(--on-surface) !important;
        font-weight: 600 !important;
    }

    [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        background-color: var(--surface-container-low) !important;
    }

    /* ========== ALERTS (success, warning, info, error) ========== */
    .stAlert, [data-testid="stAlert"] {
        border-radius: 10px !important;
    }

    div[data-testid="stAlert"][data-baseweb="notification"]{
        background-color: var(--surface-container-high) !important;
    }

    .stSuccess, [role="alert"][data-baseweb="notification"][kind="positive"] {
        background-color: rgba(78, 222, 163, 0.1) !important;
        border: 1px solid rgba(78, 222, 163, 0.3) !important;
        color: var(--secondary) !important;
    }

    .stWarning {
        background-color: rgba(255, 185, 95, 0.1) !important;
        border: 1px solid rgba(255, 185, 95, 0.3) !important;
    }

    .stError {
        background-color: rgba(255, 180, 171, 0.1) !important;
        border: 1px solid rgba(255, 180, 171, 0.3) !important;
    }

    .stInfo {
        background-color: rgba(163, 201, 255, 0.1) !important;
        border: 1px solid rgba(163, 201, 255, 0.3) !important;
    }

    /* ========== SPINNER ========== */
    .stSpinner > div {
        border-top-color: var(--primary) !important;
    }

    /* ========== DOWNLOAD BUTTON ========== */
    .stDownloadButton > button {
        background-color: var(--surface-container-high) !important;
        color: var(--on-surface) !important;
        border: 1px solid var(--outline-variant) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }

    .stDownloadButton > button:hover {
        background-color: var(--primary-container) !important;
        color: var(--on-primary-container) !important;
        border-color: var(--primary) !important;
        box-shadow: 0 0 12px rgba(0, 120, 212, 0.3) !important;
    }

    /* ========== TABS ========== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem !important;
        background-color: var(--surface-container-lowest) !important;
        padding: 0.25rem !important;
        border-radius: 10px !important;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        color: var(--on-surface-variant) !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
    }

    .stTabs [aria-selected="true"] {
        background-color: var(--primary-container) !important;
        color: var(--on-primary-container) !important;
        box-shadow: 0 0 12px rgba(0, 120, 212, 0.35) !important;
    }

    /* ========== IMAGE ========== */
    [data-testid="stImage"] {
        border-radius: 12px !important;
        overflow: hidden !important;
    }

    /* ========== DIVIDER ========== */
    hr {
        border-color: var(--outline-variant) !important;
        opacity: 0.3 !important;
    }

    /* ========== CUSTOM COMPONENT CLASSES ========== */

    /* Main gradient header */
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
        background: linear-gradient(135deg, #a3c9ff 0%, #0078d4 50%, #4edea3 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.2rem;
        letter-spacing: -0.02em;
    }

    .sub-header {
        font-size: 1rem;
        color: #c0c7d4 !important;
        margin-bottom: 1.5rem;
        line-height: 1.6;
    }

    /* Stage stepper bar */
    .stage-stepper {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem 1.25rem;
        background-color: #131a33;
        border-radius: 12px;
        border: 1px solid #2c344d;
        margin-bottom: 1.5rem;
        flex-wrap: wrap;
    }

    .stage-step {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.8rem;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        color: #c0c7d4;
        opacity: 0.5;
        padding: 0.3rem 0.8rem;
        border-radius: 8px;
        white-space: nowrap;
    }

    .stage-step.completed {
        color: #4edea3;
        opacity: 0.8;
    }

    .stage-step.active {
        color: #dbe1ff;
        opacity: 1;
        background-color: #212942;
        box-shadow: 0 0 8px rgba(163, 201, 255, 0.2);
    }

    .stage-step.active::before {
        content: '';
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #a3c9ff;
        animation: pulse-dot 1.5s ease-in-out infinite;
    }

    .stage-connector {
        width: 20px;
        height: 1px;
        background-color: #2c344d;
        flex-shrink: 0;
    }

    @keyframes pulse-dot {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.4; }
    }

    /* Card containers */
    .dark-card {
        background-color: #171e37;
        border: 1px solid #2c344d;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }

    .dark-card-elevated {
        background-color: #212942;
        border: 1px solid rgba(44, 52, 77, 0.6);
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 0.75rem;
    }

    /* Skill badges */
    .skill-badge-matched {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        background-color: rgba(78, 222, 163, 0.12);
        color: #4edea3;
        font-weight: 600;
        font-size: 0.82rem;
        padding: 0.35rem 0.8rem;
        border-radius: 20px;
        margin: 0.2rem;
        border: 1px solid rgba(78, 222, 163, 0.3);
        font-family: 'Inter', sans-serif;
    }

    .skill-badge-high {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        background-color: rgba(255, 180, 171, 0.12);
        color: #ffb4ab;
        font-weight: 600;
        font-size: 0.82rem;
        padding: 0.35rem 0.8rem;
        border-radius: 20px;
        margin: 0.2rem;
        border: 1px solid rgba(255, 180, 171, 0.3);
        font-family: 'Inter', sans-serif;
    }

    .skill-badge-med {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        background-color: rgba(255, 185, 95, 0.12);
        color: #ffb95f;
        font-weight: 600;
        font-size: 0.82rem;
        padding: 0.35rem 0.8rem;
        border-radius: 20px;
        margin: 0.2rem;
        border: 1px solid rgba(255, 185, 95, 0.3);
        font-family: 'Inter', sans-serif;
    }

    .skill-badge-low {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        background-color: rgba(163, 201, 255, 0.1);
        color: #a3c9ff;
        font-weight: 600;
        font-size: 0.82rem;
        padding: 0.35rem 0.8rem;
        border-radius: 20px;
        margin: 0.2rem;
        border: 1px solid rgba(163, 201, 255, 0.3);
        font-family: 'Inter', sans-serif;
    }

    /* Interview question box */
    .interview-q-box {
        background-color: #171e37;
        border-left: 4px solid #0078d4;
        padding: 1.25rem 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        font-size: 1.1rem;
        font-weight: 600;
        color: #dbe1ff;
        box-shadow: 0 2px 12px rgba(0, 120, 212, 0.15);
        position: relative;
    }

    .interview-q-box::before {
        content: 'CURRENT QUESTION';
        position: absolute;
        top: -0.6rem;
        left: 1rem;
        font-size: 0.65rem;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 0.08em;
        color: #0078d4;
        background-color: #171e37;
        padding: 0 0.5rem;
    }

    /* Demo answer box */
    .demo-box {
        background-color: rgba(78, 222, 163, 0.08);
        border: 1px solid rgba(78, 222, 163, 0.25);
        border-radius: 10px;
        padding: 0.8rem 1.2rem;
        margin-bottom: 0.8rem;
        color: #dbe1ff;
    }

    /* Mono-spaced metric labels */
    .metric-mono {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        font-weight: 500;
        letter-spacing: 0.04em;
        color: #c0c7d4;
        text-transform: uppercase;
    }

    /* Score card for report */
    .score-card {
        background-color: #171e37;
        border: 1px solid #2c344d;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
    }

    .score-card .score-label {
        font-size: 0.75rem;
        color: #c0c7d4;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        margin-bottom: 0.3rem;
    }

    .score-card .score-value {
        font-size: 1.5rem;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        color: #a3c9ff;
    }

    .score-card .score-value.green { color: #4edea3; }
    .score-card .score-value.amber { color: #ffb95f; }
    .score-card .score-value.blue { color: #a3c9ff; }

    /* Status badges */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        font-size: 0.72rem;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 0.03em;
        padding: 0.25rem 0.7rem;
        border-radius: 20px;
    }

    .status-badge.connected {
        background-color: rgba(78, 222, 163, 0.1);
        color: #4edea3;
        border: 1px solid rgba(78, 222, 163, 0.3);
    }

    .status-badge.active {
        background-color: rgba(163, 201, 255, 0.1);
        color: #a3c9ff;
        border: 1px solid rgba(163, 201, 255, 0.3);
    }

    .status-badge.warning {
        background-color: rgba(255, 185, 95, 0.1);
        color: #ffb95f;
        border: 1px solid rgba(255, 185, 95, 0.3);
    }

    /* Gap analysis priority labels */
    .priority-high {
        display: inline-block;
        font-size: 0.68rem;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 0.05em;
        color: #ffb4ab;
        background-color: rgba(147, 0, 10, 0.3);
        padding: 0.15rem 0.6rem;
        border-radius: 4px;
    }

    .priority-med {
        display: inline-block;
        font-size: 0.68rem;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 0.05em;
        color: #ffb95f;
        background-color: rgba(166, 105, 0, 0.25);
        padding: 0.15rem 0.6rem;
        border-radius: 4px;
    }

    .priority-low {
        display: inline-block;
        font-size: 0.68rem;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 0.05em;
        color: #a3c9ff;
        background-color: rgba(0, 120, 212, 0.15);
        padding: 0.15rem 0.6rem;
        border-radius: 4px;
    }

    /* Executive summary banner */
    .exec-banner {
        background: linear-gradient(135deg, #171e37 0%, #0d1529 100%);
        border: 1px solid #2c344d;
        border-radius: 14px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.3);
    }

    .exec-banner .overall-score {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.8rem;
        font-weight: 800;
        color: #dbe1ff;
        letter-spacing: -0.02em;
    }

    .exec-banner .overall-score .highlight {
        color: #a3c9ff;
    }

    .exec-banner .verdict-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 700;
        background-color: rgba(78, 222, 163, 0.12);
        color: #4edea3;
        border: 1px solid rgba(78, 222, 163, 0.3);
    }

    .exec-banner .verdict-badge::before {
        content: '';
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background-color: #4edea3;
    }

    /* Gap analysis skill row */
    .gap-skill-row {
        background-color: #171e37;
        border: 1px solid #2c344d;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
        transition: background-color 0.15s ease;
    }

    .gap-skill-row:hover {
        background-color: #212942;
    }

    .gap-skill-row .skill-name {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.05rem;
        font-weight: 600;
        color: #dbe1ff;
        margin-bottom: 0.3rem;
    }

    .gap-skill-row .skill-reason {
        font-size: 0.88rem;
        color: #c0c7d4;
        line-height: 1.5;
    }

    /* Strength/weakness cards in report */
    .feedback-card {
        background-color: #050d25;
        border-radius: 8px;
        padding: 0.75rem 1rem;
    }

    .feedback-card .fb-label {
        font-size: 0.78rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 0.4rem;
        margin-bottom: 0.3rem;
    }

    .feedback-card .fb-label.strength { color: #4edea3; }
    .feedback-card .fb-label.weakness { color: #ffb4ab; }
    .feedback-card .fb-label.model { color: #a3c9ff; }

    .feedback-card p {
        font-size: 0.88rem;
        color: #c0c7d4 !important;
        line-height: 1.55;
        margin: 0;
    }

    /* Section heading */
    .section-heading {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.15rem;
        font-weight: 700;
        color: #dbe1ff;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(44, 52, 77, 0.6);
    }

    .section-heading .icon {
        font-size: 1.3rem;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================
# STAGE STEPPER HELPER
# ==========================================
def render_stage_stepper(active_stage: str):
    """Renders the 4-stage progress stepper bar at the top of each stage."""
    stages = [
        ("setup", "1. Setup & Profile"),
        ("analysis", "2. Gap Analysis"),
        ("interview", "3. Live Mock Interview"),
        ("report", "4. Coaching Report"),
    ]
    stage_order = [s[0] for s in stages]
    active_idx = stage_order.index(active_stage) if active_stage in stage_order else 0

    steps_html = []
    for idx, (key, label) in enumerate(stages):
        if idx < active_idx:
            steps_html.append(f'<span class="stage-step completed">✓ {label}</span>')
        elif idx == active_idx:
            steps_html.append(f'<span class="stage-step active">{label}</span>')
        else:
            steps_html.append(f'<span class="stage-step">○ {label}</span>')

        if idx < len(stages) - 1:
            steps_html.append('<span class="stage-connector"></span>')

    st.markdown(
        f'<div class="stage-stepper">{"".join(steps_html)}</div>',
        unsafe_allow_html=True,
    )


# ==========================================
# SESSION STATE
# ==========================================
def init_session_state():
    """Initializes default session state variables."""
    defaults = {
        "stage": "setup",  # setup -> analysis -> interview -> report
        "resume_text": "",
        "jd_text": "",
        "mode": "Technical",
        "level": "Mid-level",
        "n_questions": DEFAULT_QUESTIONS,
        "demo_mode": False,
        "gap": None,
        "history": [],  # list of {question, answer, score}
        "current_q": "",
        "report_md": "",
        "radar_png": None,
        "score_df": None,
        "avg_scores": None,
        "error_msg": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


init_session_state()


def reset_interview():
    """Clears interview progress and returns to setup stage."""
    st.session_state.stage = "setup"
    st.session_state.resume_text = ""
    st.session_state.jd_text = ""
    st.session_state.demo_mode = False
    st.session_state.gap = None
    st.session_state.history = []
    st.session_state.current_q = ""
    st.session_state.report_md = ""
    st.session_state.radar_png = None
    st.session_state.score_df = None
    st.session_state.avg_scores = None
    st.session_state.error_msg = None
    st.rerun()


# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    # Branding header
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.3rem;">
            <div>
                <div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.15rem; font-weight: 700; color: #dbe1ff; letter-spacing: -0.01em;">AI Interview Coach</div>
                <div class="metric-mono" style="font-size: 0.65rem; color: #c0c7d4;">ENTERPRISE EVALUATION SUITE</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Environment Validation Status
    is_valid_env, missing_keys = validate_config()
    if is_valid_env:
        st.markdown(
            '<div class="status-badge connected" style="margin: 0.5rem 0;">● Azure AI Connected</div>',
            unsafe_allow_html=True,
        )
    else:
        st.warning(
            f"Missing Azure OpenAI Config:\n`{', '.join(missing_keys)}`\nPlease configure `.env` file."
        )

    st.markdown("---")

    # Session context panel
    st.markdown(
        f"""
        <div class="dark-card-elevated" style="padding: 0.8rem;">
            <div class="metric-mono" style="margin-bottom: 0.5rem; color: #8a919e;">ACTIVE SESSION</div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.3rem;">
                <span style="font-size: 0.82rem; color: #c0c7d4;">Stage</span>
                <span class="metric-mono" style="color: #a3c9ff;">{st.session_state.stage.upper()}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.3rem;">
                <span style="font-size: 0.82rem; color: #c0c7d4;">Mode</span>
                <span class="metric-mono" style="color: #dbe1ff;">{st.session_state.mode}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.3rem;">
                <span style="font-size: 0.82rem; color: #c0c7d4;">Seniority</span>
                <span class="metric-mono" style="color: #dbe1ff;">{st.session_state.level}</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="font-size: 0.82rem; color: #c0c7d4;">Questions</span>
                <span class="metric-mono" style="color: #ffb95f;">{st.session_state.n_questions}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.demo_mode:
        st.markdown(
            '<div class="status-badge warning" style="margin: 0.5rem 0;">DEMO MODE</div>',
            unsafe_allow_html=True,
        )

    if st.session_state.stage in ["interview", "report"]:
        completed = len(st.session_state.history)
        total = st.session_state.n_questions
        pct = int((completed / total) * 100) if total > 0 else 0
        st.markdown(
            f"""
            <div class="dark-card-elevated" style="padding: 0.8rem; margin-top: 0.5rem;">
                <div class="metric-mono" style="margin-bottom: 0.4rem; color: #8a919e;">PROGRESS</div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 0.85rem; font-weight: 600; color: #dbe1ff;">{completed} / {total}</span>
                    <span class="metric-mono" style="color: #a3c9ff;">{pct}%</span>
                </div>
                <div style="width: 100%; background-color: #050d25; border-radius: 10px; height: 6px; margin-top: 0.4rem; overflow: hidden;">
                    <div style="width: {pct}%; background: linear-gradient(90deg, #0078d4, #a3c9ff); height: 100%; border-radius: 10px; transition: width 0.3s ease;"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    if st.button("Reset / Start New Interview", use_container_width=True):
        reset_interview()

    st.markdown("---")

    # Privacy notice
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 0.4rem; margin-top: 0.5rem;">
            <span style="width: 6px; height: 6px; border-radius: 50%; background-color: #4edea3;"></span>
            <span style="font-size: 0.75rem; color: #4edea3; font-weight: 500;">Private & Ephemeral</span>
        </div>
        <p style="font-size: 0.72rem; color: #8a919e !important; margin-top: 0.3rem; line-height: 1.45;">
            Coaching tool only. No candidate data is stored permanently. All data is processed in-session only.
        </p>
        """,
        unsafe_allow_html=True,
    )


# ==========================================
# STAGE 1: SETUP
# ==========================================
if st.session_state.stage == "setup":
    render_stage_stepper("setup")

    st.markdown('<div class="main-header">AI Interview Coach</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Upload your resume and the target job description to practice personalized, high-impact mock interviews tailored to your exact skill gaps.</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.error_msg:
        st.error(st.session_state.error_msg)
        st.session_state.error_msg = None

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown('<div class="section-heading">Your Resume</div>', unsafe_allow_html=True)
        uploaded_pdf = st.file_uploader(
            "Upload your Resume (PDF format only)",
            type=["pdf"],
            help="Your PDF will be extracted locally and analyzed against the job description.",
        )

        sample_col1, sample_col2 = st.columns([1, 1])
        with sample_col1:
            if st.button("Load Sample Profile & JD", help="Loads pre-configured sample resume & JD for quick testing"):
                st.session_state.resume_text = SAMPLE_RESUME
                st.session_state.jd_text = SAMPLE_JD
                st.session_state.mode = "Technical"
                st.session_state.level = "Mid-level"
                st.rerun()
        with sample_col2:
            if st.session_state.resume_text:
                st.markdown(
                    f'<div class="status-badge connected" style="margin-top: 0.5rem;">✓ Resume loaded ({len(st.session_state.resume_text)} chars)</div>',
                    unsafe_allow_html=True,
                )

        st.markdown('<div class="section-heading" style="margin-top: 1.5rem;">Target Job Description</div>', unsafe_allow_html=True)
        jd_input = st.text_area(
            "Paste the complete Job Description (JD)",
            value=st.session_state.jd_text,
            height=240,
            placeholder="Paste responsibilities, requirements, and tech stack here...",
        )

    with col2:
        st.markdown('<div class="section-heading">Interview Configuration</div>', unsafe_allow_html=True)

        demo_mode_val = st.checkbox(
            "Presentation Demo Mode (3 Relatable Questions + 1-Click Fast Answers)",
            value=st.session_state.demo_mode,
            help="Designed for 5-minute class presentations: uses 3 relatable student-friendly questions and 1-click answer buttons.",
        )

        mode_val = st.selectbox(
            "Interview Mode",
            options=MODES,
            index=MODES.index(st.session_state.mode) if st.session_state.mode in MODES else 0,
            help=(
                "- Technical: Deep dive into tools, systems, code, and debugging.\n"
                "- HR/Behavioral: STAR-method questions on leadership, conflict, and teamwork.\n"
                "- Mixed: 60% technical + 40% behavioral."
            ),
        )

        level_val = st.selectbox(
            "Target Seniority Level",
            options=DIFFICULTY_LEVELS,
            index=DIFFICULTY_LEVELS.index(st.session_state.level) if st.session_state.level in DIFFICULTY_LEVELS else 1,
            help="Adjusts difficulty, complexity of scenarios, and depth expectation.",
        )

        default_q_count = 3 if demo_mode_val else st.session_state.n_questions
        n_questions_val = st.slider(
            "Number of Interview Questions",
            min_value=MIN_QUESTIONS,
            max_value=MAX_QUESTIONS,
            value=default_q_count,
            step=1,
            help="Choose between 3 to 15 questions for the mock interview session.",
        )

        st.markdown("<br>", unsafe_allow_html=True)
        start_btn = st.button("Analyze Fit & Start Interview", type="primary", use_container_width=True)

    if start_btn:
        if not uploaded_pdf and not st.session_state.resume_text:
            st.warning("Please upload a resume in PDF format (or click 'Load Sample Profile & JD').")
        elif not jd_input.strip():
            st.warning("Please paste the target Job Description.")
        else:
            with st.spinner("Extracting resume and running pre-interview gap analysis..."):
                try:
                    # Extract text from uploaded PDF
                    if uploaded_pdf:
                        extracted_text, warn_msg = extract_text_from_pdf(uploaded_pdf)
                        if warn_msg:
                            st.warning(warn_msg)
                        resume_text = extracted_text
                    else:
                        resume_text = st.session_state.resume_text

                    # Truncate if excessively long
                    safe_resume, r_trunc = truncate_text(resume_text)
                    safe_jd, j_trunc = truncate_text(jd_input)

                    # Update session state
                    st.session_state.resume_text = safe_resume
                    st.session_state.jd_text = safe_jd
                    st.session_state.mode = mode_val
                    st.session_state.level = level_val
                    st.session_state.demo_mode = demo_mode_val
                    st.session_state.n_questions = 3 if demo_mode_val else n_questions_val

                    # Run Gap Analysis
                    gap_result = analyze_gap(safe_resume, safe_jd)
                    st.session_state.gap = gap_result
                    st.session_state.stage = "analysis"
                    st.rerun()

                except Exception as e:
                    st.error(f"Error during setup and gap analysis: {str(e)}")


# ==========================================
# STAGE 2: PRE-INTERVIEW GAP ANALYSIS
# ==========================================
elif st.session_state.stage == "analysis":
    render_stage_stepper("analysis")

    st.markdown('<div class="main-header">Pre-Interview Gap Analysis</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Review your alignment with the target role before the interview begins. The AI interviewer will tailor questions to probe identified gaps.</div>',
        unsafe_allow_html=True,
    )

    gap = st.session_state.gap
    if gap is None:
        st.warning("No gap analysis data found. Returning to setup.")
        st.session_state.stage = "setup"
        st.rerun()

    # Match Score & Summary
    match_val = gap.match_score if hasattr(gap, "match_score") else gap.get("match_score", 0)
    summary_val = gap.summary if hasattr(gap, "summary") else gap.get("summary", "")

    # Executive banner
    verdict = "Strong Match" if match_val >= 75 else "Moderate Fit" if match_val >= 50 else "Significant Gaps"
    verdict_color = "#4edea3" if match_val >= 75 else "#ffb95f" if match_val >= 50 else "#ffb4ab"

    st.markdown(
        f"""
        <div class="exec-banner">
            <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 0.8rem; margin-bottom: 0.8rem;">
                <span class="verdict-badge" style="color: {verdict_color}; background-color: {verdict_color}18; border-color: {verdict_color}45;">{verdict}</span>
                <span class="metric-mono" style="color: #8a919e;">Candidate vs. Target Role</span>
            </div>
            <div class="overall-score" style="margin-bottom: 0.6rem;">
                Match Score: <span class="highlight">{match_val}</span> <span style="font-size: 1.1rem; color: #8a919e; font-weight: 400;">/ 100</span>
            </div>
            <p style="color: #c0c7d4 !important; font-size: 0.95rem; line-height: 1.6; margin: 0;">{summary_val}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.progress(max(0, min(100, match_val)) / 100.0)

    # Matched vs Missing Skills
    c1, c2 = st.columns([1, 1], gap="large")

    with c1:
        st.markdown('<div class="section-heading">Matched Skills & Strengths</div>', unsafe_allow_html=True)
        matched = gap.matched_skills if hasattr(gap, "matched_skills") else gap.get("matched_skills", [])
        if matched:
            chips_html = "".join([f'<span class="skill-badge-matched">✓ {skill}</span>' for skill in matched])
            st.markdown(chips_html, unsafe_allow_html=True)
        else:
            st.info("No explicit skill matches found in resume.")

        st.markdown("<br>", unsafe_allow_html=True)
        weak = gap.weak_areas if hasattr(gap, "weak_areas") else gap.get("weak_areas", [])
        if weak:
            with st.expander("Weak / Low-Evidence Resume Areas", expanded=True):
                for item in weak:
                    st.markdown(f"- **{item}**")

    with c2:
        st.markdown('<div class="section-heading">Missing / Required Skills</div>', unsafe_allow_html=True)
        missing = gap.missing_skills if hasattr(gap, "missing_skills") else gap.get("missing_skills", [])
        if missing:
            for item in missing:
                skill_name = item.skill if hasattr(item, "skill") else item.get("skill", "")
                importance = (item.importance if hasattr(item, "importance") else item.get("importance", "medium")).lower()
                reason = item.reason if hasattr(item, "reason") else item.get("reason", "")

                badge_class = "skill-badge-high" if importance == "high" else "skill-badge-med" if importance == "medium" else "skill-badge-low"
                priority_class = "priority-high" if importance == "high" else "priority-med" if importance == "medium" else "priority-low"
                priority_label = "HIGH IMPACT" if importance == "high" else "MEDIUM IMPACT" if importance == "medium" else "LOW IMPACT"

                st.markdown(
                    f"""
                    <div class="gap-skill-row">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
                            <span class="skill-name">● {skill_name}</span>
                            <span class="{priority_class}">{priority_label}</span>
                        </div>
                        <div class="skill-reason">{reason}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.success("No critical skill gaps identified!")

        st.markdown("<br>", unsafe_allow_html=True)
        flags = gap.resume_red_flags if hasattr(gap, "resume_red_flags") else gap.get("resume_red_flags", [])
        if flags:
            with st.expander("Resume Red Flags & Formatting Gaps", expanded=False):
                for f in flags:
                    st.markdown(f"- {f}")

    st.markdown("---")
    b_col1, b_col2, _ = st.columns([2, 1, 3])

    with b_col1:
        if st.button("Begin Live Mock Interview", type="primary", use_container_width=True):
            with st.spinner("Preparing your personalized opening interview question..."):
                try:
                    if st.session_state.demo_mode and len(DEMO_QUESTIONS) > 0:
                        first_q = DEMO_QUESTIONS[0]
                    else:
                        first_q = get_next_question(
                            resume_text=st.session_state.resume_text,
                            jd_text=st.session_state.jd_text,
                            gaps=st.session_state.gap,
                            mode=st.session_state.mode,
                            level=st.session_state.level,
                            history=[],
                            current_q_idx=0,
                            total_questions=st.session_state.n_questions,
                        )
                    st.session_state.current_q = first_q
                    st.session_state.stage = "interview"
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to generate first question: {str(e)}")

    with b_col2:
        if st.button("Back to Setup", use_container_width=True):
            st.session_state.stage = "setup"
            st.rerun()


# ==========================================
# STAGE 3: INTERACTIVE INTERVIEW
# ==========================================
elif st.session_state.stage == "interview":
    current_idx = len(st.session_state.history)
    total_q = st.session_state.n_questions

    render_stage_stepper("interview")

    st.markdown('<div class="main-header">Live Mock Interview</div>', unsafe_allow_html=True)

    # Progress telemetry bar
    progress_val = min(1.0, current_idx / float(total_q))
    pct = int(progress_val * 100)

    st.markdown(
        f"""
        <div class="dark-card" style="display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 1rem; padding: 0.8rem 1.25rem;">
            <div style="display: flex; align-items: center; gap: 0.6rem;">
                <span style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.1rem; font-weight: 700; color: #dbe1ff;">Question {current_idx + 1} of {total_q}</span>
                <span style="color: #8a919e;">•</span>
                <span style="font-size: 0.88rem; color: #a3c9ff; font-weight: 500;">{st.session_state.mode} Mode</span>
                <span style="color: #8a919e;">•</span>
                <span style="font-size: 0.88rem; color: #ffb95f; font-weight: 500;">{st.session_state.level}</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <div style="width: 160px; background-color: #050d25; border-radius: 10px; height: 6px; overflow: hidden;">
                    <div style="width: {pct}%; background: linear-gradient(90deg, #0078d4, #a3c9ff); height: 100%; border-radius: 10px; transition: width 0.3s ease;"></div>
                </div>
                <span class="metric-mono" style="color: #c0c7d4;">{pct}%</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Render previous dialogue turns
    for idx, turn in enumerate(st.session_state.history):
        with st.chat_message("assistant"):
            st.markdown(f"**Question {idx + 1}:** {turn['question']}")
        with st.chat_message("user"):
            st.markdown(turn["answer"])

    # Active Question Display
    if st.session_state.current_q:
        st.markdown(
            f'<div class="interview-q-box"><b>Interviewer:</b> {st.session_state.current_q}</div>',
            unsafe_allow_html=True,
        )

    # 1-Click Presentation Demo Helper
    demo_selected_answer = None
    if st.session_state.demo_mode and current_idx < len(DEMO_ANSWERS):
        sample_ans = DEMO_ANSWERS[current_idx]
        with st.container():
            st.markdown(
                f'<div class="demo-box"><b>5-Min Presentation Quick-Answer:</b><br><i>"{sample_ans}"</i></div>',
                unsafe_allow_html=True,
            )
            if st.button("1-Click Submit Demo Answer", key=f"demo_btn_{current_idx}", type="secondary", use_container_width=True):
                demo_selected_answer = sample_ans

    # Candidate text-only input via st.chat_input
    candidate_answer = st.chat_input(
        placeholder=f"Type your answer to Question {current_idx + 1} here and press Enter..."
    )

    final_answer = demo_selected_answer or (candidate_answer.strip() if candidate_answer else None)

    if final_answer:
        cleaned_answer = final_answer.strip()
        if not cleaned_answer:
            st.warning("Answer cannot be empty. Please type your response.")
        else:
            with st.spinner("Scoring response silently & preparing next turn..."):
                try:
                    # 1. Silently score the current answer
                    score_res = score_answer(
                        question=st.session_state.current_q,
                        answer=cleaned_answer,
                        jd_text=st.session_state.jd_text,
                        mode=st.session_state.mode,
                        level=st.session_state.level,
                    )

                    # 2. Append to history
                    st.session_state.history.append({
                        "question": st.session_state.current_q,
                        "answer": cleaned_answer,
                        "score": score_res,
                    })

                    # 3. Check termination condition
                    if len(st.session_state.history) >= total_q:
                        # Interview finished -> Generate final report & radar chart
                        with st.spinner("Synthesizing comprehensive final coaching report..."):
                            avg_scores = compute_aggregate_scores(st.session_state.history)
                            st.session_state.avg_scores = avg_scores
                            st.session_state.radar_png = make_radar_chart(avg_scores)

                            # Build score dataframe
                            table_rows = []
                            for i, t in enumerate(st.session_state.history):
                                sc = t["score"]
                                r = sc.relevance if hasattr(sc, "relevance") else sc.get("relevance", 0)
                                d = sc.depth if hasattr(sc, "depth") else sc.get("depth", 0)
                                s = sc.structure if hasattr(sc, "structure") else sc.get("structure", 0)
                                c = sc.clarity if hasattr(sc, "clarity") else sc.get("clarity", 0)
                                a = round((r + d + s + c) / 4.0, 2)
                                table_rows.append({
                                    "#": i + 1,
                                    "Question": t["question"],
                                    "Relevance": r,
                                    "Depth": d,
                                    "Structure": s,
                                    "Clarity": c,
                                    "Avg": a,
                                })
                            st.session_state.score_df = pd.DataFrame(table_rows)

                            # Generate final markdown report
                            report_text = generate_report(
                                resume_text=st.session_state.resume_text,
                                jd_text=st.session_state.jd_text,
                                gap=st.session_state.gap,
                                history=st.session_state.history,
                                avg_scores=avg_scores,
                            )
                            st.session_state.report_md = report_text
                            st.session_state.stage = "report"
                            st.rerun()
                    else:
                        # Generate next question
                        if st.session_state.demo_mode and len(st.session_state.history) < len(DEMO_QUESTIONS):
                            next_q = DEMO_QUESTIONS[len(st.session_state.history)]
                        else:
                            next_q = get_next_question(
                                resume_text=st.session_state.resume_text,
                                jd_text=st.session_state.jd_text,
                                gaps=st.session_state.gap,
                                mode=st.session_state.mode,
                                level=st.session_state.level,
                                history=st.session_state.history,
                                current_q_idx=len(st.session_state.history),
                                total_questions=total_q,
                            )
                        st.session_state.current_q = next_q
                        st.rerun()

                except Exception as e:
                    st.error(f"Error processing interview answer: {str(e)}")


# ==========================================
# STAGE 4: FINAL REPORT & VISUALS
# ==========================================
elif st.session_state.stage == "report":
    render_stage_stepper("report")

    st.markdown('<div class="main-header">Final Interview Assessment & Report</div>', unsafe_allow_html=True)

    avg_scores = st.session_state.avg_scores or compute_aggregate_scores(st.session_state.history)
    radar_png = st.session_state.radar_png
    score_df = st.session_state.score_df
    report_md = st.session_state.report_md

    overall = avg_scores.get("overall", 0)
    verdict = "Strong Advance" if overall >= 7.5 else "Moderate Performance" if overall >= 5.0 else "Needs Improvement"
    verdict_color = "#4edea3" if overall >= 7.5 else "#ffb95f" if overall >= 5.0 else "#ffb4ab"

    # Executive Summary Banner
    st.markdown(
        f"""
        <div class="exec-banner">
            <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 0.8rem; margin-bottom: 0.6rem;">
                <span class="verdict-badge" style="color: {verdict_color}; background-color: {verdict_color}18; border-color: {verdict_color}45;">{verdict}</span>
                <span class="metric-mono" style="color: #8a919e;">{st.session_state.mode.upper()} • {st.session_state.level.upper()}</span>
            </div>
            <div class="overall-score" style="margin-bottom: 0.5rem;">
                Overall Score: <span class="highlight">{overall}</span> <span style="font-size: 1.1rem; color: #8a919e; font-weight: 400;">/ 10.0</span>
            </div>
            <p style="color: #c0c7d4 !important; font-size: 0.92rem; line-height: 1.6; margin: 0;">
                Completed {st.session_state.n_questions} questions in {st.session_state.mode} mode at {st.session_state.level} difficulty.
                Review your score breakdown, radar chart, and actionable recommendations below.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Downloads in the top area
    d_col1, d_col2, d_col3 = st.columns([1, 1, 1], gap="medium")

    meta_dict = {
        "mode": st.session_state.mode,
        "level": st.session_state.level,
        "n_questions": st.session_state.n_questions,
    }

    full_md_export = build_markdown(
        report_md=report_md,
        score_df=score_df,
        gap_data=st.session_state.gap,
        avg_scores=avg_scores,
        metadata=meta_dict,
    )

    pdf_bytes = None
    try:
        pdf_bytes = build_pdf(
            report_md=report_md,
            radar_png=radar_png,
            score_df=score_df,
            gap_data=st.session_state.gap,
            avg_scores=avg_scores,
            metadata=meta_dict,
        )
    except Exception as e:
        st.warning(f"Note: PDF compilation encountered an issue: {str(e)}. Markdown download is fully available below.")

    with d_col1:
        if pdf_bytes:
            st.download_button(
                label="Download PDF Report",
                data=pdf_bytes,
                file_name=f"interview_coach_report_{st.session_state.mode.lower()}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        else:
            st.button("PDF Unavailable", disabled=True, use_container_width=True)

    with d_col2:
        st.download_button(
            label="Download Markdown Report",
            data=full_md_export,
            file_name=f"interview_coach_report_{st.session_state.mode.lower()}.md",
            mime="text/markdown",
            use_container_width=True,
        )

    with d_col3:
        if st.button("Start New Mock Interview", type="primary", use_container_width=True):
            reset_interview()

    st.markdown("---")

    # Score Cards + Radar Chart
    r_col1, r_col2 = st.columns([1, 1], gap="large")

    with r_col1:
        st.markdown('<div class="section-heading">Performance Radar</div>', unsafe_allow_html=True)
        if radar_png:
            st.image(radar_png, caption="Competency Radar Chart", use_container_width=True)

    with r_col2:
        st.markdown('<div class="section-heading">Score Breakdown</div>', unsafe_allow_html=True)

        # Individual score cards
        sc_html = f"""
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-bottom: 1rem;">
            <div class="score-card">
                <div class="score-label">Overall Average</div>
                <div class="score-value blue">{avg_scores.get('overall', 0)} / 10</div>
            </div>
            <div class="score-card">
                <div class="score-label">Relevance</div>
                <div class="score-value green">{avg_scores.get('relevance', 0)} / 10</div>
            </div>
            <div class="score-card">
                <div class="score-label">Technical Depth</div>
                <div class="score-value amber">{avg_scores.get('depth', 0)} / 10</div>
            </div>
            <div class="score-card">
                <div class="score-label">Structure</div>
                <div class="score-value blue">{avg_scores.get('structure', 0)} / 10</div>
            </div>
            <div class="score-card">
                <div class="score-label">Clarity & Delivery</div>
                <div class="score-value green">{avg_scores.get('clarity', 0)} / 10</div>
            </div>
            <div class="score-card">
                <div class="score-label">Seniority Target</div>
                <div class="score-value" style="color: #ffb95f; font-size: 1.1rem;">{st.session_state.level}</div>
            </div>
        </div>
        """
        st.markdown(sc_html, unsafe_allow_html=True)

    st.markdown("---")

    # Score Breakdown Table
    st.markdown('<div class="section-heading">Per-Question Score Breakdown</div>', unsafe_allow_html=True)
    if score_df is not None and not score_df.empty:
        st.dataframe(score_df, use_container_width=True, hide_index=True)

    # Detailed Turn-by-Turn Expanders
    st.markdown("---")
    st.markdown('<div class="section-heading">Question-by-Question Deep Dive</div>', unsafe_allow_html=True)

    for idx, turn in enumerate(st.session_state.history):
        sc = turn["score"]
        strengths = sc.strengths if hasattr(sc, "strengths") else sc.get("strengths", "")
        weaknesses = sc.weaknesses if hasattr(sc, "weaknesses") else sc.get("weaknesses", "")
        improved = sc.improved_answer if hasattr(sc, "improved_answer") else sc.get("improved_answer", "")

        r_val = sc.relevance if hasattr(sc, "relevance") else sc.get("relevance", 0)
        d_val = sc.depth if hasattr(sc, "depth") else sc.get("depth", 0)
        s_val = sc.structure if hasattr(sc, "structure") else sc.get("structure", 0)
        c_val = sc.clarity if hasattr(sc, "clarity") else sc.get("clarity", 0)
        avg_val = round((r_val + d_val + s_val + c_val) / 4.0, 1)

        with st.expander(f"Q{idx + 1}: {turn['question'][:80]}{'...' if len(turn['question']) > 80 else ''} — Score: {avg_val}/10", expanded=False):
            st.markdown(f"**Your Answer:** {turn['answer']}")
            st.markdown("---")

            fc1, fc2 = st.columns(2)
            with fc1:
                st.markdown(
                    f"""
                    <div class="feedback-card">
                        <div class="fb-label strength">✓ Strengths</div>
                        <p>{strengths}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with fc2:
                st.markdown(
                    f"""
                    <div class="feedback-card">
                        <div class="fb-label weakness">⚠ Area to Improve</div>
                        <p>{weaknesses}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown(
                f"""
                <div class="feedback-card" style="margin-top: 0.75rem;">
                    <div class="fb-label model">★ Gold-Standard Sample Answer</div>
                    <p><em>{improved}</em></p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # Full Markdown Report
    st.markdown('<div class="section-heading">Detailed Assessment & 2-Week Action Plan</div>', unsafe_allow_html=True)
    st.markdown(report_md)
