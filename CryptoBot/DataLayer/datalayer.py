from database import DatabaseCryptoBot
from datetime import datetime

class datalayer:
    def __init__(self, db_config):
        self.db = DatabaseCryptoBot(db_config)
        self.db.connect()
    
    def get_all_cryptos(self):
        return self.db.get_all_cryptos()
    
    def get_crypto_data(self, crypto_id: int):
        data = self.db.get_all_crypto_informations(crypto_id)
        return data