from scrapy.data.database import CryptoDatabase as SentimentDatabase
import scrapy.utils.logger as Logger

class SentimentGeneralAnalyser:
    """Aggregate and analyze sentiment scores across all tracked cryptocurrencies.
    
    Computes average sentiment scores over 12-hour and 24-hour windows for each
    cryptocurrency based on collected tweet sentiment data. Stores aggregated
    results for use in trading decision logic.
    """
    
    def __init__(self):
        """Initialize sentiment general analyzer with database connection."""
        self.db = SentimentDatabase()
        self.logger = Logger.get_logger("SentimentGeneralAnalyser")
    
    def analyze_sentiments(self):
        """Analyze and aggregate sentiment scores for all cryptocurrencies.
        
        For each tracked cryptocurrency, retrieves sentiment data from the last
        12 and 24 hours, calculates average scores and tweet counts, then stores
        the aggregated results. Skips cryptocurrencies with no recent sentiment data.
        """
        crypto_list = self.db.get_all_crypto_id()
        for crypto_id in crypto_list:
            sentiments_12h = self.db.get_sentiments_for_crypto_12h(crypto_id)
            sentiments_24h = self.db.get_sentiments_for_crypto_24h(crypto_id)
            
            if not sentiments_12h and not sentiments_24h:
                self.logger.warning(f"No sentiment data for crypto_id {crypto_id}")
                continue
            
            if sentiments_12h:
                avg_score_12h = sum(sentiments_12h) / len(sentiments_12h)
                count_12h = len(sentiments_12h)
            else:
                avg_score_12h = 0.0
                count_12h = 0
            
            if sentiments_24h:
                avg_score_24h = sum(sentiments_24h) / len(sentiments_24h)
                count_24h = len(sentiments_24h)
            else:
                avg_score_24h = 0.0
                count_24h = 0
            
            self.db.insert_sentiment_score(crypto_id, avg_score_12h, count_12h, avg_score_24h, count_24h)
            self.logger.info(f"Analyzed crypto_id {crypto_id}: 12h={avg_score_12h:.3f} ({count_12h} tweets), 24h={avg_score_24h:.3f} ({count_24h} tweets)")