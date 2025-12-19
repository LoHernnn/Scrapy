import psycopg2
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

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
    
    def get_all_crypto_informations(self,crypto_id) -> List[Dict[str, Any]]:
        """
        Get all cryptocurrencies with their complete information including
        base data, detailed data, and Binance data.
        
        Returns:
            List of dictionaries with complete crypto info.
        """
        try:
            self.cur.execute("""
                SELECT * from cyptos_data_base where crypto_id=%s order by timestamp desc limit 10
            """,(crypto_id,))
            base_data = self._rows_to_dicts(self.cur.fetchall())
            self.cur.execute("""
                SELECT * from cyptos_data_details where crypto_id=%s order by timestamp desc limit 10
            """,(crypto_id,))
            details_data = self._rows_to_dicts(self.cur.fetchall())
            self.cur.execute("""
                SELECT * from cyptos_data_binance where crypto_id=%s order by timestamp desc limit 10
            """,(crypto_id,))
            binance_data = self._rows_to_dicts(self.cur.fetchall())
            self.cur.execute("""
                SELECT * FROM crypto_sentiment_scores where crypto_id=%s order by timestamp desc limit 1
            """,(crypto_id,))
            sentiment_data = self._rows_to_dicts(self.cur.fetchall())
            return {
                "base_data": base_data,
                "details_data": details_data,
                "binance_data": binance_data,
                "sentiment_data": sentiment_data
            }
        except Exception as e:
            print(f"Error fetching complete crypto info: {e}")
            return {
                "base_data": [],
                "details_data": [],
                "binance_data": [],
                "sentiment_data": []
            }