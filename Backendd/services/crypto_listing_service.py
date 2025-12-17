import pandas as pd
from datetime import datetime, timedelta
import time
from typing import Optional, List, Dict
from collectors.coingecko_collector import CoinGeckoCollector
from collectors.binance_collector import BinanceCollector
from models.crypto import Crypto
import utils.logger as Logger

class CryptoListingService:
    def __init__(self, refresh_interval_minutes: int = 60):
        self.CoinGecko = CoinGeckoCollector()
        self.Binance = BinanceCollector()
        self.refresh_interval = refresh_interval_minutes
        self.dico_crypto = {}
        self.logger = Logger.get_logger('CryptoListingService')

    def _refresh_cache(self):
        dico_crypto = {} 

    def _add_crypto_to_cache(self, name: str, symbol: str, id_coingecko: str, rank: int, symbol_binance: str ):
        New_Crypto = Crypto(name, symbol, id_coingecko, rank, symbol_binance)
        self.dico_crypto[id_coingecko] = New_Crypto

    def _uptade_crypto_symbol_binance(self, id_coingecko: str,symbol_binance: str):
        tmp_crypto = self.dico_crypto[id_coingecko]
        tmp_crypto.update_data('symbol_binance', symbol_binance)
    
    def _update_crypto_rank(self, id_coingecko: str,rank: str):
        tmp_crypto = self.dico_crypto[id_coingecko]
        tmp_crypto.update_data('rank', rank)
    
    def add_value_crypto(self, id_coingecko: str, key: str, value):
        tmp_crypto = self.dico_crypto[id_coingecko]
        tmp_crypto.update_data(key, value)

    def add_values_crypto_binance(self, symbol_binance: str, key: str, value):
        for crypto in self.dico_crypto.values():
            if crypto.symbol_binance == symbol_binance:
                crypto.update_data(key, value)
                break
    
    def get_crypto_by_id(self, id_coingecko: str):
        return self.dico_crypto.get(id_coingecko)
    
    def get_all_cryptos(self) -> List[Crypto]:
        return list(self.dico_crypto.values())
    
    def list_all_cryptos(self):
        self.logger.info("Recovery of all cryptocurrencies from CoinGecko...")
        all_coin = self.CoinGecko.top_coin_market()
        all_binance_symbols = self.Binance.get_binance_symbols()
        
        if not all_coin:
            self.logger.critical("Failed to retrieve cryptocurrency data from CoinGecko.")
            return

        for coin in all_coin:
            name = coin["name"]
            symbol = coin["symbol"].upper()
            id_coingecko = coin["id"]
            rank = coin["market_cap_rank"]
            symbol_upper = coin["symbol"].upper()
            symbol_binance = None
            for quote in ["USDT", "BUSD", "BTC"]:
                pair = f"{symbol_upper}{quote}"
                if pair in all_binance_symbols:
                    symbol_binance = pair
                    break
            self._add_crypto_to_cache(name, symbol, id_coingecko, rank, symbol_binance)
    