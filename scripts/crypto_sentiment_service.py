"""Crypto Sentiment Analysis Service.

Scheduled service that continuously scrapes Twitter/social media, performs ABSA sentiment analysis
on cryptocurrency mentions, and aggregates sentiment scores at configured intervals.
"""

import schedule
from datetime import datetime
import time

from scrapy.sentiment.service import SentimentCoordinator
from scrapy.data.database import CryptoDatabase as SentimentDatabase
from scrapy.sentiment.analysis.sentimentGeneralAnalyser import SentimentGeneralAnalyser
import scrapy.config.settings as conf

def Sentiment():
    """Execute a complete sentiment analysis cycle.
    
    This function orchestrates the entire sentiment analysis pipeline:
    1. Creates/ensures sentiment database tables exist
    2. Scrapes tweets from configured Twitter accounts via SentimentCoordinator
    3. Performs ABSA (Aspect-Based Sentiment Analysis) on crypto mentions
    4. Cleans up old tweets beyond retention period
    5. Aggregates sentiment scores for 12h and 24h windows per cryptocurrency
    
    Each cycle creates a new log folder with timestamp for debugging and tracking.
    """
    cycle_timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    conf.logger_folder = f"cycle_{cycle_timestamp}"
    db = SentimentDatabase()
    db.create_sentiment_tables()
    coordinator = SentimentCoordinator( conf.SCRAPER_CONFIG)
    coordinator.service_run()
    coordinator.close()
    db.update_database()
    sga =SentimentGeneralAnalyser()
    sga.analyze_sentiments()



def main():
    """Main entry point for the crypto sentiment analysis service.
    
    Runs an initial sentiment analysis cycle immediately, then schedules subsequent
    cycles at intervals defined by SENTIMENT_COLLECTION_INTERVAL_MINUTES.
    
    The service runs continuously until interrupted with Ctrl+C. Each cycle:
    - Scrapes tweets from configured accounts
    - Analyzes sentiment using DeBERTa-based ABSA model
    - Aggregates and stores sentiment scores in database
    - Cleans up old tweet data
    
    Displays a banner with service information and handles graceful shutdown.
    """
    INTERVAL_MINUTES = conf.SENTIMENT_COLLECTION_INTERVAL_MINUTES
    
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║               CRYPTO SENTIMENT SERVICE                    ║
    ║                                                           ║
    ║  Mode: Continuous crypto sentiment analysis               ║
    ║  Interval: Every {INTERVAL_MINUTES} minutes{' ' * (35 - len(str(INTERVAL_MINUTES)))}║
    ║                                                           ║
    ║  Press Ctrl+C to stop the service                         ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    Sentiment()
    
    schedule.every(INTERVAL_MINUTES).minutes.do(Sentiment)
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n╔═══════════════════════════════════════════════════════════╗")
        print("║                 SERVICE STOP REQUESTED                    ║")
        print("╚═══════════════════════════════════════════════════════════╝\n")
        print("Service stopped cleanly. Goodbye!")

if __name__ == "__main__":
    main()

