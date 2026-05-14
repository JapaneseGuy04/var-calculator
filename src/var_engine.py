import numpy as np
import pandas as pd
from scipy.stats import norm
from src.options import black_scholes, delta as bs_delta


def _pnl_historico_mesa(posicoes, dados_historicos, taxa_livre_risco):
    retornos = dados_historicos.pct_change().dropna()
    pnl_total = pd.Series(0.0, index=retornos.index)

    for pos in posicoes:
        ticker = pos["ticker"]
        qtd = pos["quantidade"]
        tipo = pos["tipo"]

        if ticker not in retornos.columns:
            continue

        ret_serie = retornos[ticker]
        preco_atual = dados_historicos[ticker].iloc[-1]

        if tipo == "Ação":
            pnl_total += ret_serie * qtd * preco_atual

        elif tipo in ("Call", "Put"):
            K = pos["strike"]
            T_dias = pos["vencimento_dias"]
            sigma = pos["volatilidade"]
            r = taxa_livre_risco
            tipo_op = tipo.lower()

            pnl_op = pd.Series(0.0, index=ret_serie.index)
            for data, ret in ret_serie.items():
                S_hist = preco_atual * (1 + ret)
                T_hist = max(T_dias / 365, 1 / 365)
                preco_hoje = black_scholes(preco_atual, K, T_dias / 365, r, sigma, tipo_op)
                preco_cen = black_scholes(S_hist, K, T_hist, r, sigma, tipo_op)
                pnl_op[data] = (preco_cen - preco_hoje) * qtd

            pnl_total += pnl_op

    return pnl_total


def var_historico(posicoes, dados_historicos, taxa_livre_risco=0.1075,
                  confianca=0.99, horizonte=1):
    pnl = _pnl_historico_mesa(posicoes, dados_historicos, taxa_livre_risco)
    if pnl.empty or pnl.std() == 0:
        return {"var": 0, "es": 0, "pnl": pnl, "ok": False}

    pnl_h = pnl * np.sqrt(horizonte)
    var = float(-np.percentile(pnl_h, (1 - confianca) * 100))
    es = float(-pnl_h[pnl_h <= -var].mean()) if len(pnl_h[pnl_h <= -var]) > 0 else var
    return {"var": var, "es": es, "pnl": pnl, "ok": True}


def var_parametrico(posicoes, dados_historicos, taxa_livre_risco=0.1075,
                    confianca=0.99, horizonte=1):
    tickers = [p["ticker"] for p in posicoes if p["ticker"] in dados_historicos.columns]
    if not tickers:
        return {"var": 0, "es": 0, "ok": False}

    retornos = dados_historicos[tickers].pct_change().dropna()
    cov = retornos.cov().values * 252
    z = norm.ppf(confianca)

    exposicoes = []
    for ticker in tickers:
        preco = dados_historicos[ticker].iloc[-1]
        exp = 0.0
        for pos in posicoes:
            if pos["ticker"] != ticker:
                continue
            if pos["tipo"] == "Ação":
                exp += pos["quantidade"] * preco
            elif pos["tipo"] in ("Call", "Put"):
                d = bs_delta(preco, pos["strike"], pos["vencimento_dias"] / 365,
                             taxa_livre_risco, pos["volatilidade"], pos["tipo"].lower())
                exp += d * pos["quantidade"] * preco
        exposicoes.append(exp)

    w = np.array(exposicoes)
    variancia = float(w @ cov @ w)
    if variancia <= 0:
        return {"var": 0, "es": 0, "ok": False}

    sigma_port = np.sqrt(variancia / 252)
    var = float(z * sigma_port * np.sqrt(horizonte))
    es = float(norm.pdf(norm.ppf(confianca)) / (1 - confianca) * sigma_port * np.sqrt(horizonte))
    return {"var": var, "es": es, "ok": True}


def var_monte_carlo(posicoes, dados_historicos, taxa_livre_risco=0.1075,
                    confianca=0.99, horizonte=1, n_sim=10000):
    tickers = [p["ticker"] for p in posicoes if p["ticker"] in dados_historicos.columns]
    if not tickers:
        return {"var": 0, "es": 0, "perdas": np.array([]), "ok": False}

    retornos = dados_historicos[tickers].pct_change().dropna()
    mu = retornos.mean().values
    cov = retornos.cov().values
    T = horizonte / 252

    try:
        L = np.linalg.cholesky(cov + np.eye(len(tickers)) * 1e-10)
    except np.linalg.LinAlgError:
        return {"var": 0, "es": 0, "perdas": np.array([]), "ok": False}

    Z = np.random.standard_normal((n_sim, len(tickers)))
    corr_Z = Z @ L.T
    log_ret = (mu - 0.5 * np.diag(cov)) * T + corr_Z * np.sqrt(T)

    precos_atuais = {t: dados_historicos[t].iloc[-1] for t in tickers}
    pnl_sim = np.zeros(n_sim)

    for pos in posicoes:
        ticker = pos["ticker"]
        if ticker not in tickers:
            continue
        idx = tickers.index(ticker)
        S0 = precos_atuais[ticker]
        S_T = S0 * np.exp(log_ret[:, idx])

        if pos["tipo"] == "Ação":
            pnl_sim += (S_T - S0) * pos["quantidade"]
        elif pos["tipo"] in ("Call", "Put"):
            K = pos["strike"]
            T_op = max(pos["vencimento_dias"] / 365, 1 / 365)
            sigma = pos["volatilidade"]
            r = taxa_livre_risco
            tipo_op = pos["tipo"].lower()
            preco_hoje = black_scholes(S0, K, T_op, r, sigma, tipo_op)
            T_restante = max(T_op - T, 1 / 365)
            preco_sim = np.array([black_scholes(s, K, T_restante, r, sigma, tipo_op) for s in S_T])
            pnl_sim += (preco_sim - preco_hoje) * pos["quantidade"]

    perdas = -pnl_sim
    var = float(np.percentile(perdas, confianca * 100))
    es_vals = perdas[perdas >= var]
    es = float(es_vals.mean()) if len(es_vals) > 0 else var
    return {"var": var, "es": es, "perdas": perdas, "ok": True}


def backtesting(pnl_serie, confianca=0.99, janela=252):
    if len(pnl_serie) < janela:
        return None

    vars_calc = []
    pnl_real = []
    datas = []

    pnl_array = pnl_serie.values
    idx = pnl_serie.index

    for i in range(janela, len(pnl_array)):
        janela_hist = pnl_array[i - janela:i]
        var_d = float(-np.percentile(janela_hist, (1 - confianca) * 100))
        vars_calc.append(var_d)
        pnl_real.append(pnl_array[i])
        datas.append(idx[i])

    vars_calc = np.array(vars_calc)
    pnl_real = np.array(pnl_real)
    excecoes = int(np.sum(pnl_real < -vars_calc))
    n_obs = len(pnl_real)
    excecoes_esperadas = round((1 - confianca) * n_obs, 1)
    taxa = excecoes / n_obs if n_obs > 0 else 0

    if n_obs >= 250:
        if excecoes <= 4:
            semaforo = "verde"
        elif excecoes <= 9:
            semaforo = "amarelo"
        else:
            semaforo = "vermelho"
    else:
        semaforo = "inconclusivo"

    return {
        "excecoes": excecoes,
        "excecoes_esperadas": excecoes_esperadas,
        "n_observacoes": n_obs,
        "taxa_excecao": taxa,
        "semaforo": semaforo,
        "vars_calc": vars_calc,
        "pnl_real": pnl_real,
        "datas": datas,
    }


def calcular_var_todas_mesas(mesas, posicoes, dados_historicos, parametros):
    resultados = {}
    metodo = parametros.get("metodo", "Histórico")
    confianca = parametros.get("confianca", 0.99)
    horizonte = parametros.get("horizonte", 1)
    n_sim = parametros.get("n_simulacoes", 10000)
    r = parametros.get("taxa_livre_risco", 0.1075)

    for mesa in mesas:
        nome = mesa["nome"]
        pos_mesa = [p for p in posicoes if p["mesa"] == nome]
        if not pos_mesa:
            resultados[nome] = {"var": 0, "es": 0, "ok": False, "limite": mesa["limite"]}
            continue

        if metodo == "Histórico":
            res = var_historico(pos_mesa, dados_historicos, r, confianca, horizonte)
        elif metodo == "Paramétrico":
            res = var_parametrico(pos_mesa, dados_historicos, r, confianca, horizonte)
        else:
            res = var_monte_carlo(pos_mesa, dados_historicos, r, confianca, horizonte, n_sim)

        res["limite"] = mesa["limite"]
        res["posicoes"] = pos_mesa

        if res.get("ok") and "pnl" not in res:
            pnl_res = var_historico(pos_mesa, dados_historicos, r, confianca, horizonte)
            res["pnl"] = pnl_res.get("pnl", pd.Series())

        resultados[nome] = res

    return resultados
