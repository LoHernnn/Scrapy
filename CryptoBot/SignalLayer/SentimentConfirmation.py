import DataLayer.datalayer as dl 

class SentimentConfirmation:
    def __init__(self):
        self.dl = dl.datalayer({
            'host': 'localhost',
            'port': '5432',
            'database': 'cryptobot_db',
            'user': 'cryptobot_user',
            'password': 'secure_password'
        })

    def weighted_sentiment(self, score, count):
        """
        Ajuste le score selon le nombre de tweets
        """
        factor = min(1.0, count / self.min_tweets)  # max 1.0
        return score * factor
    
    def sentiment_trend_bonus(self, score_12h, score_24h):
        """
        Calcule un bonus si le sentiment est en croissance.
        """
        delta = score_24h - score_12h
        if delta > 0:
            return 0.1
        elif delta < 0:
            return -0.1
    
    def confirm_sentiment(self, score_24h: float, score_12h: float, nb_tweets_24h: int):
        score_24h_weighted = self.weighted_sentiment(score_24h, nb_tweets_24h)
        trend_bonus = self.sentiment_trend_bonus(score_12h, score_24h)
        final_score = score_24h_weighted + trend_bonus
        if final_score > 0.2:
            return 1 # Positive confirmation
        elif final_score < -0.1:
            return -1 # Negative confirmation
        else:
            return 0 # Neutral confirmation
