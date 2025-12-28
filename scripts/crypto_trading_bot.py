"""Crypto Trading Bot Service.

Automated cryptocurrency trading system that combines technical analysis, sentiment analysis,
market regime detection, and multi-layered risk management to execute trades automatically.

The bot operates in a continuous loop, evaluating trading opportunities across all tracked
cryptocurrencies and managing open positions with multi-level take-profit and stop-loss logic.
"""

import time
import schedule
from scrapy.data.database import CryptoDatabase as DatabaseCryptoBot
from scrapy.trading.SignalLayer.Technical_signal_scoring import TechnicalSignalScoring
from scrapy.trading.SignalLayer.Market_detection_detection import MarketDetection
from scrapy.trading.SignalLayer.SentimentConfirmation import SentimentConfirmation
from scrapy.trading.SignalLayer.Risk_filter import RiskFilter
from scrapy.trading.DecisionLayer.Entry_logic import EntryLogic
from scrapy.trading.DecisionLayer.Stop_tp_logic import StopTpLogic
from scrapy.trading.DecisionLayer.Trade_frequency_control import Trade_frequency_control
from scrapy.trading.RiskLayer.Correlation_exposure import CorrelationExposure
from scrapy.trading.RiskLayer.Daily_loss_limit import DailyLossLimit
from scrapy.trading.RiskLayer.Max_drawdown_controle import MaxDrawdownControl
from scrapy.trading.ExecutionLayer.Fees_model import FeesModel
from scrapy.core.enums import MarketRegime, LongShort
import scrapy.config.settings as conf


class CryptoBotPipeline:
    """Automated cryptocurrency trading pipeline with multi-layer architecture.
    
    Implements a complete trading system with:
    - SignalLayer: Technical scoring, market detection, sentiment confirmation, risk filtering
    - DecisionLayer: Entry logic, stop/TP management, trade frequency control
    - RiskLayer: Correlation exposure, daily loss limits, max drawdown control
    - ExecutionLayer: Fee modeling and order placement
    
    The pipeline manages portfolio capital, tracks open trades, and enforces strict
    risk management rules across all trading decisions.
    """
    
    def __init__(self):
        """Initialize all trading pipeline layers and database tables.
        
        Sets up:
        - Database connection and table structure
        - Initial capital allocation from configuration
        - Signal layer components (market detection, technical scoring, sentiment)
        - Risk layer components (daily loss, drawdown, correlation limits)
        - Decision layer components (entry logic, trade frequency)
        - Execution layer components (stop/TP management, fee calculation)
        - Initial portfolio performance snapshot
        """
        
        
        self.db = DatabaseCryptoBot()
        
        self.db.drop_tables_scores_and_trade()
        self.db.create_score_table()
        self.db.create_trade_table()
        self.db.create_portfolio_table()

        self.initial_capital = conf.INITIAL_CAPITAL
        self.base_sl = 0.6  # 0.6%

        self.MarketDetectionInstance = MarketDetection()
        self.TechnicalSignalScoringInstance = TechnicalSignalScoring()
        self.SentimentConfirmationInstance = SentimentConfirmation(min_tweets=1)

        self.DailyLossinstance=DailyLossLimit(max_daily_loss_percent=conf.MAX_DAILY_LOSS_PERCENT, initial_capital=self.initial_capital)
        self.MaxDrawdowninstance=MaxDrawdownControl(initial_capital=self.initial_capital, max_drawdown_percent=conf.MAX_DRAWDOWN_PERCENT)
        self.CorrelationExposureinstance=CorrelationExposure(max_correlation_exposure=conf.MAX_CORRELATION_EXPOSURE)
        self.RiskFilterInstance = RiskFilter(self.DailyLossinstance,self.MaxDrawdowninstance, self.CorrelationExposureinstance)

        self.EntryLogicInstance = EntryLogic(self.TechnicalSignalScoringInstance, self.SentimentConfirmationInstance)
        self.TradeFrequencyControlInstance = Trade_frequency_control(min_trade_interval=conf.MIN_TRADE_INTERVAL)

        self.StopTpLogicInstance = StopTpLogic()
        self.FeesModelInstance = FeesModel(fee_percentage=conf.TRADING_FEE_PERCENTAGE)
        
        self.db.insert_portfolio_performance(self.initial_capital, self.initial_capital, 0.0)
        

    def place_order(self, crypto_id, position_size: float, entry_price: float, direction: int, risk_reward_ratio: float, take_profit_1: float, stop_loss_1: float, take_profit_2: float, stop_loss_2: float, runner: float):
        """Execute a trade order and update available capital.
        
        Inserts trade into database with multi-level take-profit and stop-loss targets,
        then deducts position size from available capital.
        
        Args:
            crypto_id (int): Cryptocurrency database ID
            position_size (float): Dollar amount allocated to this position
            entry_price (float): Entry price level
            direction (int): Trade direction (1 for long, -1 for short)
            risk_reward_ratio (float): Risk/reward ratio for the trade
            take_profit_1 (float): First take-profit level (percentage)
            stop_loss_1 (float): Stop-loss for first position (percentage)
            take_profit_2 (float): Second take-profit level (percentage)
            stop_loss_2 (float): Stop-loss for second position (percentage)
            runner (float): Runner/trailing stop level (percentage)
        """
        self.db.insert_trade(crypto_id, position_size, entry_price, direction, risk_reward_ratio, take_profit_1, stop_loss_1, take_profit_2, stop_loss_2, runner)
        self.initial_capital -= position_size

    
    def pipeline_step_placeOrder(self, crypto_id):
        """Evaluate and execute trading decision for a specific cryptocurrency.
        
        Complete decision pipeline:
        1. Detect market regime (skip if PANIC)
        2. Fetch latest market data and sentiment
        3. Calculate entry decision and score
        4. Determine dynamic stop-loss distance based on signal strength
        5. Calculate position sizing based on confidence and risk
        6. Apply risk filters (correlation, daily loss, drawdown)
        7. Check trade frequency limits
        8. Execute order if all checks pass
        
        Args:
            crypto_id (int): Cryptocurrency database ID to evaluate
        """
        regime = self.MarketDetectionInstance.detect_market_regime(crypto_id)
        if regime == MarketRegime.PANIC:
            print(f"Market in PANIC for crypto {crypto_id}. No trades executed.")
            return
        data = self.db.get_crypto_data(crypto_id)
        if not data:
            print(f"No data available for crypto {crypto_id}.")
            return

        latest_data = data[0] if isinstance(data, list) else data
        decision, score = self.EntryLogicInstance.decide_entry(data)
        
        min_sl_pct = 0.25
        signal_strength = min(abs(score), 0.8)
        stop_distance_pct = max(min_sl_pct, self.base_sl * (1 - signal_strength))
        
        if decision == LongShort.NoTrade:
            print(f"No trade decision for crypto {crypto_id}.")
            return
        elif decision == LongShort.EnterShort:
            instructions = self.EntryLogicInstance.position_sizing(
                capital=self.initial_capital,
                final_score=score,
                MR=LongShort.EnterShort,
                stop_distance_pct=stop_distance_pct
            )
            if(self.RiskFilterInstance.can_place_trade(crypto_id, self.initial_capital) and self.TradeFrequencyControlInstance.can_trade(crypto_id, time.time())):
                print(f"Placing SHORT trade for crypto {crypto_id} with instructions: {instructions}")
                self.TradeFrequencyControlInstance.set_last_trade(crypto_id, time.time())
                self.place_order(
                    crypto_id=crypto_id,
                    position_size=instructions['position_size'],
                    entry_price=latest_data['price'],
                    direction=-1,
                    risk_reward_ratio=2,

                    take_profit_1=stop_distance_pct *1.6,
                    stop_loss_1=stop_distance_pct,

                    take_profit_2=stop_distance_pct *2.4,
                    stop_loss_2=stop_distance_pct *0.8,

                    runner=stop_distance_pct * 3.5
                )
            else:
                print(f"Trade blocked by risk filters for crypto {crypto_id}.")

        elif decision == LongShort.EnterLong:
            instructions = self.EntryLogicInstance.position_sizing(
                capital=self.initial_capital,
                final_score=score,
                MR=LongShort.EnterLong,
                stop_distance_pct=stop_distance_pct 
            )
            if(self.RiskFilterInstance.can_place_trade(crypto_id, self.initial_capital) and self.TradeFrequencyControlInstance.can_trade(crypto_id, time.time())):
                print(f"Placing LONG trade for crypto {crypto_id} with instructions: {instructions}")
                self.TradeFrequencyControlInstance.set_last_trade(crypto_id, time.time())
                self.place_order(
                    crypto_id=crypto_id,
                    position_size=instructions['position_size'],
                    entry_price=latest_data['price'],
                    direction=1,
                    risk_reward_ratio=1.0,
                    take_profit_1=stop_distance_pct *1.2,
                    stop_loss_1=stop_distance_pct,
                    take_profit_2=stop_distance_pct *0.8,
                    stop_loss_2=stop_distance_pct * 2.0,
                    runner=stop_distance_pct * 3.5
                )
            else:
                print(f"Trade blocked by risk filters for crypto {crypto_id}.")
    
    def pipeline_step_stopTpManagement(self):
        """Monitor and execute stop-loss/take-profit actions for all open trades.
        
        Checks all active positions against current market prices and:
        - Executes partial exits when take-profit levels are hit
        - Closes positions when stop-loss levels are triggered
        - Updates trade status in database
        - Calculates realized P&L including fees
        - Returns capital to available balance
        """
        actions = self.StopTpLogicInstance.check_all_current_trades()
        for action in actions:
            print(f"Executing action {action['action']} for trade ID {action['trade_id']} on take profit number {action['take_profit_number']}")
            self.StopTpLogicInstance.update_trade_status(action['trade_id'], action['take_profit_number'])
            print(f"P&L for trade ID {action['trade_id']}: {action['profit_loss']} with fees applied : {action['profit_loss'] - self.FeesModelInstance.calculate_fee(action['last_price'])}")
            self.initial_capital += action['profit_loss'] - self.FeesModelInstance.calculate_fee(action['last_price'])
    
    def calculate_portfolio_metrics(self):
        """Calculate comprehensive portfolio metrics from open positions.
        
        Aggregates all open trades to compute:
        - Total balance: free cash + unrealized P&L
        - Free cash: available capital for new trades
        - Unrealized P&L: mark-to-market gains/losses on open positions
        
        Returns:
            tuple: (total_balance, free_cash, unrealized_pnl)
        """
        # Get all current open trades
        open_trades = self.db.select_all_trades_current()
        
        # Calculate unrealized PnL from open positions
        unrealized_pnl = 0.0
        allocated_capital = 0.0
        
        for trade in open_trades:
            crypto_id = trade['crypto_id']
            entry_price = float(trade['entry_price'])
            position_size = float(trade['position_size'])
            direction = trade['direction']
            
            # Get current price
            current_price = self.db.get_last_crypto_price(crypto_id)
            if current_price is None:
                continue
            
            current_price = float(current_price)
            
            # Calculate unrealized PnL
            if direction == 1:  # Long position
                pnl = (current_price - entry_price) / entry_price * position_size
            else:  # Short position
                pnl = (entry_price - current_price) / entry_price * position_size
            
            unrealized_pnl += pnl
            allocated_capital += position_size
        
        # Calculate free cash and total balance
        free_cash = self.initial_capital
        total_balance = free_cash + unrealized_pnl
        
        return total_balance, free_cash, unrealized_pnl
    
    def save_portfolio_performance(self):
        """Save current portfolio performance snapshot to database.
        
        Records a timestamped snapshot of portfolio state including total balance,
        free cash, and unrealized P&L for performance tracking and analysis.
        """
        total_balance, free_cash, unrealized_pnl = self.calculate_portfolio_metrics()
        self.db.insert_portfolio_performance(total_balance, free_cash, unrealized_pnl)
        print(f"Portfolio saved - Total: ${total_balance:.2f} | Free: ${free_cash:.2f} | Unrealized PnL: ${unrealized_pnl:.2f}")

    def run_pipeline(self, crypto_ids):
        """Execute complete trading pipeline for all cryptocurrencies.
        
        Pipeline steps:
        1. Check and execute stop-loss/take-profit actions on existing trades
        2. Evaluate new trading opportunities for each crypto ID
        3. Save portfolio performance snapshot after all trading actions
        
        Args:
            crypto_ids (list): List of cryptocurrency database IDs to evaluate
        """
        self.pipeline_step_stopTpManagement()
        for crypto_id in crypto_ids:
            self.pipeline_step_placeOrder(crypto_id)
        
        # Save portfolio performance after all trades
        self.save_portfolio_performance()


    def get_all_ids(self):
        """Retrieve all tracked cryptocurrency database IDs.
        
        Returns:
            list: List of crypto IDs to trade
        """
        return self.db.get_all_crypto_id()


pipeline = None
crypto_ids_to_trade = None

def run_trading_cycle():
    """Execute one complete trading cycle across all cryptocurrencies.
    
    Runs the full trading pipeline including position management and new trade evaluation.
    Displays cycle start/completion timestamps for monitoring and logging.
    """
    global pipeline, crypto_ids_to_trade
    from datetime import datetime
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'='*63}")
    print(f"  Trading Cycle Started - {current_time}")
    print(f"{'='*63}\n")
    
    pipeline.run_pipeline(crypto_ids_to_trade)
    
    print(f"\n{'='*63}")
    print(f"  Trading Cycle Completed")
    print(f"{'='*63}\n")


def main():
    """Main entry point for the automated crypto trading bot service.
    
    Initializes the trading pipeline with all layers (Signal, Decision, Risk, Execution),
    then runs an initial trading cycle immediately before scheduling subsequent cycles
    at intervals defined by TRADING_DECISION_INTERVAL_MINUTES.
    
    The bot runs continuously until interrupted with Ctrl+C. Each cycle:
    - Manages existing positions (stop-loss/take-profit)
    - Evaluates new trading opportunities
    - Enforces risk management rules
    - Tracks portfolio performance
    
    Displays a banner with bot configuration and handles graceful shutdown.
    """
    global pipeline, crypto_ids_to_trade
    
    INTERVAL_MINUTES = conf.TRADING_DECISION_INTERVAL_MINUTES
    
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║                  CRYPTOBOT TRADING SERVICE                ║
    ║                                                           ║
    ║  Mode: Automated crypto trading pipeline                 ║
    ║  Interval: Every {INTERVAL_MINUTES} minutes{' ' * (33 - len(str(INTERVAL_MINUTES)))}║
    ║  Capital: $10,000                                         ║
    ║                                                           ║
    ║  Press Ctrl+C to stop the service                         ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    pipeline = CryptoBotPipeline()
    crypto_ids_to_trade = pipeline.get_all_ids()

    run_trading_cycle()

    schedule.every(INTERVAL_MINUTES).minutes.do(run_trading_cycle)
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n╔═══════════════════════════════════════════════════════════╗")
        print("║                 SERVICE STOP REQUESTED                    ║")
        print("╚═══════════════════════════════════════════════════════════╝\n")
        print("Service stopped cleanly. Goodbye!")

    
if __name__ == "__main__":
    main()