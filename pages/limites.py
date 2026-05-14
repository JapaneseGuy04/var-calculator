import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.title("🚦 Monitoramento de Limites")
st.markdown("---")

if not st.session_state.resultados:
    st.info("Execute o cálculo de VaR primeiro.")
    st.stop()

resultados = st.session_state.resultados
mesas = st.session_state.mesas

verdes = amarelos = vermelhos = 0
for mesa in mesas:
    res = resultados.get(mesa["nome"], {})
    var = res.get("var", 0)
    limite = mesa["limite"]
    util = var / limite * 100 if limite > 0 else 0
    if util >= 100:
        vermelhos += 1
    elif util >= 70:
        amarelos += 1
    else:
        verdes += 1

col1, col2, col3 = st.columns(3)
col1.metric("🟢 Dentro do Limite", verdes)
col2.metric("🟡 Em Atenção (>70%)", amarelos)
col3.metric("🔴 Limite Excedido", vermelhos)

if vermelhos > 0:
    st.error(f"⚠️ {vermelhos} mesa(s) com limite excedido!")
if amarelos > 0:
    st.warning(f"⚠️ {amarelos} mesa(s) em zona de atenção (>70% do limite).")

st.markdown("---")
st.subheader("Detalhamento por Mesa")

rows = []
for mesa in mesas:
    nome = mesa["nome"]
    res = resultados.get(nome, {})
    var = res.get("var", 0)
    es = res.get("es", 0)
    limite = mesa["limite"]
    util = var / limite * 100 if limite > 0 else 0
    disponivel = max(limite - var, 0)
    status = "🟢 OK" if util < 70 else ("🟡 Atenção" if util < 100 else "🔴 Excedido")
    rows.append({
        "Mesa": nome,
        "VaR (R$)": f"R$ {var:,.0f}",
        "ES (R$)": f"R$ {es:,.0f}",
        "Limite (R$)": f"R$ {limite:,.0f}",
        "Utilização (%)": f"{util:.1f}%",
        "Disponível (R$)": f"R$ {disponivel:,.0f}",
        "Status": status,
    })

st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

st.markdown("---")
st.subheader("Utilização dos Limites")

nomes = [m["nome"] for m in mesas]
utils = []
for mesa in mesas:
    res = resultados.get(mesa["nome"], {})
    var = res.get("var", 0)
    util = var / mesa["limite"] * 100 if mesa["limite"] > 0 else 0
    utils.append(min(util, 150))

cores = ["green" if u < 70 else ("orange" if u < 100 else "red") for u in utils]

fig = go.Figure(go.Bar(
    x=utils,
    y=nomes,
    orientation="h",
    marker_color=cores,
    text=[f"{u:.1f}%" for u in utils],
    textposition="outside",
))
fig.add_vline(x=70, line_dash="dot", line_color="orange", annotation_text="70%")
fig.add_vline(x=100, line_dash="dash", line_color="red", annotation_text="100%")
fig.update_layout(xaxis_title="Utilização (%)", height=350, xaxis=dict(range=[0, max(max(utils) * 1.2, 120)]))
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("Ranking de Risco")
ranking = sorted(rows, key=lambda x: float(x["Utilização (%)"].replace("%", "")), reverse=True)
st.dataframe(pd.DataFrame(ranking), use_container_width=True, hide_index=True)
