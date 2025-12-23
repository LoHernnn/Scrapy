import psycopg2
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta


def safe_float(value, default=0.0):
    """
    Safely convert a value to float.
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
    Returns:
        Float value or default
    """
    try:
        return float(value) if value is not None else default
    except (ValueError, TypeError):
        return default


class DatabaseCryptoBot:
    """
    Database class for CryptoBot to read all cryptocurrency data including
    market data, technical indicators, and sentiment analysis.
    """
    
    def __init__(self, db_config: Dict[str, str]):
        """
        Initialize the database connection.
        
        Args:
            db_config: Dictionary with keys: host, port, database, user, password
        """
        self.db_config = db_config
        self.conn = None
        self.cur = None
        self.connect()
    
    def connect(self):
        """Establish connection to PostgreSQL database."""
        try:
            self.conn = psycopg2.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                database=self.db_config['database'],
                user=self.db_config['user'],
                password=self.db_config['password']
            )
            self.cur = self.conn.cursor()
            return True
        except Exception as e:
            print(f"Database connection failed: {e}")
            return False
    
    def disconnect(self):
        """Close database connection."""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
        self.conn = None
        self.cur = None
    
    def _rows_to_dicts(self, rows) -> List[Dict[str, Any]]:
        """Convert cursor rows to list of dictionaries."""
        if not rows:
            return []
        colnames = [desc[0] for desc in self.cur.description]
        return [dict(zip(colnames, row)) for row in rows]
    
    # ============================================================================
    # CRYPTO LISTING & BASIC INFO
    # ============================================================================

    def get_all_crypto_ids(self) -> List[int]:
        """
        Get a list of all cryptocurrency IDs in the database.
        
        Returns:
            List of cryptocurrency IDs.
        """
        try:
            self.cur.execute("SELECT id FROM cryptos")
            rows = self.cur.fetchall()
            return [row[0] for row in rows]
        except Exception as e:
            print(f"Error fetching crypto IDs: {e}")
            return []
    
    def get_all_cryptos(self) -> List[Dict[str, Any]]:
        """
        Get all cryptocurrencies with their basic information.
        
        Returns:
            List of dictionaries with crypto info (id, name, symbol, id_coingecko, symbol_binance)
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
            print(f"Error fetching cryptos: {e}")
            return []
        
    def get_last_crypto_price(self, crypto_id: int) -> Optional[float]:
        """
        Get the last recorded price for a given cryptocurrency.
        
        Args:
            crypto_id: ID of the cryptocurrency.
        Returns:
            Last price as float or None if not found.
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
            print(f"Error fetching last crypto price: {e}")
            return None
        
    def get_historical_prices(self, crypto_id: int, days: int) -> List[Dict[str, Any]]:
        """
        Get historical prices for a cryptocurrency over a specified number of days.
        
        Args:
            crypto_id: ID of the cryptocurrency.
            days: Number of days to look back.
        Returns:
            List of dictionaries with timestamp and price_usd.
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
            print(f"Error fetching historical prices: {e}")
            return []
    
    def get_crypto_data(self, crypto_id: int) -> Dict[str, Any]:
        """
        Get crypto data in format expected by Market_detection_detection.
        Alias for get_all_crypto_informations.
        
        Args:
            crypto_id: ID of the cryptocurrency
        Returns:
            Dictionary with base_data, details_data, binance_data, sentiment_data
        """
        return self.get_all_crypto_informations(crypto_id)
    
    def get_all_crypto_informations(self,crypto_id) -> List[Dict[str, Any]]:
        """
        Get all cryptocurrencies with their complete information including
        base data, detailed data, and Binance data merged into a single structure.
        
        Returns:
            List of dictionaries with merged crypto data, one entry per timestamp.
        """
        try:
            # Récupérer la ligne la plus récente de chaque table et les fusionner
            # Utilise LATERAL JOIN pour trouver la ligne la plus proche temporellement
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
            print(f"Error fetching complete crypto info: {e}")
            return []
    # ============================================================================
    # CRYPTO TRADE DATA
    # ============================================================================

    def create_score_table(self):
        try:
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS crypto_scores (
                    crypto_id INTEGER NOT NULL REFERENCES cryptos(id) ON DELETE CASCADE,
                    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    score_metric FLOAT,
                    score_total INTEGER,
                    Trend FLOAT,
                    priceUnit FLOAT,
                    PRIMARY KEY (crypto_id, timestamp)
                )
            """)
            self.conn.commit()
        except Exception as e:
            print(f"Error creating scores table: {e}")
            self.conn.rollback()

    def create_trade_table(self):
        """
        Create the crypto_trade_data table if it does not exist.
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
            print(f"Error creating trade data table: {e}")
            self.conn.rollback()
            
    def drop_tables(self):
        try:
            self.cur.execute("DROP TABLE IF EXISTS crypto_scores CASCADE")
            self.cur.execute("DROP TABLE IF EXISTS crypto_trade_data CASCADE")
            self.conn.commit()
        except Exception as e:
            print(f"Error dropping tables: {e}")
            self.conn.rollback()

    def insert_score(self, crypto_id: int, score_metric: float, score_total: int, Trend: float, priceUnit: float):
        try:
            self.cur.execute("""
                INSERT INTO crypto_scores (crypto_id, score_metric, score_total, Trend, priceUnit)
                VALUES (%s, %s, %s, %s, %s)
            """, (crypto_id, score_metric, score_total, Trend, priceUnit))
            self.conn.commit()
        except Exception as e:
            print(f"Error inserting score: {e}")
            self.conn.rollback()
    
    def insert_trade(self, crypto_id: int, position_size: float, entry_price: float, direction: int,
                        risk_reward_ratio: float, take_profit_1: float, stop_loss_1: float,
                        take_profit_2: float, stop_loss_2: float, runner: float = None):
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
                print(f"Error inserting trade data: {e}")
                self.conn.rollback()

    def select_trades_current(self, crypto_id: int) -> List[Dict[str, Any]]:
        """
        Select current trades for a given cryptocurrency.
        
        Args:
            crypto_id: ID of the cryptocurrency.
        Returns:
            List of dictionaries with current trade data.
        """
        try:
            self.cur.execute("""
                SELECT * FROM crypto_trade_data 
                WHERE crypto_id=%s AND status=0
            """, (crypto_id,))
            return self._rows_to_dicts(self.cur.fetchall())
        except Exception as e:
            print(f"Error fetching current trades: {e}")
            return []
    
    def select_all_trades_current(self) -> List[Dict[str, Any]]:
        """
        Select all current trades across all cryptocurrencies.
        
        Returns:
            List of dictionaries with current trade data.
        """
        try:
            self.cur.execute("""
                SELECT * FROM crypto_trade_data 
                WHERE status=0 or status_1=0 or status_2=0
            """)
            return self._rows_to_dicts(self.cur.fetchall())
        except Exception as e:
            print(f"Error fetching all current trades: {e}")
            return []
        
        
    def update_trade_status(self, trade_id: int, take_profit_number: int, status: int):
        """
        Update the status of a trade's take profit or overall status.
        
        Args:
            trade_id: ID of the trade.
            take_profit_number: 1 or 2 for respective take profits, or 0 for overall status.
            status: New status value.
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
            print(f"Error updating trade status: {e}")
            self.conn.rollback()
        
    