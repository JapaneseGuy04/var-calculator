import streamlit as st
import pandas as pd
import io
from src.options import greeks, implied_vol, black_scholes

st.title("📋 Posições")
st.markdown("Cadastre os ativos de cada mesa de trading.")
st.markdown("---")

if not st.session_state.mesas:
    st.warning("Cadastre mesas de trading primeiro.")
    st.stop()

# Mensagem de confirmação persistente entre reruns
if st.session_state.get("_msg_posicao"):
    st.success(st.session_state._msg_posicao)
    del st.session_state["_msg_posicao"]

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
            if tipo_ativo in ("Call", "Put"):
                preco_spot = st.number_input(
                    "Preço Spot do Ativo Objeto (S)",
                    min_value=0.01, value=50.0, step=0.01,
                    help="Preço atual do ativo subjacente (ação), não da opção."
                )
                preco_entrada = st.number_input(
                    "Preço de Mercado da Opção (R$)",
                    min_value=0.01, value=3.0, step=0.01,
                    help="Preço de negociação da opção. A volatilidade implícita será calculada automaticamente."
                )
                strike = st.number_input("Strike (R$)", min_value=0.01, value=50.0, step=0.01)
                vencimento_dias = st.number_input("Dias até Vencimento", min_value=1, value=30, step=1)
            else:
                preco_entrada = st.number_input("Preço de Entrada (R$)", min_value=0.01, value=30.0, step=0.01)
                preco_spot = 0.0
                strike = 0.0
                vencimento_dias = 0

        submitted = st.form_submit_button("Adicionar Posição", use_container_width=True)
        if submitted:
            if not ticker:
                st.error("Informe o ticker.")
            else:
                volatilidade = 0.0
                if tipo_ativo in ("Call", "Put"):
                    r = st.session_state.parametros.get("taxa_livre_risco", 0.1075)
                    T = vencimento_dias / 365
                    iv = implied_vol(preco_spot, strike, T, r, preco_entrada, tipo_ativo.lower())
                    if iv is None:
                        st.error(
                            "Não foi possível calcular a volatilidade implícita. "
                            "Verifique se o preço da opção é maior que o valor intrínseco."
                        )
                        st.stop()
                    volatilidade = iv

                pos = {
                    "mesa": mesa_sel,
                    "tipo": tipo_ativo,
                    "ticker": ticker,
                    "quantidade": quantidade,
                    "preco_entrada": preco_entrada,
                    "strike": strike,
                    "vencimento_dias": int(vencimento_dias),
                    "volatilidade": round(volatilidade, 6),
                }
                st.session_state.posicoes.append(pos)

                if tipo_ativo in ("Call", "Put"):
                    msg = (
                        f"Posição adicionada: {quantidade}x {ticker} ({tipo_ativo}) "
                        f"na {mesa_sel} — Vol. Implícita calculada: {volatilidade*100:.2f}%"
                    )
                else:
                    msg = f"Posição adicionada: {quantidade}x {ticker} ({tipo_ativo}) na {mesa_sel}"

                st.session_state["_msg_posicao"] = msg
                st.rerun()

with tab2:
    st.subheader("Calculadora de Greeks (Black-Scholes)")

    modo_iv = st.radio(
        "Modo de entrada",
        ["Informar volatilidade diretamente", "Calcular volatilidade implícita a partir do preço"],
        horizontal=True,
    )

    with st.form("form_greeks"):
        col1, col2 = st.columns(2)
        with col1:
            g_S = st.number_input("Preço do Ativo (S)", min_value=0.01, value=50.0)
            g_K = st.number_input("Strike (K)", min_value=0.01, value=50.0)
            g_T = st.number_input("Dias até Vencimento", min_value=1, value=30)
        with col2:
            g_r = st.number_input("Taxa Livre de Risco (ex: 0.1075)", min_value=0.0, value=0.1075, step=0.001)
            if modo_iv == "Informar volatilidade diretamente":
                g_sigma = st.number_input("Volatilidade (ex: 0.30 = 30%)", min_value=0.001, value=0.30, step=0.01)
                g_preco_mercado = None
            else:
                g_preco_mercado = st.number_input("Preço de Mercado da Opção (R$)", min_value=0.001, value=3.0, step=0.01)
                g_sigma = None
            g_tipo = st.selectbox("Tipo", ["call", "put"])
        calc = st.form_submit_button("Calcular Greeks")

    if calc:
        T_anos = g_T / 365
        if modo_iv == "Calcular volatilidade implícita a partir do preço":
            g_sigma = implied_vol(g_S, g_K, T_anos, g_r, g_preco_mercado, g_tipo)
            if g_sigma is None:
                st.error("Não foi possível calcular a volatilidade implícita. Verifique se o preço é maior que o valor intrínseco.")
                st.stop()
            st.info(f"Volatilidade implícita calculada: **{g_sigma*100:.2f}%**")

        g = greeks(g_S, g_K, T_anos, g_r, g_sigma, g_tipo)
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Preço BS", f"R$ {g['preco']:.4f}")
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

    Para opções, informe a **volatilidade** diretamente no arquivo (coluna `volatilidade`).
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
        mesa_filtro = st.selectbox("Filtrar por Mesa", ["Todas"] + [m["nome"] for m in st.session_state.mesas])

        posicoes_exibidas = st.session_state.posicoes
        if mesa_filtro != "Todas":
            posicoes_exibidas = [p for p in posicoes_exibidas if p["mesa"] == mesa_filtro]

        st.markdown(f"**{len(posicoes_exibidas)} posição(ões)**")

        for i, pos in enumerate(posicoes_exibidas):
            idx_real = st.session_state.posicoes.index(pos)
            col_info, col_btn = st.columns([5, 1])
            with col_info:
                if pos["tipo"] == "Ação":
                    detalhe = f"{pos['quantidade']}x **{pos['ticker']}** ({pos['tipo']}) — Entrada: R$ {pos['preco_entrada']:.2f}"
                else:
                    detalhe = (
                        f"{pos['quantidade']}x **{pos['ticker']}** ({pos['tipo']}) — "
                        f"Strike: R$ {pos['strike']:.2f} | "
                        f"Venc: {pos['vencimento_dias']}d | "
                        f"Vol: {pos['volatilidade']*100:.1f}%"
                    )
                st.markdown(f"📌 {pos['mesa']} — {detalhe}")
            with col_btn:
                if st.button("🗑️ Remover", key=f"del_{idx_real}"):
                    st.session_state.posicoes.pop(idx_real)
                    st.session_state["_msg_posicao"] = f"Posição {pos['ticker']} removida."
                    st.rerun()

        st.markdown("---")
        if st.button("Remover Todas as Posições da Seleção", type="secondary"):
            if mesa_filtro == "Todas":
                st.session_state.posicoes = []
            else:
                st.session_state.posicoes = [p for p in st.session_state.posicoes if p["mesa"] != mesa_filtro]
            st.session_state["_msg_posicao"] = "Posições removidas."
            st.rerun()
