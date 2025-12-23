import DataLayer.database as dl
from utils.enum import MarketRegime


class MarketDetection:
    def __init__(self,db_config):
        self.dl = dl.DatabaseCryptoBot(db_config)

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
        data = self.dl.get_all_crypto_informations(crypto_id)

        prices = [(r["price"]) for r in data][::-1]
        highs = [(r["high_24h"]) for r in data][::-1]
        lows = [(r["low_24h"]) for r in data][::-1]
        volumes = [(r["total_volume"]) for r in data][::-1]

        if len(prices) < 5:
            return MarketRegime.NO_TRADE

        price = prices[-1]
        volume = volumes[-1]
        volume_mean = sum(volumes[:-1]) / max(len(volumes) - 1, 1)

        ema_50 = data["ema_50"]
        ema_200 = data["ema_200"]
        rsi = data["rsi_values"]
        
        # === ATR (volatilité) ===
        atr = self.compute_atr(
            highs,
            lows,
            prices,
            period=min(14, len(prices) - 1)
        )

        atr_pct = atr / price if atr and price > 0 else 0
        volume_ratio = volume / volume_mean if volume_mean > 0 else 1

        funding = data["funding_rate"] if data["funding_rate"] is not None else 0

        if ( atr_pct > 0.05 or volume_ratio > 2.0 or abs(funding) > 0.1):
            return MarketRegime.PANIC

        if (ema_50 > ema_200 and price > ema_200 and rsi > 52 ):
            return MarketRegime.TREND_UP
        
        if ( ema_50 < ema_200 and price < ema_200 and rsi < 48 ):
            return MarketRegime.TREND_DOWN

        if 48 <= rsi <= 52:
            return MarketRegime.RANGE

        return MarketRegime.NO_TRADE