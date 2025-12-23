class Trade_frequency_control:
    def __init__(self, min_trade_interval: int):
        self.min_trade_interval = min_trade_interval  # in seconds
        self.last_trade_time = {}

    def set_last_trade(self, crypto_id: int, trade_time: int):
        self.last_trade_time[crypto_id] = trade_time

    def can_trade(self, crypto_id: int, current_time: int) -> bool:
        last_time = self.last_trade_time.get(crypto_id)
        if last_time is None:
            return True
        return (current_time - last_time) >= self.min_trade_interval