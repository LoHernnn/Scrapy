# Crypto Data Collector - Backend

Python Backend service for collecting, processing, and storing cryptocurrency market data from multiple sources (CoinGecko, Binance) into PostgreSQL.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [Logging](#logging)
- [API Integration](#api-integration)

---

## Features

- **Multi-source data collection**: CoinGecko + Binance APIs
- **Automated scheduling**: Configurable collection cycles
- **Technical analysis**: RSI, MACD, SMA/EMA, Pivot Points, Fibonacci levels
- **PostgreSQL storage**: Structured database with time-series data
- **Comprehensive logging**: Cycle-based log organization
- **Rate limiting handling**: Automatic retry with exponential backoff
- **Error resilience**: Graceful error handling and recovery

---

## Architecture

```
┌─────────────────┐
│   Main Service  │  ← Scheduler & Orchestrator
└────────┬────────┘
         │
    ┌────┴─────┐
    │ Services │
    └────┬─────┘
         │
    ┌────┴─────────────────────┐
    │                          │
┌───▼────────┐        ┌───────▼──────┐
│ Collectors │        │   Database   │
│  CoinGecko │        │  PostgreSQL  │
│  Binance   │        └──────────────┘
└────────────┘
```

### Components:

1. **Services**: Business logic layer
   - `CryptoListingService`: Manages crypto list and caching
   - `CoingeckoService`: Market data from CoinGecko
   - `BinanceService`: Order book & futures data from Binance
   - `TechnicalAnalysisService`: Technical indicators calculation

2. **Collectors**: API interaction layer
   - `CoinGeckoCollector`: CoinGecko API wrapper
   - `BinanceCollector`: Binance API wrapper

3. **Models**: Data structures
   - `Crypto`: Cryptocurrency entity
   - `MarketData`: Market data structure

4. **Database**: PostgreSQL integration
   - Connection management
   - CRUD operations
   - Schema creation

5. **Utils**: Helper functions
   - `logger`: Logging system
   - `metrics`: Technical analysis calculations

---

## Installation

### Prerequisites

- Python 3.10+
- PostgreSQL 14+
- pip or conda

### 1. Install PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**Windows:**
Download from [postgresql.org](https://www.postgresql.org/download/windows/)

### 2. Create Database

```bash
sudo -u postgres psql

# In psql:
CREATE USER crypto WITH PASSWORD 'crypto';
CREATE DATABASE crypto OWNER crypto;
GRANT ALL PRIVILEGES ON DATABASE crypto TO crypto;
\q
```

### 3. Python Dependencies

```bash
# Using pip
pip install psycopg2-binary requests pandas numpy python-binance pycoingecko schedule

# Using conda
conda install psycopg2 requests pandas numpy
pip install python-binance pycoingecko schedule
```

### 4. Install TA-Lib (Technical Analysis Library)

**Ubuntu/Debian:**
```bash
sudo apt install build-essential wget
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
pip install TA-Lib
```

**macOS:**
```bash
brew install ta-lib
pip install TA-Lib
```

**Windows:**
Download pre-built wheel from [here](https://github.com/cgohlke/talib-build/releases)
```bash
pip install TA_Lib‑0.4.XX‑cpXX‑cpXX‑win_amd64.whl
```

---

## Configuration

---

## 🚀 Usage

### Run Single Cycle

```bash
cd Backend
python main.py
```

The service will:
1. Execute one data collection cycle immediately
2. Schedule subsequent cycles every x minutes
3. Run continuously until stopped (Ctrl+C)

---

## 📊 Logging

### Log Organization

Logs are organized by collection cycle:
```
logs/
└── cycle_2025-xx-xx_xx-xx-xx/
    ├── CryptoListingService.log
    ├── CoingeckoServicelog
    ├── BinanceService.log
    ├── TechnicalAnalysisService.log
    └── Database.log
```

### Log Levels

- **DEBUG**: Detailed information for diagnosing problems
- **INFO**: General information about operation flow
- **WARNING**: Something unexpected but not critical
- **ERROR**: Error occurred but service continues
- **CRITICAL**: Critical error, service may stop

## 🔌 API Integration

### CoinGecko API

**Base URL**: `https://api.coingecko.com/api/v3/`

**Endpoints Used**:
- `/coins/markets` - Market data (batch: 249 cryptos)
- `/coins/{id}/market_chart` - Historical price/volume
- `/coins/{id}` - Detailed coin information
- `/global` - Global market data

### Binance API

**Base URL**: `https://fapi.binance.com/`

**Endpoints Used**:
- `/fapi/v1/depth` - Order book
- `/fapi/v1/premiumIndex` - Funding rate
- `/fapi/v1/openInterest` - Open interest

---

## 📄 License

This project is private and proprietary.

