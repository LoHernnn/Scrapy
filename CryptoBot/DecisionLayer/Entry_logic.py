#L’Entry Logic est l’étape où tu transformes ton score multi-facteurs (technique + sentiment) en décision concrète d’entrée.
from enum import Enum, auto
from utils.enum import LongShort
from DataLayer.database import DatabaseCryptoBot


class EntryLogic:
    def __init__(self, db_config, technical_layer, sentiment_layer):
        self.technical_layer = technical_layer
        self.sentiment_layer = sentiment_layer
        self.db_instance = DatabaseCryptoBot(db_config)

    def decide_entry(self, crypto_data):
        # Prendre les données les plus récentes (premier élément de la liste)
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
        combined_score = (technical_score * 0.85) + (sentiment_score * 0.15)
        
        # Seuil encore plus strict pour réduire davantage le nombre de trades
        if combined_score > 0.55:
            self.db_instance.insert_score(data['crypto_id'], technical_score, combined_score, LongShort.EnterLong.value, data['price'])
            return LongShort.EnterLong, combined_score
        elif combined_score < -0.55:
            self.db_instance.insert_score(data['crypto_id'], technical_score, combined_score, LongShort.EnterShort.value, data['price'])
            return LongShort.EnterShort, combined_score
        else:
            self.db_instance.insert_score(data['crypto_id'], technical_score, combined_score, LongShort.NoTrade.value, data['price'])
            return LongShort.NoTrade, combined_score
        

    def position_sizing(self, capital, final_score, MR, stop_distance_pct):
        """
        Position sizing with granular risk allocation based on score confidence.
        
        Args:
            capital: Total capital available
            final_score: Combined score from -1.0 to 1.0
            MR: MarketRegime (EnterLong, EnterShort, NoTrade)
            stop_distance_pct: Stop loss distance in percentage (e.g., 0.02 for 2%)
        
        Returns:
            dict: {"direction": str, "risk_pct": float, "position_size": float, "confidence": str}
        """
        
        # NO TRADE ZONE (-0.55 to 0.55) - Seuil plus strict
        if -0.55 < final_score < 0.55:
            return {
                "direction": LongShort.NoTrade,
                "risk_pct": 0.0,
                "position_size": 0.0,
            }
        
        # ========== LONG POSITIONS (Bullish) ==========
        if final_score >= 0.55 and MR == LongShort.EnterLong:
            
            if 0.55 <= final_score < 0.65:
                direction = LongShort.EnterLong
                risk_pct = 0.0025  # Réduit de 0.003
                #confidence = "WEAK"
            
            elif 0.65 <= final_score < 0.75:
                direction = LongShort.EnterLong
                risk_pct = 0.004  # Réduit de 0.005
                #confidence = "MODERATE"
            
            elif 0.75 <= final_score < 0.85:
                direction = LongShort.EnterLong
                risk_pct = 0.006  # Réduit de 0.0075
                #confidence = "STRONG"
            
            elif 0.85 <= final_score < 0.95:
                direction = LongShort.EnterLong
                risk_pct = 0.008  # Réduit de 0.01
                #confidence = "VERY_STRONG"
            
            else:  # >= 0.95
                direction = LongShort.EnterLong
                risk_pct = 0.012  # Réduit de 0.015
                #confidence = "EXTREME"
        
        # ========== SHORT POSITIONS (Bearish) ==========
        elif final_score <= -0.55 and MR == LongShort.EnterShort:
            
            if -0.65 < final_score <= -0.55:
                direction = LongShort.EnterShort
                risk_pct = 0.0025  # Réduit de 0.003
                #confidence = "WEAK"
            
            elif -0.75 < final_score <= -0.65:
                direction = LongShort.EnterShort
                risk_pct = 0.004  # Réduit de 0.005
                #confidence = "MODERATE"
            
            elif -0.85 < final_score <= -0.75:
                direction = LongShort.EnterShort
                risk_pct = 0.006  # Réduit de 0.0075
                #confidence = "STRONG"
            
            elif -0.95 < final_score <= -0.85:
                direction = LongShort.EnterShort
                risk_pct = 0.008  # Réduit de 0.01
                #confidence = "VERY_STRONG"
            
            else:  # <= -0.95
                direction = LongShort.EnterShort
                risk_pct = 0.012  # Réduit de 0.015
                #confidence = "EXTREME"
        
        else:
            return {
                "direction": "NO-TRADE",
                "risk_pct": 0.0,
                "position_size": 0.0,
            }
        
        # ========== PROTECTIONS ==========
        # 1. Stop distance minimum de 0.5% pour éviter des positions énormes
        MIN_STOP_DISTANCE = 0.005  # 0.5%
        if stop_distance_pct < MIN_STOP_DISTANCE:
            print(f"⚠️ Stop distance trop petit ({stop_distance_pct*100:.3f}%) - ajusté à {MIN_STOP_DISTANCE*100}%")
            stop_distance_pct = MIN_STOP_DISTANCE
        
        # 2. Calcul de la position size
        position_size = (capital * risk_pct) / stop_distance_pct
        
        # 3. Position size maximum = 10% du capital
        max_position_size = capital * 0.10
        if position_size > max_position_size:
            print(f"⚠️ Position size trop élevée ({position_size:.2f}) - plafonnée à {max_position_size:.2f}")
            position_size = max_position_size
        
        return {
            "direction": direction,
            "risk_pct": risk_pct,
            "position_size": position_size,
        }
