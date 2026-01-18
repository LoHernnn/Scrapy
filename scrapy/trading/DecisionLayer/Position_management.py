"""Position Management Module.

Handles advanced position management features including:
- Inertia cut-off: Closes stagnant trades when entry signals are no longer valid
- Capital reinjection: Adds to winning positions up to maximum allocation
"""

from scrapy.data.database import CryptoDatabase as DatabaseCryptoBot
from scrapy.core.enums import LongShort, TakeStop
import scrapy.utils.logger as Logger
import scrapy.config.settings as conf


class PositionManager:
    """Manages advanced position operations including inertia exits and capital reinjection.
    
    Monitors open positions for:
    - Stagnation: Trades that haven't moved significantly after a timeout period
    - Signal validity: Re-evaluates entry signals to decide if position should be kept
    - Reinjection opportunities: Adds capital to winning positions
    """
    
    def __init__(self, entry_logic_instance, technical_layer, sentiment_layer):
        """Initialize position manager with required dependencies.
        
        Args:
            entry_logic_instance: EntryLogic instance for re-evaluating signals
            technical_layer: TechnicalSignalScoring instance
            sentiment_layer: SentimentConfirmation instance
        """
        self.db = DatabaseCryptoBot()
        self.logger = Logger.get_logger("PositionManager")
        self.entry_logic = entry_logic_instance
        self.technical_layer = technical_layer
        self.sentiment_layer = sentiment_layer
        
        # Inertia configuration
        self.inertia_timeout_hours = getattr(conf, 'INERTIA_TIMEOUT_HOURS', 4)
        self.stagnation_threshold_pct = getattr(conf, 'INERTIA_STAGNATION_THRESHOLD_PCT', 0.5)
        self.min_score_to_keep = getattr(conf, 'INERTIA_MIN_SCORE_TO_KEEP', 0.3)
        
        # Reinjection configuration
        self.enable_reinjection = getattr(conf, 'ENABLE_CAPITAL_REINJECTION', True)
        self.reinjection_min_profit_pct = getattr(conf, 'REINJECTION_MIN_PROFIT_PCT', 1.5)
        self.reinjection_amount_pct = getattr(conf, 'REINJECTION_AMOUNT_PCT', 0.25)
        self.max_reinjections = getattr(conf, 'MAX_REINJECTIONS_PER_TRADE', 2)
        self.reinjection_min_score = getattr(conf, 'REINJECTION_MIN_SCORE', 0.5)

    def check_inertia_exits(self) -> list:
        """Check all trades for inertia timeout and evaluate for exit.
        
        For trades older than the timeout threshold:
        1. Check if price has stagnated (moved less than threshold)
        2. Re-evaluate entry signals
        3. If signals are no longer valid, mark for exit
        
        Returns:
            list: List of trades to be closed due to inertia
        """
        trades_to_close = []
        eligible_trades = self.db.get_trades_for_inertia_check(self.inertia_timeout_hours)
        
        self.logger.debug(f"Checking {len(eligible_trades)} trades for inertia timeout")
        
        for trade in eligible_trades:
            crypto_id = trade['crypto_id']
            entry_price = float(trade['entry_price'])
            direction = trade['direction']
            trade_id = trade['id_trade']
            
            # Get current price
            current_price = self.db.get_last_crypto_price(crypto_id)
            if current_price is None:
                continue
            current_price = float(current_price)
            
            # Calculate price movement since entry
            price_change_pct = abs((current_price - entry_price) / entry_price * 100)
            
            # Check if trade is stagnant
            is_stagnant = price_change_pct < self.stagnation_threshold_pct
            
            if not is_stagnant:
                self.logger.debug(f"Trade {trade_id}: Not stagnant (moved {price_change_pct:.2f}%)")
                continue
            
            # Re-evaluate entry signals
            signal_still_valid = self._evaluate_signal_validity(crypto_id, direction)
            
            if not signal_still_valid:
                self.logger.info(f"Trade {trade_id}: Stagnant ({price_change_pct:.2f}% move) and signals invalid - marking for inertia exit")
                
                # Calculate remaining position value for P&L
                position_size = float(trade['position_size'])
                remaining_pct = self._calculate_remaining_position_pct(trade)
                remaining_size = position_size * remaining_pct
                
                # Calculate P&L for remaining position
                if direction == 1:  # Long
                    pnl = ((current_price - entry_price) / entry_price) * remaining_size
                else:  # Short
                    pnl = ((entry_price - current_price) / entry_price) * remaining_size
                
                trades_to_close.append({
                    'trade_id': trade_id,
                    'crypto_id': crypto_id,
                    'action': 'INERTIA_EXIT',
                    'profit_loss': pnl,
                    'position_size_closed': remaining_size,
                    'last_price': current_price,
                    'reason': f'Stagnant for {self.inertia_timeout_hours}h (moved only {price_change_pct:.2f}%), signals no longer valid'
                })
            else:
                self.logger.debug(f"Trade {trade_id}: Stagnant but signals still valid - keeping position")
                # Update last check timestamp
                self.db.update_trade_last_check(trade_id, current_price)
        
        return trades_to_close

    def _evaluate_signal_validity(self, crypto_id: int, original_direction: int) -> bool:
        """Re-evaluate if the original entry signal is still valid.
        
        Args:
            crypto_id (int): Cryptocurrency ID
            original_direction (int): Original trade direction (1=Long, -1=Short)
            
        Returns:
            bool: True if signal is still valid for the original direction
        """
        try:
            # Get current market data
            data = self.db.get_crypto_data(crypto_id)
            if not data:
                return False
            
            # Calculate current score
            decision, score = self.entry_logic.decide_entry(data)
            
            # Check if score still supports the original direction
            if original_direction == 1:  # Long position
                # Signal valid if score is positive and above minimum threshold
                return score >= self.min_score_to_keep
            else:  # Short position
                # Signal valid if score is negative and below minimum threshold
                return score <= -self.min_score_to_keep
                
        except Exception as e:
            self.logger.error(f"Error evaluating signal validity for crypto {crypto_id}: {e}")
            return True  # Keep position if evaluation fails (conservative approach)

    def _calculate_remaining_position_pct(self, trade: dict) -> float:
        """Calculate what percentage of the position is still open.
        
        Args:
            trade (dict): Trade data from database
            
        Returns:
            float: Percentage of position still open (0.0 to 1.0)
        """
        tp_weights = conf.TP_WEIGHTS
        remaining = 0.0
        
        # Check each phase
        if trade['status_1'] == 0:
            remaining += tp_weights[1]
        if trade['status_2'] == 0:
            remaining += tp_weights[2]
        if trade['status'] == 0 and trade['runner'] is not None:
            remaining += tp_weights[3]
            
        return remaining

    def check_reinjection_opportunities(self, available_capital: float, num_tradable_cryptos: int) -> list:
        """Check open positions for capital reinjection opportunities.
        
        Conditions for reinjection:
        1. Position is in profit by at least the minimum threshold
        2. Current signals still support the trade direction
        3. Maximum reinjections not reached
        4. Doesn't exceed max allocation per crypto
        
        Args:
            available_capital (float): Current free cash available
            num_tradable_cryptos (int): Number of cryptos being traded
            
        Returns:
            list: List of reinjection instructions
        """
        if not self.enable_reinjection:
            return []
        
        reinjections = []
        current_trades = self.db.select_all_trades_current()
        
        # Calculate max position size per crypto
        total_capital = available_capital + sum(
            float(t.get('position_size', 0) or 0) for t in current_trades
        )
        max_position_per_crypto = total_capital / max(num_tradable_cryptos, 1)
        
        self.logger.debug(f"Checking reinjection opportunities. Max per crypto: ${max_position_per_crypto:.2f}")
        
        for trade in current_trades:
            crypto_id = trade['crypto_id']
            trade_id = trade['id_trade']
            entry_price = float(trade['entry_price'])
            position_size = float(trade['position_size'])
            direction = trade['direction']
            reinjection_count = trade.get('reinjection_count', 0) or 0
            
            # Check if max reinjections reached
            if reinjection_count >= self.max_reinjections:
                continue
            
            # Check if position already at max size
            if position_size >= max_position_per_crypto:
                continue
            
            # Get current price
            current_price = self.db.get_last_crypto_price(crypto_id)
            if current_price is None:
                continue
            current_price = float(current_price)
            
            # Calculate current profit percentage
            if direction == 1:  # Long
                profit_pct = ((current_price - entry_price) / entry_price) * 100
            else:  # Short
                profit_pct = ((entry_price - current_price) / entry_price) * 100
            
            # Check if minimum profit threshold reached
            if profit_pct < self.reinjection_min_profit_pct:
                continue
            
            # Re-evaluate signals
            try:
                data = self.db.get_crypto_data(crypto_id)
                if not data:
                    continue
                decision, score = self.entry_logic.decide_entry(data)
                
                # Check if score supports reinjection
                score_valid = (direction == 1 and score >= self.reinjection_min_score) or \
                              (direction == -1 and score <= -self.reinjection_min_score)
                
                if not score_valid:
                    self.logger.debug(f"Trade {trade_id}: Profitable but score ({score:.3f}) doesn't support reinjection")
                    continue
                
            except Exception as e:
                self.logger.error(f"Error evaluating reinjection for trade {trade_id}: {e}")
                continue
            
            # Calculate reinjection amount
            base_reinjection = position_size * self.reinjection_amount_pct
            
            # Cap at max position size
            max_additional = max_position_per_crypto - position_size
            reinjection_amount = min(base_reinjection, max_additional, available_capital)
            
            if reinjection_amount < 10:  # Minimum meaningful reinjection
                continue
            
            # Calculate new average entry price
            total_value = (position_size * entry_price) + (reinjection_amount * current_price)
            new_position_size = position_size + reinjection_amount
            new_average_price = total_value / new_position_size
            
            reinjections.append({
                'trade_id': trade_id,
                'crypto_id': crypto_id,
                'additional_size': reinjection_amount,
                'current_price': current_price,
                'new_average_price': new_average_price,
                'profit_pct': profit_pct,
                'score': score,
                'reason': f'Position +{profit_pct:.2f}% with valid signal (score: {score:.3f})'
            })
            
            self.logger.info(f"Trade {trade_id}: Reinjection opportunity - adding ${reinjection_amount:.2f} at ${current_price:.4f}")
        
        return reinjections

    def execute_inertia_exit(self, trade_id: int) -> float:
        """Execute the inertia exit by closing all remaining phases.
        
        Args:
            trade_id (int): Trade ID to close
            
        Returns:
            float: Position size that was closed
        """
        self.db.close_trade_inertia(trade_id)
        self.logger.info(f"Trade {trade_id}: Closed due to inertia timeout")
        return 0.0  # P&L calculated separately

    def execute_reinjection(self, trade_id: int, additional_size: float, new_average_price: float) -> bool:
        """Execute capital reinjection into an existing position.
        
        Args:
            trade_id (int): Trade ID to add to
            additional_size (float): Amount to add
            new_average_price (float): New weighted average entry price
            
        Returns:
            bool: True if successful
        """
        try:
            self.db.update_trade_reinjection(trade_id, additional_size, new_average_price)
            self.logger.info(f"Trade {trade_id}: Reinjected ${additional_size:.2f}, new avg price: ${new_average_price:.4f}")
            return True
        except Exception as e:
            self.logger.error(f"Error executing reinjection for trade {trade_id}: {e}")
            return False
