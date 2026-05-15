import streamlit as st
from src.session import init_session

st.set_page_config(
    page_title="Sistema VaR - Gestão de Risco",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session()

st.markdown("""
<style>
/* ── Sidebar ─────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background-color: #1B2A4A !important;
}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] a,
section[data-testid="stSidebar"] div {
    color: #B8C8E0 !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover {
    background-color: rgba(255,255,255,0.07) !important;
    border-radius: 5px;
}
section[data-testid="stSidebar"] [aria-selected="true"] {
    background-color: rgba(255,255,255,0.12) !important;
    border-radius: 5px;
}

/* ── Tipografia ──────────────────────────────────────── */
/* Base: aumenta o tamanho geral do texto */
.main .block-container p,
.main .block-container li,
.main .block-container label,
.main .block-container span:not([data-testid]),
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {
    font-size: 1.05rem !important;
    line-height: 1.7 !important;
    color: #374151 !important;
}

/* Títulos — seletores de alta especificidade */
[data-testid="stHeading"] h1,
.main h1 {
    color: #1B2A4A !important;
    font-weight: 700 !important;
    font-size: 2.6rem !important;
    letter-spacing: -0.02em !important;
    line-height: 1.15 !important;
}
[data-testid="stHeading"] h2,
.main h2 {
    color: #1B2A4A !important;
    font-weight: 600 !important;
    font-size: 1.8rem !important;
    letter-spacing: -0.01em !important;
}
[data-testid="stHeading"] h3,
.main h3 {
    color: #2D4A72 !important;
    font-weight: 500 !important;
    font-size: 1.4rem !important;
}

/* ── Metric cards — elevação + tint, sem side-stripe ─── */
[data-testid="stMetric"] {
    background-color: #F5F8FE;
    border-radius: 8px;
    padding: 1.1rem 1.4rem !important;
    border: 1px solid #DDE6F5;
    box-shadow: 0 1px 3px rgba(27,42,74,0.07);
}
[data-testid="stMetricLabel"] {
    color: #6B7A99 !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
}
[data-testid="stMetricValue"] {
    color: #1B2A4A !important;
    font-weight: 700 !important;
    font-size: 1.5rem !important;
}

/* ── Botões ──────────────────────────────────────────── */
.stButton > button {
    border-radius: 5px !important;
    font-weight: 600 !important;
    letter-spacing: 0.01em !important;
    transition: opacity 0.15s ease !important;
}
.stButton > button:hover { opacity: 0.88 !important; }
[data-testid="stFormSubmitButton"] > button {
    background-color: #1B4F8A !important;
    color: white !important;
    border: none !important;
    border-radius: 5px !important;
    font-weight: 600 !important;
}

/* ── Tabela ──────────────────────────────────────────── */
[data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; }

/* ── Alertas ─────────────────────────────────────────── */
[data-testid="stAlert"] { border-radius: 7px !important; }

/* ── Divisores ───────────────────────────────────────── */
hr { border-color: #E8EDF5 !important; margin: 1.5rem 0 !important; }

/* ── Tabs ────────────────────────────────────────────── */
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: #1B4F8A !important;
    border-bottom-color: #1B4F8A !important;
    font-weight: 600 !important;
}

/* ── Formulários ─────────────────────────────────────── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] > div {
    border-radius: 5px !important;
}
</style>
""", unsafe_allow_html=True)

pages = {
    "Visão Geral": [
        st.Page("pages/home.py", title="Home", icon="🏠"),
        st.Page("pages/dashboard.py", title="Dashboard Executivo", icon="📊"),
    ],
    "Configuração": [
        st.Page("pages/mesas.py", title="Mesas de Trading", icon="🏦"),
        st.Page("pages/posicoes.py", title="Posições", icon="📋"),
        st.Page("pages/parametros.py", title="Parâmetros", icon="⚙️"),
    ],
    "Análise de Risco": [
        st.Page("pages/calculo.py", title="Cálculo VaR", icon="📈"),
        st.Page("pages/limites.py", title="Monitoramento de Limites", icon="🚦"),
    ],
}

pg = st.navigation(pages)
pg.run()
