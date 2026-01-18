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
                "APompliano", "woonomic", "Pentosh1", "bluntz_capital", "zachxbt", "WatcherGuru", "adam3us", "CryptoCred", "HsakaTrades", "rektcapital", "IncomeSharks", "TheCryptoDog", 
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
MIN_TRADE_INTERVAL = 3600  
TRADING_FEE_PERCENTAGE = 0.001  
MAX_CORRELATION_EXPOSURE = 0.7
ENTRY_SCORE_THRESHOLD_LONG = 0.62 
ENTRY_SCORE_THRESHOLD_SHORT = -0.62  
TECHNICAL_WEIGHT = 0.90  
SENTIMENT_WEIGHT = 0.10 

TECHNICAL_WEIGHTS = {
    'ema': 0.25,      # Trend following principal
    'macd': 0.20,     # Momentum
    'rsi': 0.18,      # Timing 
    'sma': 0.12,     
    'volatility': 0.10,  
    'pivot': 0.08,   
    'fibo': 0.07      
}

PANIC_ATR_THRESHOLD = 0.05 
PANIC_VOLUME_RATIO = 2.0  
PANIC_FUNDING_RATE = 0.1  
TREND_RSI_UPPER = 55  
TREND_RSI_LOWER = 45  
RANGE_RSI_LOWER = 45 
RANGE_RSI_UPPER = 55 
ATR_PERIOD = 14  

RSI_OVERSOLD_EXTREME = 25  
RSI_OVERBOUGHT_EXTREME = 75 
RSI_OVERSOLD_MODERATE = 35 
RSI_OVERBOUGHT_MODERATE = 65

VOLATILITY_LOW_THRESHOLD = 1.5 
VOLATILITY_HIGH_THRESHOLD = 8.0

RISK_HIGH_CONFIDENCE = 0.015
RISK_MEDIUM_CONFIDENCE = 0.01
RISK_LOW_CONFIDENCE = 0.005 

TP_WEIGHTS = {
    1: 0.70, 
    2: 0.20,  
    3: 0.10   
}

# ----------------------------------------------------------------------------
# TRAILING STOP CONFIGURATION
# ----------------------------------------------------------------------------

# Trailing stop percentage: SL moves up at this ratio of the price gain
# Example: 0.33 means if price goes up 3%, trailing SL will be at +1% from entry
RUNNER_TRAILING_STOP_RATIO = 0.33

# Minimum profit to lock before trailing stop activates (percentage)
RUNNER_MIN_PROFIT_TO_TRAIL = 1.0

# Dynamic TP2 adjustment based on score strength
TP2_SCORE_MULTIPLIER = 1.5  # TP2 increases by this factor for high-confidence trades

# Dynamic runner adjustment based on score strength  
RUNNER_SCORE_MULTIPLIER = 2.0  # Runner increases by this factor for high-confidence trades

# ----------------------------------------------------------------------------
# INERTIA CUT-OFF CONFIGURATION
# ----------------------------------------------------------------------------

# Time in hours after which stagnant trades are evaluated for exit
INERTIA_TIMEOUT_HOURS = 4

# Price movement threshold (%) - trade is "stagnant" if price moved less than this
INERTIA_STAGNATION_THRESHOLD_PCT = 0.5

# Minimum score required to keep a stagnant trade open (re-evaluation threshold)
INERTIA_MIN_SCORE_TO_KEEP = 0.3

# ----------------------------------------------------------------------------
# CAPITAL REINJECTION CONFIGURATION
# ----------------------------------------------------------------------------

# Enable/disable capital reinjection feature
ENABLE_CAPITAL_REINJECTION = True

# Minimum profit percentage before considering reinjection
REINJECTION_MIN_PROFIT_PCT = 1.5

# Reinjection amount as percentage of original position
REINJECTION_AMOUNT_PCT = 0.25

# Maximum number of reinjections per trade
MAX_REINJECTIONS_PER_TRADE = 2

# Minimum score required for reinjection (must still be a valid signal)
REINJECTION_MIN_SCORE = 0.5

SENTIMENT_MIN_TWEETS = 15  
