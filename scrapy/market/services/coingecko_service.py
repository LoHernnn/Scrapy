import pandas as pd
from datetime import datetime, timedelta
import time
from typing import Optional, List, Dict

from scrapy.market.collectors.coingecko_collector import CoinGeckoCollector
from scrapy.market.services.crypto_listing_service import CryptoListingService
from scrapy.core.models.crypto import Crypto
import scrapy.utils.logger as Logger


class CoingeckoService:
    """Service for fetching and managing cryptocurrency data from CoinGecko API.
    
    Provides methods to retrieve market data, historical charts, and detailed
    cryptocurrency information from CoinGecko. Updates the crypto listing
    service with fresh market data including prices, volumes, and market caps.
    """
    
    def __init__(self, ListingService, refresh_interval_minutes: int = 60 ):
        """Initialize CoinGecko service with data collector and listing service.
        
        Args:
            ListingService: Crypto listing service instance to update with fetched data
            refresh_interval_minutes (int, optional): Cache refresh interval. Defaults to 60.
        """
        self.CoinGecko = CoinGeckoCollector()
        self.CryptoListingService = ListingService
        self.refresh_interval = refresh_interval_minutes
        self.dico_crypto = {}
        self.logger = Logger.get_logger('CoingeckoService')

    def _refresh_cache(self):
        """Refresh internal cache (placeholder for future implementation)."""
        self.dico_crypto = {}
    
    def coin_market_chart_range(self,crypto_id, nb):
        """Fetch historical market chart data for a cryptocurrency.
        
        Args:
            crypto_id (str): CoinGecko ID of the cryptocurrency
            nb (int): Number of days of historical data to retrieve
            
        Returns:
            Historical market data including prices, volumes, and market caps
        """
        return self.CoinGecko.coin_market_chart_range(crypto_id, nb)
    
    def coins_markets_details(self,crypto_id):
        """Fetch detailed market information for a specific cryptocurrency.
        
        Args:
            crypto_id (str): CoinGecko ID of the cryptocurrency
            
        Returns:
            Detailed market data including supply metrics and price levels
        """
        return self.CoinGecko.coins_markets_details(crypto_id)
    
    def list_data(self):
        """Fetch and update market data for all tracked cryptocurrencies.
        
        Retrieves current market data from CoinGecko API in batches (max 249 per request)
        to respect API limits. Updates the listing service cache with:
        - Current price and 24h high/low
        - Price and market cap changes (24h)
        - Trading volume and market cap
        - All-time high/low data with dates
        - Fully diluted valuation
        - Last update timestamp
        
        Logs warnings for cryptocurrencies without available data.
        """
        batch_size = 249 
        crypto_data = []
        cryptos_id = list(self.CryptoListingService.dico_crypto.keys()) 
        for i in range(0, len(cryptos_id), batch_size):
            batch = cryptos_id[i:i + batch_size] 
            crypto_data_nonExtend = self.CoinGecko.coins_markets(batch)
            crypto_data.extend(crypto_data_nonExtend)
        for crypto_id in cryptos_id:
            self.logger.info(f"Updating Coingecko data for cryptocurrency ID: {crypto_id}")
            data_crypto_gene = next((crypto for crypto in crypto_data if crypto["id"] == crypto_id), None)
            if data_crypto_gene:
                self.CryptoListingService.dico_crypto[crypto_id].update_data('current_price',data_crypto_gene.get('current_price'))
                self.CryptoListingService.dico_crypto[crypto_id].update_data('high_24h',data_crypto_gene.get('high_24h'))
                self.CryptoListingService.dico_crypto[crypto_id].update_data('low_24h',data_crypto_gene.get('low_24h'))
                self.CryptoListingService.dico_crypto[crypto_id].update_data('price_change_24h',data_crypto_gene.get('price_change_24h'))
                self.CryptoListingService.dico_crypto[crypto_id].update_data('price_change_24h_pct',data_crypto_gene.get('price_change_percentage_24h'))
                self.CryptoListingService.dico_crypto[crypto_id].update_data('market_change_24h_pct',data_crypto_gene.get('market_cap_change_percentage_24h'))
                self.CryptoListingService.dico_crypto[crypto_id].update_data('market_change_24h',data_crypto_gene.get('market_cap_change_24h'))
                self.CryptoListingService.dico_crypto[crypto_id].update_data('market_cap',data_crypto_gene.get('market_cap'))
                self.CryptoListingService.dico_crypto[crypto_id].update_data('total_volume',data_crypto_gene.get('total_volume'))
                self.CryptoListingService.dico_crypto[crypto_id].update_data('fully_diluted_valuation',data_crypto_gene.get('fully_diluted_valuation'))
                self.CryptoListingService.dico_crypto[crypto_id].update_data('ath',data_crypto_gene.get('ath'))
                self.CryptoListingService.dico_crypto[crypto_id].update_data('ath_date',data_crypto_gene.get('ath_date'))
                self.CryptoListingService.dico_crypto[crypto_id].update_data('ath_change_percentage',data_crypto_gene.get('ath_change_percentage'))
                self.CryptoListingService.dico_crypto[crypto_id].update_data('atl',data_crypto_gene.get('atl'))
                self.CryptoListingService.dico_crypto[crypto_id].update_data('atl_date',data_crypto_gene.get('atl_date'))
                self.CryptoListingService.dico_crypto[crypto_id].update_data('atl_change_percentage',data_crypto_gene.get('atl_change_percentage'))
                self.CryptoListingService.dico_crypto[crypto_id].update_data('last_updated',data_crypto_gene.get('last_updated'))
            else:
                self.logger.warning(f"No data found for cryptocurrency ID: {crypto_id}")