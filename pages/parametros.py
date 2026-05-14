import streamlit as st

st.title("⚙️ Parâmetros de Risco")
st.markdown("Configure os parâmetros para o cálculo do VaR.")
st.markdown("---")

p = st.session_state.parametros

col1, col2 = st.columns(2)

with col1:
    st.subheader("Parâmetros Principais")

    confianca_opcoes = {0.90: "90%", 0.95: "95%", 0.99: "99%"}
    confianca_atual = p.get("confianca", 0.99)
    confianca_sel = st.selectbox(
        "Nível de Confiança",
        options=list(confianca_opcoes.keys()),
        format_func=lambda x: confianca_opcoes[x],
        index=list(confianca_opcoes.keys()).index(confianca_atual),
    )

    horizonte_opcoes = {1: "1 dia", 5: "5 dias (1 semana)", 10: "10 dias", 21: "21 dias (1 mês)"}
    horizonte_atual = p.get("horizonte", 1)
    horizonte_sel = st.selectbox(
        "Horizonte de Tempo",
        options=list(horizonte_opcoes.keys()),
        format_func=lambda x: horizonte_opcoes[x],
        index=list(horizonte_opcoes.keys()).index(horizonte_atual),
    )

    metodo_sel = st.selectbox(
        "Metodologia VaR",
        ["Histórico", "Paramétrico", "Monte Carlo"],
        index=["Histórico", "Paramétrico", "Monte Carlo"].index(p.get("metodo", "Histórico")),
    )

with col2:
    st.subheader("Parâmetros Avançados")

    janela_opcoes = {126: "126 dias (~6 meses)", 252: "252 dias (~1 ano)", 504: "504 dias (~2 anos)"}
    janela_atual = p.get("janela_historica", 252)
    janela_sel = st.selectbox(
        "Janela Histórica",
        options=list(janela_opcoes.keys()),
        format_func=lambda x: janela_opcoes[x],
        index=list(janela_opcoes.keys()).index(janela_atual),
    )

    if metodo_sel == "Monte Carlo":
        n_sim_opcoes = {1000: "1.000", 5000: "5.000", 10000: "10.000", 50000: "50.000"}
        n_sim_atual = p.get("n_simulacoes", 10000)
        n_sim_sel = st.selectbox(
            "Número de Simulações",
            options=list(n_sim_opcoes.keys()),
            format_func=lambda x: n_sim_opcoes[x],
            index=list(n_sim_opcoes.keys()).index(n_sim_atual),
        )
    else:
        n_sim_sel = p.get("n_simulacoes", 10000)

    taxa_sel = st.number_input(
        "Taxa Selic / Livre de Risco (ex: 0.1075 = 10,75%)",
        min_value=0.0,
        max_value=1.0,
        value=p.get("taxa_livre_risco", 0.1075),
        step=0.0025,
        format="%.4f",
    )

st.markdown("---")
if st.button("💾 Salvar Parâmetros", type="primary", use_container_width=True):
    st.session_state.parametros = {
        "confianca": confianca_sel,
        "horizonte": horizonte_sel,
        "metodo": metodo_sel,
        "janela_historica": janela_sel,
        "n_simulacoes": n_sim_sel,
        "taxa_livre_risco": taxa_sel,
    }
    st.success("Parâmetros salvos!")

st.markdown("---")
st.subheader("Configuração Atual")
col1, col2, col3 = st.columns(3)
col1.metric("Confiança", f"{int(p['confianca']*100)}%")
col2.metric("Horizonte", f"{p['horizonte']} dia(s)")
col3.metric("Metodologia", p["metodo"])
col1.metric("Janela Histórica", f"{p['janela_historica']} dias")
col2.metric("Taxa Livre de Risco", f"{p['taxa_livre_risco']*100:.2f}%")
if p["metodo"] == "Monte Carlo":
    col3.metric("Simulações", f"{p['n_simulacoes']:,}")
