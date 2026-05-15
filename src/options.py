import numpy as np
from scipy.stats import norm


def black_scholes(S, K, T, r, sigma, tipo="call"):
    if T <= 0:
        if tipo == "call":
            return max(S - K, 0)
        else:
            return max(K - S, 0)
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if tipo == "call":
        return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)


def delta(S, K, T, r, sigma, tipo="call"):
    if T <= 0:
        if tipo == "call":
            return 1.0 if S > K else 0.0
        else:
            return -1.0 if S < K else 0.0
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    if tipo == "call":
        return norm.cdf(d1)
    else:
        return norm.cdf(d1) - 1


def gamma(S, K, T, r, sigma):
    if T <= 0:
        return 0.0
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    return norm.pdf(d1) / (S * sigma * np.sqrt(T))


def vega(S, K, T, r, sigma):
    if T <= 0:
        return 0.0
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    return S * norm.pdf(d1) * np.sqrt(T) * 0.01


def theta(S, K, T, r, sigma, tipo="call"):
    if T <= 0:
        return 0.0
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if tipo == "call":
        t = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T))
             - r * K * np.exp(-r * T) * norm.cdf(d2))
    else:
        t = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T))
             + r * K * np.exp(-r * T) * norm.cdf(-d2))
    return t / 365


def implied_vol(S, K, T, r, market_price, tipo="call", tol=1e-6, max_iter=300):
    """Calcula volatilidade implícita via bisseção invertendo Black-Scholes."""
    if T <= 0 or S <= 0 or K <= 0:
        return None

    # Preço intrínseco mínimo
    if tipo == "call":
        intrinsic = max(S - K * np.exp(-r * T), 0)
    else:
        intrinsic = max(K * np.exp(-r * T) - S, 0)

    if market_price <= intrinsic:
        return None  # Preço abaixo do intrínseco — IV indefinida

    vol_low, vol_high = 1e-4, 10.0
    for _ in range(max_iter):
        vol_mid = (vol_low + vol_high) / 2
        price_mid = black_scholes(S, K, T, r, vol_mid, tipo)
        diff = price_mid - market_price
        if abs(diff) < tol:
            return vol_mid
        if diff < 0:
            vol_low = vol_mid
        else:
            vol_high = vol_mid
    return (vol_low + vol_high) / 2


def greeks(S, K, T, r, sigma, tipo="call"):
    return {
        "delta": delta(S, K, T, r, sigma, tipo),
        "gamma": gamma(S, K, T, r, sigma),
        "vega": vega(S, K, T, r, sigma),
        "theta": theta(S, K, T, r, sigma, tipo),
        "preco": black_scholes(S, K, T, r, sigma, tipo),
    }
