import pandas as pd
from datetime import datetime, timedelta
import time
from typing import Optional, List, Dict
from scrapy.market.metrics.metrics import *
from scrapy.market.services.crypto_listing_service import CryptoListingService
from scrapy.market.services.coingecko_service import CoingeckoService
from scrapy.core.models.crypto import Crypto
import scrapy.utils.logger as Logger

class TechnicalAnalysisService:
    """Service for calculating and updating technical analysis indicators for cryptocurrencies.
    
    Computes a comprehensive suite of technical indicators including:
    - Volume metrics and variations
    - Price variations across multiple timeframes
    - Moving averages (SMA, EMA)
    - Momentum indicators (RSI, MACD)
    - Support/resistance levels (Pivot Points, Fibonacci)
    - Point of Control (POC) from volume profile
    
    Updates are performed periodically for all tracked cryptocurrencies.
    """
    
    def __init__(self, ListingService, CoingeckoService, refresh_interval_minutes: int = 60 ):
        """Initialize technical analysis service with data providers.
        
        Args:
            ListingService: Crypto listing service instance for accessing crypto registry
            CoingeckoService: CoinGecko service instance for market data
            refresh_interval_minutes (int, optional): Cache refresh interval. Defaults to 60.
        """
        self.CryptoListingService = ListingService
        self.refresh_interval = refresh_interval_minutes
        self.dico_crypto = {}
        self.CoingeckoService = CoingeckoService
        self.logger = Logger.get_logger('TechnicalAnalysisService')

    def _refresh_cache(self):
        """Refresh internal cache (placeholder for future implementation)."""
        dico_crypto = {}
    
    def perform_analysis(self):
        """Perform complete technical analysis for all tracked cryptocurrencies.
        
        For each cryptocurrency:
        1. Fetches 30-day market data from CoinGecko
        2. Calculates technical indicators:
           - Volume metrics (current, 1d, 7d, 30d averages and variations)
           - Price variations (1d, 7d, 14d, 30d with percentages and vs average)
           - Supply metrics (circulating, total, max)
           - Pivot points and support/resistance levels (PP, R1, R2, S1, S2)
           - RSI (Relative Strength Index)
           - MACD (hourly and daily timeframes with signal lines and histograms)
           - Moving averages (SMA 50/200, EMA 50/200)
           - Point of Control (POC)
           - Fibonacci retracement levels (7 levels)
        3. Updates cryptocurrency data dictionary with calculated values
        
        Logs errors for individual cryptocurrencies but continues processing others.
        """
        cryptos_id = list(self.CryptoListingService.dico_crypto.keys()) 
        for crypto_id in cryptos_id:
            data_market = self.CoingeckoService.coin_market_chart_range(crypto_id, 30)
            data_coin = self.CoingeckoService.coins_markets_details(crypto_id)

            volume_variation = volume_data(data_market)
            price_variation = calcul_variation_price(data_market,crypto_id)
            circulating_supply, total_supply, max_supply = get_supply(crypto_id,data_coin)
            PP, R1, R2, S1, S2 = calculer_pivot_support_resistance(crypto_id,data_coin)
            rsi = calcul_rsi(data_market)
            macd_h, signal_line_h, histogram_h = calcul_macd(data_market)
            macd_j, signal_line_j, histogram_j = calcul_macd(data_market, 12*24, 26*24, 9*24)
            df = moving_averages(data_market)
            POC = calculate_poc(data_market)
            fib_levels_1, fib_levels_2, fib_levels_3, fib_levels_4, fib_levels_5, fib_levels_6, fib_levels_7 = fibonacci_levels(data_market)
            try:
                self.CryptoListingService.dico_crypto[crypto_id].update_data('volume_actuel', volume_variation['volume_actuel'])
                self.CryptoListingService.dico_crypto[crypto_id].update_data('volume_1j', volume_variation['volume_1j'])
                self.CryptoListingService.dico_crypto[crypto_id].update_data('volume_7j', volume_variation['volume_7j'])
                self.CryptoListingService.dico_crypto[crypto_id].update_data('volume_30j', volume_variation['volume_30j'])
                self.CryptoListingService.dico_crypto[crypto_id].update_data('variation_1j', volume_variation['variation_1j'])
                self.CryptoListingService.dico_crypto[crypto_id].update_data('variation_7j', volume_variation['variation_7j'])
                self.CryptoListingService.dico_crypto[crypto_id].update_data('variation_30j', volume_variation['variation_30j'])
                self.CryptoListingService.dico_crypto[crypto_id].update_data('volume_moyen_30j', volume_variation['volume_moyen_30j'])
                self.CryptoListingService.dico_crypto[crypto_id].update_data('variation_moyenne_30j', volume_variation['variation_moyenne_30j'])
                self.CryptoListingService.dico_crypto[crypto_id].update_data('volume_moyen_7j', volume_variation['volume_moyen_7j'])
                self.CryptoListingService.dico_crypto[crypto_id].update_data('variation_moyenne_7j', volume_variation['variation_moyenne_7j'])
                self.CryptoListingService.dico_crypto[crypto_id].update_data('volume_moyen_1j', volume_variation['volume_moyen_1j'])
                self.CryptoListingService.dico_crypto[crypto_id].update_data('variation_moyenne_1j', volume_variation['variation_moyenne_1j'])
                self.CryptoListingService.dico_crypto[crypto_id].update_data('current_price', price_variation['current_price'])

                self.CryptoListingService.dico_crypto[crypto_id].update_data('d1_percentage', round(float(price_variation["1d"]["percentage"]), 8))
                self.CryptoListingService.dico_crypto[crypto_id].update_data('d1_value', round(float(price_variation["1d"]["value"]), 8))
                self.CryptoListingService.dico_crypto[crypto_id].update_data('d1_vs_avg', round(float(price_variation["1d"]["vs_avg"]), 8))
                self.CryptoListingService.dico_crypto[crypto_id].update_data('d1_mean', round(float(price_variation["1d"]["mean"]), 8))
                self.CryptoListingService.dico_crypto[crypto_id].update_data('d7_percentage', round(float(price_variation["7d"]["percentage"]), 8))
                self.CryptoListingService.dico_crypto[crypto_id].update_data('d7_value', round(float(price_variation["7d"]["value"]), 8))
                self.CryptoListingService.dico_crypto[crypto_id].update_data('d7_vs_avg', round(float(price_variation["7d"]["vs_avg"]), 8))
                self.CryptoListingService.dico_crypto[crypto_id].update_data('d7_mean', round(float(price_variation["7d"]["mean"]), 8))
                self.CryptoListingService.dico_crypto[crypto_id].update_data('d14_percentage', round(float(price_variation["14d"]["percentage"]), 8))
                self.CryptoListingService.dico_crypto[crypto_id].update_data('d14_value', round(float(price_variation["14d"]["value"]), 8))
                self.CryptoListingService.dico_crypto[crypto_id].update_data('d14_vs_avg', round(float(price_variation["14d"]["vs_avg"]), 8))
                self.CryptoListingService.dico_crypto[crypto_id].update_data('d14_mean', round(float(price_variation["14d"]["mean"]), 8))
                self.CryptoListingService.dico_crypto[crypto_id].update_data('d30_percentage', round(float(price_variation["30d"]["percentage"]), 8))
                self.CryptoListingService.dico_crypto[crypto_id].update_data('d30_value', round(float(price_variation["30d"]["value"]), 8))
                self.CryptoListingService.dico_crypto[crypto_id].update_data('d30_vs_avg', round(float(price_variation["30d"]["vs_avg"]), 8))
                self.CryptoListingService.dico_crypto[crypto_id].update_data('d30_mean', round(float(price_variation["30d"]["mean"]), 8))

                self.CryptoListingService.dico_crypto[crypto_id].update_data('circulating_supply', circulating_supply)
                self.CryptoListingService.dico_crypto[crypto_id].update_data('total_supply', total_supply)
                self.CryptoListingService.dico_crypto[crypto_id].update_data('max_supply', max_supply)

                self.CryptoListingService.dico_crypto[crypto_id].update_data('PP', PP)
                self.CryptoListingService.dico_crypto[crypto_id].update_data('R1', R1)
                self.CryptoListingService.dico_crypto[crypto_id].update_data('R2', R2)
                self.CryptoListingService.dico_crypto[crypto_id].update_data('S1', S1)
                self.CryptoListingService.dico_crypto[crypto_id].update_data('S2', S2)
                self.CryptoListingService.dico_crypto[crypto_id].update_data('rsi_values', rsi.iloc[-1])
                self.CryptoListingService.dico_crypto[crypto_id].update_data('macd_h', macd_h.iloc[-1])
                self.CryptoListingService.dico_crypto[crypto_id].update_data('signal_line_h', signal_line_h.iloc[-1])
                self.CryptoListingService.dico_crypto[crypto_id].update_data('histogram_h', histogram_h.iloc[-1])
                self.CryptoListingService.dico_crypto[crypto_id].update_data('macd_j', macd_j.iloc[-1])
                self.CryptoListingService.dico_crypto[crypto_id].update_data('signal_line_j', signal_line_j.iloc[-1])
                self.CryptoListingService.dico_crypto[crypto_id].update_data('histogram_j', histogram_j.iloc[-1])
                self.CryptoListingService.dico_crypto[crypto_id].update_data('sma_50', df['SMA_50'].iloc[-1])
                self.CryptoListingService.dico_crypto[crypto_id].update_data('sma_200', df['SMA_200'].iloc[-1])
                self.CryptoListingService.dico_crypto[crypto_id].update_data('ema_50', df['EMA_50'].iloc[-1])
                self.CryptoListingService.dico_crypto[crypto_id].update_data('ema_200', df['EMA_200'].iloc[-1])
                self.CryptoListingService.dico_crypto[crypto_id].update_data('POC', POC)
                try:
                    self.CryptoListingService.dico_crypto[crypto_id].update_data('fib_levels_1', fib_levels_1)
                    self.CryptoListingService.dico_crypto[crypto_id].update_data('fib_levels_2', fib_levels_2)
                    self.CryptoListingService.dico_crypto[crypto_id].update_data('fib_levels_3', fib_levels_3)
                    self.CryptoListingService.dico_crypto[crypto_id].update_data('fib_levels_4', fib_levels_4)
                    self.CryptoListingService.dico_crypto[crypto_id].update_data('fib_levels_5', fib_levels_5)
                    self.CryptoListingService.dico_crypto[crypto_id].update_data('fib_levels_6', fib_levels_6)
                    self.CryptoListingService.dico_crypto[crypto_id].update_data('fib_levels_7', fib_levels_7)
                except Exception as e:
                    self.logger.error(f"Error updating Fibonacci levels for {crypto_id}: {e}")

            except Exception as e:
                self.logger.error(f"Error updating technical analysis data for {crypto_id}: {e}")
                continue
