import DataLayer.datalayer as dl
from enum import Enum, auto

class MarketRegime(Enum):
    TREND_UP = auto()
    TREND_DOWN = auto()
    RANGE = auto()
    PANIC = auto()
    NO_TRADE = auto()



class MarketDetection:
    def __init__(self):
        self.dl = dl.datalayer({
            'host': 'localhost',
            'port': '5432',
            'database': 'cryptobot_db',
            'user': 'cryptobot_user',
            'password': 'secure_password'
        })

    def true_range(self, high, low, prev_close):
        return max(
            high - low,
            abs(high - prev_close),
            abs(low - prev_close)
        )
    
    def compute_atr(self,highs, lows, closes, period=14):
        trs = []
        for i in range(1, len(closes)):
            tr = self.true_range(highs[i], lows[i], closes[i-1])
            trs.append(tr)

        if len(trs) < period:
            return None

        return sum(trs[-period:]) / period
    
    def detect_market_regime(self, crypto_id: int):
        data = self.dl.get_crypto_data(crypto_id)

        # === BASE DATA (volatilité + volume) ===
        base = data["base_data"]

        prices = [dl.safe_float(r["price"]) for r in base][::-1]
        highs = [dl.safe_float(r["high_24h"]) for r in base][::-1]
        lows = [dl.safe_float(r["low_24h"]) for r in base][::-1]
        volumes = [dl.safe_float(r["total_volume"]) for r in base][::-1]

        if len(prices) < 5:
            return MarketRegime.NO_TRADE

        price = prices[-1]
        volume = volumes[-1]
        volume_mean = sum(volumes[:-1]) / max(len(volumes) - 1, 1)

        # === TECHNICAL DATA ===
        details = data["details_data"][0] if data["details_data"] else {}

        ema_50 = dl.safe_float(details.get("ema_50"))
        ema_200 = dl.safe_float(details.get("ema_200"))
        rsi = dl.safe_float(details.get("rsi_values"))

        # === ATR (volatilité) ===
        atr = self.compute_atr(
            highs,
            lows,
            prices,
            period=min(14, len(prices) - 1)
        )

        atr_pct = atr / price if atr and price > 0 else 0
        volume_ratio = volume / volume_mean if volume_mean > 0 else 1

        binance = data.get("binance_data", [])
        funding = dl.safe_float(binance[0].get("funding_rate")) if binance else 0

        if ( atr_pct > 0.05 or volume_ratio > 2.0 or abs(funding) > 0.1):
            return MarketRegime.PANIC

        if (ema_50 > ema_200 and price > ema_200 and rsi > 55 ):
            return MarketRegime.TREND_UP
        
        if ( ema_50 < ema_200 and price < ema_200 and rsi < 45 ):
            return MarketRegime.TREND_DOWN

        if 45 <= rsi <= 55:
            return MarketRegime.RANGE

        return MarketRegime.NO_TRADE