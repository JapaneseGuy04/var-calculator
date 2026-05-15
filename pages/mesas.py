import streamlit as st
import pandas as pd
from src.session import init_session
init_session()

MESAS_PADRAO = [
    {"nome": "Mesa Renda Variável", "limite": 500_000},
    {"nome": "Mesa Renda Fixa", "limite": 300_000},
    {"nome": "Mesa Derivativos", "limite": 800_000},
    {"nome": "Mesa Cambial", "limite": 400_000},
    {"nome": "Mesa Commodities", "limite": 350_000},
]

st.title("🏦 Mesas de Trading")
st.markdown("Gerencie as mesas de trading e seus limites de VaR.")
st.markdown("---")

if st.session_state.get("_msg_mesa"):
    st.success(st.session_state._msg_mesa)
    del st.session_state["_msg_mesa"]

if st.session_state.mesas:
    st.subheader("Mesas Cadastradas")
    df_mesas = pd.DataFrame(st.session_state.mesas)
    df_mesas.columns = ["Nome da Mesa", "Limite VaR (R$)"]
    df_mesas["Limite VaR (R$)"] = df_mesas["Limite VaR (R$)"].apply(lambda x: f"R$ {x:,.0f}")
    st.dataframe(df_mesas, use_container_width=True, hide_index=True)
else:
    st.warning("Nenhuma mesa cadastrada.")

st.markdown("---")
st.subheader("Adicionar / Editar Mesa")

with st.form("form_mesa"):
    col1, col2 = st.columns(2)
    with col1:
        nome_mesa = st.text_input("Nome da Mesa", placeholder="Ex: Mesa Renda Variável")
    with col2:
        limite_mesa = st.number_input("Limite VaR (R$)", min_value=0.0, value=500000.0, step=10000.0)

    submitted = st.form_submit_button("Adicionar Mesa", use_container_width=True)

    if submitted:
        if not nome_mesa:
            st.error("Informe o nome da mesa.")
        else:
            nomes_existentes = [m["nome"] for m in st.session_state.mesas]
            if nome_mesa in nomes_existentes:
                idx = nomes_existentes.index(nome_mesa)
                st.session_state.mesas[idx]["limite"] = limite_mesa
                st.session_state["_msg_mesa"] = f"Mesa '{nome_mesa}' atualizada com limite R$ {limite_mesa:,.0f}"
            else:
                st.session_state.mesas.append({"nome": nome_mesa, "limite": limite_mesa})
                st.session_state["_msg_mesa"] = f"Mesa '{nome_mesa}' adicionada com limite R$ {limite_mesa:,.0f}"
            st.rerun()

st.markdown("---")
st.subheader("Remover Mesa")

if st.session_state.mesas:
    nomes = [m["nome"] for m in st.session_state.mesas]
    mesa_remover = st.selectbox("Selecione a mesa para remover", nomes)
    if st.button("Remover Mesa Selecionada", type="secondary"):
        st.session_state.mesas = [m for m in st.session_state.mesas if m["nome"] != mesa_remover]
        st.session_state.posicoes = [p for p in st.session_state.posicoes if p["mesa"] != mesa_remover]
        st.session_state["_msg_mesa"] = f"Mesa '{mesa_remover}' removida."
        st.rerun()

if st.button("Restaurar Mesas Padrão"):
    st.session_state.mesas = MESAS_PADRAO.copy()
    st.session_state["_msg_mesa"] = "Mesas padrão restauradas."
    st.rerun()
