import scrapy.utils.logger as Logger
import scrapy.config.settings as conf

class Trade_frequency_control:
    """Control the frequency of trades to prevent overtrading.
    
    Enforces a minimum time interval between consecutive trades for each cryptocurrency,
    preventing excessive trading activity and reducing transaction costs.
    """
    
    def __init__(self, min_trade_interval: int = None):
        """Initialize trade frequency control with minimum interval between trades.
        
        Args:
            min_trade_interval (int, optional): Minimum seconds between trades for same crypto. Defaults to conf.MIN_TRADE_INTERVAL.
        """
        if min_trade_interval is None:
            min_trade_interval = conf.MIN_TRADE_INTERVAL
        self.min_trade_interval = min_trade_interval
        self.last_trade_time = {}
        self.logger = Logger.get_logger("TradeFrequencyControl")

    def set_last_trade(self, crypto_id: int, trade_time: int):
        """Record the timestamp of the last trade for a cryptocurrency.
        
        Updates the internal tracking to enforce frequency control on subsequent trades.
        
        Args:
            crypto_id (int): Cryptocurrency identifier
            trade_time (int): Unix timestamp of the trade execution
        """
        self.last_trade_time[crypto_id] = trade_time

    def can_trade(self, crypto_id: int, current_time: int) -> bool:
        """Check if enough time has passed since last trade to allow a new one.
        
        Compares elapsed time since last trade against minimum interval threshold.
        Always allows first trade for a cryptocurrency.
        
        Args:
            crypto_id (int): Cryptocurrency identifier to check
            current_time (int): Current Unix timestamp
            
        Returns:
            bool: True if trade is allowed, False if blocked by frequency control
        """
        last_time = self.last_trade_time.get(crypto_id)
        if last_time is None:
            self.logger.debug(f"Crypto {crypto_id}: First trade allowed")
            return True
        time_since_last = current_time - last_time
        can_proceed = time_since_last >= self.min_trade_interval
        if not can_proceed:
            self.logger.info(f"Crypto {crypto_id}: Trade blocked by frequency control ({time_since_last}s < {self.min_trade_interval}s)")
        return can_proceed