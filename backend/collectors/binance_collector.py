import requests
import time
import utils.logger as Logger
import conf

class BinanceCollector:
    def __init__(self, base_delay=2):
        self.base_delay = base_delay
        self.logger = Logger.get_logger("BinanceCollector")
    
    def _api_generic(self, url, params=None):
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
        url = f"https://api.binance.com/api/v3/depth"
        params = {"symbol": symbol, "limit": 3}
        response = self._api_generic(url, params)
        if response is None:
            return None, None
        bids = response["bids"] 
        asks = response["asks"] 
        return bids, asks

    def get_funding_rate(self,crypto_id):
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
        url = "https://fapi.binance.com/fapi/v1/openInterest"
        params = {"symbol": symbol}
        response = self._api_generic(url, params)
        if response is None:
            return None
        if "openInterest" in response:
            open_interest = float(response["openInterest"])
            return open_interest
        return None