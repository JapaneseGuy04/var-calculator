import streamlit as st

st.set_page_config(
    page_title="Sistema VaR - Gestão de Risco",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

MESAS_PADRAO = [
    {"nome": "Mesa Renda Variável", "limite": 500_000},
    {"nome": "Mesa Renda Fixa", "limite": 300_000},
    {"nome": "Mesa Derivativos", "limite": 800_000},
    {"nome": "Mesa Cambial", "limite": 400_000},
    {"nome": "Mesa Commodities", "limite": 350_000},
]


def init_session():
    if "mesas" not in st.session_state:
        st.session_state.mesas = MESAS_PADRAO.copy()
    if "posicoes" not in st.session_state:
        st.session_state.posicoes = []
    if "parametros" not in st.session_state:
        st.session_state.parametros = {
            "confianca": 0.99,
            "horizonte": 1,
            "metodo": "Histórico",
            "janela_historica": 252,
            "n_simulacoes": 10000,
            "taxa_livre_risco": 0.1075,
        }
    if "resultados" not in st.session_state:
        st.session_state.resultados = {}
    if "dados_historicos" not in st.session_state:
        st.session_state.dados_historicos = None


init_session()

st.markdown("""
<style>
/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #1B2A4A !important;
}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] a,
section[data-testid="stSidebar"] div {
    color: #CBD5E8 !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover {
    background-color: rgba(255,255,255,0.08) !important;
    border-radius: 6px;
}
section[data-testid="stSidebar"] [aria-selected="true"] {
    background-color: rgba(27,79,138,0.6) !important;
    border-radius: 6px;
}

/* Headings */
h1 { color: #1B2A4A !important; font-weight: 700 !important; }
h2, h3 { color: #1E3A6E !important; }

/* Metric cards */
[data-testid="stMetric"] {
    background-color: #F0F6FF;
    border-radius: 10px;
    padding: 1rem 1.2rem !important;
    border-left: 4px solid #1B4F8A;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
[data-testid="stMetricLabel"] { color: #4A5568 !important; font-size: 0.82rem !important; }
[data-testid="stMetricValue"] { color: #1B2A4A !important; font-weight: 700 !important; }

/* Buttons */
.stButton > button, [data-testid="stFormSubmitButton"] > button {
    border-radius: 6px !important;
    font-weight: 600 !important;
}
[data-testid="stFormSubmitButton"] > button {
    background-color: #1B4F8A !important;
    color: white !important;
    border: none !important;
}

/* Dataframe */
[data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; }

/* Alert boxes */
[data-testid="stAlert"] { border-radius: 8px !important; }

/* Divider */
hr { border-color: #E2E8F0 !important; }

/* Tabs */
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: #1B4F8A !important;
    border-bottom-color: #1B4F8A !important;
    font-weight: 600 !important;
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
