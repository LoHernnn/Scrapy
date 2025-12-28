from datetime import datetime, timedelta
import psycopg2
from typing import List, Dict, Any, Optional
import scrapy.utils.logger as Logger
import scrapy.config.settings as conf

class CryptoDatabase:
    """PostgreSQL database interface for cryptocurrency trading system.
    
    Manages all database operations including crypto listings, market data, sentiment analysis,
    technical indicators, trading data, and portfolio performance tracking.
    """
    
    def __init__(self):
        """Initialize database connection and logger."""
        self.logger = Logger.get_logger("CryptoDatabase")
        self.conn, self.cur = self.connect()

    def connect(self):
        """Establish PostgreSQL database connection.
        
        Returns:
            tuple: (connection, cursor) objects for database operations
        """
        conn = psycopg2.connect(
            host=conf.DB_CONFIG['host'],
            port=conf.DB_CONFIG['port'],
            database=conf.DB_CONFIG['database'],
            user=conf.DB_CONFIG['user'],
            password=conf.DB_CONFIG['password']
        )
        cur = conn.cursor()
        return conn, cur

    def close(self):
        """Close database connection and logger handlers."""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
        
        self.logger.info("Database connection and logger closed.")
        self.logger.close()
        
        
    def _rows_to_dicts(self, rows) -> List[Dict[str, Any]]:
        """Convert cursor rows to list of dicts using cursor.description for keys."""
        if rows is None:
            return []
        colnames = [desc[0] for desc in self.cur.description]
        return [dict(zip(colnames, row)) for row in rows]
    
    def _safe_float(self, value, default=0.0):
        """
        Safely convert a value to float. Returns default if conversion fails.
        """
        try:
            return float(value) if value is not None else default
        except (ValueError, TypeError):
            return default
        
#------------------------------------------------------------------------------------
# ------------------------------ Create All Tables ----------------------------------
#------------------------------------------------------------------------------------

    def create_table_listing(self):
        """Create cryptos table for storing cryptocurrency listings.
        
        Stores cryptocurrency identifiers including name, symbol, CoinGecko ID,
        and Binance trading symbol.
        """
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS cryptos (
                id SERIAL PRIMARY KEY, 
                name TEXT NOT NULL,
                symbol TEXT NOT NULL,
                id_coingecko TEXT UNIQUE NOT NULL,
                symbol_binance TEXT DEFAULT 'UNKNOWN'
            );
        """)
        self.conn.commit()

    def create_table_crypto_ranks(self):
        """Create crypto_ranks table for storing market cap rankings.
        
        Maintains the current market cap rank for each tracked cryptocurrency.
        """
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS crypto_ranks (
            id SERIAL PRIMARY KEY,
            crypto_id INTEGER NOT NULL UNIQUE REFERENCES cryptos(id) ON DELETE CASCADE,
            rank INTEGER NOT NULL
        );
        """)
        self.conn.commit()


    def create_table_base(self):
        """Create cyptos_data_base table for core market metrics.
        
        Stores fundamental market data including price, 24h high/low, market cap,
        volume, all-time high data, and dominance metrics.
        """
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS cyptos_data_base (
            crypto_id INTEGER NOT NULL REFERENCES cryptos(id) ON DELETE CASCADE,
            price DECIMAL(24,8),
            high_24h DECIMAL(24,8),
            low_24h DECIMAL(24,8),
            dominance DECIMAL(24,4),
            variation24h_pst DECIMAL(10,4),
            variation24h DECIMAL(24,8),
            mc_variation24h_pst DECIMAL(10,4),
            mc_variation24h DECIMAL(24,8),
            market_cap DECIMAL(24,2),
            total_volume DECIMAL(24,2),
            fully_diluted_valuation DECIMAL(24,2),
            all_time_high DECIMAL(24,8),
            all_time_high_timestamp TIMESTAMP,
            all_time_high_pst DECIMAL(24,4),
            timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            
            PRIMARY KEY (crypto_id, timestamp)
        );
        """)
        self.conn.commit()

    def create_table_detail(self):
        """Create cyptos_data_details table for technical analysis data.
        
        Stores comprehensive technical indicators including volume metrics, price variations,
        supply data, pivot points, RSI, MACD, moving averages, POC, and Fibonacci levels.
        """
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS cyptos_data_details (
            crypto_id INTEGER NOT NULL REFERENCES cryptos(id) ON DELETE CASCADE,
            volume_actuel DECIMAL(24,8),
            volume_1j DECIMAL(24,8),
            volume_7j DECIMAL(24,8),
            volume_30j DECIMAL(24,8),
            variation_1j DECIMAL(24,8),
            variation_7j DECIMAL(24,8),
            variation_30j DECIMAL(24,8),
            volume_moyen_30j DECIMAL(24,8),
            variation_moyenne_30j DECIMAL(24,8),
            volume_moyen_7j DECIMAL(24,8),
            variation_moyenne_7j DECIMAL(24,8),
            volume_moyen_1j DECIMAL(24,8),
            variation_moyenne_1j DECIMAL(24,8),
            current_price DECIMAL(24,8),
            d1_percentage DECIMAL(24,8),
            d1_value DECIMAL(24,8),
            d1_vs_avg DECIMAL(24,8),
            d1_mean DECIMAL(24,8),
            d7_percentage DECIMAL(24,8),
            d7_value DECIMAL(24,8),
            d7_vs_avg DECIMAL(24,8),
            d7_mean DECIMAL(24,8),
            d14_percentage DECIMAL(24,8),
            d14_value DECIMAL(24,8),
            d14_vs_avg DECIMAL(24,8),
            d14_mean DECIMAL(24,8),
            d30_percentage DECIMAL(24,8),
            d30_value DECIMAL(24,8),
            d30_vs_avg DECIMAL(24,8),
            d30_mean DECIMAL(24,8),
            circulating_supply DECIMAL(24,8),
            total_supply DECIMAL(24,8),
            max_supply DECIMAL(24,8),
            pp DECIMAL(24,8),
            r1 DECIMAL(24,8),
            r2 DECIMAL(24,8),
            s1 DECIMAL(24,8),
            s2 DECIMAL(24,8),
            rsi_values DECIMAL(24,8),
            macd_h DECIMAL(24,8),
            signal_line_h DECIMAL(24,8),
            histogram_h DECIMAL(24,8),
            macd_j DECIMAL(24,8),
            signal_line_j DECIMAL(24,8),
            histogram_j DECIMAL(24,8),
            sma_50 DECIMAL(24,8),
            sma_200 DECIMAL(24,8),
            ema_50 DECIMAL(24,8),
            ema_200 DECIMAL(24,8),
            poc DECIMAL(24,8),
            fib_levels_1 DECIMAL(24,8),
            fib_levels_2 DECIMAL(24,8),
            fib_levels_3 DECIMAL(24,8),
            fib_levels_4 DECIMAL(24,8),
            fib_levels_5 DECIMAL(24,8),
            fib_levels_6 DECIMAL(24,8),
            fib_levels_7 DECIMAL(24,8),
            timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (crypto_id, timestamp)
        );
        """)
        self.conn.commit()

    def create_table_data_binance(self):
        """Create cyptos_data_binance table for Binance-specific trading data.
        
        Stores order book depth (top 3 bid/ask levels), funding rates, and open interest
        for futures contracts.
        """
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS cyptos_data_binance (
            crypto_id INTEGER NOT NULL REFERENCES cryptos(id) ON DELETE CASCADE,
            bids_price_1 DECIMAL(24,8),
            bids_quantity_1 DECIMAL(24,8),
            bids_price_2 DECIMAL(24,8),
            bids_quantity_2 DECIMAL(24,8),
            bids_price_3 DECIMAL(24,8),
            bids_quantity_3 DECIMAL(24,8),
            asks_price_1 DECIMAL(24,8),
            asks_quantity_1 DECIMAL(24,8),
            asks_price_2 DECIMAL(24,8),
            asks_quantity_2 DECIMAL(24,8),
            asks_price_3 DECIMAL(24,8),
            asks_quantity_3 DECIMAL(24,8),
            funding_rate DECIMAL(24,4),
            open_interest DECIMAL(24,2),
            timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

            PRIMARY KEY (crypto_id, timestamp)
        );

        """)
        self.conn.commit()
        
    def create_sentiment_tables(self):
        """Create all sentiment analysis related tables.
        
        Creates tables for storing sentiment scores, tweet hashes, tweet content,
        crypto-tweet associations, and Twitter account tracking.
        """
        self.cur.execute("""
                CREATE TABLE IF NOT EXISTS crypto_sentiment_scores (
                    crypto_id INTEGER NOT NULL,
                    score_12h FLOAT,
                    count_12h INTEGER,
                    score_24h FLOAT,
                    count_24h INTEGER,
                    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
                    PRIMARY KEY (crypto_id, timestamp),
                    FOREIGN KEY (crypto_id) REFERENCES cryptos(id) ON DELETE CASCADE
                );
            """)
            
        self.cur.execute("""
                CREATE TABLE IF NOT EXISTS tweet_hash (
                    tweet_id SERIAL PRIMARY KEY,
                    hash TEXT NOT NULL UNIQUE
                );
            """)

        self.cur.execute("""
                CREATE TABLE IF NOT EXISTS tweet_sentiments (
                    tweet_id INTEGER PRIMARY KEY,
                    account TEXT,
                    tweet_content TEXT,
                    timestamp BIGINT,
                    FOREIGN KEY (tweet_id) REFERENCES tweet_hash(tweet_id) ON DELETE CASCADE
                );
            """)

        self.cur.execute("""
                CREATE TABLE IF NOT EXISTS tweet_crypto (
                    tweet_id INTEGER,
                    crypto_id INTEGER,
                    sentiment_score FLOAT,
                    PRIMARY KEY (tweet_id, crypto_id),
                    FOREIGN KEY (tweet_id) REFERENCES tweet_hash(tweet_id) ON DELETE CASCADE,
                    FOREIGN KEY (crypto_id) REFERENCES cryptos(id) ON DELETE CASCADE
                );
            """)

        self.cur.execute("""
                CREATE TABLE IF NOT EXISTS account (
                    account_id SERIAL PRIMARY KEY,
                    account_name TEXT UNIQUE NOT NULL
                );
            """)
        self.conn.commit()
    
    
    def create_score_table(self):
        """Create crypto_scores table for trading signal scores.
        
        Stores calculated scoring metrics including technical scores, total scores,
        trend indicators, and price unit data.
        """
        try:
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS crypto_scores (
                    crypto_id INTEGER NOT NULL REFERENCES cryptos(id) ON DELETE CASCADE,
                    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    score_metric FLOAT,
                    score_total FLOAT,
                    Trend FLOAT,
                    priceUnit FLOAT,
                    PRIMARY KEY (crypto_id, timestamp)
                )
            """)
            self.conn.commit()
        except Exception as e:
            self.logger.error(f"Error creating scores table: {e}")
            self.conn.rollback()

    def create_trade_table(self):
        """Create crypto_trade_data table for tracking active and historical trades.
        
        Stores trade information including position size, entry price, direction,
        stop-loss/take-profit levels, and status tracking for multi-level exits.
        """
        try:
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS crypto_trade_data (
                    id_trade SERIAL PRIMARY KEY,
                    crypto_id INTEGER NOT NULL REFERENCES cryptos(id) ON DELETE CASCADE,
                    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    position_size FLOAT,
                    entry_price FLOAT,
                    direction INTEGER,
                    risk_reward_ratio FLOAT,
                    take_profit_1 FLOAT,
                    stop_loss_1 FLOAT,
                    status_1 INTEGER DEFAULT 0,
                    take_profit_2 FLOAT,
                    status_2 INTEGER DEFAULT 0,
                    stop_loss_2 FLOAT,
                    runner FLOAT,
                    status INTEGER DEFAULT 0
                )
            """)
            self.conn.commit()
        except Exception as e:
            self.logger.error(f"Error creating trade data table: {e}")
            self.conn.rollback()
    
    def create_portfolio_table(self):
        """Create portfolio_performance table for tracking portfolio metrics.
        
        Stores snapshots of total balance, free cash, and unrealized P&L over time.
        """
        try:
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS portfolio_performance (
                    id SERIAL PRIMARY KEY,
                    total_balance FLOAT,
                    free_cash FLOAT,
                    unrealized_pnl FLOAT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            self.conn.commit()
        except Exception as e:
            self.logger.error(f"Error creating portfolio table: {e}")
            self.conn.rollback()
        
#------------------------------------------------------------------------------------
# ----------------------------------- All Insert ------------------------------------
#------------------------------------------------------------------------------------
    def insert_portfolio_performance(self, total_balance: float, free_cash: float, unrealized_pnl: float):
        """Insert portfolio performance snapshot.
        
        Args:
            total_balance (float): Total portfolio value
            free_cash (float): Available cash for trading
            unrealized_pnl (float): Unrealized profit/loss from open positions
        """
        try:
            self.cur.execute("""
                INSERT INTO portfolio_performance (total_balance, free_cash, unrealized_pnl)
                VALUES (%s, %s, %s)
            """, (total_balance, free_cash, unrealized_pnl))
            self.conn.commit()
        except Exception as e:
            self.logger.error(f"Error inserting portfolio performance: {e}")
            self.conn.rollback()

    def insert_crypto(self, name, symbol, id_coingecko, symbol_binance):
        """Insert or update cryptocurrency listing.
        
        Args:
            name (str): Cryptocurrency full name
            symbol (str): Trading symbol (e.g., 'BTC')
            id_coingecko (str): CoinGecko identifier
            symbol_binance (str): Binance trading pair symbol
            
        Returns:
            int: Database ID of the inserted/updated crypto
        """
        self.cur.execute("""
            INSERT INTO cryptos (name, symbol, id_coingecko, symbol_binance)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id_coingecko) DO UPDATE
            SET name = EXCLUDED.name,
                symbol = EXCLUDED.symbol,
                symbol_binance = EXCLUDED.symbol_binance
            RETURNING id;
            """, (name, symbol, id_coingecko, symbol_binance))
        crypto_id = self.cur.fetchone()[0]
        self.conn.commit()
        return crypto_id

    def insert_or_update_rank(self, crypto_id, rank):
        """Insert or update cryptocurrency market cap rank.
        
        Args:
            crypto_id (int): Database ID of the cryptocurrency
            rank (int): Market cap ranking position
        """
        try:
            self.cur.execute("""
                INSERT INTO crypto_ranks (crypto_id, rank)
                VALUES (%s, %s)
                ON CONFLICT (crypto_id) DO UPDATE
                SET rank = EXCLUDED.rank;
            """, (crypto_id, rank))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            self.logger.error(f"Error inserting/updating rank (crypto_id={crypto_id}): {e}")

    def insert_cyptos_base(self, crypto_id, data):
        """Insert base market data for a cryptocurrency.
        
        Args:
            crypto_id (int): Database ID of the cryptocurrency
            data (dict): Dictionary containing market metrics (price, volume, market cap, ATH, etc.)
        """
        try:
            self.cur.execute("""
                INSERT INTO cyptos_data_base (
                    crypto_id, price, high_24h, low_24h, dominance, variation24h_pst, variation24h,
                    mc_variation24h_pst, mc_variation24h, market_cap, total_volume,
                    fully_diluted_valuation, all_time_high, all_time_high_timestamp,
                    all_time_high_pst
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                crypto_id, data.get('current_price'), data.get('high_24h'), data.get('low_24h'), 
                data.get('dominance'), data.get('price_change_24h_pct'), data.get('price_change_24h'),
                data.get('market_change_24h_pct'), data.get('market_change_24h'), data.get('market_cap'), 
                data.get('total_volume'), data.get('fully_diluted_valuation'), data.get('ath'), 
                data.get('ath_date'), data.get('ath_change_percentage')
            ))
            self.conn.commit()

        except Exception as e:
            self.conn.rollback()
            self.logger.error(f"Error inserting into cyptos_data_base (crypto_id={crypto_id}): {e}")


    def insert_cyptos_data_details(self, crypto_id, data):
        """Insert detailed technical analysis data for a cryptocurrency.
        
        Converts numpy types to Python native types and stores comprehensive technical
        indicators including volume metrics, price variations, RSI, MACD, moving averages,
        pivot points, and Fibonacci levels.
        
        Args:
            crypto_id (int): Database ID of the cryptocurrency
            data (dict): Dictionary containing 50+ technical indicator fields
        """
        try:
            def to_python_type(value):
                if value is None:
                    return None
                if hasattr(value, 'item'): 
                    return float(value.item())
                return float(value) if isinstance(value, (int, float)) else value
            
            self.cur.execute("""
                INSERT INTO cyptos_data_details (
                    crypto_id,
                    volume_actuel, volume_1j, volume_7j, volume_30j, variation_1j,
                    variation_7j, variation_30j, volume_moyen_30j, variation_moyenne_30j,
                    volume_moyen_7j, variation_moyenne_7j, volume_moyen_1j, variation_moyenne_1j,
                    current_price, d1_percentage, d1_value, d1_vs_avg, d1_mean,
                    d7_percentage, d7_value, d7_vs_avg, d7_mean,
                    d14_percentage, d14_value, d14_vs_avg, d14_mean,
                    d30_percentage, d30_value, d30_vs_avg, d30_mean,
                    circulating_supply, total_supply, max_supply,
                    pp, r1, r2, s1, s2,
                    rsi_values, macd_h, signal_line_h, histogram_h,
                    macd_j, signal_line_j, histogram_j,
                    sma_50, sma_200, ema_50, ema_200, poc,
                    fib_levels_1, fib_levels_2, fib_levels_3, fib_levels_4, fib_levels_5,
                    fib_levels_6, fib_levels_7
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                crypto_id,
                to_python_type(data.get('volume_actuel')),
                to_python_type(data.get('volume_1j')),
                to_python_type(data.get('volume_7j')),
                to_python_type(data.get('volume_30j')),
                to_python_type(data.get('variation_1j')),
                to_python_type(data.get('variation_7j')),
                to_python_type(data.get('variation_30j')),
                to_python_type(data.get('volume_moyen_30j')),
                to_python_type(data.get('variation_moyenne_30j')),
                to_python_type(data.get('volume_moyen_7j')),
                to_python_type(data.get('variation_moyenne_7j')),
                to_python_type(data.get('volume_moyen_1j')),
                to_python_type(data.get('variation_moyenne_1j')),
                to_python_type(data.get('current_price')),
                to_python_type(data.get('d1_percentage')),
                to_python_type(data.get('d1_value')),
                to_python_type(data.get('d1_vs_avg')),
                to_python_type(data.get('d1_mean')),
                to_python_type(data.get('d7_percentage')),
                to_python_type(data.get('d7_value')),
                to_python_type(data.get('d7_vs_avg')),
                to_python_type(data.get('d7_mean')),
                to_python_type(data.get('d14_percentage')),
                to_python_type(data.get('d14_value')),
                to_python_type(data.get('d14_vs_avg')),
                to_python_type(data.get('d14_mean')),
                to_python_type(data.get('d30_percentage')),
                to_python_type(data.get('d30_value')),
                to_python_type(data.get('d30_vs_avg')),
                to_python_type(data.get('d30_mean')),
                to_python_type(data.get('circulating_supply')),
                to_python_type(data.get('total_supply')),
                to_python_type(data.get('max_supply')),
                to_python_type(data.get('PP') or data.get('pp')),
                to_python_type(data.get('R1') or data.get('r1')),
                to_python_type(data.get('R2') or data.get('r2')),
                to_python_type(data.get('S1') or data.get('s1')),
                to_python_type(data.get('S2') or data.get('s2')),
                to_python_type(data.get('rsi_values')),
                to_python_type(data.get('macd_h')),
                to_python_type(data.get('signal_line_h')),
                to_python_type(data.get('histogram_h')),
                to_python_type(data.get('macd_j')),
                to_python_type(data.get('signal_line_j')),
                to_python_type(data.get('histogram_j')),
                to_python_type(data.get('sma_50')),
                to_python_type(data.get('sma_200')),
                to_python_type(data.get('ema_50')),
                to_python_type(data.get('ema_200')),
                to_python_type(data.get('POC') or data.get('poc')),
                to_python_type(data.get('fib_levels_1')),
                to_python_type(data.get('fib_levels_2')),
                to_python_type(data.get('fib_levels_3')),
                to_python_type(data.get('fib_levels_4')),
                to_python_type(data.get('fib_levels_5')),
                to_python_type(data.get('fib_levels_6')),
                to_python_type(data.get('fib_levels_7'))
            ))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            self.logger.error(f"Error inserting into cyptos_data_details (crypto_id={crypto_id}): {e}")



    def insert_cyptos_data_binance(self, crypto_id, data):
        """Insert Binance trading data for a cryptocurrency.
        
        Args:
            crypto_id (int): Database ID of the cryptocurrency
            data (dict): Dictionary containing order book depth, funding rate, and open interest
        """
        try:
            self.cur.execute("""
                INSERT INTO cyptos_data_binance (
                    crypto_id, bids_price_1, bids_quantity_1, bids_price_2, bids_quantity_2,
                    bids_price_3, bids_quantity_3, asks_price_1, asks_quantity_1,
                    asks_price_2, asks_quantity_2, asks_price_3, asks_quantity_3,
                    funding_rate, open_interest
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (crypto_id, data.get('bids_price_1'), data.get('bids_quantity_1'), data.get('bids_price_2'), data.get('bids_quantity_2'),
            data.get('bids_price_3'), data.get('bids_quantity_3'), data.get('asks_price_1'), data.get('asks_quantity_1'),
            data.get('asks_price_2'), data.get('asks_quantity_2'), data.get('asks_price_3'), data.get('asks_quantity_3'),
            data.get('funding_rate'), data.get('open_interest')))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            self.logger.error(f"Error inserting into cyptos_data_binance (crypto_id={crypto_id}): {e}")
            
    def insert_sentiment_score(self, crypto_id: int, avg_score_12h: float, count_12h: int, avg_score_24h: float, count_24h: int):
        """Insert aggregated sentiment scores for a cryptocurrency.
        
        Args:
            crypto_id (int): Database ID of the cryptocurrency
            avg_score_12h (float): Average sentiment score over 12 hours
            count_12h (int): Number of tweets analyzed in 12h window
            avg_score_24h (float): Average sentiment score over 24 hours
            count_24h (int): Number of tweets analyzed in 24h window
        """
        try:
            self.cur.execute("""
                INSERT INTO crypto_sentiment_scores (
                    crypto_id,
                    score_12h, count_12h,
                    score_24h, count_24h
                ) VALUES (%s, %s, %s, %s, %s)
            """, (
                crypto_id,
                avg_score_12h, count_12h,
                avg_score_24h, count_24h
            ))
            self.conn.commit()
            self.logger.info(f"Sentiment score saved for crypto_id {crypto_id}")
        except Exception as e:
            self.conn.rollback()
            self.logger.error(f"Error inserting sentiment: {e}")

    def insert_new_account(self, account_name: str):
        """Insert a Twitter account into tracking list.
        
        Args:
            account_name (str): Twitter account name to track
        """
        try:
            self.cur.execute("""
                INSERT INTO account (account_name)
                VALUES (%s)
                ON CONFLICT (account_name) DO NOTHING
            """, (account_name,))
            self.conn.commit()
            self.logger.info(f"Account '{account_name}' inserted/exists already.")
        except Exception as e:
            self.conn.rollback()
            self.logger.error(f"Error inserting account '{account_name}': {e}")

    def insert_tweet_hash(self, tweet_hash: str):
        """Insert tweet hash for deduplication.
        
        Args:
            tweet_hash (str): Unique hash of the tweet content
            
        Returns:
            int: Tweet ID (new or existing), or None if error
        """
        try:
            self.cur.execute("""
                INSERT INTO tweet_hash (hash)
                VALUES (%s)
                ON CONFLICT (hash) DO NOTHING
                RETURNING tweet_id
            """, (tweet_hash,))
            
            result = self.cur.fetchone()
            if result:
                tweet_id = result[0]
                self.conn.commit()
                self.logger.info(f"Tweet hash saved with ID {tweet_id}")
                return tweet_id
            else:
                self.cur.execute("""
                    SELECT tweet_id FROM tweet_hash WHERE hash = %s
                """, (tweet_hash,))
                tweet_id = self.cur.fetchone()[0]
                self.logger.info(f"Tweet hash already exists with ID {tweet_id}")
                return tweet_id
        except Exception as e:
            self.conn.rollback()
            self.logger.error(f"Error inserting tweet hash: {e}") 
            return None
    
    def insert_tweet_sentiment(self, tweet_id: int, account: str, tweet_content: str, timestamp: int):
        """Insert tweet content and metadata.
        
        Args:
            tweet_id (int): Tweet ID from tweet_hash table
            account (str): Twitter account name that posted the tweet
            tweet_content (str): Full tweet text
            timestamp (int): Unix timestamp of the tweet
        """
        try:
            self.cur.execute("""
                INSERT INTO tweet_sentiments (tweet_id, account, tweet_content, timestamp)
                VALUES (%s, %s, %s, %s)
            """, (tweet_id, account, tweet_content, timestamp))
            self.conn.commit()
            self.logger.info(f"Tweet sentiment inserted with ID {tweet_id}")
            
        except Exception as e:
            self.conn.rollback()
            self.logger.error(f"Error inserting tweet sentiment: {e}")
    
    def link_tweet_to_crypto(self, tweet_id: int, crypto_id: int, sentiment_score: float):
        """Link a tweet to a cryptocurrency with its sentiment score.
        
        Args:
            tweet_id (int): Tweet ID from tweet_hash table
            crypto_id (int): Cryptocurrency database ID
            sentiment_score (float): Sentiment score for this crypto mention (-1 to 1)
        """
        try:
            self.cur.execute("""
                INSERT INTO tweet_crypto (tweet_id, crypto_id, sentiment_score)
                VALUES (%s, %s, %s)
                ON CONFLICT (tweet_id, crypto_id) DO NOTHING
            """, (tweet_id, crypto_id, sentiment_score))
            
            self.conn.commit()
            self.logger.info(f"Linked tweet {tweet_id} to crypto {crypto_id} with score {sentiment_score}")
        except Exception as e:
            self.conn.rollback()
            self.logger.error(f"Error linking tweet to crypto: {e}")
            
    def insert_score(self, crypto_id: int, score_metric: float, score_total: int, Trend: float, priceUnit: float):
        """Insert calculated trading signal scores.
        
        Args:
            crypto_id (int): Cryptocurrency database ID
            score_metric (float): Metric-based score component
            score_total (int): Combined total score
            Trend (float): Trend indicator value
            priceUnit (float): Price unit for calculations
        """
        try:
            self.cur.execute("""
                INSERT INTO crypto_scores (crypto_id, score_metric, score_total, Trend, priceUnit)
                VALUES (%s, %s, %s, %s, %s)
            """, (crypto_id, score_metric, score_total, Trend, priceUnit))
            self.conn.commit()
        except Exception as e:
            self.logger.error(f"Error inserting score data: {e}")
            self.conn.rollback()
    
    def insert_trade(self, crypto_id: int, position_size: float, entry_price: float, direction: int,
                        risk_reward_ratio: float, take_profit_1: float, stop_loss_1: float,
                        take_profit_2: float, stop_loss_2: float, runner: float = None):
        """Insert a new trade with multi-level take-profit targets.
        
        Args:
            crypto_id (int): Cryptocurrency database ID
            position_size (float): Size of the position
            entry_price (float): Entry price level
            direction (int): Trade direction (1 for long, -1 for short)
            risk_reward_ratio (float): Risk/reward ratio
            take_profit_1 (float): First take-profit level
            stop_loss_1 (float): Stop-loss for first position
            take_profit_2 (float): Second take-profit level
            stop_loss_2 (float): Stop-loss for second position
            runner (float, optional): Runner/trailing stop level. Defaults to None.
        """
        try:
            self.cur.execute("""
                INSERT INTO crypto_trade_data 
                (crypto_id, position_size, entry_price, direction, risk_reward_ratio, 
                take_profit_1, stop_loss_1, take_profit_2, stop_loss_2, runner)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (crypto_id, position_size, entry_price, direction, risk_reward_ratio,
                      take_profit_1, stop_loss_1, take_profit_2, stop_loss_2, runner))
            self.conn.commit()
        except Exception as e:
            self.logger.error(f"Error inserting trade data: {e}")
            self.conn.rollback()
            
            
#------------------------------------------------------------------------------------
# ----------------------------------- All drop tables -------------------------------
#------------------------------------------------------------------------------------

    def drop_tables(self):
        """Drop all main cryptocurrency data tables in correct cascade order."""
        tables = ['cyptos_data_binance', 'cyptos_data_details', 'cyptos_data_base', 'crypto_ranks', 'cryptos']
        for table in tables:
            self.cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
            self.conn.commit()
            
    def drop_sentiment_tables(self):
        """Drop all sentiment analysis related tables in correct cascade order."""
        self.cur.execute("DROP TABLE IF EXISTS tweet_crypto;")
        self.cur.execute("DROP TABLE IF EXISTS tweet_sentiments;")
        self.cur.execute("DROP TABLE IF EXISTS tweet_hash;")
        self.cur.execute("DROP TABLE IF EXISTS crypto_sentiment_scores;")
        self.cur.execute("DROP TABLE IF EXISTS account;")
        self.conn.commit()
        
    def drop_tables_scores_and_trade(self):
        """Drop trading scores, trade data, and portfolio performance tables."""
        self.cur.execute("DROP TABLE IF EXISTS crypto_scores CASCADE")
        self.cur.execute("DROP TABLE IF EXISTS crypto_trade_data CASCADE")
        self.cur.execute("DROP TABLE IF EXISTS portfolio_performance CASCADE")
        self.conn.commit()


#------------------------------------------------------------------------------------
# ----------------------------------- All select ------------------------------------
#------------------------------------------------------------------------------------

    def check_tweet_exists(self, tweet_hash: str) -> bool:
        """Check if a tweet hash already exists in the database.
        
        Args:
            tweet_hash (str): Unique hash of the tweet
            
        Returns:
            bool: True if tweet exists, False otherwise
        """
        try:
            self.cur.execute("""
                SELECT COUNT(*) FROM tweet_hash WHERE hash = %s
            """, (tweet_hash,))
            count = self.cur.fetchone()[0]
            return count > 0
        except Exception as e:
            self.logger.error(f"Error checking tweet existence: {e}")
            return False
    
    def get_crypto_list(self) -> List[str]:
        """Get list of all cryptocurrency symbols and names.
        
        Returns:
            List[str]: Flattened list alternating between symbol and name
        """
        try:
            self.cur.execute("SELECT symbol,name FROM cryptos")
            cryptos = []
            for row in self.cur.fetchall():
                cryptos.append(row[0])
                cryptos.append(row[1])
            return cryptos
        except Exception as e:
            self.logger.error(f"Error retrieving crypto list: {e}")
            raise

    def get_all_crypto_id(self):
        """Get list of all cryptocurrency database IDs.
        
        Returns:
            List[int]: List of crypto IDs
        """
        try:
            self.cur.execute("SELECT id FROM cryptos")
            crypto_ids = [row[0] for row in self.cur.fetchall()]
            return crypto_ids
        except Exception as e:
            self.logger.error(f"Error retrieving crypto IDs: {e}")
            raise
        
    def get_sentiments_for_crypto(self, crypto_id: int) -> List[float]:
        """Get all sentiment scores for a specific cryptocurrency.
        
        Args:
            crypto_id (int): Cryptocurrency database ID
            
        Returns:
            List[float]: List of sentiment scores
        """
        try:
            self.cur.execute("""
                SELECT sentiment_score FROM tweet_crypto
                WHERE crypto_id = %s
            """, (crypto_id,))
            sentiments = [row[0] for row in self.cur.fetchall()]
            return sentiments
        except Exception as e:
            self.logger.error(f"Error retrieving sentiments for crypto {crypto_id}: {e}")
            raise
        
    def get_sentiments_for_crypto_24h(self, crypto_id: int) -> List[float]:
        """Get sentiment scores from the last 24 hours for a cryptocurrency.
        
        Args:
            crypto_id (int): Cryptocurrency database ID
            
        Returns:
            List[float]: List of sentiment scores from last 24h
        """
        try:
            self.cur.execute("""
                SELECT tc.sentiment_score 
                FROM tweet_crypto tc
                JOIN tweet_sentiments ts ON tc.tweet_id = ts.tweet_id
                WHERE tc.crypto_id = %s 
                AND ts.timestamp >= EXTRACT(EPOCH FROM (NOW() - INTERVAL '24 hours'))
            """, (crypto_id,))
            sentiments = [row[0] for row in self.cur.fetchall()]
            return sentiments
        except Exception as e:
            self.logger.error(f"Error retrieving sentiments for crypto {crypto_id} in last 24h: {e}")
            raise

    def get_sentiments_for_crypto_12h(self, crypto_id: int) -> List[float]:
        """Get sentiment scores from the last 12 hours for a cryptocurrency.
        
        Args:
            crypto_id (int): Cryptocurrency database ID
            
        Returns:
            List[float]: List of sentiment scores from last 12h
        """
        try:
            self.cur.execute("""
                SELECT tc.sentiment_score 
                FROM tweet_crypto tc
                JOIN tweet_sentiments ts ON tc.tweet_id = ts.tweet_id
                WHERE tc.crypto_id = %s 
                AND ts.timestamp >= EXTRACT(EPOCH FROM (NOW() - INTERVAL '12 hours'))
            """, (crypto_id,))
            sentiments = [row[0] for row in self.cur.fetchall()]
            return sentiments
        except Exception as e:
            self.logger.error(f"Error retrieving sentiments for crypto {crypto_id} in last 12h: {e}")
            raise
    
    
    def get_crypto_id_by_symbol_or_name(self, symbol_or_name: str) -> int:
        """Find cryptocurrency ID by symbol or name.
        
        Args:
            symbol_or_name (str): Cryptocurrency symbol or name
            
        Returns:
            int: Crypto database ID, or None if not found
        """
        try:
            self.cur.execute("""
                SELECT id FROM cryptos
                WHERE symbol = %s OR name = %s
            """, (symbol_or_name, symbol_or_name))
            result = self.cur.fetchone()
            if result:
                return result[0]
            else:
                return None
        except Exception as e:
            self.logger.error(f"Error retrieving crypto ID by symbol or name {symbol_or_name}: {e}")
            raise

    def get_all_sentiment_scores(self) -> List[Dict]:
        """Get all sentiment score records from database.
        
        Returns:
            List[Dict]: List of sentiment score dictionaries with crypto_id, scores, counts, and timestamp
        """
        try:
            self.cur.execute("""
                SELECT crypto_id, score_12h, count_12h, score_24h, count_24h, timestamp
                FROM crypto_sentiment_scores
            """)
            records = []
            for row in self.cur.fetchall():
                records.append({
                    'crypto_id': row[0],
                    'score_12h': row[1],
                    'count_12h': row[2],
                    'score_24h': row[3],
                    'count_24h': row[4],
                    'timestamp': row[5]
                })
            return records
        except Exception as e:
            self.logger.error(f"Error retrieving all sentiment scores: {e}")
            raise

    def get_all_accounts(self) -> List[str]:
        """Get list of all tracked Twitter accounts.
        
        Returns:
            List[str]: List of account names
        """
        try:
            self.cur.execute("SELECT account_name FROM account")
            accounts = [row[0] for row in self.cur.fetchall()]
            return accounts
        except Exception as e:
            self.logger.error(f"Error retrieving accounts: {e}")
            raise
    
    def get_all_cryptos(self) -> List[Dict[str, Any]]:
        """Get all cryptocurrencies with their details and rankings.
        
        Returns:
            List[Dict]: List of crypto dictionaries with id, name, symbol, CoinGecko ID, Binance symbol, and rank
        """
        try:
            self.cur.execute("""
                SELECT 
                    c.id,
                    c.name,
                    c.symbol,
                    c.id_coingecko,
                    c.symbol_binance,
                    cr.rank
                FROM cryptos c
                LEFT JOIN crypto_ranks cr ON c.id = cr.crypto_id
                ORDER BY cr.rank NULLS LAST, c.id
            """)
            return self._rows_to_dicts(self.cur.fetchall())
        except Exception as e:
            self.logger.error(f"Error fetching cryptos: {e}")
            return []
        
           
    def get_last_crypto_price(self, crypto_id: int) -> Optional[float]:
        """Get the most recent price for a cryptocurrency.
        
        Args:
            crypto_id (int): Cryptocurrency database ID
            
        Returns:
            Optional[float]: Latest price, or None if not found
        """
        try:
            self.cur.execute("""
                SELECT price FROM cyptos_data_base
                WHERE crypto_id=%s
                ORDER BY timestamp DESC
                LIMIT 1
            """, (crypto_id,))
            result = self.cur.fetchone()
            return result[0] if result else None
        except Exception as e:
            self.logger.error(f"Error fetching last crypto price: {e}")
            return None
        
       
    def get_historical_prices(self, crypto_id: int, days: int) -> List[Dict[str, Any]]:
        """Get historical price data for a cryptocurrency.
        
        Args:
            crypto_id (int): Cryptocurrency database ID
            days (int): Number of days of historical data
            
        Returns:
            List[Dict]: List of price records ordered chronologically
        """
        try:
            since_date = datetime.now() - timedelta(days=days)
            self.cur.execute("""
                SELECT price FROM cyptos_data_base
                WHERE crypto_id=%s AND timestamp >= %s
                ORDER BY timestamp ASC
            """, (crypto_id, since_date))
            return self._rows_to_dicts(self.cur.fetchall())
        except Exception as e:
            self.logger.error(f"Error fetching historical prices: {e}")
            return []
    
    def get_crypto_data(self, crypto_id: int) -> Dict[str, Any]:
        """Get comprehensive cryptocurrency data (alias for get_all_crypto_informations).
        
        Args:
            crypto_id (int): Cryptocurrency database ID
            
        Returns:
            Dict: Complete crypto data including base, technical, Binance, and sentiment data
        """
        return self.get_all_crypto_informations(crypto_id)
    
    def get_all_crypto_informations(self,crypto_id) -> List[Dict[str, Any]]:
        """Get all available data for a cryptocurrency from joined tables.
        
        Performs a complex join across base data, technical details, Binance data,
        and sentiment scores to retrieve comprehensive cryptocurrency information.
        
        Args:
            crypto_id (int): Cryptocurrency database ID
            
        Returns:
            List[Dict]: List with single dictionary containing all crypto metrics
        """
        try:
            self.cur.execute("""
                WITH base_latest AS (
                    SELECT * FROM cyptos_data_base 
                    WHERE crypto_id=%s 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                )
                SELECT 
                    b.*,
                    d.rsi_values as rsi,
                    d.macd_j as macd_j,
                    d.signal_line_j as signal_j,
                    d.macd_h as macd_h,
                    d.signal_line_h as signal_h,
                    d.histogram_h as histogram,
                    d.histogram_j as hist_norm,
                    d.ema_50,
                    d.ema_200,
                    d.sma_50,
                    d.sma_200,
                    d.r1,
                    d.s1,
                    d.pp as pivot,
                    d.fib_levels_3 as fibo_382,
                    d.fib_levels_5 as fibo_618,
                    d.d1_percentage,
                    d.d7_percentage,
                    d.d14_percentage,
                    d.volume_actuel,
                    d.volume_moyen_7j,
                    bn.funding_rate,
                    bn.open_interest,
                    s.score_12h as sentiment_score_12h,
                    s.count_12h as sentiment_count_12h,
                    s.score_24h as sentiment_score_24h,
                    s.count_24h as sentiment_count_24h
                FROM base_latest b
                LEFT JOIN LATERAL (
                    SELECT * FROM cyptos_data_details 
                    WHERE crypto_id=%s 
                    ORDER BY ABS(EXTRACT(EPOCH FROM (timestamp - b.timestamp)))
                    LIMIT 1
                ) d ON TRUE
                LEFT JOIN LATERAL (
                    SELECT * FROM cyptos_data_binance 
                    WHERE crypto_id=%s 
                    ORDER BY ABS(EXTRACT(EPOCH FROM (timestamp - b.timestamp)))
                    LIMIT 1
                ) bn ON TRUE
                LEFT JOIN LATERAL (
                    SELECT * FROM crypto_sentiment_scores 
                    WHERE crypto_id=%s 
                    ORDER BY timestamp DESC
                    LIMIT 1
                ) s ON TRUE
            """, (crypto_id, crypto_id, crypto_id, crypto_id))
            
            return self._rows_to_dicts(self.cur.fetchall())
        except Exception as e:
            self.logger.error(f"Error fetching crypto data for ID {crypto_id}: {e}")
            return []
        
    
    def select_trades_current(self, crypto_id: int) -> List[Dict[str, Any]]:
        """Get all active trades for a specific cryptocurrency.
        
        Args:
            crypto_id (int): Cryptocurrency database ID
            
        Returns:
            List[Dict]: List of active trade dictionaries (status=0)
        """
        try:
            self.cur.execute("""
                SELECT * FROM crypto_trade_data 
                WHERE crypto_id=%s AND status=0
            """, (crypto_id,))
            return self._rows_to_dicts(self.cur.fetchall())
        except Exception as e:
            self.logger.error(f"Error fetching current trades: {e}")
            return []
    
    def select_all_trades_current(self) -> List[Dict[str, Any]]:
        """Get all active trades across all cryptocurrencies.
        
        Returns:
            List[Dict]: List of all trades with any active positions (status=0 or status_1=0 or status_2=0)
        """
        try:
            self.cur.execute("""
                SELECT * FROM crypto_trade_data 
                WHERE status=0 or status_1=0 or status_2=0
            """)
            return self._rows_to_dicts(self.cur.fetchall())
        except Exception as e:
            self.logger.error(f"Error fetching all current trades: {e}")
            return []
        
    
# ------------------------------------------------------------------------------------
# ------------------- Maintenance Methods -----------------------------
# ------------------------------------------------------------------------------------

    def update_database(self):
        """Clean up old tweets beyond retention period.
        
        Deletes tweets older than TWEET_RETENTION_DAYS from all sentiment tables
        to maintain database performance and comply with data retention policies.
        """
        try:
            seven_days_ago = int((datetime.now().timestamp() - (conf.TWEET_RETENTION_DAYS * 24 * 60 * 60)))
            self.cur.execute("""
                SELECT tweet_id FROM tweet_sentiments
                WHERE timestamp < %s
            """, (seven_days_ago,))
            old_tweet_ids = [row[0] for row in self.cur.fetchall()]
            if not old_tweet_ids:
                self.logger.info("No tweets older than 7 days to delete")
                return
            self.cur.execute("""
                DELETE FROM tweet_crypto
                WHERE tweet_id = ANY(%s)
            """, (old_tweet_ids,))
            self.cur.execute("""
                DELETE FROM tweet_sentiments
                WHERE tweet_id = ANY(%s)
            """, (old_tweet_ids,))
            self.cur.execute("""
                DELETE FROM tweet_hash
                WHERE tweet_id = ANY(%s)
            """, (old_tweet_ids,))
            self.conn.commit()
            self.logger.info(f"Deleted {len(old_tweet_ids)} tweets older than 7 days")
        except Exception as e:
            self.conn.rollback()
            self.logger.error(f"Error cleaning old tweets: {e}")
            raise
    
    def update_trade_status(self, trade_id: int, take_profit_number: int, status: int):
        """Update status of a specific take-profit level for a trade.
        
        Args:
            trade_id (int): Trade database ID
            take_profit_number (int): Which TP level to update (1, 2, or 3 for runner)
            status (int): New status value (0=active, 1=hit, -1=stopped)
        """
        try:
            if take_profit_number == 1:
                self.cur.execute("""
                    UPDATE crypto_trade_data
                    SET status_1=%s
                    WHERE id_trade=%s
                """, (status, trade_id))
            elif take_profit_number == 2:
                self.cur.execute("""
                    UPDATE crypto_trade_data
                    SET status_2=%s
                    WHERE id_trade=%s
                """, (status, trade_id))
            elif take_profit_number == 3:
                self.cur.execute("""
                    UPDATE crypto_trade_data
                    SET status=%s
                    WHERE id_trade=%s
                """, (status, trade_id))
            self.conn.commit()
        except Exception as e:
            self.logger.error(f"Error updating trade status for trade_id {trade_id}: {e}")
            self.conn.rollback()
