import datetime
import time
import pandas as pd
import numpy as np
import utils.logger as Logger

logger = Logger.get_logger('metrics_utils')


def calcul_variation(vol_actuel, vol_passe):
    return ((vol_actuel - vol_passe) / vol_passe) * 100 if vol_passe != 0 else 0

def volume_data(data):
    result = {}
    volumes = data["total_volumes"]

    volume_actuel = volumes[-1][1]  # Last value = current volume
    if len(volumes) < 24:
        volume_1j = volumes[0][1]
    else:
        volume_1j = volumes[-24][1]  # Second to last value = volume 1 day ago
    if len(volumes) < 168:
        volume_7j = volumes[0][1]
    else:
        volume_7j = volumes[-168][1]
    volume_30j = volumes[0][1]  # First element = volume 30 days ago

    variation_1j = calcul_variation(volume_actuel, volume_1j)
    variation_7j = calcul_variation(volume_actuel, volume_7j)
    variation_30j = calcul_variation(volume_actuel, volume_30j)

    volumes_30j = [v[1] for v in volumes]  # Get only the volumes
    volume_moyen_30j = sum(volumes_30j) / len(volumes_30j)  # Average of the last 30 days
    variation_moyenne_30j = calcul_variation(volume_actuel, volume_moyen_30j)

    volumes_7j = [v[1] for v in volumes[-168:]]  # Get only the volumes
    volume_moyen_7j = sum(volumes_7j) / len(volumes_7j)  # Average of the last 7 days
    variation_moyenne_7j = calcul_variation(volume_actuel, volume_moyen_7j)

    volumes_1j = [v[1] for v in volumes[-24:]]  # Get only the volumes
    volume_moyen_1j = sum(volumes_1j) / len(volumes_1j)  # Average of the last 1 day
    variation_moyenne_1j = calcul_variation(volume_actuel, volume_moyen_1j)

    result["volume_actuel"] = volume_actuel
    result["volume_1j"] = volume_1j
    result["volume_7j"] = volume_7j
    result["volume_30j"] = volume_30j
    result["variation_1j"] = variation_1j
    result["variation_7j"] = variation_7j
    result["variation_30j"] = variation_30j
    result["volume_moyen_30j"] = volume_moyen_30j
    result["variation_moyenne_30j"] = variation_moyenne_30j
    result["volume_moyen_7j"] = volume_moyen_7j
    result["variation_moyenne_7j"] = variation_moyenne_7j
    result["volume_moyen_1j"] = volume_moyen_1j
    result["variation_moyenne_1j"] = variation_moyenne_1j

    return result

def variation_1j(data):
    """Calculate 1-day variation."""
    if data is None:
        return None
    prices = data["prices"]
    if len(prices) < 2:
        return None
    if len(prices) < 24:
        price_1j = prices[0][1]
    else:
        price_1j = prices[-24][1]
    price_now = prices[-1][1]
    pct = (price_now - price_1j) / price_1j * 100
    mean_1j = sum([p[1] for p in prices[-24:]]) / len(prices[-24:])
    vs_avg = (price_now - mean_1j) / mean_1j * 100
    return pct , (price_now - price_1j), vs_avg, price_now

def variation_7j(data):
    """Calculate 7-day variation."""
    if data is None:
        return None
    prices = data["prices"]
    if len(prices) < 8:
        return None
    if len(prices) < 168:
        price_7j = prices[0][1]
    else:
        price_7j = prices[-168][1]
    price_now = prices[-1][1]
    pct = (price_now - price_7j) / price_7j * 100
    mean_7j = sum([p[1] for p in prices[-168:]]) / len(prices[-168:])
    vs_avg = (price_now - mean_7j) / mean_7j * 100
    return pct, (price_now - price_7j), vs_avg, mean_7j

def variation_14j(data):
    """Calculate 14-day variation."""
    if data is None:
        return None
    prices = data["prices"]
    if len(prices) < 15:
        return None
    if len(prices) < 336:
        price_14j = prices[0][1]
    else:
        price_14j = prices[-336][1]
    price_now = prices[-1][1]
    pct = (price_now - price_14j) / price_14j * 100
    mean_14j = sum([p[1] for p in prices[-336:]]) / len(prices[-336:])
    vs_avg = (price_now - mean_14j) / mean_14j * 100
    return pct, (price_now - price_14j), vs_avg, mean_14j

def variation_30j(data):
    """Calculate 30-day variation."""
    if data is None:
        return None
    prices = data["prices"]
    if len(prices) < 31:
        return None
    price_30j = prices[0][1]
    price_now = prices[-1][1]
    pct = (price_now - price_30j) / price_30j * 100
    mean_30j = sum([p[1] for p in prices]) / len(prices)
    vs_avg = (price_now - mean_30j) / mean_30j * 100
    return pct, (price_now - price_30j), vs_avg, mean_30j

def calcul_variation_price(data_all,cryto):
    if data_all is None:
        return None
    current_price = data_all["prices"][-1][1]
    var_1d_pct, var_1d_val, var_1d_val_avr_pct, mean_val_1j = variation_1j(data_all)
    var_7d_pct, var_7d_val, var_7d_val_avr_pct, mean_val_7j = variation_7j(data_all)
    var_14d_pct, var_14d_val, var_14d_val_avr_pct, mean_val_14j = variation_14j(data_all)
    var_30d_pct, var_30d_val, var_30d_val_avr_pct, mean_val_30j = variation_30j(data_all)
    results = {
        "current_price": current_price,
        "1d": {"percentage": var_1d_pct, "value": var_1d_val, "vs_avg": var_1d_val_avr_pct, "mean": mean_val_1j},
        "7d": {"percentage": var_7d_pct, "value": var_7d_val, "vs_avg": var_7d_val_avr_pct, "mean": mean_val_7j},
        "14d": {"percentage": var_14d_pct, "value": var_14d_val, "vs_avg": var_14d_val_avr_pct, "mean": mean_val_14j},
        "30d": {"percentage": var_30d_pct, "value": var_30d_val, "vs_avg": var_30d_val_avr_pct, "mean": mean_val_30j}
    }
    return results

def get_supply(crypto_id,data):
    circulating_supply = data["market_data"]["circulating_supply"]
    total_supply = data["market_data"]["total_supply"]
    max_supply = data["market_data"]["max_supply"]
    return circulating_supply, total_supply, max_supply


def calculer_pivot_support_resistance(crypto_id,data):
    high = data["market_data"]["high_24h"]["usd"]
    low = data["market_data"]["low_24h"]["usd"]
    close = data["market_data"]["current_price"]["usd"]
    PP = (high + low + close) / 3
    # Calculate resistances
    R1 = (2 * PP) - low
    R2 = PP + (high - low)
    # Calculate supports
    S1 = (2 * PP) - high
    S2 = PP - (high - low)
    return PP, R1, R2, S1, S2

def calcul_rsi(data, period=168):
    prices = [item[1] for item in data["prices"]]
    # Calculate price variations
    delta = pd.Series(prices).diff()
    # Separate gains and losses
    gains = delta.where(delta > 0, 0)
    losses = -delta.where(delta < 0, 0)
    # Average of gains and losses
    avg_gain = gains.rolling(window=period).mean()
    avg_loss = losses.rolling(window=period).mean()
    # Calculate RS (Relative Strength)
    rs = avg_gain / avg_loss
    # Calculate RSI
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calcul_macd(data, fast_period=12, slow_period=26, signal_period=9):
    prices = [item[1] for item in data["prices"]]
    if len(prices) < fast_period or len(prices) < slow_period or len(prices) < signal_period:
        return None, None, None
    # Convert to pandas Series
    prices_series = pd.Series(prices)
    # Calculate exponential moving averages
    ema_fast = prices_series.ewm(span=fast_period, adjust=False).mean()
    ema_slow = prices_series.ewm(span=slow_period, adjust=False).mean()
    # Calculate MACD
    macd = ema_fast - ema_slow
    # Calculate signal line (9 periods)
    signal_line = macd.ewm(span=signal_period, adjust=False).mean()
    # Calculate histogram
    histogram = macd - signal_line
    return macd, signal_line, histogram

def moving_averages(data, short_period=50, long_period=200):
    prices = [item[1] for item in data["prices"]]
    if len(prices) < short_period or len(prices) < long_period:
        return None
    df = pd.DataFrame(prices, columns=["Close"])
    df["SMA_50"] = df["Close"].rolling(window=short_period).mean()  # SMA 50 périodes
    df["SMA_200"] = df["Close"].rolling(window=long_period).mean()  # SMA 200 périodes
    df["EMA_50"] = df["Close"].ewm(span=short_period, adjust=False).mean()  # EMA 50
    df["EMA_200"] = df["Close"].ewm(span=long_period, adjust=False).mean()  # EMA 200
    return df

def calculate_poc(data,period=14, nb_bins=50):
    prices = [item[1] for item in data["prices"]][-(period*24):]
    volumes = [item[1] for item in data["total_volumes"]][-(period*24):]
    if not prices or not volumes or len(prices) != len(volumes):
        logger.error(" Error: Price and volume lists must be the same length and non-empty.")
        return None
    # Create a DataFrame
    df = pd.DataFrame({"price": prices, "volume": volumes})
    # Define price intervals (bins)
    df["price_bin"] = pd.cut(df["price"], bins=nb_bins)
    # Calculate volume traded by price level
    volume_profile = df.groupby("price_bin", observed=False)["volume"].sum()
    # Find the price with the most volume (POC)
    poc_bin = volume_profile.idxmax()  # POC price interval
    if pd.isna(poc_bin):
        logger.warning(" Warning: POC bin is NaN.")
        return None
    poc_price = (poc_bin.left + poc_bin.right) / 2  # Average price of the bin
    return poc_price

def get_crypto_dominance(data_global, market_cap , crypto_id="bitcoin"):
    global_market_cap = data_global["data"]["total_market_cap"]["usd"]
    dominance = (market_cap / global_market_cap) * 100
    return dominance

def fibonacci_levels(data):
    prices = [price[1] for price in data["prices"]]
    high = max(prices)
    low = min(prices)
    fib_levels_1 = high
    fib_levels_2 = high - (high - low) * 0.236
    fib_levels_3 = high - (high - low) * 0.382
    fib_levels_4 = high - (high - low) * 0.5
    fib_levels_5 = high - (high - low) * 0.618
    fib_levels_6 = high - (high - low) * 0.786
    fib_levels_7 = low
    return fib_levels_1, fib_levels_2, fib_levels_3, fib_levels_4, fib_levels_5, fib_levels_6, fib_levels_7