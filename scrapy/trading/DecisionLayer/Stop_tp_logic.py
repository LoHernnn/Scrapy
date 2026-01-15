from scrapy.core.enums import TakeStop
from scrapy.data.database import CryptoDatabase as DatabaseCryptoBot
import scrapy.utils.logger as Logger

class StopTpLogic:
    """Manage stop-loss and take-profit logic for active trades.
    
    Monitors current market prices against configured TP/SL levels and triggers
    exit signals when thresholds are breached. Supports multiple TP levels and
    runner positions for partial profit-taking strategies.
    """
    
    def __init__(self):
        """Initialize stop-loss and take-profit logic controller."""
        self.db_instance = DatabaseCryptoBot()
        self.logger = Logger.get_logger("StopTpLogic")
    def check_price_crypto(self, crypto_id, entry_price, direction,
                        take_profit_pct: float, stop_loss_pct: float, position_size: float, allow_stop_loss: bool = True):
        """Check if current price has hit take-profit or stop-loss levels.
        
        Calculates TP/SL prices based on entry price and percentages, then compares
        with current market price. Logic adjusts for long vs short positions.
        
        Args:
            crypto_id (int): Cryptocurrency identifier
            entry_price (float): Original entry price of the position
            direction (int): Trade direction (1 for LONG, -1 for SHORT)
            take_profit_pct (float): Take profit percentage threshold
            stop_loss_pct (float): Stop loss percentage threshold
            
        Returns:
            tuple: (action, profit_loss, last_price) where:
                - action (TakeStop): TakeProfit, StopLoss, or Hold
                - profit_loss (float): Realized profit/loss amount
                - last_price (float): Current market price
        """

        last_price = self.db_instance.get_last_crypto_price(crypto_id)
        
        entry_price = float(entry_price)
        last_price = float(last_price) if last_price is not None else None
        
        if last_price is None:
            return TakeStop.Hold, 0.0, 0.0

        if direction == 1:
            tp_price = entry_price * (1 + take_profit_pct / 100)
            sl_price = entry_price * (1 - stop_loss_pct / 100) if allow_stop_loss and stop_loss_pct > 0 else None
        else:
            tp_price = entry_price * (1 - take_profit_pct / 100)
            sl_price = entry_price * (1 + stop_loss_pct / 100) if allow_stop_loss and stop_loss_pct > 0 else None

        if (direction == 1 and last_price >= tp_price) or \
        (direction == -1 and last_price <= tp_price):
            pnl = ((last_price - entry_price) / entry_price) * position_size * direction
            self.logger.info(f"Crypto {crypto_id}: TAKE PROFIT triggered at {last_price:.4f} (entry: {entry_price:.4f})")
            return TakeStop.TakeProfit, pnl, last_price

        if sl_price is not None and ((direction == 1 and last_price <= sl_price) or \
        (direction == -1 and last_price >= sl_price)):
            pnl = ((last_price - entry_price) / entry_price) * position_size * direction
            self.logger.warning(f"Crypto {crypto_id}: STOP LOSS triggered at {last_price:.4f} (entry: {entry_price:.4f})")
            return TakeStop.StopLoss, pnl, last_price

        return TakeStop.Hold, 0.0, last_price

    def check_all_current_trades(self):
        """Scan all active trades for TP/SL trigger conditions.
        
        Iterates through all current open trades and checks each active TP/SL level:
        - TP1/SL1: First take-profit and stop-loss level (if status_1 == 0)
        - TP2/SL2: Second take-profit and stop-loss level (if status_1 != 0 and status_2 == 0)
          Note: SL2 only activates AFTER TP1 is hit (trailing stop to lock in profits)
        - Runner: Trailing position with only TP, no SL (if status_2 != 0 and status == 0)
        
        Returns:
            list: List of dictionaries containing triggered trades with:
                - trade_id: Trade identifier
                - take_profit_number: Which TP level triggered (1, 2, or 3 for runner)
                - action: TakeProfit or StopLoss
                - profit_loss: Realized P&L
                - last_price: Current market price at trigger
        """
        current_trades = self.db_instance.select_all_trades_current()
        self.logger.debug(f"Checking {len(current_trades)} active trades for TP/SL")
        results = []
        for trade in current_trades:
            position_size = float(trade.get('position_size', 0) or 0)
            if position_size <= 0:
                continue
            tp_weights = {1: 0.5, 2: 0.3, 3: 0.2}
            
            # Phase 1: TP1/SL1 - Position initiale (50%)
            if trade['status_1'] == 0:
                size_1 = position_size * tp_weights[1]
                action, profit, last_price = self.check_price_crypto(
                    trade['crypto_id'],
                    trade['entry_price'],
                    trade['direction'],
                    trade['take_profit_1'],
                    trade['stop_loss_1'],
                    size_1,
                    allow_stop_loss=True
                )
                if action != TakeStop.Hold:
                    results.append({'trade_id': trade['id_trade'],
                                    'take_profit_number': 1,
                                    'action': action,
                                    'profit_loss': profit,
                                    'position_size_closed': size_1
                                    ,'last_price': last_price
                                    })
                    
            # Phase 2: TP2/SL2 - S'active SEULEMENT après que TP1 soit touché
            # Cela permet de protéger les profits avec un trailing stop
            elif trade['status_1'] != 0 and trade['status_2'] == 0:
                size_2 = position_size * tp_weights[2]
                action, profit, last_price = self.check_price_crypto(
                    trade['crypto_id'],
                    trade['entry_price'],
                    trade['direction'],
                    trade['take_profit_2'],
                    trade['stop_loss_2'],
                    size_2,
                    allow_stop_loss=True
                )
                if action != TakeStop.Hold:
                    results.append({'trade_id': trade['id_trade'],
                                    'take_profit_number': 2,
                                    'action': action,
                                    'profit_loss': profit,
                                    'position_size_closed': size_2,
                                    'last_price': last_price
                                    })
                    
            # Phase 3: Runner - S'active SEULEMENT après que TP2 soit touché
            # Pas de stop loss, on laisse courir pour maximiser les gains
            if trade['runner'] is not None and trade['status_2'] != 0 and trade['status'] == 0:
                size_3 = position_size * tp_weights[3]
                action, profit, last_price = self.check_price_crypto(
                    trade['crypto_id'],
                    trade['entry_price'],
                    trade['direction'],
                    trade['runner'],
                    0,
                    size_3,
                    allow_stop_loss=False
                )
                if action != TakeStop.Hold:
                    results.append({'trade_id': trade['id_trade'],
                                    'take_profit_number': 3,
                                    'action': action,
                                    'profit_loss': profit,
                                    'position_size_closed': size_3,
                                    'last_price': last_price
                                    })
        return results
    
    def update_trade_status(self, trade_id: int, take_profit_number: int, status: int):
        """Mark a take-profit level as triggered/closed.
        
        Updates the database to record that a specific TP level has been hit,
        preventing duplicate processing of the same exit signal.
        
        Args:
            trade_id (int): Trade identifier to update
            take_profit_number (int): Which TP level to close (1, 2, or 3)
        """
        self.db_instance.update_trade_status(trade_id, take_profit_number, status)