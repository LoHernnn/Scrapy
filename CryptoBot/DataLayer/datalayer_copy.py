from database import DatabaseCryptoBot
from datetime import datetime

def safe_float(value, default=0):
    """Convert value to float, return default if None or conversion fails."""
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def print_crypto_info(crypto_name, crypto_symbol, data):
    """
    Pretty print all cryptocurrency information.
    
    Args:
        crypto_name: Name of the cryptocurrency
        crypto_symbol: Symbol of the cryptocurrency
        data: Dictionary containing base_data, details_data, binance_data, sentiment_data
    """
    print("\n" + "="*80)
    print(f"  {crypto_name} ({crypto_symbol})")
    print("="*80)
    
    # Base Market Data
    if data.get("base_data"):
        print("\n MARKET DATA (Last 10 records)")
        print("-" * 80)
        for i, record in enumerate(data["base_data"], 1):
            print(f"\n  [{i}] Timestamp: {record.get('timestamp', 'N/A')}")
            print(f"       Price: ${safe_float(record.get('price')):,.8f}")
            print(f"       High 24h: ${safe_float(record.get('high_24h')):,.8f}  |   Low 24h: ${safe_float(record.get('low_24h')):,.8f}")
            print(f"       Market Cap: ${safe_float(record.get('market_cap')):,.2f}")
            print(f"       Volume 24h: ${safe_float(record.get('total_volume')):,.2f}")
            print(f"       Dominance: {safe_float(record.get('dominance')):.4f}%")
            var24h = safe_float(record.get('variation24h_pst'))
            emoji = "V" if var24h >= 0 else "X"
            print(f"      {emoji} Variation 24h: {var24h:.2f}%")
            print(f"       ATH: ${safe_float(record.get('all_time_high')):,.8f} ({record.get('all_time_high_timestamp', 'N/A')})")
    else:
        print("\n MARKET DATA: No data available")
    
    # Technical Details
    if data.get("details_data"):
        print("\n\n TECHNICAL INDICATORS (Last 10 records)")
        print("-" * 80)
        for i, record in enumerate(data["details_data"], 1):
            print(f"\n  [{i}] Timestamp: {record.get('timestamp', 'N/A')}")
            print(f"       Current Price: ${safe_float(record.get('current_price')):,.8f}")
            
            # RSI
            rsi = record.get('rsi_values')
            if rsi is not None:
                rsi_val = safe_float(rsi)
                rsi_status = " Overbought" if rsi_val > 70 else " Oversold" if rsi_val < 30 else " Neutral"
                print(f"       RSI: {rsi_val:.2f} {rsi_status}")
            
            # Moving Averages
            print(f"       SMA 50: ${safe_float(record.get('sma_50')):,.8f}  |  SMA 200: ${safe_float(record.get('sma_200')):,.8f}")
            print(f"       EMA 50: ${safe_float(record.get('ema_50')):,.8f}  |  EMA 200: ${safe_float(record.get('ema_200')):,.8f}")
            
            # MACD
            macd_h = safe_float(record.get('macd_h'))
            signal_h = safe_float(record.get('signal_line_h'))
            histogram_h = safe_float(record.get('histogram_h'))
            print(f"       MACD (Hourly): {macd_h:.6f}  |  Signal: {signal_h:.6f}  |  Histogram: {histogram_h:.6f}")
            
            # Pivot Points
            print(f"        Pivot Point: ${safe_float(record.get('pp')):,.8f}")
            print(f"       R1: ${safe_float(record.get('r1')):,.8f}  |  R2: ${safe_float(record.get('r2')):,.8f}")
            print(f"       S1: ${safe_float(record.get('s1')):,.8f}  |  S2: ${safe_float(record.get('s2')):,.8f}")
            
            # Supply
            circ_supply = safe_float(record.get('circulating_supply'))
            if circ_supply > 0:
                print(f"       Circulating Supply: {circ_supply:,.0f}")
                max_supply = safe_float(record.get('max_supply'))
                if max_supply > 0:
                    print(f"       Max Supply: {max_supply:,.0f}")
    else:
        print("\n\n TECHNICAL INDICATORS: No data available")
    
    # Binance Data
    if data.get("binance_data"):
        print("\n\n BINANCE DATA (Last 10 records)")
        print("-" * 80)
        for i, record in enumerate(data["binance_data"], 1):
            print(f"\n  [{i}] Timestamp: {record.get('timestamp', 'N/A')}")
            
            # Funding Rate
            funding = safe_float(record.get('funding_rate'))
            funding_emoji = "V" if funding > 0 else "X" if funding < 0 else "="
            print(f"      {funding_emoji} Funding Rate: {funding:.4f}%")
            print(f"       Open Interest: ${safe_float(record.get('open_interest')):,.2f}")
            
            # Order Book - Bids
            print(f"       Top Bids:")
            for j in range(1, 4):
                price_key = f'bids_price_{j}'
                qty_key = f'bids_quantity_{j}'
                price_val = safe_float(record.get(price_key))
                if price_val > 0:
                    print(f"         {j}. ${price_val:,.8f} × {safe_float(record.get(qty_key)):,.4f}")
            
            # Order Book - Asks
            print(f"       Top Asks:")
            for j in range(1, 4):
                price_key = f'asks_price_{j}'
                qty_key = f'asks_quantity_{j}'
                price_val = safe_float(record.get(price_key))
                if price_val > 0:
                    print(f"         {j}. ${price_val:,.8f} × {safe_float(record.get(qty_key)):,.4f}")
    else:
        print("\n\n BINANCE DATA: No data available")
    
    # Sentiment Data
    if data.get("sentiment_data"):
        print("\n\n SENTIMENT ANALYSIS")
        print("-" * 80)
        for i, record in enumerate(data["sentiment_data"], 1):
            print(f"\n  [{i}] Timestamp: {record.get('timestamp', 'N/A')}")
            
            # 24h sentiment
            score_24h = safe_float(record.get('score_24h'))
            count_24h = safe_float(record.get('count_24h'), 0)
            sentiment_emoji_24h = "V" if score_24h > 0.1 else "X" if score_24h < -0.1 else "="
            sentiment_label_24h = "Positive" if score_24h > 0.1 else "Negative" if score_24h < -0.1 else "Neutral"
            print(f"      {sentiment_emoji_24h} 24h Score: {score_24h:.4f} ({sentiment_label_24h}) - {int(count_24h)} tweets")
            
            # 12h sentiment
            score_12h = safe_float(record.get('score_12h'))
            count_12h = safe_float(record.get('count_12h'), 0)
            sentiment_emoji_12h = "V" if score_12h > 0.1 else "X" if score_12h < -0.1 else "="
            sentiment_label_12h = "Positive" if score_12h > 0.1 else "Negative" if score_12h < -0.1 else "Neutral"
            print(f"      {sentiment_emoji_12h} 12h Score: {score_12h:.4f} ({sentiment_label_12h}) - {int(count_12h)} tweets")
    else:
        print("\n\n SENTIMENT ANALYSIS: No data available")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    db_config = {
    "host": "localhost",
    "port": 5432,
    "database": "crypto",
    "user": "crypto",
    "password": "crypto",
}
    
    db = DatabaseCryptoBot(db_config)
    if db.connect():
        cryptos = db.get_all_cryptos()
        print(f"\n Found {len(cryptos)} cryptocurrencies in database\n")
        
        for crypto in cryptos:
            data = db.get_all_crypto_informations(crypto['id'])
            
            print_crypto_info(crypto['name'], crypto['symbol'], data)
            
        db.disconnect()
        print(" Database connection closed")
    else:
        print(" Failed to connect to database")