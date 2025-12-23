class FeesModel:
    def __init__(self, fee_percentage: float = 0.005, fee_flat: float = 0.0):
        self.fee_percentage = fee_percentage
        self.fee_flat = fee_flat

    def calculate_fee(self, transaction_amount: float) -> float:
        return (transaction_amount * self.fee_percentage) + self.fee_flat