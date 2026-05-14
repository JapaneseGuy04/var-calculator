import streamlit as st

st.markdown("""
<div style="padding: 2rem 0 1rem 0;">
    <p style="color:#6B7A99; font-size:0.78rem; font-weight:600; letter-spacing:0.1em;
               text-transform:uppercase; margin-bottom:0.4rem;">
        Gestão de Risco de Mercado
    </p>
    <h1 style="color:#1B2A4A; font-size:2.1rem; font-weight:700; letter-spacing:-0.02em;
                margin:0 0 0.5rem 0; line-height:1.2;">
        VaR Calculator
    </h1>
    <p style="color:#4A5568; font-size:1rem; max-width:60ch; line-height:1.65; margin:0;">
        Calcule o <strong style="color:#1B2A4A;">Value at Risk</strong> de carteiras de mesas de trading
        com três metodologias distintas: Histórico, Paramétrico e Monte Carlo.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

st.markdown("""
<p style="color:#6B7A99; font-size:0.78rem; font-weight:600; letter-spacing:0.1em;
           text-transform:uppercase; margin-bottom:1rem;">Fluxo de uso</p>
""", unsafe_allow_html=True)

cols = st.columns(5)
steps = [
    ("01", "Mesas", "Cadastre as mesas e seus limites de VaR"),
    ("02", "Posições", "Registre ações e opções por mesa"),
    ("03", "Parâmetros", "Configure confiança, horizonte e método"),
    ("04", "Cálculo", "Execute o VaR e veja os resultados"),
    ("05", "Monitor", "Acompanhe os limites em tempo real"),
]
for col, (num, title, desc) in zip(cols, steps):
    with col:
        st.markdown(f"""
        <div style="padding:1.2rem 1rem; border-top:2px solid #1B4F8A; background:#FAFBFF;">
            <div style="font-size:0.72rem; font-weight:700; color:#1B4F8A;
                        letter-spacing:0.06em; margin-bottom:0.5rem;">{num}</div>
            <div style="font-weight:600; color:#1B2A4A; font-size:0.9rem;
                        margin-bottom:0.4rem;">{title}</div>
            <div style="color:#6B7A99; font-size:0.78rem; line-height:1.5;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("""
    <p style="color:#6B7A99; font-size:0.78rem; font-weight:600; letter-spacing:0.1em;
               text-transform:uppercase; margin-bottom:1rem;">Metodologias</p>
    """, unsafe_allow_html=True)

    for title, desc in [
        ("Histórico", "Distribuição empírica dos retornos realizados"),
        ("Paramétrico", "Matriz de covariância com assumida normalidade"),
        ("Monte Carlo", "Simulação GBM com decomposição de Cholesky"),
    ]:
        st.markdown(f"""
        <div style="margin-bottom:1rem; padding-bottom:1rem; border-bottom:1px solid #EEF1F8;">
            <span style="font-weight:600; color:#1B2A4A; font-size:0.9rem;">{title}</span>
            <span style="color:#9AA5BC; font-size:0.82rem; margin-left:0.5rem;">—</span>
            <span style="color:#4A5568; font-size:0.82rem;"> {desc}</span>
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <p style="color:#6B7A99; font-size:0.78rem; font-weight:600; letter-spacing:0.1em;
               text-transform:uppercase; margin-bottom:1rem;">Métricas e ativos</p>
    """, unsafe_allow_html=True)

    for title, desc in [
        ("VaR", "Perda máxima dado o nível de confiança"),
        ("Expected Shortfall", "Média das perdas além do VaR"),
        ("Backtesting", "Validação histórica pelo semáforo Basel"),
        ("Ações", "Retorno logarítmico sobre exposição"),
        ("Calls e Puts", "Repricing completo via Black-Scholes"),
    ]:
        st.markdown(f"""
        <div style="margin-bottom:0.85rem; padding-bottom:0.85rem; border-bottom:1px solid #EEF1F8;">
            <span style="font-weight:600; color:#1B2A4A; font-size:0.9rem;">{title}</span>
            <span style="color:#9AA5BC; font-size:0.82rem; margin-left:0.5rem;">—</span>
            <span style="color:#4A5568; font-size:0.82rem;"> {desc}</span>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.info("Comece cadastrando as **Mesas de Trading** e depois registre as **Posições**.")
