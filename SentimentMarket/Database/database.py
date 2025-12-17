import psycopg2
import logging
from typing import List, Dict
from datetime import datetime
import conf
import utils.logger as Logger

class SentimentDatabase:
    
    def __init__(self, db_config: Dict):
        self.db_config = db_config
        self.logger = Logger.get_logger("SentimentDatabase")
    
    def connect(self):
        try:
            conn = psycopg2.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                database=self.db_config['database'],
                user=self.db_config['user'],
                password=self.db_config['password']
            )
            return conn
        except Exception as e:
            self.logger.error(f"Database connection failed: {e}")
            raise

#------------------------------------------------------------------------------------
# ------------------- Sentiment Analysis Tables -----------------------------
#------------------------------------------------------------------------------------
    
    def create_sentiment_tables(self):
        conn = self.connect()
        cur = conn.cursor()
        try:
            cur.execute("""
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
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tweet_hash (
                    tweet_id SERIAL PRIMARY KEY,
                    hash TEXT NOT NULL UNIQUE
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS tweet_sentiments (
                    tweet_id INTEGER PRIMARY KEY,
                    account TEXT,
                    tweet_content TEXT,
                    timestamp BIGINT,
                    FOREIGN KEY (tweet_id) REFERENCES tweet_hash(tweet_id) ON DELETE CASCADE
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS tweet_crypto (
                    tweet_id INTEGER,
                    crypto_id INTEGER,
                    sentiment_score FLOAT,
                    PRIMARY KEY (tweet_id, crypto_id),
                    FOREIGN KEY (tweet_id) REFERENCES tweet_hash(tweet_id) ON DELETE CASCADE,
                    FOREIGN KEY (crypto_id) REFERENCES cryptos(id) ON DELETE CASCADE
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS account (
                    account_id SERIAL PRIMARY KEY,
                    account_name TEXT UNIQUE NOT NULL
                );
            """)

            conn.commit()
            
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Error creating tables: {e}")
            raise
        finally:
            cur.close()
            conn.close()

    def drop_sentiment_tables(self):
        conn = self.connect()
        cur = conn.cursor()
        try:
            cur.execute("DROP TABLE IF EXISTS tweet_crypto;")
            cur.execute("DROP TABLE IF EXISTS tweet_sentiments;")
            cur.execute("DROP TABLE IF EXISTS tweet_hash;")
            cur.execute("DROP TABLE IF EXISTS crypto_sentiment_scores;")
            cur.execute("DROP TABLE IF EXISTS account;")
            conn.commit()
            self.logger.info("Sentiment analysis tables dropped successfully.")
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Error dropping tables: {e}")
            raise
        finally:
            cur.close()
            conn.close()
    
# ------------------------------------------------------------------------------------
# ------------------- Sentiment Analysis Insert -----------------------------
# ------------------------------------------------------------------------------------

    def insert_sentiment_score(self, crypto_id: int, avg_score_12h: float, count_12h: int, avg_score_24h: float, count_24h: int):
        conn = self.connect()
        cur = conn.cursor()
        
        try:
            cur.execute("""
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
            conn.commit()
            self.logger.info(f"Sentiment score saved for crypto_id {crypto_id}")
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Error inserting sentiment: {e}")
            raise
        finally:
            cur.close()
            conn.close()

    def insert_new_account(self, account_name: str):
        conn = self.connect()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                INSERT INTO account (account_name)
                VALUES (%s)
                ON CONFLICT (account_name) DO NOTHING
            """, (account_name,))
            conn.commit()
            self.logger.info(f"Account '{account_name}' inserted/exists already.")
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Error inserting account '{account_name}': {e}")
            raise
        finally:
            cur.close()
            conn.close()

    def insert_tweet_hash(self, tweet_hash: str):
        conn = self.connect()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                INSERT INTO tweet_hash (hash)
                VALUES (%s)
                RETURNING tweet_id
            """, (tweet_hash,))
            
            tweet_id = cur.fetchone()[0]
            conn.commit()
            self.logger.info(f"Tweet hash saved with ID {tweet_id}")
            return tweet_id
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Error inserting tweet hash: {e}")
            raise
        finally:
            cur.close()
            conn.close()
    
    def insert_tweet_sentiment(self, tweet_id: int, account: str, tweet_content: str, timestamp: int):
        conn = self.connect()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO tweet_sentiments (tweet_id, account, tweet_content, timestamp)
                VALUES (%s, %s, %s, %s)
            """, (tweet_id, account, tweet_content, timestamp))
            conn.commit()
            self.logger.info(f"Tweet sentiment inserted with ID {tweet_id}")
            
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Error inserting tweet sentiment: {e}")
            raise
        finally:
            cur.close()
            conn.close()
    
    def link_tweet_to_crypto(self, tweet_id: int, crypto_id: int, sentiment_score: float):
        conn = self.connect()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO tweet_crypto (tweet_id, crypto_id, sentiment_score)
                VALUES (%s, %s, %s)
                ON CONFLICT (tweet_id, crypto_id) DO NOTHING
            """, (tweet_id, crypto_id, sentiment_score))
            
            conn.commit()
            self.logger.info(f"Linked tweet {tweet_id} to crypto {crypto_id} with score {sentiment_score}")
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Error linking tweet to crypto: {e}")
            raise
        finally:
            cur.close()
            conn.close()

# ------------------------------------------------------------------------------------
# ------------------- Select Analysis Insert -----------------------------
# ------------------------------------------------------------------------------------
    
    def check_tweet_exists(self, tweet_hash: str) -> bool:
        conn = self.connect()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT COUNT(*) FROM tweet_hash WHERE hash = %s
            """, (tweet_hash,))
            count = cur.fetchone()[0]
            return count > 0
        finally:
            cur.close()
            conn.close()
    
    def get_crypto_list(self) -> List[str]:
        conn = self.connect()
        cur = conn.cursor()
        try:
            cur.execute("SELECT symbol,name FROM cryptos")
            cryptos = []
            for row in cur.fetchall():
                cryptos.append(row[0])
                cryptos.append(row[1])
            return cryptos
        finally:
            cur.close()
            conn.close()

    def get_all_crypto_id(self):
        conn = self.connect()
        cur = conn.cursor()
        try:
            cur.execute("SELECT id FROM cryptos")
            crypto_ids = [row[0] for row in cur.fetchall()]
            return crypto_ids
        finally:
            cur.close()
            conn.close()

    def get_sentiments_for_crypto(self, crypto_id: int) -> List[float]:
        conn = self.connect()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT sentiment_score FROM tweet_crypto
                WHERE crypto_id = %s
            """, (crypto_id,))
            sentiments = [row[0] for row in cur.fetchall()]
            return sentiments
        finally:
            cur.close()
            conn.close()

    def get_sentiments_for_crypto_24h(self, crypto_id: int) -> List[float]:
        conn = self.connect()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT tc.sentiment_score 
                FROM tweet_crypto tc
                JOIN tweet_sentiments ts ON tc.tweet_id = ts.tweet_id
                WHERE tc.crypto_id = %s 
                AND ts.timestamp >= EXTRACT(EPOCH FROM (NOW() - INTERVAL '24 hours'))
            """, (crypto_id,))
            sentiments = [row[0] for row in cur.fetchall()]
            return sentiments
        finally:
            cur.close()
            conn.close()

    def get_sentiments_for_crypto_12h(self, crypto_id: int) -> List[float]:
        conn = self.connect()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT tc.sentiment_score 
                FROM tweet_crypto tc
                JOIN tweet_sentiments ts ON tc.tweet_id = ts.tweet_id
                WHERE tc.crypto_id = %s 
                AND ts.timestamp >= EXTRACT(EPOCH FROM (NOW() - INTERVAL '12 hours'))
            """, (crypto_id,))
            sentiments = [row[0] for row in cur.fetchall()]
            return sentiments
        finally:
            cur.close()
            conn.close()
    
    
    def get_crypto_id_by_symbol_or_name(self, symbol_or_name: str) -> int:
        conn = self.connect()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT id FROM cryptos
                WHERE symbol = %s OR name = %s
            """, (symbol_or_name, symbol_or_name))
            result = cur.fetchone()
            if result:
                return result[0]
            else:
                return None
        finally:
            cur.close()
            conn.close()

    def get_all_sentiment_scores(self) -> List[Dict]:
        conn = self.connect()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT crypto_id, score_12h, count_12h, score_24h, count_24h, timestamp
                FROM crypto_sentiment_scores
            """)
            records = []
            for row in cur.fetchall():
                records.append({
                    'crypto_id': row[0],
                    'score_12h': row[1],
                    'count_12h': row[2],
                    'score_24h': row[3],
                    'count_24h': row[4],
                    'timestamp': row[5]
                })
            return records
        finally:
            cur.close()
            conn.close()

    def get_all_accounts(self) -> List[str]:
        conn = self.connect()
        cur = conn.cursor()
        try:
            cur.execute("SELECT account_name FROM account")
            accounts = [row[0] for row in cur.fetchall()]
            return accounts
        except Exception as e:
            self.logger.error(f"Error retrieving accounts: {e}")
            raise
        finally:
            cur.close()
            conn.close()

# ------------------------------------------------------------------------------------
# ------------------- Maintenance Methods -----------------------------
# ------------------------------------------------------------------------------------

    def update_database(self):
        try:
            conn = self.connect()
            cur = conn.cursor()
            seven_days_ago = int((datetime.now().timestamp() - (conf.TWEET_RETENTION_DAYS * 24 * 60 * 60)))
            cur.execute("""
                SELECT tweet_id FROM tweet_sentiments
                WHERE timestamp < %s
            """, (seven_days_ago,))
            old_tweet_ids = [row[0] for row in cur.fetchall()]
            if not old_tweet_ids:
                self.logger.info("No tweets older than 7 days to delete")
                conn.close()
                return
            cur.execute("""
                DELETE FROM tweet_crypto
                WHERE tweet_id = ANY(%s)
            """, (old_tweet_ids,))
            cur.execute("""
                DELETE FROM tweet_sentiments
                WHERE tweet_id = ANY(%s)
            """, (old_tweet_ids,))
            cur.execute("""
                DELETE FROM tweet_hash
                WHERE tweet_id = ANY(%s)
            """, (old_tweet_ids,))
            conn.commit()
            self.logger.info(f"Deleted {len(old_tweet_ids)} tweets older than 7 days")
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Error cleaning old tweets: {e}")
            raise
        finally:
            cur.close()
            conn.close()
