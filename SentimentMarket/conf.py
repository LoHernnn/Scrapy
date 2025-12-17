# ============================================================================
# SentimentMarket Configuration File
# ============================================================================

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
# Interval between data collection cycles (minutes)
COLLECTION_INTERVAL_MINUTES = 60

# ----------------------------------------------------------------------------
# SCRAPER CONFIGURATION
# ----------------------------------------------------------------------------
SCRAPER_CONFIG = {
        'html_dir': 'html_output',
        'headless': False,
        'timeout': 15
    }

SENTIMENT_MODEL_NAME = 'cardiffnlp/twitter-roberta-base-sentiment-latest'
FUZZY_MATCH_THRESHOLD = 80
TWEET_RETENTION_DAYS = 7
