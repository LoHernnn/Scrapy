# ============================================================================
# CRYPTO DATA COLLECTOR - CONFIGURATION FILE
# ============================================================================

# ----------------------------------------------------------------------------
# RESET CONFIGURATION
# ----------------------------------------------------------------------------

DROP_MARKET_DATA_TABLES = False
DROP_SENTIMENT_DATA_TABLES = False
DROP_SCORES_AND_TRADES_TABLES = False
CREATE_ALL_TABLES_IF_MISSING = False
ADD_ALL_TWITTER_ACCOUNTS = False

# ----------------------------------------------------------------------------
# LOGGING CONFIGURATION
# ----------------------------------------------------------------------------

logger_folder = "default"

# ----------------------------------------------------------------------------
# DATABASE CONFIGURATION
# ----------------------------------------------------------------------------

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "crypto",
    "user": "crypto",
    "password": "crypto",
}
# ----------------------------------------------------------------------------
# DATA COLLECTION CONFIGURATION
# ----------------------------------------------------------------------------

SENTIMENT_COLLECTION_INTERVAL_MINUTES = 30
MARKET_DATA_COLLECTION_INTERVAL_MINUTES = 60 
TRADING_DECISION_INTERVAL_MINUTES = 15

# ----------------------------------------------------------------------------
# API CONFIGURATION
# ----------------------------------------------------------------------------

API_BASE_DELAY = 2 
API_BACKOFF_DELAY = 60 
NUMBER_OF_CRTYPTO_PER_REQUEST = 10
NUMBER_OF_PAGES_TO_FETCH = 1

# ----------------------------------------------------------------------------
# SCRAPER CONFIGURATION
# ----------------------------------------------------------------------------

SCRAPER_CONFIG = {
        'html_dir': 'html_output',
        'headless': False,
        'timeout': 15
    }

#SENTIMENT_MODEL_NAME = 'cardiffnlp/twitter-roberta-base-sentiment-latest'
#SENTIMENT_MODEL_NAME = 'ProsusAI/finbert'
SENTIMENT_MODEL_NAME = "yangheng/deberta-v3-base-absa-v1.1"
TWEET_RETENTION_DAYS = 7 

NITTER_INSTANCES = [
    "https://nitter.catsarch.com",
    "https://nitter.net",
    "https://nitter.tiekoetter.com/",
    "https://xcancel.com/",
    "https://nitter.poast.org",
    "https://nitter.privacyredirect.com",
    "https://lightbrd.com",
    "https://nuku.trabun.org/"
]

NITTER_MAX_RETRY_PER_INSTANCE = 3
NITTER_RETRY_DELAYS = [5, 10, 15] 

TWITTER_ACCOUNTS = ["BitcoinMagazine", "binance", "Bitcoin", "aixbt_agent", "lookonchain", "coinbase", "tier10k", "CoinbaseIntExch", "CoinbaseAssets", "sama", "Blockworks_", "VitalikButerin", "santimentfeed", 
                "CoinDesk", "bubblemaps", "KaikoData", "0xResearch", "0xngmi", "DegenerateNews", "cryptoquant_com", "whale_alert", "nansen_ai", "EricBalchunas", "JSeyff", "martyparty", "EleanorTerrett", "saylor", 
                "APompliano", "woonomic", "Pentosh1", "ansem", "bluntz_capital", "zachxbt", "WatcherGuru", "adam3us", "CryptoCred", "HsakaTrades", "rektcapital", "CryptoDonAlt", "IncomeSharks", "TheCryptoDog", 
                "CryptoHayes", "MikybullCrypto", "CredibleCrypto", "ColdBloodShill", "KillaXBT", "astronomer_zero", "100trillionUSD", "DocumentingBTC", "lopp", "cobie", "RaoulGMI", "scottmelker", "cz_binance", 
                "CathieDWood", "aantonop", "CamiRusso", "DTAPCAP", "girlgone_crypto", "Rewkang", "milesdeutscher", "elliotrades", "AlphaInsiders", "OnChainWizard", "BenArmstrongsX", "AltcoinDailyio", "cryptomanran", 
                "IvanOnTech", "intocryptoverse", "ErikVoorhees", "novogratz", "piovincenzo_", "ToneVays", "sassal0x", "tyler", "pierre_crypt0", "CryptoWendyO", "nickszabo4", "davidgokhshtein", "HaileyLennonBTC", 
                "justinsuntron", "danheld", "PeterMcCormack", "layahheilpern", "balajis", "elonmusk", "starkness", "glassnode", "chainalysis","SolanaFloor"]

# ----------------------------------------------------------------------------
# TRADING CONFIGURATION
# ----------------------------------------------------------------------------

INITIAL_CAPITAL = 10000.0 
MAX_DAILY_LOSS_PERCENT = 2.0
MAX_DRAWDOWN_PERCENT = 20.0
MIN_TRADE_INTERVAL = 7200
TRADING_FEE_PERCENTAGE = 0.005
MAX_CORRELATION_EXPOSURE = 0.7
ENTRY_SCORE_THRESHOLD_LONG = 0.55
ENTRY_SCORE_THRESHOLD_SHORT = -0.55
TECHNICAL_WEIGHT = 0.85
SENTIMENT_WEIGHT = 0.15

TECHNICAL_WEIGHTS = {
    'ema': 0.22,
    'macd': 0.22,
    'rsi': 0.13,
    'sma': 0.09,
    'volatility': 0.20,
    'pivot': 0.07,
    'fibo': 0.07
}

PANIC_ATR_THRESHOLD = 0.05 
PANIC_VOLUME_RATIO = 2.0  
PANIC_FUNDING_RATE = 0.1  
TREND_RSI_UPPER = 52  
TREND_RSI_LOWER = 48  
RANGE_RSI_LOWER = 48 
RANGE_RSI_UPPER = 52 
ATR_PERIOD = 14  

RSI_OVERSOLD_EXTREME = 35 
RSI_OVERBOUGHT_EXTREME = 65 
RSI_OVERSOLD_MODERATE = 42 
RSI_OVERBOUGHT_MODERATE = 58 

VOLATILITY_LOW_THRESHOLD = 2.0  
VOLATILITY_HIGH_THRESHOLD = 5.0  

RISK_HIGH_CONFIDENCE = 0.02 
RISK_MEDIUM_CONFIDENCE = 0.015  
RISK_LOW_CONFIDENCE = 0.01
