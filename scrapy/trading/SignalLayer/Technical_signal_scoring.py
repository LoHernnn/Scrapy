from scrapy.data.database import CryptoDatabase as DatabaseCryptoBot
import scrapy.utils.logger as Logger
import scrapy.config.settings as conf


class TechnicalSignalScoring:
    def __init__(self):
        self.dl = DatabaseCryptoBot()
        self.logger = Logger.get_logger("TechnicalSignalScoring")
        self.weights = conf.TECHNICAL_WEIGHTS
        self.rsi_oversold_extreme = conf.RSI_OVERSOLD_EXTREME
        self.rsi_overbought_extreme = conf.RSI_OVERBOUGHT_EXTREME
        self.rsi_oversold_moderate = conf.RSI_OVERSOLD_MODERATE
        self.rsi_overbought_moderate = conf.RSI_OVERBOUGHT_MODERATE
        self.volatility_low_threshold = conf.VOLATILITY_LOW_THRESHOLD
        self.volatility_high_threshold = conf.VOLATILITY_HIGH_THRESHOLD

    def _to_float(self, value):
        """Convert a value to float, handling Decimal and None types.
        
        Args:
            value: Value to convert (can be Decimal, float, int, or None)
            
        Returns:
            float: Converted value, or 0.0 if None
        """
        if value is None:
            return 0.0
        return float(value)
            
    def RSITiming(self, rsi_values):
        """Calculate RSI score between -1 and +1 using strict extreme zones.
        
        Args:
            rsi_values: Current RSI value
            
        Returns:
            float: Score between -1 (overbought) and +1 (oversold)
        """
        rsi_values = self._to_float(rsi_values)
        # Strict extreme zones to reduce number of trades
        if rsi_values <= self.rsi_oversold_extreme:
            return 1.0  # Extremely oversold - strong long signal
        elif rsi_values >= self.rsi_overbought_extreme:
            return -1.0  # Extremely overbought - strong short signal
        elif rsi_values <= self.rsi_oversold_moderate:
            return 0.5  # Moderately oversold
        elif rsi_values >= self.rsi_overbought_moderate:
            return -0.5  # Moderately overbought
        else:
            return 0.0  # Neutral zone - no signal
        
    def MACDTiming(self, macd_value_j, signal_value_j, macd_value_h, signal_value_h, histogram_value, hist_norm ):
        """Calculate MACD timing score combining daily and hourly timeframes.
        
        Args:
            macd_value_j (float): MACD value on daily timeframe
            signal_value_j (float): Signal line value on daily timeframe
            macd_value_h (float): MACD value on hourly timeframe
            signal_value_h (float): Signal line value on hourly timeframe
            histogram_value (float): Current MACD histogram value
            hist_norm (float): Normalization factor for histogram
            
        Returns:
            float: Combined MACD score (range: approximately -2.5 to +2.5)
        """
        macd_value_j = self._to_float(macd_value_j)
        signal_value_j = self._to_float(signal_value_j)
        macd_value_h = self._to_float(macd_value_h)
        signal_value_h = self._to_float(signal_value_h)
        histogram_value = self._to_float(histogram_value)
        hist_norm = self._to_float(hist_norm)
        
        # Daily timeframe score: +1 bullish, -1 bearish
        macd_j_score = +1 if macd_value_j > signal_value_j else -1
        # Hourly timeframe score: +0.5 bullish, -0.5 bearish
        macd_h_score = +0.5 if macd_value_h > signal_value_h else -0.5
        # Histogram score: normalized momentum strength
        if histogram_value > 0 and hist_norm != 0:
            hist_score = min(histogram_value / hist_norm, 1)
        elif hist_norm != 0:
            hist_score = max(histogram_value / hist_norm, -1)
        else:
            hist_score = 0
        return macd_j_score + macd_h_score + hist_score
    
    def ema50200Timing(self, ema_50, ema_200, price):
        """Calculate EMA trend score based on 50/200 crossover and price position.
        
        Args:
            ema_50 (float): 50-period Exponential Moving Average
            ema_200 (float): 200-period Exponential Moving Average
            price (float): Current price
            
        Returns:
            float: Score between -1 (bearish) and +1 (bullish)
        """
        ema_50 = self._to_float(ema_50)
        ema_200 = self._to_float(ema_200)
        price = self._to_float(price)
        
        ema_score = 0.0
        # Strong bullish: uptrend with price above EMA50
        if ema_50 > ema_200 and price > ema_50:
            ema_score += 1.0
        # Strong bearish: downtrend with price below EMA50
        elif ema_50 < ema_200 and price < ema_50:
            ema_score += -1.0
        # Moderate bullish: uptrend but price below EMA50
        elif ema_50 > ema_200:
            ema_score += 0.5
        # Moderate bearish: downtrend but price above EMA50
        elif ema_50 < ema_200:
            ema_score += -0.5
        return ema_score
    
    def PivotSupportResistanceTiming(self, price, r1, s1 , pivot_points):
        """Calculate pivot point score based on price position relative to support/resistance.
        
        Args:
            price (float): Current price
            r1 (float): First resistance level
            s1 (float): First support level
            pivot_points (float): Central pivot point
            
        Returns:
            float: Score between -0.5 (at resistance) and +0.5 (at support)
        """
        price = self._to_float(price)
        r1 = self._to_float(r1)
        s1 = self._to_float(s1)
        pivot_points = self._to_float(pivot_points)
        
        pivot_score = 0.0
        # Price above resistance: potential reversal (bearish)
        if price > r1:
            pivot_score -= 0.5
        # Price below support: potential bounce (bullish)
        elif price < s1:
            pivot_score += 0.5
        # Price above pivot: mild bullish
        elif price > pivot_points:
            pivot_score += 0.25
        # Price below pivot: mild bearish
        else:
            pivot_score -= 0.25
        return pivot_score
    
    def fibonacciTiming(self, price, fibo_382, fibo_618  ):
        """Calculate Fibonacci retracement score based on key levels.
        
        Args:
            price (float): Current price
            fibo_382 (float): 38.2% Fibonacci retracement level
            fibo_618 (float): 61.8% Fibonacci retracement level
            
        Returns:
            float: Score between -0.5 and +0.5 based on Fibonacci zones
        """
        price = self._to_float(price)
        fibo_382 = self._to_float(fibo_382)
        fibo_618 = self._to_float(fibo_618)
        
        fibo_score = 0.0
        # Price below 38.2%: deep retracement, potential buy zone
        if price < fibo_382:
            fibo_score = +0.5
        # Price above 61.8%: extended move, potential sell zone
        elif price > fibo_618:
            fibo_score = -0.5
        # Price in golden zone (38.2% - 61.8%): neutral
        else:
            fibo_score = 0
        return fibo_score
    
    def sma50200Timing(self, sma_50, sma_200, price):
        """Calculate SMA trend score based on 50/200 crossover (Golden/Death Cross).
        
        Args:
            sma_50 (float): 50-period Simple Moving Average
            sma_200 (float): 200-period Simple Moving Average
            price (float): Current price
            
        Returns:
            float: Score of -1 (bearish), 0 (neutral), or +1 (bullish)
        """
        sma_50 = self._to_float(sma_50)
        sma_200 = self._to_float(sma_200)
        price = self._to_float(price)
        
        sma_score = 0.0
        # Golden cross with price confirmation: strong bullish
        if price > sma_50 > sma_200:
            sma_score = +1
        # Death cross with price confirmation: strong bearish
        elif price < sma_50 < sma_200:
            sma_score = -1
        # Mixed signals: neutral
        else:
            sma_score = 0
        return sma_score
    
    def volatilityTiming(self, d1_percentage, d7_percentage, d14_percentage, volume_actuel, volume_moyen_7j):
        """
        Calcule un score de volatilité combiné entre -1 et +1.
        Haute volatilité favorise les trades (score positif), basse volatilité les pénalise (score négatif).
        
        Args:
            d1_percentage: Variation de prix sur 1 jour
            d7_percentage: Variation de prix sur 7 jours
            d14_percentage: Variation de prix sur 14 jours
            volume_actuel: Volume de trading actuel
            volume_moyen_7j: Volume moyen sur 7 jours
            
        Returns:
            Score entre -1 (volatilité très faible) et +1 (volatilité très élevée)
        """
        d1_pct = abs(self._to_float(d1_percentage))
        d7_pct = abs(self._to_float(d7_percentage))
        d14_pct = abs(self._to_float(d14_percentage))
        vol_actuel = self._to_float(volume_actuel)
        vol_moyen_7j = self._to_float(volume_moyen_7j)
        
        # Method 1: Score based on weighted price variations
        volatility_score = (0.5 * d1_pct) + (0.3 * d7_pct) + (0.2 * d14_pct)
        
        # Method 2: Smart volatility - weight variation by volume ratio
        volume_ratio = vol_actuel / vol_moyen_7j if vol_moyen_7j > 0 else 1.0
        smart_volatility = d1_pct * volume_ratio
        
        # Combine both methods (60% volatility_score, 40% smart_volatility)
        combined_volatility = (0.6 * volatility_score) + (0.4 * smart_volatility)
        
        if combined_volatility < self.volatility_low_threshold:
            score = (combined_volatility / self.volatility_low_threshold) - 1.0
        elif combined_volatility < self.volatility_high_threshold:
            score = (combined_volatility - self.volatility_low_threshold) / (self.volatility_high_threshold - self.volatility_low_threshold)
        else:
            score = min(1.0, 0.5 + (combined_volatility - self.volatility_high_threshold) / 10.0)
        
        return max(min(score, 1.0), -1.0)
    
    def compute_technical_score(self, price, rsi_values,macd_value_j, signal_value_j, macd_value_h, signal_value_h, histogram_value, hist_norm, ema_50, ema_200,
                                sma_50, sma_200, r1, s1, pivot_points, fibo_382, fibo_618, d1_percentage=0, d7_percentage=0, d14_percentage=0, volume_actuel=0, volume_moyen_7j=1):
        """Compute comprehensive technical analysis score combining multiple indicators.
        
        This method aggregates scores from various technical indicators using configurable
        weights to produce a final score between -1 (strong bearish) and +1 (strong bullish).
        
        Args:
            price (float): Current asset price
            rsi_values (float): RSI indicator value
            macd_value_j (float): MACD value on daily timeframe
            signal_value_j (float): MACD signal line on daily timeframe
            macd_value_h (float): MACD value on hourly timeframe
            signal_value_h (float): MACD signal line on hourly timeframe
            histogram_value (float): MACD histogram value
            hist_norm (float): Histogram normalization factor
            ema_50 (float): 50-period Exponential Moving Average
            ema_200 (float): 200-period Exponential Moving Average
            sma_50 (float): 50-period Simple Moving Average
            sma_200 (float): 200-period Simple Moving Average
            r1 (float): First resistance pivot level
            s1 (float): First support pivot level
            pivot_points (float): Central pivot point
            fibo_382 (float): 38.2% Fibonacci retracement level
            fibo_618 (float): 61.8% Fibonacci retracement level
            d1_percentage (float, optional): 1-day price change percentage. Defaults to 0.
            d7_percentage (float, optional): 7-day price change percentage. Defaults to 0.
            d14_percentage (float, optional): 14-day price change percentage. Defaults to 0.
            volume_actuel (float, optional): Current trading volume. Defaults to 0.
            volume_moyen_7j (float, optional): 7-day average trading volume. Defaults to 1.
            
        Returns:
            float: Combined technical score between -1 and +1
        """
        # Calculate individual indicator scores
        rsi_score = self.RSITiming(rsi_values)
        macd_score = self.MACDTiming(macd_value_j, signal_value_j, macd_value_h, signal_value_h,histogram_value, hist_norm)
        ema_score = self.ema50200Timing(ema_50, ema_200, price)
        sma_score = self.sma50200Timing(sma_50, sma_200, price)
        pivot_score = self.PivotSupportResistanceTiming(price, r1, s1, pivot_points)
        fibo_score = self.fibonacciTiming(price, fibo_382, fibo_618)
        volatility_score = self.volatilityTiming(d1_percentage, d7_percentage, d14_percentage, volume_actuel, volume_moyen_7j)

        # Weights configurable from settings.py
        weighted_score = (
            ema_score * self.weights['ema'] +
            macd_score * self.weights['macd'] + 
            rsi_score * self.weights['rsi'] + 
            sma_score * self.weights['sma'] + 
            volatility_score * self.weights['volatility'] +
            pivot_score * self.weights['pivot'] +
            fibo_score * self.weights['fibo']
        )
        # Clamp final score to [-1, +1] range
        final_score = max(min(weighted_score, 1), -1)
        
        self.logger.debug(f"Technical scoring: RSI={rsi_score:.2f}, MACD={macd_score:.2f}, EMA={ema_score:.2f}, Volatility={volatility_score:.2f} -> Final={final_score:.3f}")
        
        return final_score