# SentimentMarket - Crypto Twitter Sentiment Analysis

**SentimentMarket** is an automated sentiment analysis system that tracks cryptocurrency sentiment from Twitter accounts using Nitter (Twitter mirror), analyzes tweets with AI models, and stores sentiment scores in PostgreSQL for time-series analysis.

---

## ✨ Features

- **Automated Twitter Scraping**: Scrapes tweets from specified Twitter accounts via Nitter (no API key required)
- **Entity-Level Sentiment Analysis**: Detects cryptocurrency mentions and analyzes sentiment per entity using HuggingFace transformers
- **Context Segmentation**: Prevents sentiment contamination between multiple cryptos mentioned in the same tweet
- **PostgreSQL Storage**: Stores tweets, sentiment scores, and time-series aggregates
- **Time-Based Filtering**: Calculates 12h and 24h sentiment averages
- **Automatic Cleanup**: Purges tweets older than 7 days to maintain database size
- **Scheduled Execution**: Runs continuously at configurable intervals
- **Comprehensive Logging**: Tracks all operations with timestamped log files per cycle

---

## 🏗️ Architecture

```
┌─────────────────┐
│  Twitter/Nitter │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ NitterScraper   │ ◄── Selenium + BeautifulSoup
│  (Scraper/)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│SentimentAnalyzer│ ◄── HuggingFace Transformers
│(SentimentAnal/) │     (twitter-roberta-base-sentiment)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│SentimentDatabase│ ◄── PostgreSQL
│   (Database/)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│SentimentGeneral │ ◄── Aggregates 12h/24h scores
│   Analyser      │
└─────────────────┘
```

**Orchestration**: `SentimentCoordinator` (ServiceManager/) manages the entire pipeline.

---

## 📦 Installation

### Prerequisites

- **Python 3.10+**
- **PostgreSQL 12+**
- **Google Chrome** (for Selenium WebDriver)
- **Git**

### Step 1: Clone the Repository

```bash
git clone <repository_url>
cd SentimentMarket
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt** should contain:
```txt
psycopg2-binary
selenium
webdriver-manager
beautifulsoup4
lxml
transformers
torch
unidecode
rapidfuzz
schedule
```

### Step 3: Download Sentiment Model (First Run)

The HuggingFace model (`cardiffnlp/twitter-roberta-base-sentiment-latest`) will download automatically on first run (~500MB). Ensure you have a stable internet connection.

---

## ⚙️ Configuration

Edit `conf.py` to customize the system:

### Database Configuration
```python
DB_CONFIG = {
    "host": "localhost",        # PostgreSQL host
    "port": 5432,               # PostgreSQL port
    "database": "crypto",       # Database name
    "user": "crypto",           # Database user
    "password": "crypto",       # Database password
}
```

### Scraper Configuration
```python
SCRAPER_CONFIG = {
    'html_dir': 'html_output',  # Directory to save HTML files
    'headless': False,          # Run Chrome in headless mode (True/False)
    'timeout': 15               # Page load timeout in seconds
}
```

### Sentiment Analysis Configuration
```python
SENTIMENT_MODEL_NAME = 'cardiffnlp/twitter-roberta-base-sentiment-latest'
FUZZY_MATCH_THRESHOLD = 80      # Fuzzy matching threshold (0-100) for crypto detection
TWEET_RETENTION_DAYS = 7        # Auto-delete tweets older than N days
```

### Execution Configuration
```python
COLLECTION_INTERVAL_MINUTES = 60  # Run sentiment analysis every N minutes
logger_folder = "default"         # Log folder name (auto-generated per cycle)
```

---

## 🗄️ Database Setup

### Step 1: Create PostgreSQL Database

Check the readme file in the Backend.

### Step 2: Create Required Tables

The system will automatically create these tables on first run:
- `tweet_hash` - Master table for tweet IDs
- `tweet_sentiments` - Tweet content and metadata
- `tweet_crypto` - Junction table linking tweets to cryptos with sentiment scores
- `crypto_sentiment_scores` - Time-series aggregated sentiment data
- `account` - Twitter accounts being tracked

### Step 3: Add Twitter Accounts to Track

```sql
INSERT INTO account (account_name) VALUES
    ('santimentfeed'),
    ('CoinDesk'),
    ('TheBittensorHub'),
    ('cryptoquant_com');
```

---

## 🚀 Usage

### Run Once (Single Execution)

```bash
python main.py
```

Press `Ctrl+C` to stop after the first cycle.

### Run Continuously (Scheduled)

The system runs automatically every `COLLECTION_INTERVAL_MINUTES` (default: 60 minutes):

```bash
python main.py
```

**Output:**
```
╔═══════════════════════════════════════════════════════════╗
║               CRYPTO SENTIMENT SERVICE                    ║
║                                                           ║
║  Mode: Continuous crypto sentiment analysis               ║
║  Interval: Every 60 minutes                               ║
║                                                           ║
║  Press Ctrl+C to stop the service                         ║
╚═══════════════════════════════════════════════════════════╝

2025-12-17 14:30:00 - NitterScraper - INFO - Scraping santimentfeed...
2025-12-17 14:30:05 - NitterScraper - INFO - ✓ HTML saved: html_output/twitter_search_santimentfeed.html
2025-12-17 14:30:06 - NitterScraper - INFO - santimentfeed: 42 tweets parsed
...
```

---

## 🔍 How It Works

### 1. **Scraping (NitterScraper)**
   - Connects to `https://nitter.net/{account}` using Selenium WebDriver
   - Extracts tweets using BeautifulSoup (tweet content, timestamp, author)
   - Saves HTML to `html_output/` for debugging
   - Returns list of tweet dictionaries with content hash for deduplication

### 2. **Sentiment Analysis (SentimentAnalyzer)**
   - **Entity Detection**: Uses fuzzy matching (rapidfuzz) to find crypto names/symbols in tweet text
   - **Context Segmentation**: Extracts text segment for each entity (from entity start to next entity)
   - **Sentiment Scoring**: Analyzes each segment with HuggingFace transformer model
   - **Output**: Dictionary of `{crypto_name: sentiment_score}` where score ∈ [-1, +1]
     - **-1**: Very negative
     - **0**: Neutral
     - **+1**: Very positive

   **Example:**
   ```
   Tweet: "Solana network down again. However, Bitcoin breaks $100K!"
   
   Segments:
   - "Solana network down again. However," → Solana: -0.85
   - "Bitcoin breaks $100K!" → Bitcoin: +0.92
   ```

### 3. **Database Storage (SentimentDatabase)**
   - Checks if tweet already exists (by hash)
   - Inserts into `tweet_hash` (auto-incremented ID)
   - Inserts into `tweet_sentiments` (content, timestamp, account)
   - Links to cryptos in `tweet_crypto` (tweet_id, crypto_id, sentiment_score)

### 4. **Aggregation (SentimentGeneralAnalyser)**
   - Retrieves all sentiments for each crypto from last 12h and 24h
   - Calculates average scores and tweet counts
   - Inserts into `crypto_sentiment_scores` for time-series tracking

### 5. **Cleanup (SentimentDatabase.update_database)**
   - Automatically runs to delete tweets older than `TWEET_RETENTION_DAYS` (default: 7 days)
   - Cascade deletes from `tweet_crypto`, `tweet_sentiments`, `tweet_hash`

---

## 📊 Logging

Logs are saved to `logs/cycle_{timestamp}/` with separate files per component:

- `NitterScraper_*.log`: Scraping operations
- `SentimentAnalyzer_*.log`: Sentiment analysis details
- `SentimentDatabase_*.log`: Database operations
- `SentimentCoordinator_*.log`: Pipeline orchestration

**Log Format:**
```
2025-12-17 14:30:00 - SentimentDatabase - INFO - Tweet hash saved with ID 42
2025-12-17 14:30:01 - SentimentAnalyzer - INFO - Analyzed crypto_id 1: 12h=0.45 (12 tweets), 24h=0.38 (23 tweets)
```

