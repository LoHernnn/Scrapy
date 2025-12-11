import time
import schedule
from datetime import datetime
from services.coingecko_service import CoingeckoService
from services.crypto_listing_service import CryptoListingService
from services.binance_service import BinanceService
from services.technical_analysis_service import TechnicalAnalysisService
from database.database import *
import utils.logger as Logger

import conf

def run_data_collection():
    cycle_timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    conf.logger_folder = f"cycle_{cycle_timestamp}"
    
    try:
        logger = Logger.get_logger('ServiceManager')
        logger.info(f"START OF CYCLE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        conn, cur = connect()
        create_table_listing(cur, conn)
        create_table_crypto_ranks(cur, conn)
        create_table_base(cur, conn)
        create_table_detail(cur, conn)
        create_table_data_binance(cur, conn)
        logger.info("Database tables ensured.")

        listing_service = CryptoListingService(refresh_interval_minutes=conf.COLLECTION_INTERVAL_MINUTES)
        logger.info("CryptoListingService initialized.")
        coingeko_instance = CoingeckoService(listing_service,refresh_interval_minutes=conf.COLLECTION_INTERVAL_MINUTES)
        logger.info("CoingeckoService initialized.")
        binance_instance = BinanceService(listing_service,refresh_interval_minutes=conf.COLLECTION_INTERVAL_MINUTES)
        logger.info("BinanceService initialized.")
        technical_analysis_instance = TechnicalAnalysisService(listing_service, coingeko_instance,refresh_interval_minutes=conf.COLLECTION_INTERVAL_MINUTES)
        logger.info("TechnicalAnalysisService initialized.")

        
        listing_service.list_all_cryptos()
        logger.info(f"{len(listing_service.dico_crypto)} cryptos loaded into listing service.")
        coingeko_instance.list_data()
        logger.info("Coingecko data updated.")
        binance_instance.list_data()
        logger.info("Binance data updated.")
        technical_analysis_instance.perform_analysis()
        logger.info("Technical analysis performed.")
        
        success_count = 0
        error_count = 0
        
        for crypto_id, crypto in listing_service.dico_crypto.items():
            try:
                db_id = insert_crypto(cur, conn, crypto.name, crypto.symbol, crypto.id_coingecko, crypto.symbol_binance)
                if db_id is None:
                    logger.error(f"Unable to get DB id for {crypto.id_coingecko}, skipping...")
                    error_count += 1
                    continue
                insert_or_update_rank(cur, conn, db_id, crypto.rank)
                insert_cyptos_base(cur, conn, db_id, listing_service.dico_crypto[crypto_id].data)
                insert_cyptos_data_details(cur, conn, db_id, listing_service.dico_crypto[crypto_id].data)
                insert_cyptos_data_binance(cur, conn, db_id, listing_service.dico_crypto[crypto_id].data)
                success_count += 1
                logger.info(f"Data for {crypto.name} ({crypto.symbol}) inserted/updated successfully.")
                
            except Exception as e:
                error_count += 1
                logger.error(f"Error processing {crypto.name} ({crypto.symbol}): {e}")
                conn.rollback()
                continue
        
        print(f"\n{'='*100}")
        print(f"CYCLE SUMMARY")
        print(f"{'='*100}")
        print(f"Success: {success_count}/{len(listing_service.dico_crypto)}")
        print(f"Errors: {error_count}/{len(listing_service.dico_crypto)}")

        logger.info(f"Cycle completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Success: {success_count}/{len(listing_service.dico_crypto)}")
        logger.info(f"Errors: {error_count}/{len(listing_service.dico_crypto)}")
        
        cur.close()
        conn.close()
        
        print(f"\n{'='*100}")
        print(f"END OF CYCLE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*100}\n")
        
    except Exception as e:
        logger.critical(f"CRITICAL ERROR in cycle: {e}")
        print(f"CRITICAL ERROR in cycle: {e}")
        import traceback
        traceback.print_exc()

def main():
    INTERVAL_MINUTES = conf.COLLECTION_INTERVAL_MINUTES
    
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║               CRYPTO DATA COLLECTOR SERVICE               ║
    ║                                                           ║
    ║  Mode: Continuous crypto data collection                  ║
    ║  Interval: Every {INTERVAL_MINUTES} minutes{' ' * (35 - len(str(INTERVAL_MINUTES)))}║
    ║                                                           ║
    ║  Press Ctrl+C to stop the service                         ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    run_data_collection()
    
    schedule.every(INTERVAL_MINUTES).minutes.do(run_data_collection)
    
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