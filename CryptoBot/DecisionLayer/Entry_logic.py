#L’Entry Logic est l’étape où tu transformes ton score multi-facteurs (technique + sentiment) en décision concrète d’entrée.
from enum import Enum, auto

class MarketRegime(Enum):
    EnterLong = auto()
    EnterShort = auto()
    NoTrade = auto()


class EntryLogic:
    def __init__(self, technical_layer, sentiment_layer, risk_filter):
        self.technical_layer = technical_layer
        self.sentiment_layer = sentiment_layer
        #self.risk_filter = risk_filter

    def decide_entry(self, crypto_data):
        technical_score = self.technical_layer.compute_technical_score(crypto_data)
        sentiment_score = self.sentiment_layer.confirm_sentiment(crypto_data)
        combined_score = (technical_score * 0.85) + (sentiment_score * 0.15)
        
        #if not self.risk_filter.passes_filters(crypto_data):
        #    return "No Trade", combined_score
        
        if combined_score > 0.4:
            return MarketRegime.EnterLong, combined_score
        elif combined_score < -0.4:
            return MarketRegime.EnterShort, combined_score
        else:
            return MarketRegime.NoTrade, combined_score
        

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
        
        # NO TRADE ZONE (-0.4 to 0.4)
        if -0.4 < final_score < 0.4:
            return {
                "direction": MarketRegime.NoTrade,
                "risk_pct": 0.0,
                "position_size": 0.0,
            }
        
        # ========== LONG POSITIONS (Bullish) ==========
        if final_score >= 0.4 and MR == MarketRegime.EnterLong:
            
            if 0.40 <= final_score < 0.50:
                direction = MarketRegime.EnterLong
                risk_pct = 0.003  
                #confidence = "VERY_WEAK"
            
            elif 0.50 <= final_score < 0.60:
                direction = MarketRegime.EnterLong
                risk_pct = 0.005 
                #confidence = "WEAK"
            
            elif 0.60 <= final_score < 0.70:
                direction = MarketRegime.EnterLong
                risk_pct = 0.0075 
                #confidence = "MODERATE"
            
            elif 0.70 <= final_score < 0.80:
                direction = MarketRegime.EnterLong
                risk_pct = 0.01  
                #confidence = "STRONG"
            
            elif 0.80 <= final_score < 0.90:
                direction = MarketRegime.EnterLong
                risk_pct = 0.015 
                #confidence = "VERY_STRONG"
            
            else:
                direction = MarketRegime.EnterLong
                risk_pct = 0.02 
                #confidence = "EXTREME"
        
        # ========== SHORT POSITIONS (Bearish) ==========
        elif final_score <= -0.4 and MR == MarketRegime.EnterShort:
            
            if -0.50 < final_score <= -0.40:
                direction = MarketRegime.EnterShort
                risk_pct = 0.003  
                #confidence = "VERY_WEAK"
            
            elif -0.60 < final_score <= -0.50:
                direction = MarketRegime.EnterShort
                risk_pct = 0.005 
                #confidence = "WEAK"
            
            elif -0.70 < final_score <= -0.60:
                direction = MarketRegime.EnterShort
                risk_pct = 0.0075 
                #confidence = "MODERATE"
            
            elif -0.80 < final_score <= -0.70:
                direction = MarketRegime.EnterShort
                risk_pct = 0.01  
                #confidence = "STRONG"
            
            elif -0.90 < final_score <= -0.80:
                direction = MarketRegime.EnterShort
                risk_pct = 0.015 
                #confidence = "VERY_STRONG"
            
            else:
                direction = MarketRegime.EnterShort
                risk_pct = 0.02  
                #confidence = "EXTREME"
        
        else:
            return {
                "direction": "NO-TRADE",
                "risk_pct": 0.0,
                "position_size": 0.0,
            }
        
        position_size = (capital * risk_pct) / stop_distance_pct
        
        return {
            "direction": direction,
            "risk_pct": risk_pct,
            "position_size": position_size,
        }
