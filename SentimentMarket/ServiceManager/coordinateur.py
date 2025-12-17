from Scraper.nitterScraper import NitterScraper
from Database.database import SentimentDatabase
from SentimentAnalysis.sentimentAnalyzer import SentimentAnalyzer
import utils.logger as Logger


class SentimentCoordinator:
    def __init__(self, db_config, scraper_config):
        self.db = SentimentDatabase(db_config)
        self.scraper = NitterScraper(**scraper_config)
        self.analyzer = SentimentAnalyzer()
        self.all_crypto_list = self.db.get_crypto_list()
        self.logger = Logger.get_logger("SentimentCoordinator")
    
    def process_account(self, accounts):
        for account in accounts:
            try:
                success = self.scraper.scrape_account(account)
                if success:
                    tweets = self.scraper.parse_account(account)
                    for tweet in tweets:
                        if self.db.check_tweet_exists(tweet['hash_content']):
                            continue  
                        else:
                            sentiment_results = self.analyzer.analyze_tweet(tweet['content'], self.all_crypto_list)
                            if sentiment_results:
                                tweet_id = self.db.insert_tweet_hash(tweet['hash_content'])
                                self.db.insert_tweet_sentiment(tweet_id, account, tweet['content'], tweet['timestamp'])
                                for crypto in sentiment_results.keys():
                                    crypto_id = self.db.get_crypto_id_by_symbol_or_name(crypto)
                                    if crypto_id is not None:
                                        sentiment_score = sentiment_results[crypto]
                                        self.db.link_tweet_to_crypto(tweet_id, crypto_id, sentiment_score)
                else:
                    self.logger.warning(f"Failed to scrape {account}")
            except Exception as e:
                self.logger.error(f"Error processing account {account}: {e}")
    
    def get_account_list(self):
        all_accounts = self.db.get_all_accounts()
        return all_accounts

    def service_run(self):
        accounts = self.get_account_list()
        with self.scraper:
            self.process_account(accounts)

