import datetime
import time
import pandas as pd
import numpy as np
import scrapy.utils.logger as Logger

logger = Logger.get_logger('metrics_utils')


def calcul_variation(vol_actuel, vol_passe):
    """Calculate percentage variation between current and past values.
    
    Args:
        vol_actuel: Current value
        vol_passe: Past value to compare against
        
    Returns:
        float: Percentage change, or 0 if past value is 0
    """
    return ((vol_actuel - vol_passe) / vol_passe) * 100 if vol_passe != 0 else 0

def volume_data(data):
    """Calculate volume metrics and variations across multiple timeframes.
    
    Computes current volume, historical volumes (1d, 7d, 30d ago), percentage
    variations, and average volumes with their respective variations.
    
    Args:
        data (dict): Market data containing 'total_volumes' key with timestamp-volume pairs
        
    Returns:
        dict: Dictionary containing 13 volume metrics:
            - volume_actuel: Current volume
            - volume_1j/7j/30j: Volume N days ago
            - variation_1j/7j/30j: Percentage change from N days ago
            - volume_moyen_1j/7j/30j: Average volume over N days
            - variation_moyenne_1j/7j/30j: Percentage change vs average
    """
    result = {}
    volumes = data["total_volumes"]

    volume_actuel = volumes[-1][1]
    if len(volumes) < 24:
        volume_1j = volumes[0][1]
    else:
        volume_1j = volumes[-24][1]
    if len(volumes) < 168:
        volume_7j = volumes[0][1]
    else:
        volume_7j = volumes[-168][1]
    volume_30j = volumes[0][1]

    variation_1j = calcul_variation(volume_actuel, volume_1j)
    variation_7j = calcul_variation(volume_actuel, volume_7j)
    variation_30j = calcul_variation(volume_actuel, volume_30j)

    volumes_30j = [v[1] for v in volumes]
    volume_moyen_30j = sum(volumes_30j) / len(volumes_30j)
    variation_moyenne_30j = calcul_variation(volume_actuel, volume_moyen_30j)

    volumes_7j = [v[1] for v in volumes[-168:]]
    volume_moyen_7j = sum(volumes_7j) / len(volumes_7j)
    variation_moyenne_7j = calcul_variation(volume_actuel, volume_moyen_7j)

    volumes_1j = [v[1] for v in volumes[-24:]]
    volume_moyen_1j = sum(volumes_1j) / len(volumes_1j)
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
    """Calculate 1-day price variation metrics.
    
    Args:
        data (dict): Market data containing 'prices' key
        
    Returns:
        tuple: (percentage_change, absolute_change, vs_avg_percentage, current_price)
            or None if insufficient data
    """
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
    """Calculate 7-day price variation metrics.
    
    Args:
        data (dict): Market data containing 'prices' key
        
    Returns:
        tuple: (percentage_change, absolute_change, vs_avg_percentage, mean_7d)
            or None if insufficient data
    """
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
    """Calculate 14-day price variation metrics.
    
    Args:
        data (dict): Market data containing 'prices' key
        
    Returns:
        tuple: (percentage_change, absolute_change, vs_avg_percentage, mean_14d)
            or None if insufficient data
    """
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
    """Calculate 30-day price variation metrics.
    
    Args:
        data (dict): Market data containing 'prices' key
        
    Returns:
        tuple: (percentage_change, absolute_change, vs_avg_percentage, mean_30d)
            or None if insufficient data
    """
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
    """Calculate comprehensive price variation metrics across multiple timeframes.
    
    Aggregates variation data for 1d, 7d, 14d, and 30d periods.
    
    Args:
        data_all (dict): Complete market data
        cryto (str): Cryptocurrency identifier (currently unused)
        
    Returns:
        dict: Nested dictionary with current_price and timeframe metrics (1d, 7d, 14d, 30d),
            each containing percentage, value, vs_avg, and mean keys
    """
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
    """Extract supply metrics from cryptocurrency market data.
    
    Args:
        crypto_id (str): Cryptocurrency identifier (currently unused)
        data (dict): Market data containing 'market_data' key
        
    Returns:
        tuple: (circulating_supply, total_supply, max_supply)
    """
    circulating_supply = data["market_data"]["circulating_supply"]
    total_supply = data["market_data"]["total_supply"]
    max_supply = data["market_data"]["max_supply"]
    return circulating_supply, total_supply, max_supply


def calculer_pivot_support_resistance(crypto_id,data):
    """Calculate pivot points and support/resistance levels.
    
    Uses the standard pivot point formula with 24h high, low, and close prices.
    
    Args:
        crypto_id (str): Cryptocurrency identifier (currently unused)
        data (dict): Market data containing 24h price information
        
    Returns:
        tuple: (pivot_point, R1, R2, S1, S2) resistance and support levels
    """
    high = data["market_data"]["high_24h"]["usd"]
    low = data["market_data"]["low_24h"]["usd"]
    close = data["market_data"]["current_price"]["usd"]
    PP = (high + low + close) / 3
    R1 = (2 * PP) - low
    R2 = PP + (high - low)
    S1 = (2 * PP) - high
    S2 = PP - (high - low)
    return PP, R1, R2, S1, S2

def calcul_rsi(data, period=168):
    """Calculate Relative Strength Index (RSI) indicator.
    
    RSI measures momentum by comparing average gains to average losses over a period.
    Default period of 168 hours = 7 days.
    
    Args:
        data (dict): Market data containing 'prices' key
        period (int, optional): RSI calculation period. Defaults to 168 (7 days).
        
    Returns:
        pandas.Series: RSI values from 0 to 100
    """
    prices = [item[1] for item in data["prices"]]
    delta = pd.Series(prices).diff()
    gains = delta.where(delta > 0, 0)
    losses = -delta.where(delta < 0, 0)
    avg_gain = gains.rolling(window=period).mean()
    avg_loss = losses.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calcul_macd(data, fast_period=12, slow_period=26, signal_period=9):
    """Calculate MACD (Moving Average Convergence Divergence) indicator.
    
    MACD shows the relationship between two exponential moving averages.
    
    Args:
        data (dict): Market data containing 'prices' key
        fast_period (int, optional): Fast EMA period. Defaults to 12.
        slow_period (int, optional): Slow EMA period. Defaults to 26.
        signal_period (int, optional): Signal line period. Defaults to 9.
        
    Returns:
        tuple: (macd_line, signal_line, histogram) as pandas Series,
            or (None, None, None) if insufficient data
    """
    prices = [item[1] for item in data["prices"]]
    if len(prices) < fast_period or len(prices) < slow_period or len(prices) < signal_period:
        return None, None, None
    prices_series = pd.Series(prices)
    ema_fast = prices_series.ewm(span=fast_period, adjust=False).mean()
    ema_slow = prices_series.ewm(span=slow_period, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal_period, adjust=False).mean()
    histogram = macd - signal_line
    return macd, signal_line, histogram

def moving_averages(data, short_period=50, long_period=200):
    """Calculate Simple and Exponential Moving Averages.
    
    Computes both SMA and EMA for short and long periods to identify trends.
    
    Args:
        data (dict): Market data containing 'prices' key
        short_period (int, optional): Short-term period. Defaults to 50.
        long_period (int, optional): Long-term period. Defaults to 200.
        
    Returns:
        pandas.DataFrame: DataFrame with Close, SMA_50, SMA_200, EMA_50, EMA_200 columns,
            or None if insufficient data
    """
    prices = [item[1] for item in data["prices"]]
    if len(prices) < short_period or len(prices) < long_period:
        return None
    df = pd.DataFrame(prices, columns=["Close"])
    df["SMA_50"] = df["Close"].rolling(window=short_period).mean()
    df["SMA_200"] = df["Close"].rolling(window=long_period).mean()
    df["EMA_50"] = df["Close"].ewm(span=short_period, adjust=False).mean()
    df["EMA_200"] = df["Close"].ewm(span=long_period, adjust=False).mean()
    return df

def calculate_poc(data,period=14, nb_bins=50):
    """Calculate Point of Control (POC) from volume profile.
    
    POC is the price level with the highest traded volume over the period.
    
    Args:
        data (dict): Market data containing 'prices' and 'total_volumes' keys
        period (int, optional): Number of days to analyze. Defaults to 14.
        nb_bins (int, optional): Number of price bins for histogram. Defaults to 50.
        
    Returns:
        float: POC price level, or None if insufficient/invalid data
    """
    prices = [item[1] for item in data["prices"]][-(period*24):]
    volumes = [item[1] for item in data["total_volumes"]][-(period*24):]
    if not prices or not volumes or len(prices) != len(volumes):
        logger.error(" Error: Price and volume lists must be the same length and non-empty.")
        return None
    df = pd.DataFrame({"price": prices, "volume": volumes})
    df["price_bin"] = pd.cut(df["price"], bins=nb_bins)
    volume_profile = df.groupby("price_bin", observed=False)["volume"].sum()
    poc_bin = volume_profile.idxmax()
    if pd.isna(poc_bin):
        logger.warning(" Warning: POC bin is NaN.")
        return None
    poc_price = (poc_bin.left + poc_bin.right) / 2
    return poc_price

def get_crypto_dominance(data_global, market_cap , crypto_id="bitcoin"):
    """Calculate cryptocurrency market dominance percentage.
    
    Args:
        data_global (dict): Global market data containing total market cap
        market_cap (float): Market cap of the specific cryptocurrency
        crypto_id (str, optional): Cryptocurrency identifier. Defaults to "bitcoin".
        
    Returns:
        float: Dominance percentage (0-100)
    """
    global_market_cap = data_global["data"]["total_market_cap"]["usd"]
    dominance = (market_cap / global_market_cap) * 100
    return dominance

def fibonacci_levels(data):
    """Calculate Fibonacci retracement levels from price range.
    
    Computes 7 Fibonacci levels from the price high to low over the period:
    100%, 76.4%, 61.8%, 50%, 38.2%, 23.6%, and 0%.
    
    Args:
        data (dict): Market data containing 'prices' key
        
    Returns:
        tuple: Seven Fibonacci levels (fib_100, fib_764, fib_618, fib_50, fib_382, fib_236, fib_0)
    """
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