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
