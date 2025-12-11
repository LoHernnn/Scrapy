# ============================================================================
# CRYPTO DATA COLLECTOR - CONFIGURATION FILE
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
# API CONFIGURATION
# ----------------------------------------------------------------------------
# Base delay between API calls (seconds)
API_BASE_DELAY = 2
API_BACKOFF_DELAY = 60  # Delay on rate limit exceed (seconds)
NUMBER_OF_CRTYPTO_PER_REQUEST = 50
NUMBER_OF_PAGES_TO_FETCH = 2
