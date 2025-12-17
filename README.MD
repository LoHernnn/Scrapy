# Cryptocurrency Data Collector & Dashboard with Sentiment Analysis

A complete full-stack application for collecting, analyzing, and visualizing cryptocurrency market data with technical indicators, Twitter sentiment analysis, and real-time insights. This project combines market data analysis with social media sentiment to provide comprehensive cryptocurrency insights.

## Project Overview

This project provides an automated cryptocurrency data collection system combined with sentiment analysis and an interactive web dashboard. It continuously fetches data from multiple sources (CoinGecko, Binance, Twitter/X), performs technical analysis, analyzes sentiment from crypto-related tweets, stores everything in a PostgreSQL database, and displays it through a modern React interface with interactive charts.

### What This Project Does

1. **Automated Data Collection**: Runs on a configurable schedule to collect cryptocurrency market data
2. **Multi-Source Integration**: Combines data from CoinGecko API and Binance exchange
3. **Technical Analysis**: Calculates RSI, MACD, moving averages, pivot points, and more
4. **Twitter Sentiment Analysis**: Scrapes and analyzes tweets from crypto influencers and news sources
5. **AI-Powered Sentiment Scoring**: Uses transformer models (RoBERTa) to score tweet sentiment
6. **Data Storage**: Organizes all data in a structured PostgreSQL database
7. **Web Dashboard**: Provides an intuitive interface to explore and analyze the data
8. **Interactive Charts**: Visualize historical trends with customizable metrics
9. **Real-time Tweets Display**: View the latest 3 tweets for each cryptocurrency with sentiment scores

### Use Cases

- **Crypto Traders**: Monitor technical indicators, market trends, and social sentiment
- **Sentiment Analysts**: Track how social media sentiment correlates with price movements
- **Data Analysts**: Access structured cryptocurrency and sentiment data for analysis
- **Developers**: Learn full-stack development with real-world APIs and ML models
- **Researchers**: Study cryptocurrency market behavior and social media influence
- **Portfolio Managers**: Track multiple cryptocurrencies with market and sentiment data in one place

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                           │
│                   React Dashboard (Port 5173)                   │
│    [Search, Grid View, Detail Modal, Charts, Tweets Display]   │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP Requests
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                      API MIDDLEWARE                             │
│                 Express Server (Port 3001)                      │
│        [/data, /crypto/:id, /history/:id, /tweets/:id]         │
└────────────────────────────┬────────────────────────────────────┘
                             │ SQL Queries
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                         DATABASE                                │
│                   PostgreSQL (Port 5432)                        │
│   [cryptos, crypto_ranks, cyptos_data_base, cyptos_data_details,│
│    cyptos_data_binance, crypto_sentiment_scores, tweet_hash,   │
│              tweet_sentiments, tweet_crypto]                    │
└──────────────┬──────────────────────────────┬───────────────────┘
               ↑ Insert/Update                ↑ Insert/Update
               │                              │
┌──────────────┴──────────────┐  ┌───────────┴───────────────────┐
│   DATA COLLECTOR (Backend)  │  │  SENTIMENT MARKET (Backend)   │
│      Python Services        │  │      Python Services          │
│ [CoinGecko, Binance,        │  │  [Twitter Scraper, Sentiment  │
│  Technical Analysis]        │  │   Analyzer, NLP Models]       │
└──────────────┬──────────────┘  └───────────┬───────────────────┘
               │ API Calls                    │ Web Scraping
               ↓                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      EXTERNAL SOURCES                           │
│    CoinGecko API | Binance API | Twitter/X (via Nitter)        │
└─────────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
Scrapy/
│
├── Backend/                          # Python market data collector
│   ├── main.py                       # Main orchestrator with scheduling
│   ├── conf.py                       # Configuration file
│   ├── collectors/                   # API data fetchers
│   │   ├── coingecko_collector.py
│   │   └── binance_collector.py
│   ├── services/                     # Business logic services
│   │   ├── crypto_listing_service.py
│   │   ├── coingecko_service.py
│   │   ├── binance_service.py
│   │   └── technical_analysis_service.py
│   ├── models/                       # Data models
│   │   └── crypto.py
│   ├── database/                     # Database operations
│   │   └── database.py               # CryptoDatabase class (OOP)
│   ├── utils/                        # Utilities
│   │   ├── logger.py
│   │   └── metrics.py
│   ├── logs/                         # Cycle-based log files
│   └── README.md                     # Backend documentation
│
├── SentimentMarket/                  # Python sentiment analyzer
│   ├── main.py                       # Sentiment analysis orchestrator
│   ├── conf.py                       # Sentiment configuration
│   ├── Scraper/                      # Twitter data collection
│   │   └── nitterScraper.py          # Nitter-based Twitter scraper
│   ├── SentimentAnalysis/            # NLP sentiment analysis
│   │   ├── sentimentAnalyzer.py      # Per-crypto sentiment scoring
│   │   └── sentimentGeneralAnalyser.py # Overall sentiment analysis
│   ├── ServiceManager/               # Service coordination
│   │   └── coordinateur.py
│   ├── Database/                     # Database operations
│   │   └── database.py               # SentimentDatabase class
│   ├── utils/                        # Utilities
│   │   └── logger.py
│   ├── logs/                         # Sentiment analysis logs
│   ├── html_output/                  # Scraped Twitter HTML (gitignored)
│   └── README.md                     # Sentiment module documentation
│
└── Frontend/                         # React web application
    └── scrapy-front/
        ├── src/
        │   ├── App.jsx               # Main React component
        │   ├── App.css               # Styling with sentiment colors
        │   └── main.jsx              # Entry point
        ├── serveur.js                # Express API middleware (enhanced)
        ├── package.json
        ├── .gitignore
        └── README.md                 # Frontend documentation
```

## 🚀 Complete Installation Guide

### Prerequisites

Before starting, ensure you have:

- **Operating System**: Windows, macOS, or Linux
- **Python**: Version 3.10 or higher
- **Node.js**: Version 18 or higher (includes npm)
- **PostgreSQL**: Version 12 or higher
- **Git**: For cloning the repository
- **Chrome/Chromium**: For Selenium-based Twitter scraping (or Firefox with geckodriver)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd Scrapy
```

### Step 2: Database Setup

#### Install PostgreSQL

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**macOS** (using Homebrew):
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Windows**:
- Download installer from [postgresql.org](https://www.postgresql.org/download/windows/)
- Run installer and follow the wizard
- Remember the password you set for the postgres user

#### Create Database and User

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Inside PostgreSQL prompt, run:
CREATE DATABASE crypto;
CREATE USER crypto WITH PASSWORD 'crypto';
GRANT ALL PRIVILEGES ON DATABASE crypto TO crypto;
\q
```

#### Configure Database Connection

The database configuration is in `Backend/conf.py`:

```python
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "crypto",
    "user": "crypto",
    "password": "crypto",
}
```

### Step 3: Backend Setup (Python - Market Data Collector)

#### Install Python Dependencies

```bash
cd Backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install psycopg2-binary pandas numpy requests schedule
```

#### Install TA-Lib (Technical Analysis Library)

**Ubuntu/Debian**:
```bash
sudo apt-get install build-essential
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
pip install TA-Lib
```

**macOS**:
```bash
brew install ta-lib
pip install TA-Lib
```

**Windows**:
- Download pre-built wheel from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib)
- Install: `pip install TA_Lib-0.4.XX-cpXX-cpXX-win_amd64.whl`

#### Configure Backend

Edit `Backend/conf.py` to adjust:
- `COLLECTION_INTERVAL_MINUTES`: How often to collect data (default: 60 minutes)
- `DB_CONFIG`: Database credentials
- `API_BASE_DELAY`: Delay between API calls to avoid rate limits

#### Test Backend Connection

```bash
python main.py
```

You should see:
```
╔═══════════════════════════════════════════════════════════╗
║               CRYPTO DATA COLLECTOR SERVICE               ║
║  Mode: Continuous crypto data collection                  ║
║  Interval: Every 60 minutes                               ║
╚═══════════════════════════════════════════════════════════╝
```

Press `Ctrl+C` to stop after confirming it works.

### Step 4: SentimentMarket Setup (Python - Twitter Sentiment Analyzer)

#### Install Sentiment Analysis Dependencies

```bash
cd ../SentimentMarket

# Use the same virtual environment or create a new one
# source ../Backend/venv/bin/activate  # Or create new venv

# Install dependencies
pip install psycopg2-binary selenium transformers torch fuzzywuzzy python-Levenshtein
```

#### Install Selenium WebDriver

**Chrome** :
```bash
# Download ChromeDriver matching your Chrome version
# From: https://chromedriver.chromium.org/downloads
# Or use webdriver-manager:
pip install webdriver-manager
```

#### Configure SentimentMarket

Edit `SentimentMarket/conf.py`:
- `COLLECTION_INTERVAL_MINUTES`: How often to scrape tweets (default: 60 minutes)
- `SCRAPER_CONFIG`: Browser settings (headless mode, timeout)
- `SENTIMENT_MODEL_NAME`: Hugging Face model (default: cardiffnlp/twitter-roberta-base-sentiment-latest)
- `FUZZY_MATCH_THRESHOLD`: For crypto name matching (default: 80)
- `TWEET_RETENTION_DAYS`: How long to keep old tweets (default: 7 days)

#### Test Sentiment Analyzer

```bash
python main.py
```

The first run will download the sentiment analysis model (~500MB). You should see the scraper collecting tweets and analyzing sentiment.

Press `Ctrl+C` to stop after confirming it works.

### Step 5: Frontend Setup (React + Node.js)

#### Install Node.js Dependencies

```bash
cd ../Frontend/scrapy-front
npm install
```

This installs:
- React & React DOM
- Vite (build tool)
- Chart.js & react-chartjs-2
- Express & pg (PostgreSQL client)
- CORS

#### Configure API Endpoint (Optional)

If your Backend API runs on a different host/port, edit `src/App.jsx`:

```javascript
// Change these URLs if needed
fetch("http://localhost:3001/data")
fetch(`http://localhost:3001/crypto/${cryptoId}`)
fetch(`http://localhost:3001/history/${cryptoId}`)
fetch(`http://localhost:3001/tweets/${cryptoId}`)
```

### Step 6: Running the Complete System

You need **four terminals** running simultaneously:

#### Terminal 1: Backend Data Collector (Market Data)

```bash
cd Backend
python main.py
```

This collects market data, technical indicators, and stores them in PostgreSQL.

#### Terminal 2: SentimentMarket (Twitter Sentiment Analysis)

```bash
cd SentimentMarket
python main.py
```

This scrapes tweets, analyzes sentiment, and updates sentiment scores in the database. Make sure that the Backend has completed at least one cycle before launching this script.

#### Terminal 3: Express API Middleware

```bash
cd Frontend/scrapy-front
node serveur.js
```

You should see:
```
API Backend OK sur http://localhost:3001
```

This provides the REST API bridge between React and PostgreSQL, including sentiment data.

#### Terminal 4: React Development Server

```bash
cd Frontend/scrapy-front
npm run dev
```

You should see:
```
VITE ready in XXX ms
➜  Local:   http://localhost:5173/
```

### Step 7: Access the Dashboard

Open your browser and navigate to:
```
http://localhost:5173
```

You should see the cryptocurrency dashboard with:
- Market data cards with sentiment grades (24h and 12h scores)
- Search functionality
- Detailed modals with technical indicators
- Interactive charts
- Recent tweets with sentiment analysis for each crypto

## Key Features

### Market Data Dashboard
- **Real-time crypto cards** displaying price, market cap, 24h change
- **Sentiment grades** showing social media sentiment (0-10 scale)
- **Search and filter** by name or symbol
- **Responsive grid layout** with hover effects

### Detailed Crypto View
- **Market data**: Price, high/low, volume, dominance, ATH
- **Technical indicators**: RSI, MACD, SMA/EMA, Fibonacci levels, Pivot points
- **Binance data**: Funding rate, open interest, order book
- **Interactive charts**: Customizable metrics overlay
- **Recent tweets**: Last 3 tweets with account, date, and sentiment score

### Backend Services
- **OOP Database classes** (CryptoDatabase, SentimentDatabase)
- **Automated scheduling** with configurable intervals
- **Comprehensive logging** per collection cycle
- **Error handling** and retry mechanisms
- **Modular architecture** for easy extension

## Database Schema

### Market Data Tables
- `cryptos`: Core cryptocurrency information
- `crypto_ranks`: Market cap rankings
- `cyptos_data_base`: Price, volume, market cap, dominance
- `cyptos_data_details`: Technical indicators (RSI, MACD, SMA, EMA, etc.)
- `cyptos_data_binance`: Binance-specific data (funding rate, order book)

### Sentiment Analysis Tables
- `crypto_sentiment_scores`: Aggregated sentiment scores (12h and 24h)
- `tweet_hash`: Unique tweet identifiers
- `tweet_sentiments`: Tweet content, account, timestamp
- `tweet_crypto`: Links tweets to cryptos with sentiment scores
- `account`: Twitter accounts being monitored

## Sentiment Analysis Details

The sentiment analysis uses:
- **Model**: `cardiffnlp/twitter-roberta-base-sentiment-latest` (RoBERTa transformer)
- **Scraping**: Selenium-based scraper targeting Nitter instances
- **Matching**: Fuzzy string matching to identify crypto mentions in tweets
- **Scoring**: Continuous sentiment scores (-1 to +1)
- **Aggregation**: 12-hour and 24-hour rolling sentiment averages
- **Display**: Color-coded sentiment labels (Positive/Neutral/Negative)

## 📚 Additional Resources

- **Backend Documentation**: `Backend/README.md`
- **SentimentMarket Documentation**: `SentimentMarket/README.md`
- **Frontend Documentation**: `Frontend/scrapy-front/README.md`
- **Metrics Documentation**: `Backend/utils/metrics_documentation.md`
- **CoinGecko API**: https://www.coingecko.com/en/api/documentation
- **Binance API**: https://binance-docs.github.io/apidocs/
- **Hugging Face Models**: https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment-latest
- **Nitter**: https://github.com/zedeus/nitter (Twitter Frontend)

## ⚖️ License

This project is for educational purposes only. Not financial advice. Use at your own risk.
