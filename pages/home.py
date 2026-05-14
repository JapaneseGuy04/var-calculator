import streamlit as st

st.title("Sistema de Gestão de Risco — VaR Calculator")
st.markdown("---")

st.markdown("""
## Sobre o Sistema

Esta plataforma calcula o **Value at Risk (VaR)** para carteiras de mesas de trading,
permitindo o monitoramento de risco de mercado com três metodologias distintas.

### Fluxo de Uso

1. **Mesas de Trading** → Cadastre as mesas e seus limites de VaR
2. **Posições** → Registre os ativos de cada mesa (ações e opções)
3. **Parâmetros** → Configure nível de confiança, horizonte e metodologia
4. **Cálculo VaR** → Execute o cálculo e visualize os resultados
5. **Monitoramento** → Acompanhe o status dos limites em tempo real
""")

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### Metodologias")
    st.markdown("""
    - **Histórico**: Distribuição empírica dos retornos
    - **Paramétrico**: Matriz de covariância + normalidade
    - **Monte Carlo**: Simulação GBM com Cholesky
    """)

with col2:
    st.markdown("### Métricas")
    st.markdown("""
    - **VaR**: Perda máxima dado nível de confiança
    - **Expected Shortfall**: Média das perdas além do VaR
    - **Backtesting**: Validação histórica do modelo
    """)

with col3:
    st.markdown("### Ativos Suportados")
    st.markdown("""
    - **Ações**: Retorno logarítmico × exposição
    - **Calls**: Repricing Black-Scholes completo
    - **Puts**: Repricing Black-Scholes completo
    """)

st.markdown("---")
st.info("Comece cadastrando as **Mesas de Trading** e depois registre as **Posições**.")
