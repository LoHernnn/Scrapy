from ServiceManager.coordinateur import SentimentCoordinator
from Database.database import SentimentDatabase
from SentimentAnalysis.sentimentGeneralAnalyser import SentimentGeneralAnalyser
import schedule
from datetime import datetime
import conf
import time

def Sentiment():
    cycle_timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    conf.logger_folder = f"cycle_{cycle_timestamp}"
    db = SentimentDatabase(conf.DB_CONFIG)

    db.drop_sentiment_tables()

    db.create_sentiment_tables()
    
    accounts = ["BitcoinMagazine", "binance","Bitcoin","cz_binance","coinacademy_ia","coinacademy_fr","aixbt_agent","TheBlock__","lookonchain","coinbase","tier10k","CoinbaseIntExch","CoinbaseAssets","sama","Blockworks_","realDonaldTrump","VitalikButerin","AltcoinsFrance","santimentfeed","HindenburgRes","CoinDesk","PiQSuite","financialjuice","bubblemaps","KaikoData","0xResearch","0xngmi","DegenerateNews","bravosresearch","Airdrops_one","cryptoquant_com","TreeNewsFeed","TheBittensorHub"]
    for account_name in accounts:
        db.insert_new_account(account_name)

    coordinator = SentimentCoordinator(conf.DB_CONFIG, conf.SCRAPER_CONFIG)
    coordinator.service_run()
    db.update_database()
    sga =SentimentGeneralAnalyser(conf.DB_CONFIG)
    sga.analyze_sentiments()



def main():
    INTERVAL_MINUTES = conf.COLLECTION_INTERVAL_MINUTES
    
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

