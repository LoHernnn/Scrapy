from scrapy.data.database import CryptoDatabase as DatabaseCryptoBot
from datetime import datetime, timedelta
from typing import Dict, Any
import scrapy.utils.logger as Logger
import scrapy.config.settings as conf


class DailyLossLimit:
    """Enforce daily loss limits to prevent excessive losses in a single trading day.
    
    Monitors cumulative losses throughout the day and blocks new trades when
    daily loss threshold is exceeded. Can use percentage-based or absolute loss limits.
    """
    
    def __init__(self, max_daily_loss_percent: float = None, max_daily_loss: float = None, initial_capital: float = None):
        """Initialize the daily loss limit control.
        
        Args:
            max_daily_loss_percent (float, optional): Maximum allowed loss as percentage of initial capital (e.g., 2.0 for 2%). Defaults to conf.MAX_DAILY_LOSS_PERCENT.
            max_daily_loss (float, optional): Maximum allowed loss in absolute value (e.g., 200 for $200 max loss). Defaults to None.
            initial_capital (float, optional): Initial capital for percentage calculation. Defaults to conf.INITIAL_CAPITAL.
        """
        if initial_capital is None:
            initial_capital = conf.INITIAL_CAPITAL
        if max_daily_loss_percent is None:
            max_daily_loss_percent = conf.MAX_DAILY_LOSS_PERCENT
        self.db_instance = DatabaseCryptoBot()
        self.initial_capital = initial_capital
        self.logger = Logger.get_logger("DailyLossLimit")
        
        if max_daily_loss_percent is not None:
            self.max_daily_loss = (max_daily_loss_percent / 100.0) * initial_capital
        elif max_daily_loss is not None:
            self.max_daily_loss = max_daily_loss
        else:
            self.max_daily_loss = 0.02 * initial_capital  # Default 2%
        
        self.daily_loss_cache = {} 

    def calculate_trade_pnl(self, trade: Dict[str, Any]) -> float:
        """Calculate the PnL (profit/loss) for a single trade.
        
        Computes unrealized profit/loss by comparing entry price with current market price,
        accounting for position direction (long/short) and position size.
        
        Args:
            trade (Dict[str, Any]): Dictionary containing trade information (entry_price, position_size, direction, crypto_id)
            
        Returns:
            float: PnL value (negative for loss, positive for profit)
        """
        entry_price = float(trade['entry_price'])
        position_size = float(trade['position_size'])
        direction = trade['direction']
        
        current_price = self.db_instance.get_last_crypto_price(trade['crypto_id'])
        
        if current_price is None:
            return 0.0
        
        current_price = float(current_price)
        
        if direction == 1:
            pnl = (current_price - entry_price) * position_size
        else:
            pnl = (entry_price - current_price) * position_size
        
        return pnl

    def get_daily_loss(self) -> float:
        """Calculate total loss for today from all open trades.
        
        Aggregates unrealized losses from all current open positions. Uses caching
        to avoid recalculating on every check. Only counts negative PnL (losses).
        
        Returns:
            float: Total daily loss (negative value represents losses)
        """
        today = datetime.now().date()
        
        if today in self.daily_loss_cache:
            return self.daily_loss_cache[today]
        
        total_pnl = 0.0
        
        current_trades = self.db_instance.select_all_trades_current()
        
        for trade in current_trades:
            pnl = self.calculate_trade_pnl(trade)
            if pnl < 0:
                total_pnl += pnl
        
        self.daily_loss_cache[today] = total_pnl
        
        return total_pnl

    def can_trade(self) -> Dict[str, Any]:
        """Check if trading is allowed based on daily loss limit.
        
        Evaluates current daily losses against configured threshold and determines
        if new trades can be opened. Provides detailed breakdown of loss status.
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - can_trade (bool): Whether new trades are allowed
                - current_loss (float): Current daily loss amount
                - remaining_allowance (float): Additional loss allowed before hitting limit
                - max_daily_loss (float): Configured maximum daily loss threshold
        """
        current_loss = abs(self.get_daily_loss())
        remaining_allowance = self.max_daily_loss - current_loss
        can_trade = current_loss < self.max_daily_loss
        
        if not can_trade:
            self.logger.warning(f"Daily loss limit REACHED: {current_loss:.2f} / {self.max_daily_loss:.2f}")
        else:
            self.logger.debug(f"Daily loss: {current_loss:.2f} / {self.max_daily_loss:.2f} (remaining: {remaining_allowance:.2f})")
        
        return {
            'can_trade': can_trade,
            'current_loss': current_loss,
            'remaining_allowance': max(0, remaining_allowance),
            'max_daily_loss': self.max_daily_loss
        }

    def reset_daily_cache(self):
        """Reset the daily loss cache.
        
        Clears cached loss calculations, forcing recalculation on next check.
        Useful for testing or manual reset at day transitions.
        """
        self.daily_loss_cache = {}

    def update_max_daily_loss(self, new_limit: float):
        """
        Update the maximum daily loss limit.
        
        Args:
            new_limit: New maximum daily loss value
        """
        self.max_daily_loss = new_limit
