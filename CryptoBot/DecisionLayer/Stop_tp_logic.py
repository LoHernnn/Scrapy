import DataLayer.database as db
from utils.enum import TakeStop

class StopTpLogic:
    def __init__(self, db_config):
        self.db_instance = db.DatabaseCryptoBot(db_config)

    def check_price_crypto(self, crypto_id, entry_price, direction,
                        take_profit_pct: float, stop_loss_pct: float):

        last_price = self.db_instance.get_last_crypto_price(crypto_id)

        if direction == 1:  # LONG
            tp_price = entry_price * (1 + take_profit_pct / 100)
            sl_price = entry_price * (1 - stop_loss_pct / 100)
        else:  # SHORT
            tp_price = entry_price * (1 - take_profit_pct / 100)
            sl_price = entry_price * (1 + stop_loss_pct / 100)

        if (direction == 1 and last_price >= tp_price) or \
        (direction == -1 and last_price <= tp_price):
            return TakeStop.TakeProfit, last_price - entry_price, last_price

        if (direction == 1 and last_price <= sl_price) or \
        (direction == -1 and last_price >= sl_price):
            return TakeStop.StopLoss, entry_price - last_price, last_price

        return TakeStop.Hold, 0.0, last_price

        
    def check_all_current_trades(self):
        current_trades = self.db_instance.select_all_trades_current()
        results = []
        for trade in current_trades:
            if trade['status_1'] == 0:
                action, profit, last_price = self.check_price_crypto(trade['crypto_id'],trade['entry_price'],trade['direction'],trade['take_profit_1'],trade['stop_loss_1'])
                if action != TakeStop.Hold:
                    results.append({'trade_id': trade['id_trade'],
                                    'take_profit_number': 1,
                                    'action': action,
                                    'profit_loss': profit
                                    ,'last_price': last_price
                                    })
            if trade['status_2'] == 0:
                action, profit, last_price = self.check_price_crypto(trade['crypto_id'],trade['entry_price'],trade['direction'],trade['take_profit_2'],trade['stop_loss_2'])
                if action != TakeStop.Hold:
                    results.append({'trade_id': trade['id_trade'],
                                    'take_profit_number': 2,
                                    'action': action,
                                    'profit_loss': profit,
                                    'last_price': last_price
                                    })
            if trade['runner'] is not None and trade['status'] == 0:
                action, profit, last_price = self.check_price_crypto(trade['crypto_id'],trade['entry_price'],trade['direction'],trade['runner'],0)
                if action != TakeStop.Hold:
                    results.append({'trade_id': trade['id_trade'],
                                    'take_profit_number': 3,
                                    'action': action,
                                    'profit_loss': profit,
                                    'last_price': last_price
                                    })
        return results
    
    def update_trade_status(self, trade_id: int, take_profit_number: int):
        self.db_instance.update_trade_status(trade_id, take_profit_number,1)