import streamlit as st

st.markdown("""
<div style="padding: 1.5rem 0 0.5rem 0;">
    <h1 style="color:#1B2A4A; font-size:2rem; font-weight:700; margin-bottom:0.25rem;">
        Sistema de Gestão de Risco
    </h1>
    <p style="color:#4A5568; font-size:1.1rem; margin-top:0;">VaR Calculator — Plataforma Institucional</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

st.markdown("""
<p style="color:#2D3748; font-size:1rem; line-height:1.7;">
Esta plataforma calcula o <strong>Value at Risk (VaR)</strong> para carteiras de mesas de trading,
permitindo o monitoramento de risco de mercado com três metodologias distintas.
</p>
""", unsafe_allow_html=True)

st.markdown("#### Fluxo de Uso")

cols = st.columns(5)
steps = [
    ("1", "Mesas de Trading", "Cadastre as mesas e seus limites de VaR"),
    ("2", "Posições", "Registre os ativos de cada mesa (ações e opções)"),
    ("3", "Parâmetros", "Configure confiança, horizonte e metodologia"),
    ("4", "Cálculo VaR", "Execute o cálculo e veja os resultados"),
    ("5", "Monitoramento", "Acompanhe os limites em tempo real"),
]
for col, (num, title, desc) in zip(cols, steps):
    with col:
        st.markdown(f"""
        <div style="background:#F0F6FF; border-radius:10px; padding:1rem; border-top:3px solid #1B4F8A; text-align:center; height:130px;">
            <div style="font-size:1.5rem; font-weight:700; color:#1B4F8A;">{num}</div>
            <div style="font-weight:600; color:#1B2A4A; font-size:0.9rem; margin:0.3rem 0;">{title}</div>
            <div style="color:#718096; font-size:0.78rem; line-height:1.4;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")

col1, col2, col3 = st.columns(3)

cards = [
    (col1, "Metodologias", "#1B4F8A", [
        ("Histórico", "Distribuição empírica dos retornos"),
        ("Paramétrico", "Matriz de covariância + normalidade"),
        ("Monte Carlo", "Simulação GBM com Cholesky"),
    ]),
    (col2, "Métricas", "#2D6A9F", [
        ("VaR", "Perda máxima dado nível de confiança"),
        ("Expected Shortfall", "Média das perdas além do VaR"),
        ("Backtesting", "Validação histórica do modelo"),
    ]),
    (col3, "Ativos Suportados", "#1A5276", [
        ("Ações", "Retorno logarítmico × exposição"),
        ("Calls", "Repricing Black-Scholes completo"),
        ("Puts", "Repricing Black-Scholes completo"),
    ]),
]

for col, title, color, items in cards:
    with col:
        items_html = "".join([
            f'<div style="margin-bottom:0.6rem;"><span style="font-weight:600;color:#1B2A4A;">{k}</span>'
            f'<br><span style="color:#718096;font-size:0.82rem;">{v}</span></div>'
            for k, v in items
        ])
        st.markdown(f"""
        <div style="background:#FFFFFF; border-radius:10px; padding:1.2rem; border:1px solid #E2E8F0;
                    box-shadow:0 2px 8px rgba(0,0,0,0.06); height:100%;">
            <div style="font-weight:700; color:{color}; font-size:1rem; margin-bottom:1rem;
                        padding-bottom:0.5rem; border-bottom:2px solid {color};">
                {title}
            </div>
            {items_html}
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.info("Comece cadastrando as **Mesas de Trading** e depois registre as **Posições**.")
