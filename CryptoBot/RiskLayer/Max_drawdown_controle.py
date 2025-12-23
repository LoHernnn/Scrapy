import DataLayer.database as db
from typing import Dict, Any, Optional


class MaxDrawdownControl:
    def __init__(self, db_config, initial_capital: float, max_drawdown_percent: float):
        """
        Initialize the max drawdown control.
        
        Args:
            db_config: Database configuration dictionary
            initial_capital: Starting capital amount
            max_drawdown_percent: Maximum allowed drawdown in percentage (e.g., 20 for 20%)
        """
        self.db_instance = db.DatabaseCryptoBot(db_config)
        self.initial_capital = initial_capital
        self.max_drawdown_percent = max_drawdown_percent
        self.peak_capital = initial_capital

    def calculate_drawdown(self, current_capital ) -> Dict[str, Any]:
        """
        Calculate current drawdown from peak.
        
        Returns:
            Dictionary with:
                - current_capital: current total capital
                - peak_capital: highest capital reached
                - drawdown_amount: absolute drawdown amount
                - drawdown_percent: drawdown as percentage
        """
        
        # Update peak if current capital is higher
        if current_capital > self.peak_capital:
            self.peak_capital = current_capital
        
        # Calculate drawdown
        drawdown_amount = self.peak_capital - current_capital
        drawdown_percent = (drawdown_amount / self.peak_capital) * 100 if self.peak_capital > 0 else 0
        return drawdown_percent >= self.max_drawdown_percent

    def reset_peak(self):
        """
        Manually reset the peak capital to current capital.
        """
        self.peak_capital = self.initial_capital

    def update_max_drawdown(self, new_limit: float):
        """
        Update the maximum drawdown percentage limit.
        
        Args:
            new_limit: New maximum drawdown percentage
        """
        self.max_drawdown_percent = new_limit
