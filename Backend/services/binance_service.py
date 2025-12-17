import pandas as pd
from datetime import datetime, timedelta
import time
from typing import Optional, List, Dict
from collectors.binance_collector import BinanceCollector
from services.crypto_listing_service import CryptoListingService
from models.crypto import Crypto
import utils.logger as Logger

class BinanceService:
    def __init__(self, ListingService, refresh_interval_minutes: int = 60 ):
        self.binance = BinanceCollector()
        self.CryptoListingService = ListingService
        self.refresh_interval = refresh_interval_minutes
        self.dico_crypto = {}
        self.logger = Logger.get_logger('BinanceService')

    def _refresh_cache(self):
        dico_crypto = {}
    
    def list_data(self):
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
                print(f"IndexError for {crypto.name}: {e}")
                continue
            except Exception as e:
                print(f"Error for {crypto.name}: {e}")
                continue