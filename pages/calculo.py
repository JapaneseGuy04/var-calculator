import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from src.data_fetcher import fetch_prices
from src.var_engine import calcular_var_todas_mesas, backtesting

st.title("📈 Cálculo de VaR")
st.markdown("---")

if not st.session_state.mesas:
    st.warning("Cadastre mesas de trading primeiro.")
    st.stop()

if not st.session_state.posicoes:
    st.warning("Cadastre posições antes de calcular.")
    st.stop()

p = st.session_state.parametros

col1, col2, col3 = st.columns(3)
col1.metric("Metodologia", p["metodo"])
col2.metric("Confiança", f"{int(p['confianca']*100)}%")
col3.metric("Horizonte", f"{p['horizonte']} dia(s)")

st.markdown("---")

if st.button("🚀 Buscar Dados e Calcular VaR", type="primary", use_container_width=True):
    tickers = tuple(set(pos["ticker"] for pos in st.session_state.posicoes))
    with st.spinner(f"Buscando dados para {len(tickers)} ticker(s)..."):
        dados = fetch_prices(tickers, p["janela_historica"])

    if dados.empty:
        st.error("Não foi possível obter dados. Verifique os tickers.")
        st.stop()

    tickers_ok = [t for t in tickers if t in dados.columns]
    tickers_erro = [t for t in tickers if t not in dados.columns]
    if tickers_erro:
        st.warning(f"Tickers não encontrados: {tickers_erro}")

    st.session_state.dados_historicos = dados

    with st.spinner("Calculando VaR..."):
        resultados = calcular_var_todas_mesas(
            st.session_state.mesas,
            st.session_state.posicoes,
            dados,
            p,
        )
    st.session_state.resultados = resultados
    st.success(f"Cálculo concluído! {len(tickers_ok)} ativo(s) carregados.")

if not st.session_state.resultados:
    st.info("Clique em 'Buscar Dados e Calcular VaR' para iniciar.")
    st.stop()

resultados = st.session_state.resultados

st.markdown("---")
st.subheader("Resultados por Mesa")

rows = []
for mesa in st.session_state.mesas:
    nome = mesa["nome"]
    res = resultados.get(nome, {})
    var = res.get("var", 0)
    es = res.get("es", 0)
    limite = mesa["limite"]
    util = var / limite * 100 if limite > 0 else 0
    status = "🟢 OK" if util < 70 else ("🟡 Atenção" if util < 100 else "🔴 Excedido")
    rows.append({
        "Mesa": nome,
        "VaR (R$)": f"R$ {var:,.0f}",
        "ES (R$)": f"R$ {es:,.0f}",
        "Limite (R$)": f"R$ {limite:,.0f}",
        "Utilização (%)": f"{util:.1f}%",
        "Status": status,
    })

df_res = pd.DataFrame(rows)
st.dataframe(df_res, use_container_width=True, hide_index=True)

st.markdown("---")
st.subheader("VaR vs Limite por Mesa")

nomes = [m["nome"] for m in st.session_state.mesas]
vars_vals = [resultados.get(n, {}).get("var", 0) for n in nomes]
limites_vals = [m["limite"] for m in st.session_state.mesas]
cores = []
for v, l in zip(vars_vals, limites_vals):
    u = v / l * 100 if l > 0 else 0
    cores.append("green" if u < 70 else ("orange" if u < 100 else "red"))

fig = go.Figure()
fig.add_trace(go.Bar(name="VaR", x=nomes, y=vars_vals, marker_color=cores))
fig.add_trace(go.Scatter(name="Limite", x=nomes, y=limites_vals,
                          mode="markers", marker=dict(symbol="line-ew-open", size=20, color="black", line_width=3)))
fig.update_layout(title="VaR vs Limite", yaxis_title="R$", height=400)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("Análise por Mesa")

mesa_sel = st.selectbox("Selecione a mesa", nomes)
res_sel = resultados.get(mesa_sel, {})

if res_sel.get("ok"):
    col1, col2 = st.columns(2)

    if "pnl" in res_sel and not res_sel["pnl"].empty:
        with col1:
            st.markdown("**Distribuição P&L Histórico**")
            pnl = res_sel["pnl"]
            var_val = res_sel.get("var", 0)
            fig_hist = px.histogram(pnl, nbins=50, labels={"value": "P&L (R$)"})
            fig_hist.add_vline(x=-var_val, line_dash="dash", line_color="red",
                               annotation_text=f"VaR: R$ {var_val:,.0f}")
            fig_hist.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig_hist, use_container_width=True)

    if "perdas" in res_sel and len(res_sel["perdas"]) > 0:
        with col2:
            st.markdown("**Distribuição de Perdas (Monte Carlo)**")
            perdas = res_sel["perdas"]
            var_val = res_sel.get("var", 0)
            fig_mc = px.histogram(perdas, nbins=80, labels={"value": "Perda (R$)"})
            fig_mc.add_vline(x=var_val, line_dash="dash", line_color="red",
                             annotation_text=f"VaR {int(p['confianca']*100)}%")
            fig_mc.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig_mc, use_container_width=True)

    dados = st.session_state.dados_historicos
    pos_mesa = [pos for pos in st.session_state.posicoes if pos["mesa"] == mesa_sel]
    tickers_mesa = [pos["ticker"] for pos in pos_mesa if pos["ticker"] in dados.columns]
    if tickers_mesa:
        st.markdown("**Evolução dos Preços**")
        fig_price = go.Figure()
        for tk in tickers_mesa:
            fig_price.add_trace(go.Scatter(x=dados.index, y=dados[tk], name=tk, mode="lines"))
        fig_price.update_layout(height=350, yaxis_title="Preço (R$)")
        st.plotly_chart(fig_price, use_container_width=True)

    st.markdown("---")
    st.subheader(f"Backtesting — {mesa_sel}")

    if "pnl" in res_sel and len(res_sel["pnl"]) > p["janela_historica"]:
        janela_bt = p["janela_historica"]
        bt = backtesting(res_sel["pnl"], p["confianca"], janela_bt)
        if bt:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Exceções", bt["excecoes"])
            col2.metric("Exceções Esperadas", bt["excecoes_esperadas"])
            col3.metric("Taxa de Exceção", f"{bt['taxa_excecao']*100:.2f}%")
            semaforo_map = {"verde": "🟢 Verde", "amarelo": "🟡 Amarelo", "vermelho": "🔴 Vermelho", "inconclusivo": "⚪ Inconclusivo"}
            col4.metric("Semáforo Basel", semaforo_map.get(bt["semaforo"], bt["semaforo"]))

            fig_bt = go.Figure()
            fig_bt.add_trace(go.Scatter(x=bt["datas"], y=bt["pnl_real"], name="P&L Real",
                                        mode="lines", line=dict(color="blue")))
            fig_bt.add_trace(go.Scatter(x=bt["datas"], y=-bt["vars_calc"], name="VaR (negativo)",
                                        mode="lines", line=dict(color="red", dash="dash")))
            excecao_idx = [i for i, (pnl, var) in enumerate(zip(bt["pnl_real"], bt["vars_calc"])) if pnl < -var]
            if excecao_idx:
                fig_bt.add_trace(go.Scatter(
                    x=[bt["datas"][i] for i in excecao_idx],
                    y=[bt["pnl_real"][i] for i in excecao_idx],
                    mode="markers", name="Exceções",
                    marker=dict(color="red", size=8, symbol="x"),
                ))
            fig_bt.update_layout(title="Backtesting: P&L Real vs VaR", height=400)
            st.plotly_chart(fig_bt, use_container_width=True)
    else:
        st.info(f"Dados insuficientes para backtesting (necessário > {p['janela_historica']} observações).")
else:
    st.warning(f"Sem dados calculados para {mesa_sel}. Verifique se há posições com tickers válidos.")
