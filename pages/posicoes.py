import streamlit as st
import pandas as pd
import io
from src.options import greeks

st.title("📋 Posições")
st.markdown("Cadastre os ativos de cada mesa de trading.")
st.markdown("---")

if not st.session_state.mesas:
    st.warning("Cadastre mesas de trading primeiro.")
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs(["➕ Cadastro Manual", "🧮 Calculadora Greeks", "📤 Upload CSV/Excel", "📊 Posições Atuais"])

with tab1:
    st.subheader("Cadastrar Posição")
    with st.form("form_posicao"):
        col1, col2 = st.columns(2)
        with col1:
            nomes_mesas = [m["nome"] for m in st.session_state.mesas]
            mesa_sel = st.selectbox("Mesa de Trading", nomes_mesas)
            tipo_ativo = st.selectbox("Tipo de Ativo", ["Ação", "Call", "Put"])
            ticker = st.text_input("Ticker", placeholder="Ex: PETR4.SA ou AAPL").upper().strip()
            quantidade = st.number_input("Quantidade", min_value=1, value=100, step=1)
        with col2:
            preco_entrada = st.number_input("Preço de Entrada (R$)", min_value=0.01, value=30.0, step=0.01)
            if tipo_ativo in ("Call", "Put"):
                strike = st.number_input("Strike (R$)", min_value=0.01, value=30.0, step=0.01)
                vencimento_dias = st.number_input("Dias até Vencimento", min_value=1, value=30, step=1)
                volatilidade = st.number_input("Volatilidade Implícita (ex: 0.30 = 30%)", min_value=0.01, max_value=5.0, value=0.30, step=0.01)
            else:
                strike = 0.0
                vencimento_dias = 0
                volatilidade = 0.0

        submitted = st.form_submit_button("Adicionar Posição", use_container_width=True)
        if submitted:
            if not ticker:
                st.error("Informe o ticker.")
            else:
                pos = {
                    "mesa": mesa_sel,
                    "tipo": tipo_ativo,
                    "ticker": ticker,
                    "quantidade": quantidade,
                    "preco_entrada": preco_entrada,
                    "strike": strike,
                    "vencimento_dias": int(vencimento_dias),
                    "volatilidade": float(volatilidade),
                }
                st.session_state.posicoes.append(pos)
                st.success(f"Posição adicionada: {quantidade}x {ticker} ({tipo_ativo}) na {mesa_sel}")
                st.rerun()

with tab2:
    st.subheader("Calculadora de Greeks (Black-Scholes)")
    with st.form("form_greeks"):
        col1, col2 = st.columns(2)
        with col1:
            g_S = st.number_input("Preço do Ativo (S)", min_value=0.01, value=50.0)
            g_K = st.number_input("Strike (K)", min_value=0.01, value=50.0)
            g_T = st.number_input("Dias até Vencimento", min_value=1, value=30)
        with col2:
            g_r = st.number_input("Taxa Livre de Risco (ex: 0.1075)", min_value=0.0, value=0.1075, step=0.001)
            g_sigma = st.number_input("Volatilidade (ex: 0.30)", min_value=0.01, value=0.30, step=0.01)
            g_tipo = st.selectbox("Tipo", ["call", "put"])
        calc = st.form_submit_button("Calcular Greeks")

    if calc:
        g = greeks(g_S, g_K, g_T / 365, g_r, g_sigma, g_tipo)
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Preço", f"R$ {g['preco']:.4f}")
        col2.metric("Delta", f"{g['delta']:.4f}")
        col3.metric("Gamma", f"{g['gamma']:.6f}")
        col4.metric("Vega (1%)", f"R$ {g['vega']:.4f}")
        col5.metric("Theta (dia)", f"R$ {g['theta']:.4f}")

with tab3:
    st.subheader("Upload de Posições")
    st.markdown("""
    **Formato esperado do arquivo:**

    | mesa | tipo | ticker | quantidade | preco_entrada | strike | vencimento_dias | volatilidade |
    |------|------|--------|-----------|---------------|--------|-----------------|--------------|
    | Mesa Renda Variável | Ação | PETR4.SA | 1000 | 36.50 | 0 | 0 | 0 |
    | Mesa Derivativos | Call | VALE3.SA | 500 | 5.20 | 70.0 | 30 | 0.30 |
    """)

    template_df = pd.DataFrame([
        {"mesa": "Mesa Renda Variável", "tipo": "Ação", "ticker": "PETR4.SA", "quantidade": 1000,
         "preco_entrada": 36.50, "strike": 0, "vencimento_dias": 0, "volatilidade": 0},
        {"mesa": "Mesa Derivativos", "tipo": "Call", "ticker": "VALE3.SA", "quantidade": 500,
         "preco_entrada": 5.20, "strike": 70.0, "vencimento_dias": 30, "volatilidade": 0.30},
    ])
    buf = io.BytesIO()
    template_df.to_excel(buf, index=False)
    st.download_button("📥 Baixar Template Excel", buf.getvalue(), "template_posicoes.xlsx",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    uploaded = st.file_uploader("Carregar arquivo", type=["csv", "xlsx"])
    if uploaded:
        try:
            if uploaded.name.endswith(".csv"):
                df_up = pd.read_csv(uploaded)
            else:
                df_up = pd.read_excel(uploaded)

            colunas_req = ["mesa", "tipo", "ticker", "quantidade", "preco_entrada"]
            if not all(c in df_up.columns for c in colunas_req):
                st.error(f"Colunas obrigatórias: {colunas_req}")
            else:
                nomes_mesas = [m["nome"] for m in st.session_state.mesas]
                adicionados = 0
                for _, row in df_up.iterrows():
                    if row["mesa"] not in nomes_mesas:
                        continue
                    pos = {
                        "mesa": str(row["mesa"]),
                        "tipo": str(row["tipo"]),
                        "ticker": str(row["ticker"]).upper().strip(),
                        "quantidade": int(row["quantidade"]),
                        "preco_entrada": float(row["preco_entrada"]),
                        "strike": float(row.get("strike", 0)),
                        "vencimento_dias": int(row.get("vencimento_dias", 0)),
                        "volatilidade": float(row.get("volatilidade", 0)),
                    }
                    st.session_state.posicoes.append(pos)
                    adicionados += 1
                st.success(f"{adicionados} posições importadas.")
                st.rerun()
        except Exception as e:
            st.error(f"Erro ao processar arquivo: {e}")

with tab4:
    st.subheader("Posições Cadastradas")
    if not st.session_state.posicoes:
        st.info("Nenhuma posição cadastrada.")
    else:
        df_pos = pd.DataFrame(st.session_state.posicoes)
        mesa_filtro = st.selectbox("Filtrar por Mesa", ["Todas"] + [m["nome"] for m in st.session_state.mesas])
        if mesa_filtro != "Todas":
            df_pos = df_pos[df_pos["mesa"] == mesa_filtro]

        st.dataframe(df_pos, use_container_width=True, hide_index=True)
        st.markdown(f"**Total: {len(df_pos)} posições**")

        if st.button("Remover Todas as Posições", type="secondary"):
            if mesa_filtro == "Todas":
                st.session_state.posicoes = []
            else:
                st.session_state.posicoes = [p for p in st.session_state.posicoes if p["mesa"] != mesa_filtro]
            st.success("Posições removidas.")
            st.rerun()
