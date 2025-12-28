from scrapy.data.database import CryptoDatabase as DatabaseCryptoBot
from scrapy.core.enums import MarketRegime
import scrapy.utils.logger as Logger
import scrapy.config.settings as conf


class MarketDetection:
    """Detect and classify market regimes for cryptocurrency trading.
    
    Analyzes market conditions using technical indicators (ATR, RSI, EMA) and
    volume/funding metrics to classify markets into regimes: TREND_UP, TREND_DOWN,
    RANGE, PANIC, or NO_TRADE. Each regime requires different trading strategies.
    """
    
    def __init__(self):
        """Initialize market detection with configurable thresholds from settings.
        
        Loads configuration parameters for regime detection including:
        - Panic detection thresholds (ATR, volume, funding rate)
        - Trend detection criteria (RSI boundaries)
        - Range detection boundaries
        """
        self.dl = DatabaseCryptoBot()
        self.logger = Logger.get_logger("MarketDetection")
        self.panic_atr_threshold = conf.PANIC_ATR_THRESHOLD
        self.panic_volume_ratio = conf.PANIC_VOLUME_RATIO
        self.panic_funding_rate = conf.PANIC_FUNDING_RATE
        self.trend_rsi_upper = conf.TREND_RSI_UPPER
        self.trend_rsi_lower = conf.TREND_RSI_LOWER
        self.range_rsi_lower = conf.RANGE_RSI_LOWER
        self.range_rsi_upper = conf.RANGE_RSI_UPPER
        self.atr_period = conf.ATR_PERIOD

    def true_range(self, high, low, prev_close):
        """Calculate True Range for a single period.
        
        True Range is the greatest of:
        - Current high minus current low
        - Absolute value of current high minus previous close
        - Absolute value of current low minus previous close
        
        Args:
            high (float): Current period's high price
            low (float): Current period's low price
            prev_close (float): Previous period's closing price
            
        Returns:
            float: True Range value
        """
        return max(
            high - low,
            abs(high - prev_close),
            abs(low - prev_close)
        )
    
    def compute_atr(self,highs, lows, closes, period=14):
        """Calculate Average True Range (ATR) indicator.
        
        ATR measures market volatility by averaging True Range values over
        a specified period. Higher ATR indicates higher volatility.
        
        Args:
            highs (list): List of high prices
            lows (list): List of low prices
            closes (list): List of closing prices
            period (int, optional): Number of periods for averaging. Defaults to 14.
            
        Returns:
            float: Average True Range value, or None if insufficient data
        """
        trs = []
        for i in range(1, len(closes)):
            tr = self.true_range(highs[i], lows[i], closes[i-1])
            trs.append(tr)

        if len(trs) < period:
            return None

        return sum(trs[-period:]) / period
    
    def detect_market_regime(self, crypto_id: int):
        """Detect current market regime for a cryptocurrency.
        
        Analyzes multiple market indicators to classify the current regime:
        
        Regimes:
        - PANIC: Extreme volatility, unusual volume, or extreme funding rates
        - TREND_UP: Bullish trend (EMA50>EMA200, price>EMA200, RSI>threshold)
        - TREND_DOWN: Bearish trend (EMA50<EMA200, price<EMA200, RSI<threshold)
        - RANGE: Sideways market (RSI within neutral range)
        - NO_TRADE: Conditions not met for any regime
        
        Args:
            crypto_id (int): Cryptocurrency ID to analyze
            
        Returns:
            MarketRegime: Detected market regime enum value
        """
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

        atr = self.compute_atr(
            highs,
            lows,
            prices,
            period=min(self.atr_period, len(prices) - 1)
        )

        atr_pct = atr / price if atr and price > 0 else 0
        volume_ratio = volume / volume_mean if volume_mean > 0 else 1

        funding = data["funding_rate"] if data["funding_rate"] is not None else 0

        if ( atr_pct > self.panic_atr_threshold or volume_ratio > self.panic_volume_ratio or abs(funding) > self.panic_funding_rate):
            self.logger.warning(f"Crypto {crypto_id}: PANIC detected (ATR={atr_pct:.4f}, Vol ratio={volume_ratio:.2f}, Funding={funding:.4f})")
            return MarketRegime.PANIC

        if (ema_50 > ema_200 and price > ema_200 and rsi > self.trend_rsi_upper ):
            self.logger.info(f"Crypto {crypto_id}: TREND_UP detected (RSI={rsi:.1f})")
            return MarketRegime.TREND_UP
        
        if ( ema_50 < ema_200 and price < ema_200 and rsi < self.trend_rsi_lower ):
            self.logger.info(f"Crypto {crypto_id}: TREND_DOWN detected (RSI={rsi:.1f})")
            return MarketRegime.TREND_DOWN

        if self.range_rsi_lower <= rsi <= self.range_rsi_upper:
            self.logger.debug(f"Crypto {crypto_id}: RANGE detected (RSI={rsi:.1f})")
            return MarketRegime.RANGE

        self.logger.debug(f"Crypto {crypto_id}: NO_TRADE - conditions not met")
        return MarketRegime.NO_TRADE