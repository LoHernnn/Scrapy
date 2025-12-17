from Database.database import SentimentDatabase
import utils.logger as Logger

class SentimentGeneralAnalyser:
    def __init__(self, db_config):
        self.db = SentimentDatabase(db_config)
        self.logger = Logger.get_logger("SentimentGeneralAnalyser")
    
    def analyze_sentiments(self):
        crypto_list = self.db.get_all_crypto_id()
        for crypto_id in crypto_list:
            sentiments_12h = self.db.get_sentiments_for_crypto_12h(crypto_id)
            sentiments_24h = self.db.get_sentiments_for_crypto_24h(crypto_id)
            
            # Skip if no data available
            if not sentiments_12h and not sentiments_24h:
                self.logger.warning(f"No sentiment data for crypto_id {crypto_id}")
                continue
            
            # Calculate 12h average
            if sentiments_12h:
                avg_score_12h = sum(sentiments_12h) / len(sentiments_12h)
                count_12h = len(sentiments_12h)
            else:
                avg_score_12h = 0.0
                count_12h = 0
            
            # Calculate 24h average
            if sentiments_24h:
                avg_score_24h = sum(sentiments_24h) / len(sentiments_24h)
                count_24h = len(sentiments_24h)
            else:
                avg_score_24h = 0.0
                count_24h = 0
            
            # Insert once with both 12h and 24h data
            self.db.insert_sentiment_score(crypto_id, avg_score_12h, count_12h, avg_score_24h, count_24h)
            self.logger.info(f"Analyzed crypto_id {crypto_id}: 12h={avg_score_12h:.3f} ({count_12h} tweets), 24h={avg_score_24h:.3f} ({count_24h} tweets)")