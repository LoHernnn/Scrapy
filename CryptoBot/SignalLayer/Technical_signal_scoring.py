import DataLayer.datalayer as dl


class MarketDetection:
    def __init__(self):
        self.dl = dl.datalayer({
            'host': 'localhost',
            'port': '5432',
            'database': 'cryptobot_db',
            'user': 'cryptobot_user',
            'password': 'secure_password'
        })
    
    def RSITiming(self, rsi_values):
        if rsi_values <= 30:
            return 1.0
        elif rsi_values >= 70:
            return -1.0
        elif rsi_values < 45 :
            return 0.5
        elif rsi_values > 55 :
            return -0.5
        else:
            return 0.0
        
    def MACDTiming(self, macd_value_j, signal_value_j, macd_value_h, signal_value_h, histogram_value, hist_norm ):
        macd_j_score = +1 if macd_value_j > signal_value_j else -1
        macd_h_score = +0.5 if macd_value_h > signal_value_h else -0.5
        if histogram_value > 0:
            hist_score = min(histogram_value / hist_norm, 1)
        else:
            hist_score = max(histogram_value / hist_norm, -1)
        return macd_j_score + macd_h_score + hist_score
    
    def ema50200Timing(self, ema_50, ema_200, price):
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
        fibo_score = 0.0
        if price < fibo_382:
            fibo_score = +0.5
        elif price > fibo_618:
            fibo_score = -0.5
        else:
            fibo_score = 0
        return fibo_score
    
    def sma50200Timing(self, sma_50, sma_200, price):
        sma_score = 0.0
        if price > sma_50 > sma_200:
            sma_score = +1
        elif price < sma_50 < sma_200:
            sma_score = -1
        else:
            sma_score = 0
        return sma_score
    
    def compute_technical_score(self, price, rsi_values,macd_value_j, signal_value_j, macd_value_h, signal_value_h, histogram_value, hist_norm, ema_50, ema_200,
                                sma_50, sma_200, r1, s1, pivot_points, fibo_382, fibo_618):
        """
        Calcule le score technique final pondéré entre -1 et +1.
        """
        rsi_score = self.RSITiming(rsi_values)
        macd_score = self.MACDTiming(macd_value_j, signal_value_j, macd_value_h, signal_value_h,histogram_value, hist_norm)
        ema_score = self.ema50200Timing(ema_50, ema_200, price)
        sma_score = self.sma50200Timing(sma_50, sma_200, price)
        pivot_score = self.PivotSupportResistanceTiming(price, r1, s1, pivot_points)
        fibo_score = self.fibonacciTiming(price, fibo_382, fibo_618)

        weights = {'ema': 0.25,'macd': 0.25,'rsi': 0.15,'hist': 0.15,'sma': 0.10,'pivot': 0.05,'fibo': 0.05}

        weighted_score = (ema_score * weights['ema'] +macd_score * weights['macd'] + rsi_score * weights['rsi'] + sma_score * weights['sma'] + pivot_score * weights['pivot'] +
            fibo_score * weights['fibo'])

        final_score = max(min(weighted_score, 1), -1)

        return final_score