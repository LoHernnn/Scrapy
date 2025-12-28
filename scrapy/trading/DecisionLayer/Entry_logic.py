from scrapy.core.enums import LongShort
from scrapy.data.database import CryptoDatabase as DatabaseCryptoBot
import scrapy.utils.logger as Logger
import scrapy.config.settings as conf


class EntryLogic:
    """Determine trade entry decisions by combining technical and sentiment analysis.
    
    Aggregates technical indicator scores and sentiment signals using configurable weights
    to generate final entry decisions (long, short, or no trade). Implements position
    sizing based on signal confidence and risk management rules.
    """
    
    def __init__(self, technical_layer, sentiment_layer):
        """Initialize entry logic with technical and sentiment analysis layers.
        
        Args:
            technical_layer: Technical signal scoring instance
            sentiment_layer: Sentiment confirmation instance
        """
        self.technical_layer = technical_layer
        self.sentiment_layer = sentiment_layer
        self.db_instance = DatabaseCryptoBot()
        self.logger = Logger.get_logger("EntryLogic")
        self.technical_weight = conf.TECHNICAL_WEIGHT
        self.sentiment_weight = conf.SENTIMENT_WEIGHT
        self.threshold_long = conf.ENTRY_SCORE_THRESHOLD_LONG
        self.threshold_short = conf.ENTRY_SCORE_THRESHOLD_SHORT
        self.risk_high_confidence = conf.RISK_HIGH_CONFIDENCE
        self.risk_medium_confidence = conf.RISK_MEDIUM_CONFIDENCE
        self.risk_low_confidence = conf.RISK_LOW_CONFIDENCE

    def decide_entry(self, crypto_data):
        """Evaluate market conditions and decide whether to enter a trade.
        
        Combines technical analysis scores with sentiment confirmation to generate
        a weighted final score. Compares against threshold levels to determine
        long, short, or no-trade decisions.
        
        Args:
            crypto_data: Dictionary or list containing crypto market data and indicators
            
        Returns:
            tuple: (decision, combined_score) where:
                - decision (LongShort): EnterLong, EnterShort, or NoTrade
                - combined_score (float): Final weighted score
        """
        data = crypto_data[0] if isinstance(crypto_data, list) and len(crypto_data) > 0 else crypto_data
        
        technical_score = self.technical_layer.compute_technical_score(
            price=data['price'],
            rsi_values=data['rsi'],
            macd_value_j=data['macd_j'],
            signal_value_j=data['signal_j'],
            macd_value_h=data['macd_h'],
            signal_value_h=data['signal_h'],
            histogram_value=data['histogram'],
            hist_norm=data['hist_norm'],
            ema_50=data['ema_50'],
            ema_200=data['ema_200'],
            sma_50=data['sma_50'],
            sma_200=data['sma_200'],
            r1=data['r1'],
            s1=data['s1'],
            pivot_points=data['pivot'],
            fibo_382=data['fibo_382'],
            fibo_618=data['fibo_618'],
            d1_percentage=data.get('d1_percentage', 0),
            d7_percentage=data.get('d7_percentage', 0),
            d14_percentage=data.get('d14_percentage', 0),
            volume_actuel=data.get('volume_actuel', 0),
            volume_moyen_7j=data.get('volume_moyen_7j', 1)
        )
        sentiment_score = self.sentiment_layer.confirm_sentiment(
            score_24h=data.get('sentiment_score_24h', 0),
            score_12h=data.get('sentiment_score_12h', 0),
            nb_tweets_24h=data.get('sentiment_count_24h', 0)
        )
        combined_score = (technical_score * self.technical_weight) + (sentiment_score * self.sentiment_weight)
        
        self.logger.info(f"Crypto {data['crypto_id']}: Technical={technical_score:.3f}, Sentiment={sentiment_score:.3f}, Combined={combined_score:.3f}")
        
        if combined_score > self.threshold_long:
            self.db_instance.insert_score(data['crypto_id'], technical_score, combined_score, LongShort.EnterLong.value, data['price'])
            self.logger.info(f"Decision: ENTER LONG for crypto {data['crypto_id']} with score {combined_score:.3f}")
            return LongShort.EnterLong, combined_score
        elif combined_score < self.threshold_short:
            self.db_instance.insert_score(data['crypto_id'], technical_score, combined_score, LongShort.EnterShort.value, data['price'])
            self.logger.info(f"Decision: ENTER SHORT for crypto {data['crypto_id']} with score {combined_score:.3f}")
            return LongShort.EnterShort, combined_score
        else:
            self.db_instance.insert_score(data['crypto_id'], technical_score, combined_score, LongShort.NoTrade.value, data['price'])
            self.logger.debug(f"Decision: NO TRADE for crypto {data['crypto_id']} (score {combined_score:.3f} not strong enough)")
            return LongShort.NoTrade, combined_score
        

    def position_sizing(self, capital, final_score, MR, stop_distance_pct):
        """Calculate position size based on signal strength and risk management.
        
        Implements granular risk allocation with tiered confidence levels. Position
        size scales with signal strength while respecting maximum risk limits.
        
        Args:
            capital (float): Total capital available for trading
            final_score (float): Combined score from -1.0 to 1.0
            MR (LongShort): Market regime (EnterLong, EnterShort, NoTrade)
            stop_distance_pct (float): Stop loss distance in percentage (e.g., 0.02 for 2%)
        
        Returns:
            dict: Position details containing:
                - direction (LongShort): Trade direction or NoTrade
                - risk_pct (float): Risk percentage of capital
                - position_size (float): Calculated position size in base currency
        """
        
        if self.threshold_short < final_score < self.threshold_long:
            return {
                "direction": LongShort.NoTrade,
                "risk_pct": 0.0,
                "position_size": 0.0,
            }
        
        if final_score >= 0.55 and MR == LongShort.EnterLong:
            
            if 0.55 <= final_score < 0.70:
                direction = LongShort.EnterLong
                risk_pct = self.risk_low_confidence
            
            elif 0.70 <= final_score < 0.85:
                direction = LongShort.EnterLong
                risk_pct = self.risk_medium_confidence
            
            else:
                direction = LongShort.EnterLong
                risk_pct = self.risk_high_confidence
        
        elif final_score <= -0.55 and MR == LongShort.EnterShort:
            
            if -0.70 < final_score <= -0.55:
                direction = LongShort.EnterShort
                risk_pct = self.risk_low_confidence
            
            elif -0.85 < final_score <= -0.70:
                direction = LongShort.EnterShort
                risk_pct = self.risk_medium_confidence
            
            else:
                direction = LongShort.EnterShort
                risk_pct = self.risk_high_confidence
        
        else:
            return {
                "direction": "NO-TRADE",
                "risk_pct": 0.0,
                "position_size": 0.0,
            }
        
        MIN_STOP_DISTANCE = 0.005
        if stop_distance_pct < MIN_STOP_DISTANCE:
            stop_distance_pct = MIN_STOP_DISTANCE
        
        position_size = (capital * risk_pct) / stop_distance_pct
        
        max_position_size = capital * 0.10
        if position_size > max_position_size:
            position_size = max_position_size
        
        return {
            "direction": direction,
            "risk_pct": risk_pct,
            "position_size": position_size,
        }
