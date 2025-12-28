from scrapy.data.database import CryptoDatabase as DatabaseCryptoBot
import scrapy.utils.logger as Logger
import scrapy.config.settings as conf

class SentimentConfirmation:
    """Analyzes and confirms trading signals based on social media sentiment.
    
    This class evaluates sentiment scores from tweets and social media data,
    applying weighting based on tweet volume and trend analysis to generate
    confirmation signals for trading decisions.
    """
    
    def __init__(self, min_tweets: int = None, positive_threshold: float = None, negative_threshold: float = None, trend_bonus: float = None):
        """Initialize sentiment confirmation analyzer with configurable thresholds.
        
        Args:
            min_tweets (int, optional): Minimum tweets required for full weight. Defaults to 10.
            positive_threshold (float, optional): Score threshold for positive signal. Defaults to 0.2.
            negative_threshold (float, optional): Score threshold for negative signal. Defaults to -0.1.
            trend_bonus (float, optional): Bonus/penalty for sentiment trend. Defaults to 0.1.
        """
        self.dl = DatabaseCryptoBot()
        self.min_tweets = min_tweets if min_tweets is not None else 10
        self.positive_threshold = positive_threshold if positive_threshold is not None else 0.2
        self.negative_threshold = negative_threshold if negative_threshold is not None else -0.1
        self.trend_bonus = trend_bonus if trend_bonus is not None else 0.1
        self.logger = Logger.get_logger("SentimentConfirmation")

    def weighted_sentiment(self, score, count):
        """Adjust sentiment score based on tweet volume.
        
        Applies a weighting factor that scales with tweet count. Scores are
        proportionally reduced if tweet count is below minimum threshold.
        
        Args:
            score (float): Raw sentiment score
            count (int): Number of tweets analyzed
            
        Returns:
            float: Weighted sentiment score (range depends on input score)
        """
        factor = min(1.0, count / self.min_tweets)
        return score * factor
    
    def sentiment_trend_bonus(self, score_12h, score_24h):
        """Calculate bonus/penalty based on sentiment trend direction.
        
        Compares recent (12h) vs longer-term (24h) sentiment to detect
        improving or deteriorating sentiment trends.
        
        Args:
            score_12h (float): Sentiment score over last 12 hours
            score_24h (float): Sentiment score over last 24 hours
            
        Returns:
            float: Trend bonus (+trend_bonus if improving, -trend_bonus if deteriorating, 0 if stable)
        """
        delta = score_24h - score_12h
        if delta > 0:
            return self.trend_bonus
        elif delta < 0:
            return -self.trend_bonus
        return 0.0
    
    def confirm_sentiment(self, score_24h: float, score_12h: float, nb_tweets_24h: int):
        """Generate final sentiment confirmation signal for trading decisions.
        
        Combines weighted 24h sentiment score with trend analysis to produce
        a directional signal. Adjusts for tweet volume reliability and rewards
        positive sentiment trends.
        
        Args:
            score_24h (float): Sentiment score over last 24 hours
            score_12h (float): Sentiment score over last 12 hours
            nb_tweets_24h (int): Number of tweets analyzed in 24h period
            
        Returns:
            int: Confirmation signal (1=positive, -1=negative, 0=neutral)
        """
        score_24h = score_24h if score_24h is not None else 0.0
        score_12h = score_12h if score_12h is not None else 0.0
        nb_tweets_24h = nb_tweets_24h if nb_tweets_24h is not None else 0
        
        score_24h_weighted = self.weighted_sentiment(score_24h, nb_tweets_24h)
        trend_bonus = self.sentiment_trend_bonus(score_12h, score_24h)
        final_score = score_24h_weighted + trend_bonus
        
        self.logger.debug(f"Sentiment: 24h={score_24h:.3f}, 12h={score_12h:.3f}, tweets={nb_tweets_24h}, weighted={score_24h_weighted:.3f}, bonus={trend_bonus:.2f}, final={final_score:.3f}")
        
        if final_score > self.positive_threshold:
            self.logger.info(f"Sentiment confirmation: POSITIVE (score={final_score:.3f})")
            return 1
        elif final_score < self.negative_threshold:
            self.logger.info(f"Sentiment confirmation: NEGATIVE (score={final_score:.3f})")
            return -1
        else:
            self.logger.debug(f"Sentiment confirmation: NEUTRAL (score={final_score:.3f})")
            return 0
