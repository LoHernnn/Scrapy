import requests
import time
import scrapy.utils.logger as Logger
import scrapy.config.settings as conf

class BinanceCollector:
    """Collector for fetching cryptocurrency trading data from Binance API.
    
    Handles API requests with automatic rate limiting, retry logic, and backoff
    for 429 (rate limit exceeded) responses. Supports both spot and futures endpoints.
    """
    
    def __init__(self):
        """Initialize the Binance API collector.
        
        Args:
            base_delay (int, optional): Delay in seconds between API requests. 
                Defaults to None, which uses conf.API_BASE_DELAY.
        """
        self.base_delay = conf.API_BASE_DELAY
        self.logger = Logger.get_logger("BinanceCollector")
    
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
                self.logger.warning(f"Binance Rate limit exceeded. Waiting before retrying : {response.status_code} ...")
                time.sleep(conf.API_BACKOFF_DELAY)
                response = requests.get(url, params=params)
            else: 
                self.logger.error(f"Error with Binance API: {response.status_code}")
                return None
        return response.json()
    
    def get_binance_symbols(self) -> str:
        """Fetch all available trading symbols from Binance exchange.
        
        Retrieves the complete list of trading pairs available on Binance spot market.
        
        Returns:
            set: Set of symbol strings (e.g., 'BTCUSDT', 'ETHUSDT'), or empty set if request fails
        """
        binance_url = "https://api.binance.com/api/v3/exchangeInfo"
        binance_response = self._api_generic(binance_url)
        if binance_response is None:
            return set()
        binance_symbols = set(
            symbol_data["symbol"] 
            for symbol_data in binance_response.get("symbols", [])
        )
        return binance_symbols
    
    def get_depth(self,symbol):
        """Fetch order book depth data for a specific trading symbol.
        
        Retrieves the top 3 bid and ask levels from the order book.
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
            
        Returns:
            tuple: (bids, asks) where each is a list of [price, quantity] pairs,
                or (None, None) if request fails
        """
        url = f"https://api.binance.com/api/v3/depth"
        params = {"symbol": symbol, "limit": 3}
        response = self._api_generic(url, params)
        if response is None:
            return None, None
        bids = response["bids"] 
        asks = response["asks"] 
        return bids, asks

    def get_funding_rate(self,crypto_id):
        """Fetch current funding rate for a futures contract.
        
        Retrieves the most recent funding rate from Binance Futures API and converts
        it to percentage format.
        
        Args:
            crypto_id (str): Futures contract symbol (e.g., 'BTCUSDT')
            
        Returns:
            float: Funding rate as percentage, or None if request fails or data unavailable
        """
        url = f"https://fapi.binance.com/fapi/v1/fundingRate?symbol={crypto_id}&limit=1"
        response = self._api_generic(url)
        if response is None:
            return None
        try:
            funding_rate = float(response[0]["fundingRate"]) * 100
            return funding_rate
        except (IndexError, ValueError):
            return None
        return None

    def get_open_interest(self,symbol):
        """Fetch current open interest for a futures contract.
        
        Retrieves the total number of outstanding derivative contracts from
        Binance Futures API.
        
        Args:
            symbol (str): Futures contract symbol (e.g., 'BTCUSDT')
            
        Returns:
            float: Open interest value, or None if request fails or data unavailable
        """
        url = "https://fapi.binance.com/fapi/v1/openInterest"
        params = {"symbol": symbol}
        response = self._api_generic(url, params)
        if response is None:
            return None
        if "openInterest" in response:
            open_interest = float(response["openInterest"])
            return open_interest
        return None