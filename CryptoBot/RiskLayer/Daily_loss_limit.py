import DataLayer.database as db
from datetime import datetime, timedelta
from typing import Dict, Any


class DailyLossLimit:
    def __init__(self, db_config, max_daily_loss_percent: float = None, max_daily_loss: float = None, initial_capital: float = 10000.0):
        """
        Initialize the daily loss limit control.
        
        Args:
            db_config: Database configuration dictionary
            max_daily_loss_percent: Maximum allowed loss as percentage of initial capital (e.g., 2.0 for 2%)
            max_daily_loss: Maximum allowed loss in absolute value (e.g., 200 for $200 max loss)
            initial_capital: Initial capital for percentage calculation
        """
        self.db_instance = db.DatabaseCryptoBot(db_config)
        self.initial_capital = initial_capital
        
        # Calculate max_daily_loss from percentage if provided
        if max_daily_loss_percent is not None:
            self.max_daily_loss = (max_daily_loss_percent / 100.0) * initial_capital
        elif max_daily_loss is not None:
            self.max_daily_loss = max_daily_loss
        else:
            self.max_daily_loss = 0.02 * initial_capital  # Default 2%
        
        self.daily_loss_cache = {}  # Cache to store today's loss

    def calculate_trade_pnl(self, trade: Dict[str, Any]) -> float:
        """
        Calculate the PnL (profit/loss) for a single trade.
        
        Args:
            trade: Dictionary containing trade information
        Returns:
            PnL value (negative for loss, positive for profit)
        """
        entry_price = trade['entry_price']
        position_size = trade['position_size']
        direction = trade['direction']  # 1 for long, -1 for short
        
        # Get current price
        current_price = self.db_instance.get_last_crypto_price(trade['crypto_id'])
        
        if current_price is None:
            return 0.0
        
        # Calculate PnL based on direction
        if direction == 1:  # Long position
            pnl = (current_price - entry_price) * position_size
        else:  # Short position
            pnl = (entry_price - current_price) * position_size
        
        return pnl

    def get_daily_loss(self) -> float:
        """
        Calculate total loss for today from all closed trades.
        
        Returns:
            Total daily loss (negative value represents losses)
        """
        today = datetime.now().date()
        
        # Check if we have cached today's loss
        if today in self.daily_loss_cache:
            return self.daily_loss_cache[today]
        
        # Get all closed trades from today
        # This would need a method in database.py to fetch trades by date
        # For now, we'll calculate from current trades
        total_pnl = 0.0
        
        # Get all current open trades and calculate unrealized PnL
        current_trades = self.db_instance.select_all_trades_current()  # Get all current trades
        
        for trade in current_trades:
            pnl = self.calculate_trade_pnl(trade)
            if pnl < 0:  # Only count losses
                total_pnl += pnl
        
        # Cache the result
        self.daily_loss_cache[today] = total_pnl
        
        return total_pnl

    def can_trade(self) -> Dict[str, Any]:
        """
        Check if trading is allowed based on daily loss limit.
        
        Returns:
            Dictionary with:
                - can_trade: bool indicating if new trades are allowed
                - current_loss: current daily loss amount
                - remaining_allowance: how much more loss is allowed before hitting limit
        """
        current_loss = abs(self.get_daily_loss())
        remaining_allowance = self.max_daily_loss - current_loss
        can_trade = current_loss < self.max_daily_loss
        
        return {
            'can_trade': can_trade,
            'current_loss': current_loss,
            'remaining_allowance': max(0, remaining_allowance),
            'max_daily_loss': self.max_daily_loss
        }

    def reset_daily_cache(self):
        """
        Reset the daily loss cache (useful for testing or manual reset).
        """
        self.daily_loss_cache = {}

    def update_max_daily_loss(self, new_limit: float):
        """
        Update the maximum daily loss limit.
        
        Args:
            new_limit: New maximum daily loss value
        """
        self.max_daily_loss = new_limit
