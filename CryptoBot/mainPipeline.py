"""
Main Pipeline for CryptoBot
Orchestrates all layers: Signal, Decision, Risk, and Execution
"""

import time
import schedule
import DataLayer.database as db
from SignalLayer.Technical_signal_scoring import TechnicalSignalScoring
from SignalLayer.Market_detection_detection import MarketDetection
from SignalLayer.SentimentConfirmation import SentimentConfirmation
from SignalLayer.Risk_filter import RiskFilter
from DecisionLayer.Entry_logic import EntryLogic
from DecisionLayer.Stop_tp_logic import StopTpLogic
from DecisionLayer.Trade_frequency_control import Trade_frequency_control
from RiskLayer.Correlation_exposure import CorrelationExposure
from RiskLayer.Daily_loss_limit import DailyLossLimit
from RiskLayer.Max_drawdown_controle import MaxDrawdownControl
from ExecutionLayer.Fees_model import FeesModel
from utils.enum import MarketRegime, LongShort


class CryptoBotPipeline:
    def __init__(self):
        """Initialize all layers with coherent parameters for crypto trading"""
        
        # Database Configuration
        self.db_config = {
            'host': 'localhost',
            'port': '5432',
            "database": "crypto",
            "user": "crypto",
            "password": "crypto",
        }
        self.db = db.DatabaseCryptoBot(self.db_config)
        
        self.db.drop_tables()
        
        self.db.create_score_table()
        self.db.create_trade_table()

        self.initial_capital = 10000.0 
        self.base_sl = 0.6  # 0.6%

        self.MarketDetectionInstance = MarketDetection(self.db_config)
        self.TechnicalSignalScoringInstance = TechnicalSignalScoring(self.db_config)
        self.SentimentConfirmationInstance = SentimentConfirmation(self.db_config, min_tweets=1)

        self.DailyLossinstance=DailyLossLimit(self.db_config, max_daily_loss_percent=2.0, initial_capital=self.initial_capital)
        self.MaxDrawdowninstance=MaxDrawdownControl(self.db_config, initial_capital=self.initial_capital, max_drawdown_percent=20.0)
        self.CorrelationExposureinstance=CorrelationExposure(self.db_config, max_correlation_exposure=0.85)
        self.RiskFilterInstance = RiskFilter(self.db_config,self.DailyLossinstance,self.MaxDrawdowninstance, self.CorrelationExposureinstance)

        self.EntryLogicInstance = EntryLogic(self.db_config, self.TechnicalSignalScoringInstance, self.SentimentConfirmationInstance)
        self.TradeFrequencyControlInstance = Trade_frequency_control(min_trade_interval=60)

        self.StopTpLogicInstance = StopTpLogic(self.db_config)
        self.FeesModelInstance = FeesModel(fee_percentage=0.005)

    def place_order(self, crypto_id, position_size: float, entry_price: float, direction: int, risk_reward_ratio: float, take_profit_1: float, stop_loss_1: float, take_profit_2: float, stop_loss_2: float, runner: float):
        self.db.insert_trade(crypto_id, position_size, entry_price, direction, risk_reward_ratio, take_profit_1, stop_loss_1, take_profit_2, stop_loss_2, runner)
        self.initial_capital -= position_size

    
    def pipeline_step_placeOrder(self, crypto_id):
        regime = self.MarketDetectionInstance.detect_market_regime(crypto_id)
        if regime == MarketRegime.PANIC:
            print(f"Market in PANIC for crypto {crypto_id}. No trades executed.")
            return
        data = self.db.get_crypto_data(crypto_id)
        if not data:
            print(f"No data available for crypto {crypto_id}.")
            return
        # Prendre les données les plus récentes
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
                stop_distance_pct=stop_distance_pct  # Utiliser le même calcul que pour SHORT
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
        actions = self.StopTpLogicInstance.check_all_current_trades()
        for action in actions:
            print(f"Executing action {action['action']} for trade ID {action['trade_id']} on take profit number {action['take_profit_number']}")
            self.StopTpLogicInstance.update_trade_status(action['trade_id'], action['take_profit_number'])
            print(f"P&L for trade ID {action['trade_id']}: {action['profit_loss']} with fees applied : {action['profit_loss'] - self.FeesModelInstance.calculate_fee(action['last_price'])}")
            self.initial_capital += action['profit_loss'] - self.FeesModelInstance.calculate_fee(action['last_price'])

    def run_pipeline(self, crypto_ids):
        self.pipeline_step_stopTpManagement()
        for crypto_id in crypto_ids:
            self.pipeline_step_placeOrder(crypto_id)


    def get_all_ids(self):
        return self.db.get_all_crypto_ids()


# Global pipeline instance
pipeline = None
crypto_ids_to_trade = None

def run_trading_cycle():
    """Execute one trading cycle"""
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
    global pipeline, crypto_ids_to_trade
    
    INTERVAL_MINUTES = 10
    
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
    
    # Initialize pipeline
    pipeline = CryptoBotPipeline()
    crypto_ids_to_trade = pipeline.get_all_ids()
    
    # Run first cycle immediately
    run_trading_cycle()
    
    # Schedule subsequent cycles
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