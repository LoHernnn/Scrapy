# Risk Filters (garde-fous obligatoires)
#Empêcher l’algo de se suicider.
#IF daily_loss > 2% → STOP TRADING
#IF global_dd > 10% → KILL SWITCH
#IF already exposed to BTC AND new trade correlated > 0.8 → BLOCK
#IF major_event_soon → NO TRADE
#MAX_TRADES_PER_DAY = 5
#MIN_TIME_BETWEEN_TRADES = 30min
#Donnée	Utilité
#Correlation	Exposition
#Open interest	Crowded trade
import DataLayer.database as db
import RiskLayer.Daily_loss_limit as dll
import RiskLayer.Max_drawdown_controle as mdc
import RiskLayer.Correlation_exposure as ce

class RiskFilter:
    def __init__(self, db_config, DailyLossinstance: dll = None, MaxDrawdowninstance: mdc = None, CorrelationExposureinstance: ce = None):
        self.db_instance = db.DatabaseCryptoBot(db_config)
        self.daily_loss_instance = DailyLossinstance
        self.max_drawdown_instance = MaxDrawdowninstance
        self.correlation_exposure_instance = CorrelationExposureinstance
    
    def can_place_trade(self, new_crypto_id: int, current_capital: float) -> bool:
        # Check daily loss limit
        if self.daily_loss_instance:
            daily_loss = self.daily_loss_instance.can_trade()
            if daily_loss['can_trade'] is False:
                return False
        # Check max drawdown
        if self.max_drawdown_instance:
            if self.max_drawdown_instance.calculate_drawdown(current_capital):
                return False
        # Check correlation exposure
        if self.correlation_exposure_instance:
            correlation_check = self.correlation_exposure_instance.check_correlation_with_current_trades(new_crypto_id)
            if not correlation_check['can_trade']:
                return False
        return True
    
    def update_risk_parameters(self, daily_loss_limit: float = None, max_drawdown_percent: float = None, max_correlation_exposure: float = None):
        if daily_loss_limit is not None and self.daily_loss_instance:
            self.daily_loss_instance.update_max_daily_loss(daily_loss_limit)
        if max_drawdown_percent is not None and self.max_drawdown_instance:
            self.max_drawdown_instance.update_max_drawdown(max_drawdown_percent)
        if max_correlation_exposure is not None and self.correlation_exposure_instance:
            self.correlation_exposure_instance.update_max_correlation_exposure(max_correlation_exposure)