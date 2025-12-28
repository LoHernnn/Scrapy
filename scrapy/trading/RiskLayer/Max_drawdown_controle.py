from scrapy.data.database import CryptoDatabase as DatabaseCryptoBot
from typing import Dict, Any, Optional
import scrapy.utils.logger as Logger
import scrapy.config.settings as conf


class MaxDrawdownControl:
    """Monitor and control maximum drawdown to prevent catastrophic losses.
    
    Tracks peak capital and calculates current drawdown percentage. Prevents trading
    when drawdown exceeds configured threshold, protecting capital from excessive losses.
    """
    
    def __init__(self, initial_capital: float = None, max_drawdown_percent: float = None):
        """Initialize the max drawdown control.
        
        Args:
            initial_capital (float, optional): Starting capital amount. Defaults to conf.INITIAL_CAPITAL.
            max_drawdown_percent (float, optional): Maximum allowed drawdown in percentage (e.g., 20 for 20%). Defaults to conf.MAX_DRAWDOWN_PERCENT.
        """
        if initial_capital is None:
            initial_capital = conf.INITIAL_CAPITAL
        if max_drawdown_percent is None:
            max_drawdown_percent = conf.MAX_DRAWDOWN_PERCENT
        
        self.db_instance = DatabaseCryptoBot()
        self.initial_capital = initial_capital
        self.max_drawdown_percent = max_drawdown_percent
        self.peak_capital = initial_capital
        self.logger = Logger.get_logger("MaxDrawdownControl")

    def calculate_drawdown(self, current_capital ) -> Dict[str, Any]:
        """Calculate current drawdown from peak and check if limit is exceeded.
        
        Updates peak capital if current capital is higher, then calculates drawdown
        percentage from peak. Logs warnings when maximum drawdown threshold is exceeded.
        
        Args:
            current_capital (float): Current total portfolio capital
        
        Returns:
            bool: True if max drawdown exceeded, False otherwise
        """
        
        if current_capital > self.peak_capital:
            self.peak_capital = current_capital
        
        drawdown_amount = self.peak_capital - current_capital
        drawdown_percent = (drawdown_amount / self.peak_capital) * 100 if self.peak_capital > 0 else 0
        
        exceeded = drawdown_percent >= self.max_drawdown_percent
        if exceeded:
            self.logger.warning(f"Max drawdown EXCEEDED: {drawdown_percent:.2f}% (limit: {self.max_drawdown_percent:.2f}%)")
        else:
            self.logger.debug(f"Drawdown: {drawdown_percent:.2f}% (peak: {self.peak_capital:.2f}, current: {current_capital:.2f})")
        
        return exceeded

    def reset_peak(self):
        """Manually reset the peak capital to initial capital.
        
        Use this to restart drawdown tracking, typically at the beginning
        of a new trading period or after recovering from a drawdown.
        """
        self.peak_capital = self.initial_capital

    def update_max_drawdown(self, new_limit: float):
        """
        Update the maximum drawdown percentage limit.
        
        Args:
            new_limit: New maximum drawdown percentage
        """
        self.max_drawdown_percent = new_limit
