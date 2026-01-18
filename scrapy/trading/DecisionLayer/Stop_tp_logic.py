from scrapy.core.enums import TakeStop
from scrapy.data.database import CryptoDatabase as DatabaseCryptoBot
import scrapy.utils.logger as Logger
import scrapy.config.settings as conf

class StopTpLogic:
    """Manage stop-loss and take-profit logic for active trades.
    
    Monitors current market prices against configured TP/SL levels and triggers
    exit signals when thresholds are breached. Supports multiple TP levels,
    runner positions with trailing stops, and dynamic TP adjustment based on
    market conditions and signal strength.
    """
    
    def __init__(self):
        """Initialize stop-loss and take-profit logic controller."""
        self.db_instance = DatabaseCryptoBot()
        self.logger = Logger.get_logger("StopTpLogic")
        self.trailing_stop_ratio = conf.RUNNER_TRAILING_STOP_RATIO
        self.min_profit_to_trail = conf.RUNNER_MIN_PROFIT_TO_TRAIL
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

    def check_runner_with_trailing_stop(self, trade, position_size: float):
        """Check runner position with dynamic trailing stop.
        
        The trailing stop moves up with price gains:
        - For LONG: If price goes up X%, the SL is set at (X * trailing_ratio)% above entry
        - For SHORT: If price goes down X%, the SL is set at (X * trailing_ratio)% below entry
        
        Example with trailing_ratio=0.33:
        - Price +3% from entry -> trailing SL at +1% (locking in 1% profit)
        - Price +6% from entry -> trailing SL at +2% (locking in 2% profit)
        
        Args:
            trade (dict): Trade data from database
            position_size (float): Size of the runner position
            
        Returns:
            tuple: (action, profit_loss, last_price)
        """
        crypto_id = trade['crypto_id']
        entry_price = float(trade['entry_price'])
        direction = trade['direction']
        runner_tp_pct = float(trade['runner'])
        trailing_ratio = float(trade.get('trailing_stop_pct', self.trailing_stop_ratio) or self.trailing_stop_ratio)
        
        last_price = self.db_instance.get_last_crypto_price(crypto_id)
        if last_price is None:
            return TakeStop.Hold, 0.0, 0.0
        last_price = float(last_price)
        
        # Update highest/lowest price for trailing stop calculation
        if direction == 1:  # LONG
            current_highest = float(trade.get('highest_price') or entry_price)
            if last_price > current_highest:
                self.db_instance.update_trade_extreme_price(trade['id_trade'], highest_price=last_price)
                current_highest = last_price
            
            # Calculate current profit percentage from entry
            current_profit_pct = ((last_price - entry_price) / entry_price) * 100
            max_profit_pct = ((current_highest - entry_price) / entry_price) * 100
            
            # TP check: runner target reached
            tp_price = entry_price * (1 + runner_tp_pct / 100)
            if last_price >= tp_price:
                pnl = ((last_price - entry_price) / entry_price) * position_size
                self.logger.info(f"Crypto {crypto_id}: RUNNER TP triggered at {last_price:.4f} (+{current_profit_pct:.2f}%)")
                return TakeStop.TakeProfit, pnl, last_price
            
            # Trailing stop check: only if we have minimum profit
            if max_profit_pct >= self.min_profit_to_trail:
                # Trailing SL is at (max_profit * trailing_ratio)% above entry
                trailing_sl_pct = max_profit_pct * trailing_ratio
                trailing_sl_price = entry_price * (1 + trailing_sl_pct / 100)
                
                self.logger.debug(f"Crypto {crypto_id}: Runner trailing - Max profit: {max_profit_pct:.2f}%, Current: {current_profit_pct:.2f}%, Trailing SL at: +{trailing_sl_pct:.2f}%")
                
                if last_price <= trailing_sl_price:
                    pnl = ((last_price - entry_price) / entry_price) * position_size
                    self.logger.info(f"Crypto {crypto_id}: RUNNER TRAILING STOP triggered at {last_price:.4f} (+{current_profit_pct:.2f}%), locked profit from peak {max_profit_pct:.2f}%")
                    return TakeStop.StopLoss, pnl, last_price
                    
        else:  # SHORT
            current_lowest = float(trade.get('lowest_price') or entry_price)
            if last_price < current_lowest:
                self.db_instance.update_trade_extreme_price(trade['id_trade'], lowest_price=last_price)
                current_lowest = last_price
            
            # Calculate current profit percentage from entry (inverted for short)
            current_profit_pct = ((entry_price - last_price) / entry_price) * 100
            max_profit_pct = ((entry_price - current_lowest) / entry_price) * 100
            
            # TP check: runner target reached
            tp_price = entry_price * (1 - runner_tp_pct / 100)
            if last_price <= tp_price:
                pnl = ((entry_price - last_price) / entry_price) * position_size
                self.logger.info(f"Crypto {crypto_id}: RUNNER TP triggered at {last_price:.4f} (+{current_profit_pct:.2f}%)")
                return TakeStop.TakeProfit, pnl, last_price
            
            # Trailing stop check: only if we have minimum profit
            if max_profit_pct >= self.min_profit_to_trail:
                # Trailing SL is at (max_profit * trailing_ratio)% below entry
                trailing_sl_pct = max_profit_pct * trailing_ratio
                trailing_sl_price = entry_price * (1 - trailing_sl_pct / 100)
                
                self.logger.debug(f"Crypto {crypto_id}: Runner trailing - Max profit: {max_profit_pct:.2f}%, Current: {current_profit_pct:.2f}%, Trailing SL at: +{trailing_sl_pct:.2f}%")
                
                if last_price >= trailing_sl_price:
                    pnl = ((entry_price - last_price) / entry_price) * position_size
                    self.logger.info(f"Crypto {crypto_id}: RUNNER TRAILING STOP triggered at {last_price:.4f} (+{current_profit_pct:.2f}%), locked profit from peak {max_profit_pct:.2f}%")
                    return TakeStop.StopLoss, pnl, last_price
        
        return TakeStop.Hold, 0.0, last_price

    def check_all_current_trades(self):
        """Scan all active trades for TP/SL trigger conditions.
        
        Iterates through all current open trades and checks each active TP/SL level:
        - TP1/SL1: First take-profit and stop-loss level (if status_1 == 0)
        - TP2/SL2: Second take-profit and stop-loss level (if status_1 != 0 and status_2 == 0)
          Note: SL2 only activates AFTER TP1 is hit (trailing stop to lock in profits)
        - Runner: Trailing position with dynamic trailing stop (if status_2 != 0 and status == 0)
        
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
            tp_weights = conf.TP_WEIGHTS
            
            # Phase 1: TP1/SL1 - Initial position (50%)
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
                    
            # Phase 2: TP2/SL2 - Activates ONLY after TP1 is hit
            # This allows protecting profits with a trailing stop
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
                    
            # Phase 3: Runner - Activates ONLY after TP2 is hit
            # Uses dynamic trailing stop that moves up with price
            if trade['runner'] is not None and trade['status_2'] != 0 and trade['status'] == 0:
                size_3 = position_size * tp_weights[3]
                action, profit, last_price = self.check_runner_with_trailing_stop(
                    trade,
                    size_3
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
    
    def adjust_tp_levels_by_score(self, trade_id: int, score: float, base_tp2: float, base_runner: float):
        """Dynamically adjust TP2 and runner levels based on signal score strength.
        
        Higher confidence signals (stronger scores) get more aggressive TP targets,
        allowing positions to run further. Lower confidence signals get more
        conservative targets to lock in profits sooner.
        
        Args:
            trade_id (int): Trade identifier to update
            score (float): Signal score from -1 to +1
            base_tp2 (float): Base TP2 percentage
            base_runner (float): Base runner percentage
        """
        tp2_multiplier = getattr(conf, 'TP2_SCORE_MULTIPLIER', 1.5)
        runner_multiplier = getattr(conf, 'RUNNER_SCORE_MULTIPLIER', 2.0)
        
        # Score strength from 0 to 1
        score_strength = min(abs(score), 1.0)
        
        # For high confidence trades (score > 0.7), increase TP targets
        # For low confidence trades (score < 0.5), keep base targets
        if score_strength >= 0.7:
            # High confidence: increase targets significantly
            adjustment_factor = 1.0 + (score_strength - 0.5) * (tp2_multiplier - 1.0) / 0.5
            new_tp2 = base_tp2 * adjustment_factor
            new_runner = base_runner * (1.0 + (score_strength - 0.5) * (runner_multiplier - 1.0) / 0.5)
        elif score_strength >= 0.55:
            # Medium confidence: slight increase
            adjustment_factor = 1.0 + (score_strength - 0.5) * 0.5
            new_tp2 = base_tp2 * adjustment_factor
            new_runner = base_runner * adjustment_factor
        else:
            # Low confidence: keep base targets
            new_tp2 = base_tp2
            new_runner = base_runner
        
        # Also adjust trailing stop ratio: tighter for low confidence, looser for high
        # High confidence = let it run more before trailing kicks in
        trailing_ratio = 0.25 + (score_strength * 0.25)  # Range: 0.25 to 0.50
        
        self.db_instance.update_trade_tp_levels(
            trade_id=trade_id,
            take_profit_2=new_tp2,
            runner=new_runner,
            trailing_stop_pct=trailing_ratio
        )
        
        self.logger.info(f"Trade {trade_id}: Adjusted TP2={new_tp2:.2f}%, Runner={new_runner:.2f}%, Trailing={trailing_ratio:.2f} (score={score:.3f})")
    
    def update_trade_status(self, trade_id: int, take_profit_number: int, status: int):
        """Mark a take-profit level as triggered/closed.
        
        Updates the database to record that a specific TP level has been hit,
        preventing duplicate processing of the same exit signal.
        
        Args:
            trade_id (int): Trade identifier to update
            take_profit_number (int): Which TP level to close (1, 2, or 3)
        """
        self.db_instance.update_trade_status(trade_id, take_profit_number, status)