from scipy.optimize import fsolve
from scipy.stats import norm
import math

def black_scholes_call(S, K, T, r, sigma):
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    call_price = S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    return call_price

def implied_volatility(option_price, S, K, T, r, initial_volatility_guess= 0.275):
    # Define the Black-Scholes equation to solve for implied volatility
    black_scholes_equation = lambda sigma: black_scholes_call(S, K, T, r, sigma) - option_price

    # Use fsolve to find the root (implied volatility)
    implied_volatility, = fsolve(black_scholes_equation, initial_volatility_guess)

    return implied_volatility

# Example usage:
option_price = 297.653  # Replace with the actual option price
S = 1209.5  # Current stock price
K = 1033  # Option strike price
T = 1.67  # Time to expiration (in years)
r = 0.05045  # Risk-free interest rate

implied_vol = implied_volatility(option_price, S, K, T, r)
print(f"Implied Volatility: {implied_vol:.4f}")
