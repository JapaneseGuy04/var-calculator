import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

st.title("📊 Dashboard Executivo")
st.markdown("---")

if not st.session_state.resultados:
    st.info("Execute o cálculo de VaR primeiro.")
    st.stop()

resultados = st.session_state.resultados
mesas = st.session_state.mesas
p = st.session_state.parametros

total_var = sum(resultados.get(m["nome"], {}).get("var", 0) for m in mesas)
total_es = sum(resultados.get(m["nome"], {}).get("es", 0) for m in mesas)
total_limite = sum(m["limite"] for m in mesas)
util_consolidada = total_var / total_limite * 100 if total_limite > 0 else 0

excedidos = sum(1 for m in mesas if resultados.get(m["nome"], {}).get("var", 0) / m["limite"] * 100 >= 100)
atencao = sum(1 for m in mesas if 70 <= resultados.get(m["nome"], {}).get("var", 0) / m["limite"] * 100 < 100)

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("VaR Total", f"R$ {total_var:,.0f}")
col2.metric("ES Total", f"R$ {total_es:,.0f}")
col3.metric("Utilização Consolidada", f"{util_consolidada:.1f}%")
col4.metric("Mesas Excedidas", excedidos)
col5.metric("Mesas em Atenção", atencao)

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    cor_gauge = "green" if util_consolidada < 70 else ("orange" if util_consolidada < 100 else "red")
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=util_consolidada,
        title={"text": "Utilização Consolidada (%)"},
        delta={"reference": 100},
        gauge={
            "axis": {"range": [0, 150]},
            "bar": {"color": cor_gauge},
            "steps": [
                {"range": [0, 70], "color": "lightgreen"},
                {"range": [70, 100], "color": "lightyellow"},
                {"range": [100, 150], "color": "lightcoral"},
            ],
            "threshold": {"line": {"color": "red", "width": 4}, "thickness": 0.75, "value": 100},
        },
    ))
    fig_gauge.update_layout(height=300)
    st.plotly_chart(fig_gauge, use_container_width=True)

with col2:
    nomes = [m["nome"].replace("Mesa ", "") for m in mesas]
    vars_vals = [resultados.get(m["nome"], {}).get("var", 0) for m in mesas]
    es_vals = [resultados.get(m["nome"], {}).get("es", 0) for m in mesas]
    limites_vals = [m["limite"] for m in mesas]

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(name="VaR", x=nomes, y=vars_vals, marker_color="steelblue"))
    fig_bar.add_trace(go.Bar(name="ES", x=nomes, y=es_vals, marker_color="coral"))
    fig_bar.add_trace(go.Scatter(name="Limite", x=nomes, y=limites_vals, mode="markers",
                                  marker=dict(symbol="line-ew-open", size=20, color="black", line_width=3)))
    fig_bar.update_layout(title="VaR, ES e Limites por Mesa", barmode="group", height=300, yaxis_title="R$")
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    utils = [resultados.get(m["nome"], {}).get("var", 0) / m["limite"] * 100 if m["limite"] > 0 else 0 for m in mesas]
    nomes_full = [m["nome"] for m in mesas]
    cores = ["green" if u < 70 else ("orange" if u < 100 else "red") for u in utils]

    fig_util = go.Figure(go.Bar(
        x=utils, y=nomes_full, orientation="h",
        marker_color=cores,
        text=[f"{u:.1f}%" for u in utils],
        textposition="outside",
    ))
    fig_util.add_vline(x=100, line_dash="dash", line_color="red")
    fig_util.update_layout(title="Utilização dos Limites", height=300,
                            xaxis=dict(range=[0, max(max(utils) * 1.2, 120)]))
    st.plotly_chart(fig_util, use_container_width=True)

with col2:
    if any(v > 0 for v in vars_vals):
        fig_pie = px.pie(values=vars_vals, names=[m["nome"].replace("Mesa ", "") for m in mesas],
                         title="Composição do VaR Total")
        fig_pie.update_layout(height=300)
        st.plotly_chart(fig_pie, use_container_width=True)

dados = st.session_state.dados_historicos
if dados is not None and not dados.empty:
    st.markdown("---")
    st.subheader("Evolução de Preços (Base 100)")
    fig_norm = go.Figure()
    for col in dados.columns[:8]:
        serie = dados[col].dropna()
        if len(serie) > 0:
            normalizada = serie / serie.iloc[0] * 100
            fig_norm.add_trace(go.Scatter(x=normalizada.index, y=normalizada.values, name=col, mode="lines"))
    fig_norm.update_layout(height=400, yaxis_title="Índice (Base 100)")
    st.plotly_chart(fig_norm, use_container_width=True)

st.markdown("---")
st.subheader("Tabela Executiva Consolidada")

exec_rows = []
for mesa in mesas:
    nome = mesa["nome"]
    res = resultados.get(nome, {})
    var = res.get("var", 0)
    es = res.get("es", 0)
    limite = mesa["limite"]
    util = var / limite * 100 if limite > 0 else 0
    status = "🟢 OK" if util < 70 else ("🟡 Atenção" if util < 100 else "🔴 Excedido")
    exec_rows.append({
        "Mesa": nome, "VaR": f"R$ {var:,.0f}", "ES": f"R$ {es:,.0f}",
        "Limite": f"R$ {limite:,.0f}", "Utilização": f"{util:.1f}%", "Status": status,
    })

exec_rows.append({
    "Mesa": "TOTAL", "VaR": f"R$ {total_var:,.0f}", "ES": f"R$ {total_es:,.0f}",
    "Limite": f"R$ {total_limite:,.0f}", "Utilização": f"{util_consolidada:.1f}%",
    "Status": "🟢 OK" if util_consolidada < 70 else ("🟡 Atenção" if util_consolidada < 100 else "🔴 Excedido"),
})

st.dataframe(pd.DataFrame(exec_rows), use_container_width=True, hide_index=True)
