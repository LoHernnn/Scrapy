import requests
import time
import utils.logger as Logger
import conf

class CoinGeckoCollector:
    def __init__(self, base_delay: int = 2):
        self.base_delay = base_delay
        self.logger = Logger.get_logger("CoinGeckoCollector")
    
    def _api_generic(self, url, params=None):
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
        url = "https://api.coingecko.com/api/v3/global"
        response = self._api_generic(url)
        return response
    
    def coin_market_chart_range(self,crypto_id, days=30):
        url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart"
        params = {
            "vs_currency": "usd",
            "days": days,
        }
        response = self._api_generic(url, params)
        return response
    
    def coins_markets(self,cryptos_id):
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
        url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}"
        response = self._api_generic(url)
        return response 
