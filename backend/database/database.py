import psycopg2
import numpy as np
from pprint import pprint
from typing import List, Dict, Any, Optional
import utils.logger as Logger
import conf

class CryptoDatabase:
    def __init__(self):
        self.logger = Logger.get_logger("CryptoDatabase")
        self.conn, self.cur = self.connect()

    def connect(self):
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
        """Close database connection."""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
        self.logger.info("Database connection closed.")

    def create_table_listing(self):
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
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS crypto_ranks (
            id SERIAL PRIMARY KEY,
            crypto_id INTEGER NOT NULL UNIQUE REFERENCES cryptos(id) ON DELETE CASCADE,
            rank INTEGER NOT NULL
        );
        """)
        self.conn.commit()


    def create_table_base(self):
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


    def insert_crypto(self, name, symbol, id_coingecko, symbol_binance):
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
            self.logger.error(f" Erreur lors de l'insertion/maj du rank (crypto_id={crypto_id}): {e}")

    def insert_cyptos_base(self, crypto_id, data):
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
            self.logger.error(f" Erreur lors de l'insertion dans cyptos_data_base (crypto_id={crypto_id}): {e}")


    def insert_cyptos_data_details(self, crypto_id, data):
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
            self.logger.error(f" Erreur lors de l'insertion dans cyptos_data_details (crypto_id={crypto_id}): {e}")



    def insert_cyptos_data_binance(self, crypto_id, data):
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
            self.logger.error(f" Erreur lors de l'insertion dans cyptos_data_binance (crypto_id={crypto_id}): {e}")

    def drop_tables(self):
        tables = ['cyptos_data_binance', 'cyptos_data_details', 'cyptos_data_base', 'crypto_ranks', 'cryptos']
        for table in tables:
            self.cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
            self.conn.commit()



    def _rows_to_dicts(self, rows) -> List[Dict[str, Any]]:
        """Convert cursor rows to list of dicts using cursor.description for keys."""
        if rows is None:
            return []
        colnames = [desc[0] for desc in self.cur.description]
        return [dict(zip(colnames, row)) for row in rows]


    def select_latest_data(self, verbose: bool = True) -> Dict[str, List[Dict[str, Any]]]:
        """Select the most recently recorded rows from the main data tables.

        This function finds the latest timestamp present in each of the
        tables `cyptos_data_base`, `cyptos_data_details` and `cyptos_data_binance`
        and selects all rows that have that timestamp. It returns a dict with
        the results for each table and prints them when `verbose` is True.

        Returns:
            {
                'base': [ {row dict}, ... ],
                'details': [ ... ],
                'binance': [ ... ]
            }
        """

        result = {"base": [], "details": [], "binance": []}

        try:
            self.cur.execute("SELECT MAX(timestamp) FROM cyptos_data_base;")
            latest_base_ts = self.cur.fetchone()[0]
            if latest_base_ts:
                self.cur.execute(
                    """
                    SELECT c.id as crypto_id, c.name, c.symbol, b.*
                    FROM cyptos_data_base b
                    JOIN cryptos c ON b.crypto_id = c.id
                    WHERE b.timestamp = %s
                    ORDER BY c.id;
                    """,
                    (latest_base_ts,)
                )
                rows = self.cur.fetchall()
                result["base"] = self._rows_to_dicts(rows)

            self.cur.execute("SELECT MAX(timestamp) FROM cyptos_data_details;")
            latest_details_ts = self.cur.fetchone()[0]
            if latest_details_ts:
                self.cur.execute(
                    """
                    SELECT c.id as crypto_id, c.name, c.symbol, d.*
                    FROM cyptos_data_details d
                    JOIN cryptos c ON d.crypto_id = c.id
                    WHERE d.timestamp = %s
                    ORDER BY c.id;
                    """,
                    (latest_details_ts,)
                )
                rows = self.cur.fetchall()
                result["details"] = self._rows_to_dicts(rows)

            self.cur.execute("SELECT MAX(timestamp) FROM cyptos_data_binance;")
            latest_binance_ts = self.cur.fetchone()[0]
            if latest_binance_ts:
                self.cur.execute(
                    """
                    SELECT c.id as crypto_id, c.name, c.symbol, bb.*
                    FROM cyptos_data_binance bb
                    JOIN cryptos c ON bb.crypto_id = c.id
                    WHERE bb.timestamp = %s
                    ORDER BY c.id;
                    """,
                    (latest_binance_ts,)
                )
                rows = self.cur.fetchall()
                result["binance"] = self._rows_to_dicts(rows)

            if verbose:
                print("\n=== Latest data summary ===")
                print(f"cyptos_data_base: {len(result['base'])} rows (timestamp={latest_base_ts})")
                print(f"cyptos_data_details: {len(result['details'])} rows (timestamp={latest_details_ts})")
                print(f"cyptos_data_binance: {len(result['binance'])} rows (timestamp={latest_binance_ts})")
                print("\n-- Sample rows (first 3 for each table) --")
                if result["base"]:
                    print("\n[base]")
                    pprint(result["base"][:3])
                if result["details"]:
                    print("\n[details]")
                    pprint(result["details"][:3])
                if result["binance"]:
                    print("\n[binance]")
                    pprint(result["binance"][:3])

            return result

        except Exception as e:
            print("Erreur lors de la sélection des dernières données:", e)
            return result