from scrapy.data.database import CryptoDatabase as DatabaseCryptoBot
import numpy as np
from typing import List, Dict, Any
import scrapy.utils.logger as Logger
import scrapy.config.settings as conf


class CorrelationExposure:
    def __init__(self, max_correlation_exposure: float = None):
        """
        Initialize the correlation exposure control.
        
        Args:
            db_config: Database configuration dictionary
            max_correlation_exposure: Maximum allowed correlation between assets (default 0.7)
        """
        if max_correlation_exposure is None:
            max_correlation_exposure = conf.MAX_CORRELATION_EXPOSURE
        self.db_instance = DatabaseCryptoBot()
        self.max_correlation_exposure = max_correlation_exposure
        self.logger = Logger.get_logger("CorrelationExposure")

    def get_price_history(self, crypto_id: int, days: int = 30) -> List[float]:
        """
        Get historical prices for a cryptocurrency.
        
        Args:
            crypto_id: ID of the cryptocurrency
            days: Number of days of history to retrieve
        Returns:
            List of prices
        """
        prices =self.db_instance.get_historical_prices(crypto_id, days)
        return [entry['price'] for entry in prices]


    def calculate_correlation(self, prices1: List[float], prices2: List[float]) -> float:
        """
        Calculate correlation coefficient between two price series.
        
        Args:
            prices1: First price series
            prices2: Second price series
        Returns:
            Correlation coefficient (-1 to 1)
        """
        if len(prices1) < 2 or len(prices2) < 2:
            return 0.0
        
        if len(prices1) != len(prices2):
            min_len = min(len(prices1), len(prices2))
            prices1 = prices1[-min_len:]
            prices2 = prices2[-min_len:]
        
        try:
            correlation_matrix = np.corrcoef(prices1, prices2)
            return abs(correlation_matrix[0, 1])
        except:
            return 0.0

    def check_correlation_with_current_trades(self, new_crypto_id: int) -> Dict[str, Any]:
        """
        Check correlation between a new crypto and all current trades.
        
        Args:
            new_crypto_id: ID of the cryptocurrency to check
        Returns:
            Dictionary with:
                - can_trade: bool indicating if trade is allowed
                - max_correlation: highest correlation found
                - correlated_cryptos: list of crypto_ids with high correlation
        """
        current_trades = self.db_instance.select_all_trades_current()
        
        if not current_trades:
            return {
                'can_trade': True,
                'max_correlation': 0.0,
                'correlated_cryptos': []
            }
        
        active_crypto_ids = list(set([trade['crypto_id'] for trade in current_trades]))
        
        new_prices = self.get_price_history(new_crypto_id)
        
        if not new_prices:
            return {
                'can_trade': True,
                'max_correlation': 0.0,
                'correlated_cryptos': []
            }
        
        max_correlation = 0.0
        correlated_cryptos: List[Dict[str, Any]] = []
        
        for active_crypto_id in active_crypto_ids:
            if active_crypto_id == new_crypto_id:
                continue
                
            active_prices = self.get_price_history(active_crypto_id)
            
            if active_prices:
                correlation = self.calculate_correlation(new_prices, active_prices)
                
                if correlation > max_correlation:
                    max_correlation = correlation
                
                if correlation >= self.max_correlation_exposure:
                    correlated_cryptos.append({
                        'crypto_id': active_crypto_id,
                        'correlation': correlation
                    })
        
        can_trade = max_correlation < self.max_correlation_exposure
        
        if not can_trade:
            self.logger.warning(f"Crypto {new_crypto_id}: Correlation too high ({max_correlation:.2f} >= {self.max_correlation_exposure:.2f}) with {len(correlated_cryptos)} cryptos")
        else:
            self.logger.debug(f"Crypto {new_crypto_id}: Max correlation {max_correlation:.2f} (limit: {self.max_correlation_exposure:.2f})")
        
        return {
            'can_trade': can_trade,
            'max_correlation': max_correlation,
            'correlated_cryptos': correlated_cryptos
        }
    
    def update_max_correlation_exposure(self, new_limit: float):
        """
        Update the maximum allowed correlation exposure.
        
        Args:
            new_limit: New maximum correlation value
        """
        self.max_correlation_exposure = new_limit
