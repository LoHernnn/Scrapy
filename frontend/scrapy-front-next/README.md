# Crypto Analytics Dashboard - Frontend

Next.js dashboard for the cryptocurrency analysis and trading platform. Modern interface with real-time data visualization, Twitter sentiment analysis, and trading bot monitoring.

## 📋 Prerequisites

- **Node.js**: 18.0 or higher
- **npm** or **yarn** or **pnpm**
- **PostgreSQL Database**: Configured and accessible (backend required)

## 🚀 Installation

### 1. Install dependencies

```bash
npm install
# or
yarn install
# or
pnpm install
```

### 2. Start the development server

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### 3. Build for production

```bash
npm run start
```


## 🔧 How It Works

### 1. **App Router & Server Components**
Next.js 14+ with App Router uses Server Components by default for optimal server-side rendering.

### 2. **API Routes**
API routes (`/api/*`) work as a serverless backend:
- Direct PostgreSQL connection via `pg` module
- SQL queries to fetch data
- JSON response for frontend

### 3. **Database Connection**
The `lib/db.js` file manages the PostgreSQL connection pool:
```javascript
import { Pool } from 'pg';
const pool = new Pool({ connectionString: process.env.DATABASE_URL });
```

### 4. **Data Flow**
```
[PostgreSQL Database] 
    ↓ (SQL queries)
[API Routes (/api/*)] 
    ↓ (fetch/JSON)
[React Components] 
    ↓ (render)
[User Interface]
```

### 5. **Chart Components**
Uses **Recharts** for visualization:
- `LineChart`: Price and technical indicators
- `BarChart`: Trading volume
- `AreaChart`: Sentiment over time
- Customizable and interactive

### 6. **Real-time Updates**
- Automatic polling via `setInterval` in components
- Data refresh every 10-30 seconds
- Manual refresh option available

## 📡 API Endpoints

### Market Data
```javascript
GET /api/market

GET /api/crypto/[id]
```

### Sentiment Analysis
```javascript
GET /api/sentiment

GET /api/crypto/[id]/tweets
```

### Trading Bot
```javascript
GET /api/bot
```

## Trading History
```javascript
GET /api/history/[id]
```

## Overview
```javascript
GET /api/overview
```
