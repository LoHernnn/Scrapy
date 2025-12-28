from scrapy.data.database import CryptoDatabase as DatabaseCryptoBot
import scrapy.trading.RiskLayer.Daily_loss_limit as dll
import scrapy.trading.RiskLayer.Max_drawdown_controle as mdc
import scrapy.trading.RiskLayer.Correlation_exposure as ce
import scrapy.utils.logger as Logger

class RiskFilter:
    """Filter trading signals based on multiple risk management criteria.
    
    This class aggregates various risk checks (daily loss limits, drawdown limits,
    correlation exposure) to determine if a new trade can be safely placed. Acts as
    a gatekeeper to prevent trades that violate risk management rules.
    """
    
    def __init__(self, DailyLossinstance: dll = None, MaxDrawdowninstance: mdc = None, CorrelationExposureinstance: ce = None):
        """Initialize risk filter with optional risk management components.
        
        Args:
            DailyLossinstance (DailyLossLimit, optional): Daily loss limiter instance. Defaults to None.
            MaxDrawdowninstance (MaxDrawdownControl, optional): Maximum drawdown controller instance. Defaults to None.
            CorrelationExposureinstance (CorrelationExposure, optional): Correlation exposure manager instance. Defaults to None.
        """
        self.db_instance = DatabaseCryptoBot()
        self.daily_loss_instance = DailyLossinstance
        self.max_drawdown_instance = MaxDrawdowninstance
        self.correlation_exposure_instance = CorrelationExposureinstance
        self.logger = Logger.get_logger("RiskFilter")
    
    def can_place_trade(self, new_crypto_id: int, current_capital: float) -> bool:
        """Evaluate if a new trade can be placed based on all active risk checks.
        
        Sequentially evaluates multiple risk criteria:
        1. Daily loss limit - prevents trading if daily losses exceed threshold
        2. Maximum drawdown - blocks trades if portfolio drawdown too severe
        3. Correlation exposure - prevents overexposure to correlated assets
        
        Args:
            new_crypto_id (int): Cryptocurrency ID for the proposed trade
            current_capital (float): Current portfolio capital value
            
        Returns:
            bool: True if all risk checks pass, False if any check fails
        """
        if self.daily_loss_instance:
            daily_loss = self.daily_loss_instance.can_trade()
            if daily_loss['can_trade'] is False:
                self.logger.warning(f"Trade blocked for crypto {new_crypto_id}: Daily loss limit exceeded ({daily_loss.get('loss_pct', 0):.2f}%)")
                return False
        if self.max_drawdown_instance:
            if self.max_drawdown_instance.calculate_drawdown(current_capital):
                self.logger.warning(f"Trade blocked for crypto {new_crypto_id}: Max drawdown exceeded")
                return False
        if self.correlation_exposure_instance:
            correlation_check = self.correlation_exposure_instance.check_correlation_with_current_trades(new_crypto_id)
            if not correlation_check['can_trade']:
                self.logger.warning(f"Trade blocked for crypto {new_crypto_id}: Correlation exposure too high ({correlation_check.get('correlation', 0):.2f})")
                return False
        self.logger.info(f"Risk checks passed for crypto {new_crypto_id}")
        return True
    
    def update_risk_parameters(self, daily_loss_limit: float = None, max_drawdown_percent: float = None, max_correlation_exposure: float = None):
        """Dynamically update risk management parameters for all active components.
        
        Allows runtime adjustment of risk thresholds without recreating instances.
        Only updates parameters for components that were initialized (not None).
        
        Args:
            daily_loss_limit (float, optional): New daily loss limit percentage. Defaults to None.
            max_drawdown_percent (float, optional): New maximum drawdown threshold. Defaults to None.
            max_correlation_exposure (float, optional): New correlation exposure limit. Defaults to None.
        """
        if daily_loss_limit is not None and self.daily_loss_instance:
            self.daily_loss_instance.update_max_daily_loss(daily_loss_limit)
        if max_drawdown_percent is not None and self.max_drawdown_instance:
            self.max_drawdown_instance.update_max_drawdown(max_drawdown_percent)
        if max_correlation_exposure is not None and self.correlation_exposure_instance:
            self.correlation_exposure_instance.update_max_correlation_exposure(max_correlation_exposure)