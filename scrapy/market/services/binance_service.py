import pandas as pd
from datetime import datetime, timedelta
import time
from typing import Optional, List, Dict

from scrapy.market.collectors.binance_collector import BinanceCollector
from scrapy.market.services.crypto_listing_service import CryptoListingService
from scrapy.core.models.crypto import Crypto
import scrapy.utils.logger as Logger

class BinanceService:
    """Service for fetching and managing cryptocurrency data from Binance exchange.
    
    Provides methods to retrieve order book depth, funding rates, and open interest
    data from Binance. Updates the crypto listing service with real-time trading data.
    """
    
    def __init__(self, ListingService, refresh_interval_minutes: int = 60 ):
        """Initialize Binance service with data collector and listing service.
        
        Args:
            ListingService: Crypto listing service instance to update with fetched data
            refresh_interval_minutes (int, optional): Cache refresh interval. Defaults to 60.
        """
        self.binance = BinanceCollector()
        self.CryptoListingService = ListingService
        self.refresh_interval = refresh_interval_minutes
        self.dico_crypto = {}
        self.logger = Logger.get_logger('BinanceService')

    def _refresh_cache(self):
        """Clear the internal cache dictionary."""
        self.dico_crypto = {}
    
    def list_data(self):
        """Fetch and update Binance trading data for all tracked cryptocurrencies.
        
        For each cryptocurrency with a valid Binance symbol, retrieves:
        - Order book depth (top 3 bid/ask levels with prices and quantities)
        - Funding rate (for perpetual futures)
        - Open interest (total outstanding contracts)
        
        Updates the listing service cache with 14 data points per crypto:
        - 6 bid levels (3 prices + 3 quantities)
        - 6 ask levels (3 prices + 3 quantities)
        - Funding rate
        - Open interest
        
        Skips cryptocurrencies without Binance symbols and logs warnings/errors
        for failed data retrieval.
        """
        for crypto_id, crypto in self.CryptoListingService.dico_crypto.items():
            symbol_binance = crypto.symbol_binance
            if symbol_binance is None:
                self.logger.warning(f"No Binance symbol for {crypto.name} ({crypto_id})")
                continue
            self.logger.info(f"Treatment of {crypto.name} - Symbol Binance: {symbol_binance}")
            try:
                bids, asks = self.binance.get_depth(symbol_binance)
                funding_rate = self.binance.get_funding_rate(symbol_binance)
                open_interest = self.binance.get_open_interest(symbol_binance)
                self.CryptoListingService.dico_crypto[crypto_id].update_data('bids_price_1', bids[0][0])
                self.CryptoListingService.dico_crypto[crypto_id].update_data('bids_quantity_1', bids[0][1])
                self.CryptoListingService.dico_crypto[crypto_id].update_data('bids_price_2', bids[1][0])
                self.CryptoListingService.dico_crypto[crypto_id].update_data('bids_quantity_2', bids[1][1])
                self.CryptoListingService.dico_crypto[crypto_id].update_data('bids_price_3', bids[2][0])
                self.CryptoListingService.dico_crypto[crypto_id].update_data('bids_quantity_3', bids[2][1])
                self.CryptoListingService.dico_crypto[crypto_id].update_data('asks_price_1', asks[0][0])
                self.CryptoListingService.dico_crypto[crypto_id].update_data('asks_quantity_1', asks[0][1])
                self.CryptoListingService.dico_crypto[crypto_id].update_data('asks_price_2', asks[1][0])
                self.CryptoListingService.dico_crypto[crypto_id].update_data('asks_quantity_2', asks[1][1])
                self.CryptoListingService.dico_crypto[crypto_id].update_data('asks_price_3', asks[2][0])
                self.CryptoListingService.dico_crypto[crypto_id].update_data('asks_quantity_3', asks[2][1])
                self.CryptoListingService.dico_crypto[crypto_id].update_data('funding_rate', funding_rate)
                self.CryptoListingService.dico_crypto[crypto_id].update_data('open_interest', open_interest)
            except IndexError as e:
                self.logger.warning(f"IndexError for {crypto.name}: {e}")
                continue
            except Exception as e:
                self.logger.error(f"Error processing {crypto.name}: {e}")
                continue