import DataLayer.database as dl


class TechnicalSignalScoring:
    def __init__(self, db_config=None):
        self.dl = dl.DatabaseCryptoBot(db_config)

    def _to_float(self, value):
        """Convertit une valeur en float, gérant les Decimal et None."""
        if value is None:
            return 0.0
        return float(value)
            
    def RSITiming(self, rsi_values):
        rsi_values = self._to_float(rsi_values)
        # Zones extrêmes strictes pour réduire le nombre de trades
        if rsi_values <= 35:
            return 1.0  # Très survendu - signal long fort
        elif rsi_values >= 65:
            return -1.0  # Très surachat - signal short fort
        elif rsi_values <= 42:
            return 0.5  # Survendu modéré
        elif rsi_values >= 58:
            return -0.5  # Surachat modéré
        else:
            return 0.0  # Zone neutre - pas de signal
        
    def MACDTiming(self, macd_value_j, signal_value_j, macd_value_h, signal_value_h, histogram_value, hist_norm ):
        macd_value_j = self._to_float(macd_value_j)
        signal_value_j = self._to_float(signal_value_j)
        macd_value_h = self._to_float(macd_value_h)
        signal_value_h = self._to_float(signal_value_h)
        histogram_value = self._to_float(histogram_value)
        hist_norm = self._to_float(hist_norm)
        
        macd_j_score = +1 if macd_value_j > signal_value_j else -1
        macd_h_score = +0.5 if macd_value_h > signal_value_h else -0.5
        if histogram_value > 0 and hist_norm != 0:
            hist_score = min(histogram_value / hist_norm, 1)
        elif hist_norm != 0:
            hist_score = max(histogram_value / hist_norm, -1)
        else:
            hist_score = 0
        return macd_j_score + macd_h_score + hist_score
    
    def ema50200Timing(self, ema_50, ema_200, price):
        ema_50 = self._to_float(ema_50)
        ema_200 = self._to_float(ema_200)
        price = self._to_float(price)
        
        ema_score = 0.0
        if ema_50 > ema_200 and price > ema_50:
            ema_score += 1.0
        elif ema_50 < ema_200 and price < ema_50:
            ema_score += -1.0
        elif ema_50 > ema_200:
            ema_score += 0.5
        elif ema_50 < ema_200:
            ema_score += -0.5
        return ema_score
    
    def PivotSupportResistanceTiming(self, price, r1, s1 , pivot_points):
        price = self._to_float(price)
        r1 = self._to_float(r1)
        s1 = self._to_float(s1)
        pivot_points = self._to_float(pivot_points)
        
        pivot_score = 0.0
        if price > r1:
            pivot_score -= 0.5
        elif price < s1:
            pivot_score += 0.5
        elif price > pivot_points:
            pivot_score += 0.25
        else:
            pivot_score -= 0.25
        return pivot_score
    
    def fibonacciTiming(self, price, fibo_382, fibo_618  ):
        price = self._to_float(price)
        fibo_382 = self._to_float(fibo_382)
        fibo_618 = self._to_float(fibo_618)
        
        fibo_score = 0.0
        if price < fibo_382:
            fibo_score = +0.5
        elif price > fibo_618:
            fibo_score = -0.5
        else:
            fibo_score = 0
        return fibo_score
    
    def sma50200Timing(self, sma_50, sma_200, price):
        sma_50 = self._to_float(sma_50)
        sma_200 = self._to_float(sma_200)
        price = self._to_float(price)
        
        sma_score = 0.0
        if price > sma_50 > sma_200:
            sma_score = +1
        elif price < sma_50 < sma_200:
            sma_score = -1
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
        
        # Méthode 1: Score basé sur les variations de prix pondérées
        volatility_score = (0.5 * d1_pct) + (0.3 * d7_pct) + (0.2 * d14_pct)
        
        # Méthode 2: Smart volatility - pondère la variation par le ratio de volume
        volume_ratio = vol_actuel / vol_moyen_7j if vol_moyen_7j > 0 else 1.0
        smart_volatility = d1_pct * volume_ratio
        
        # Combinaison des deux méthodes (60% volatility_score, 40% smart_volatility)
        combined_volatility = (0.6 * volatility_score) + (0.4 * smart_volatility)
        
        # Normalisation et conversion en score [-1, +1]
        # Seuils: <2% = faible, 2-5% = moyen, >5% = élevé
        if combined_volatility < 2.0:
            # Faible volatilité: pénalise le trading (score négatif)
            score = (combined_volatility / 2.0) - 1.0  # Range: -1 à 0
        elif combined_volatility < 5.0:
            # Volatilité moyenne: neutre à légèrement positif
            score = (combined_volatility - 2.0) / 3.0  # Range: 0 à 1
        else:
            # Haute volatilité: très favorable au trading
            score = min(1.0, 0.5 + (combined_volatility - 5.0) / 10.0)  # Range: 0.5 à 1
        
        return max(min(score, 1.0), -1.0)
    
    def compute_technical_score(self, price, rsi_values,macd_value_j, signal_value_j, macd_value_h, signal_value_h, histogram_value, hist_norm, ema_50, ema_200,
                                sma_50, sma_200, r1, s1, pivot_points, fibo_382, fibo_618, d1_percentage=0, d7_percentage=0, d14_percentage=0, volume_actuel=0, volume_moyen_7j=1):
        """
        Calcule le score technique final pondéré entre -1 et +1.
        Intègre la volatilité comme facteur de pondération pour filtrer les trades en marchés peu volatils.
        """
        rsi_score = self.RSITiming(rsi_values)
        macd_score = self.MACDTiming(macd_value_j, signal_value_j, macd_value_h, signal_value_h,histogram_value, hist_norm)
        ema_score = self.ema50200Timing(ema_50, ema_200, price)
        sma_score = self.sma50200Timing(sma_50, sma_200, price)
        pivot_score = self.PivotSupportResistanceTiming(price, r1, s1, pivot_points)
        fibo_score = self.fibonacciTiming(price, fibo_382, fibo_618)
        volatility_score = self.volatilityTiming(d1_percentage, d7_percentage, d14_percentage, volume_actuel, volume_moyen_7j)

        # Poids ajustés pour inclure la volatilité (total = 1.0)
        weights = {
            'ema': 0.22,
            'macd': 0.22,
            'rsi': 0.13,
            'sma': 0.09,
            'volatility': 0.20,
            'pivot': 0.07,
            'fibo': 0.07
        }

        weighted_score = (
            ema_score * weights['ema'] +
            macd_score * weights['macd'] + 
            rsi_score * weights['rsi'] + 
            sma_score * weights['sma'] + 
            volatility_score * weights['volatility'] +
            pivot_score * weights['pivot'] +
            fibo_score * weights['fibo']
        )
        #print(f"Final Technical Score Computation: EMA({ema_score}*{weights['ema']}) + MACD({macd_score}*{weights['macd']}) + RSI({rsi_score}*{weights['rsi']}) + SMA({sma_score}*{weights['sma']}) + Volatility({volatility_score}*{weights['volatility']}) + Pivot({pivot_score}*{weights['pivot']}) + Fibo({fibo_score}*{weights['fibo']}) = {weighted_score}")
        final_score = max(min(weighted_score, 1), -1)

        return final_score