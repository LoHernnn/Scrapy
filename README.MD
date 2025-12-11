# Cryptocurrency Data Collector & Dashboard

A complete full-stack application for collecting, analyzing, and visualizing cryptocurrency market data with technical indicators and real-time insights. This is only the first part of the project. The complete project is divided into three phases. Part 2 will focus on market sentiment analysis, and the final phase will involve building an AI model based on time-series data collected over at least six months, with the goal of developing a trading algorithm.

## Project Overview

This project provides an automated cryptocurrency data collection system combined with an interactive web dashboard. It continuously fetches data from multiple sources (CoinGecko, Binance), performs technical analysis, stores everything in a PostgreSQL database, and displays it through a modern React interface with interactive charts. 

### What This Project Does

1. **Automated Data Collection**: Runs on a configurable schedule to collect cryptocurrency data
2. **Multi-Source Integration**: Combines data from CoinGecko API and Binance exchange
3. **Technical Analysis**: Calculates RSI, MACD, moving averages, pivot points, and more
4. **Data Storage**: Organizes all data in a structured PostgreSQL database
5. **Web Dashboard**: Provides an intuitive interface to explore and analyze the data
6. **Interactive Charts**: Visualize historical trends with customizable metrics

### Use Cases

- **Crypto Traders**: Monitor technical indicators and market trends
- **Data Analysts**: Access structured cryptocurrency data for analysis
- **Developers**: Learn full-stack development with real-world APIs
- **Researchers**: Study cryptocurrency market behavior and correlations
- **Portfolio Managers**: Track multiple cryptocurrencies in one place

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                           │
│                   React Dashboard (Port 5173)                   │
│              [Search, Grid View, Detail Modal, Charts]          │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP Requests
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                      API MIDDLEWARE                             │
│                 Express Server (Port 3001)                      │
│              [/data, /crypto/:id, /history/:id]                 │
└────────────────────────────┬────────────────────────────────────┘
                             │ SQL Queries
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                         DATABASE                                │
│                   PostgreSQL (Port 5432)                        │
│   [cryptos, crypto_ranks, cyptos_data_base, cyptos_data_details,│
│                     cyptos_data_binance]                        │
└────────────────────────────┬────────────────────────────────────┘
                             ↑ Insert/Update
                             │
┌─────────────────────────────────────────────────────────────────┐
│                   DATA COLLECTOR (Backend)                      │
│                      Python Services                            │
│    [CoinGecko Service, Binance Service, Technical Analysis]    │
└────────────────────────────┬────────────────────────────────────┘
                             │ API Calls
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                      EXTERNAL APIs                              │
│              CoinGecko API  |  Binance API                      │
└─────────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
refonte/
│
├── backend/                          # Python data collector
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
│   │   └── database.py
│   ├── utils/                        # Utilities
│   │   ├── logger.py
│   │   └── metrics.py
│   ├── logs/                         # Cycle-based log files
│   └── README.md                     # Backend documentation
│
└── frontend/                         # React web application
    └── scrapy-front/
        ├── src/
        │   ├── App.jsx               # Main React component
        │   ├── App.css               # Styling
        │   └── main.jsx              # Entry point
        ├── serveur.js                # Express API middleware
        ├── package.json
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

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd refonte
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

The database configuration is in `backend/conf.py`:

```python
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "crypto",
    "user": "crypto",
    "password": "crypto",
}
```

### Step 3: Backend Setup (Python)

#### Install Python Dependencies

```bash
cd backend

# Create virtual environment (recommended with conda ou venv)

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

Edit `backend/conf.py` to adjust:
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

### Step 4: Frontend Setup (React + Node.js)

#### Install Node.js Dependencies

```bash
cd ../frontend/scrapy-front
npm install
```

This installs:
- React & React DOM
- Vite (build tool)
- Chart.js & react-chartjs-2
- Express & pg (PostgreSQL client)
- CORS

#### Configure API Endpoint (Optional)

If your backend API runs on a different host/port, edit `src/App.jsx`:

```javascript
// Change these URLs if needed
fetch("http://localhost:3001/data")
fetch(`http://localhost:3001/crypto/${cryptoId}`)
fetch(`http://localhost:3001/history/${cryptoId}`)
```

### Step 5: Running the Complete System

You need **three terminals** running simultaneously:

#### Terminal 1: Backend Data Collector

```bash
cd backend
python main.py
```

#### Terminal 2: Express API Middleware

```bash
cd frontend/scrapy-front
node serveur.js
```

You should see:
```
API backend OK sur http://localhost:3001
```

This provides the REST API bridge between React and PostgreSQL.

#### Terminal 3: React Development Server

```bash
cd frontend/scrapy-front
npm run dev
```

You should see:
```
VITE ready in XXX ms
➜  Local:   http://localhost:5173/
```

### Step 6: Access the Dashboard

Open your browser and navigate to:
```
http://localhost:5173
```

You should see the cryptocurrency dashboard with all available cryptos!

## 📚 Additional Resources

- **Backend Documentation**: `backend/README.md`
- **Frontend Documentation**: `frontend/scrapy-front/README.md`
- **Metrics Documentation**: `backend/docs/metrics_documentation.md`
- **CoinGecko API**: https://www.coingecko.com/en/api/documentation
- **Binance API**: https://binance-docs.github.io/apidocs/

## ⚖️ License

This project is for educational purposes only. Not financial advice.
