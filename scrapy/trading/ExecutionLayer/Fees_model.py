import scrapy.utils.logger as Logger
import scrapy.config.settings as conf

class FeesModel:
    """Calculate trading fees for buy and sell transactions.
    
    Supports both percentage-based fees and flat fees. Percentage fees are
    calculated on transaction amount, while flat fees are added as a constant.
    """
    
    def __init__(self, fee_percentage: float = None, fee_flat: float = 0.0):
        """Initialize the fees model with configurable fee structure.
        
        Args:
            fee_percentage (float, optional): Fee as a decimal percentage (e.g., 0.001 for 0.1%). Defaults to conf.TRADING_FEE_PERCENTAGE.
            fee_flat (float, optional): Flat fee amount added to each transaction. Defaults to 0.0.
        """
        if fee_percentage is None:
            fee_percentage = conf.TRADING_FEE_PERCENTAGE
        self.fee_percentage = fee_percentage
        self.fee_flat = fee_flat
        self.logger = Logger.get_logger("FeesModel")

    def calculate_fee(self, transaction_amount: float) -> float:
        """Calculate total fee for a transaction.
        
        Combines percentage-based and flat fees. Formula:
        total_fee = (transaction_amount × fee_percentage) + fee_flat
        
        Args:
            transaction_amount (float): Total transaction value in base currency
            
        Returns:
            float: Total fee amount to be charged
        """
        fee = (transaction_amount * self.fee_percentage) + self.fee_flat
        self.logger.debug(f"Transaction fee calculated: {fee:.4f} (amount: {transaction_amount:.2f}, rate: {self.fee_percentage*100:.2f}%)")
        return fee