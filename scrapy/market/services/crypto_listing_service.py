import pandas as pd
from datetime import datetime, timedelta
import time
from typing import Optional, List, Dict
from scrapy.market.collectors.coingecko_collector import CoinGeckoCollector
from scrapy.market.collectors.binance_collector import BinanceCollector
from scrapy.core.models.crypto import Crypto
import scrapy.utils.logger as Logger

class CryptoListingService:
    """Service for managing cryptocurrency listings and data aggregation.
    
    Maintains a registry of tracked cryptocurrencies with data from CoinGecko
    and Binance. Handles cryptocurrency discovery, symbol mapping, and
    data updates across multiple exchanges.
    """
    
    def __init__(self, refresh_interval_minutes: int = 60):
        """Initialize crypto listing service with data collectors.
        
        Args:
            refresh_interval_minutes (int, optional): Cache refresh interval. Defaults to 60.
        """
        self.CoinGecko = CoinGeckoCollector()
        self.Binance = BinanceCollector()
        self.refresh_interval = refresh_interval_minutes
        self.dico_crypto = {}
        self.logger = Logger.get_logger('CryptoListingService')

    def _refresh_cache(self):
        """Refresh internal cache (placeholder for future implementation)."""
        dico_crypto = {} 

    def _add_crypto_to_cache(self, name: str, symbol: str, id_coingecko: str, rank: int, symbol_binance: str ):
        """Add a new cryptocurrency to the internal cache.
        
        Args:
            name (str): Full name of the cryptocurrency
            symbol (str): Trading symbol/ticker
            id_coingecko (str): CoinGecko unique identifier
            rank (int): Market cap ranking
            symbol_binance (str): Binance trading pair symbol (e.g., 'BTCUSDT')
        """
        New_Crypto = Crypto(name, symbol, id_coingecko, rank, symbol_binance)
        self.dico_crypto[id_coingecko] = New_Crypto

    def _uptade_crypto_symbol_binance(self, id_coingecko: str,symbol_binance: str):
        """Update Binance symbol for a cached cryptocurrency.
        
        Args:
            id_coingecko (str): CoinGecko ID of the cryptocurrency
            symbol_binance (str): New Binance trading pair symbol
        """
        tmp_crypto = self.dico_crypto[id_coingecko]
        tmp_crypto.update_data('symbol_binance', symbol_binance)
    
    def _update_crypto_rank(self, id_coingecko: str,rank: str):
        """Update market cap rank for a cached cryptocurrency.
        
        Args:
            id_coingecko (str): CoinGecko ID of the cryptocurrency
            rank (str): New market cap ranking
        """
        tmp_crypto = self.dico_crypto[id_coingecko]
        tmp_crypto.update_data('rank', rank)
    
    def add_value_crypto(self, id_coingecko: str, key: str, value):
        """Update a data field for a cryptocurrency identified by CoinGecko ID.
        
        Args:
            id_coingecko (str): CoinGecko ID of the cryptocurrency
            key (str): Data field name to update
            value: New value for the field
        """
        tmp_crypto = self.dico_crypto[id_coingecko]
        tmp_crypto.update_data(key, value)

    def add_values_crypto_binance(self, symbol_binance: str, key: str, value):
        """Update a data field for a cryptocurrency identified by Binance symbol.
        
        Searches for cryptocurrency by Binance trading pair and updates the specified field.
        
        Args:
            symbol_binance (str): Binance trading pair symbol (e.g., 'BTCUSDT')
            key (str): Data field name to update
            value: New value for the field
        """
        for crypto in self.dico_crypto.values():
            if crypto.symbol_binance == symbol_binance:
                crypto.update_data(key, value)
                break
    
    def get_crypto_by_id(self, id_coingecko: str):
        """Retrieve a cryptocurrency object by its CoinGecko ID.
        
        Args:
            id_coingecko (str): CoinGecko ID of the cryptocurrency
            
        Returns:
            Crypto: Cryptocurrency object, or None if not found
        """
        return self.dico_crypto.get(id_coingecko)
    
    def get_all_cryptos(self) -> List[Crypto]:
        """Retrieve all cached cryptocurrency objects.
        
        Returns:
            List[Crypto]: List of all tracked cryptocurrency objects
        """
        return list(self.dico_crypto.values())
    
    def list_all_cryptos(self):
        """Fetch and cache top cryptocurrencies from CoinGecko and Binance.
        
        Retrieves top cryptocurrencies by market cap from CoinGecko, then attempts
        to match each with available Binance trading pairs (USDT, BUSD, or BTC quotes).
        Populates the internal cache with discovered cryptocurrencies.
        """
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
    