import requests
import time
import scrapy.utils.logger as Logger
import scrapy.config.settings as conf

class CoinGeckoCollector:
    """Collector for fetching cryptocurrency market data from CoinGecko API.
    
    Handles API requests with automatic rate limiting, retry logic, and backoff
    for 429 (rate limit exceeded) responses.
    """
    
    def __init__(self):
        """Initialize the CoinGecko API collector.
        
        Args:
            base_delay (int, optional): Delay in seconds between API requests. 
                Defaults to None, which uses conf.API_BASE_DELAY.
        """
        self.base_delay = conf.API_BASE_DELAY
        self.logger = Logger.get_logger("CoinGeckoCollector")
    
    def _api_generic(self, url, params=None):
        """Generic API request handler with rate limit handling and retry logic.
        
        Automatically retries requests when encountering 429 (rate limit) errors
        with exponential backoff. Logs warnings and errors appropriately.
        
        Args:
            url (str): API endpoint URL
            params (dict, optional): Query parameters for the request. Defaults to None.
            
        Returns:
            dict: JSON response data, or None if request fails with non-429 error
        """
        response = requests.get(url, params=params)
        time.sleep(self.base_delay) 
        while response.status_code != 200:
            if response.status_code == 429:
                self.logger.warning(f"CoinGecko Rate limit exceeded. Waiting before retrying : {response.status_code} ...")
                time.sleep(conf.API_BACKOFF_DELAY)
                response = requests.get(url, params=params)
            else: 
                self.logger.error(f"Error with CoinGecko API: {response.status_code}")
                return None
        return response.json()
    
    def top_coin_market(self):
        """Fetch top cryptocurrencies by market cap from CoinGecko.
        
        Retrieves multiple pages of cryptocurrency data ordered by market capitalization.
        Number of items per page and total pages fetched are controlled by configuration.
        
        Returns:
            list: List of cryptocurrency market data dictionaries from all fetched pages
        """
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": conf.NUMBER_OF_CRTYPTO_PER_REQUEST,
        }
        all_cryptos = []
        for page in range(1,conf.NUMBER_OF_PAGES_TO_FETCH + 1):
            params["page"] = page
            response = requests.get(url, params=params)
            time.sleep(2)
            response = self._api_generic(url, params)
            all_cryptos.extend(response)
        return all_cryptos
    
    def get_global_crypto_data(self):
        """Fetch global cryptocurrency market statistics.
        
        Retrieves aggregated market data including total market cap, volume,
        market dominance percentages, and other global metrics.
        
        Returns:
            dict: Global cryptocurrency market data
        """
        url = "https://api.coingecko.com/api/v3/global"
        response = self._api_generic(url)
        return response
    
    def coin_market_chart_range(self,crypto_id, days=30):
        """Fetch historical market chart data for a specific cryptocurrency.
        
        Retrieves price, market cap, and volume data over the specified time range.
        
        Args:
            crypto_id (str): CoinGecko cryptocurrency identifier (e.g., 'bitcoin')
            days (int, optional): Number of days of historical data. Defaults to 30.
            
        Returns:
            dict: Market chart data containing prices, market_caps, and total_volumes arrays
        """
        url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart"
        params = {
            "vs_currency": "usd",
            "days": days,
        }
        response = self._api_generic(url, params)
        return response
    
    def coins_markets(self,cryptos_id):
        """Fetch market data for multiple specific cryptocurrencies.
        
        Retrieves current market metrics including prices, volumes, and 7-day price changes
        for a list of cryptocurrency IDs.
        
        Args:
            cryptos_id (list): List of CoinGecko cryptocurrency identifiers
            
        Returns:
            list: List of market data dictionaries for the requested cryptocurrencies
        """
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "ids": ",".join(cryptos_id),
            "price_change_percentage": "7d",
            "per_page": 250,
            "page": 1
        }
        response = self._api_generic(url, params)
        return response
    
    def coins_markets_details(self,crypto_id):
        """Fetch detailed information for a specific cryptocurrency.
        
        Retrieves comprehensive data including market metrics, supply information,
        ATH/ATL data, community stats, and developer activity.
        
        Args:
            crypto_id (str): CoinGecko cryptocurrency identifier (e.g., 'bitcoin')
            
        Returns:
            dict: Detailed cryptocurrency data including market_data, community_data, and more
        """
        url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}"
        response = self._api_generic(url)
        return response 
