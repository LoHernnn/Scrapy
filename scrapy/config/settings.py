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
MIN_TRADE_INTERVAL = 3600  # 1 heure minimum entre trades sur même crypto
TRADING_FEE_PERCENTAGE = 0.001  # 0.1% frais réalistes (Binance/Coinbase)
MAX_CORRELATION_EXPOSURE = 0.7
ENTRY_SCORE_THRESHOLD_LONG = 0.62  # Seuil plus strict pour entrer long (moins de trades)
ENTRY_SCORE_THRESHOLD_SHORT = -0.62  # Seuil plus strict pour entrer short (moins de trades)
TECHNICAL_WEIGHT = 0.90  # 90% poids technique (sentiment peu fiable)
SENTIMENT_WEIGHT = 0.10  # 10% poids sentiment (données limitées)

TECHNICAL_WEIGHTS = {
    'ema': 0.25,      # Trend following principal
    'macd': 0.20,     # Momentum
    'rsi': 0.18,      # Timing sur survente/surachat
    'sma': 0.12,      # Confirmation de tendance
    'volatility': 0.10,  # Réduit car pas directionnel
    'pivot': 0.08,    # Support/Résistance
    'fibo': 0.07      # Niveaux Fibonacci
}

PANIC_ATR_THRESHOLD = 0.05 
PANIC_VOLUME_RATIO = 2.0  
PANIC_FUNDING_RATE = 0.1  
TREND_RSI_UPPER = 55  # RSI > 55 pour tendance haussière
TREND_RSI_LOWER = 45  # RSI < 45 pour tendance baissière
RANGE_RSI_LOWER = 45 
RANGE_RSI_UPPER = 55 
ATR_PERIOD = 14  

RSI_OVERSOLD_EXTREME = 25  # Plus strict: uniquement les surventes extrêmes
RSI_OVERBOUGHT_EXTREME = 75  # Plus strict: uniquement les surachats extrêmes
RSI_OVERSOLD_MODERATE = 35  # Zone modérée de survente
RSI_OVERBOUGHT_MODERATE = 65  # Zone modérée de surachat

VOLATILITY_LOW_THRESHOLD = 1.5  # Seuil bas pour détecter faible volatilité
VOLATILITY_HIGH_THRESHOLD = 8.0  # Seuil haut pour volatilité élevée

RISK_HIGH_CONFIDENCE = 0.015  # 1.5% du capital pour signaux forts
RISK_MEDIUM_CONFIDENCE = 0.01  # 1% pour signaux moyens
RISK_LOW_CONFIDENCE = 0.005  # 0.5% pour signaux faibles

# Take Profit / Stop Loss weights - TP1 récupère 70% pour atteindre l'équilibre rapidement
TP_WEIGHTS = {
    1: 0.70,  # TP1: 70% de la position (sécuriser les gains rapidement)
    2: 0.20,  # TP2: 20% de la position 
    3: 0.10   # Runner: 10% restant pour maximiser si ça continue
}

# Sentiment minimum tweets - besoin de plus de données pour fiabilité
SENTIMENT_MIN_TWEETS = 15  # Minimum 15 tweets pour considérer le sentiment fiable
