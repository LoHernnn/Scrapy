from scrapy.sentiment.scrapers.nitterScraper import NitterScraper
from scrapy.data.database import CryptoDatabase as SentimentDatabase
from scrapy.sentiment.analysis.sentimentAnalyzer import SentimentAnalyzer
import scrapy.config.settings as conf
import scrapy.utils.logger as Logger


class SentimentCoordinator:
    """Coordinate sentiment analysis by scraping tweets and analyzing crypto mentions.
    
    Manages the workflow of scraping social media accounts, extracting tweets,
    analyzing sentiment for cryptocurrency mentions, and storing results in database.
    Handles deduplication and multi-crypto detection in single tweets.
    """
    
    def __init__(self, scraper_config):
        """Initialize sentiment coordinator with scraper configuration.
        
        Args:
            scraper_config (dict): Configuration dictionary for NitterScraper initialization
        """
        self.scraper_config = scraper_config
        self.db = SentimentDatabase()
        self.scraper = None
        self.analyzer = SentimentAnalyzer()
        self.all_crypto_list = self.db.get_crypto_list()
        self.logger = Logger.get_logger("SentimentCoordinator")
    
    def process_account(self, accounts):
        """Process tweets from multiple social media accounts.
        
        For each account, scrapes recent tweets, analyzes sentiment for crypto mentions,
        and stores results. Handles deduplication by tweet hash and aggregates scores
        when multiple crypto identifiers (symbol/name) point to the same cryptocurrency.
        
        Args:
            accounts (list): List of social media account handles to process
        """
        for account in accounts:
            try:
                success = self.scraper.scrape_account(account)
                if success:
                    tweets = self.scraper.parse_account(account)
                    for tweet in tweets:
                        if self.db.check_tweet_exists(tweet['hash_content']):
                            self.logger.info(f"Tweet already processed, skipping: {tweet['content'][:30]}...")
                            continue  
                        sentiment_results = self.analyzer.analyze_tweet(tweet['content'], self.all_crypto_list)
                        if sentiment_results:
                            tweet_id = self.db.insert_tweet_hash(tweet['hash_content'])
                            if tweet_id is None:
                                self.logger.error(f"Failed to insert tweet hash, skipping tweet")
                                continue
                                
                            self.db.insert_tweet_sentiment(tweet_id, account, tweet['content'], tweet['timestamp'])
                            
                            # Deduplicate by crypto_id (symbol and name can point to same crypto)
                            crypto_scores = {}
                            for crypto_name, sentiment_score in sentiment_results.items():
                                crypto_id = self.db.get_crypto_id_by_symbol_or_name(crypto_name)
                                if crypto_id is not None:
                                    # Keep most recent score or average them
                                    if crypto_id not in crypto_scores:
                                        crypto_scores[crypto_id] = []
                                    crypto_scores[crypto_id].append(sentiment_score)
                            
                            # Insert once per crypto with averaged scores
                            for crypto_id, scores in crypto_scores.items():
                                avg_score = sum(scores) / len(scores)
                                self.db.link_tweet_to_crypto(tweet_id, crypto_id, round(avg_score, 3))
                else:
                    self.logger.warning(f"Failed to scrape {account}")
            except Exception as e:
                self.logger.error(f"Error processing account {account}: {e}")
    
    def get_account_list(self):
        """Retrieve list of all social media accounts to monitor.
        
        Returns:
            list: List of account handles from database
        """
        all_accounts = self.db.get_all_accounts()
        return all_accounts

    def service_run(self):
        """Execute the complete sentiment analysis workflow.
        
        Retrieves account list, initializes scraper, processes all accounts,
        and ensures proper cleanup. Main entry point for sentiment service.
        """
        accounts = self.get_account_list()
        with NitterScraper(**self.scraper_config) as scraper:
            self.scraper = scraper
            self.process_account(accounts)
            self.scraper.close()
            self.scraper = None
    
    def close(self):
        """Clean up resources by closing the scraper if active."""
        if self.scraper:
            self.scraper.close()

