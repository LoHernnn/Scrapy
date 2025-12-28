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

### 2. Configure environment variables

Create a `.env.local` file at the root of the frontend project:

```env
# Database Connection
DATABASE_URL=postgresql://user:password@localhost:5432/crypto_db

# API Configuration (optional if using external API)
NEXT_PUBLIC_API_URL=http://localhost:3000
```

### 3. Start the development server

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### 4. Build for production

```bash
npm run build
npm run start
```

## 🏗️ Architecture

```
src/
├── app/                        # Next.js App Router
│   ├── api/                    # API Routes (Serverless backend)
│   │   ├── bot/               # Trading bot endpoints
│   │   │   └── route.js       # GET: Bot status, POST: Start/Stop
│   │   ├── crypto/            # Cryptocurrency data
│   │   │   └── [id]/
│   │   │       ├── route.js   # GET: Specific crypto details
│   │   │       └── tweets/
│   │   │           └── route.js # GET: Crypto-related tweets
│   │   ├── history/           # Trading history
│   │   │   └── [id]/
│   │   │       └── route.js   # GET: History per crypto
│   │   ├── market/            # Market data
│   │   │   └── route.js       # GET: Market overview
│   │   ├── overview/          # General dashboard
│   │   │   └── route.js       # GET: Global statistics
│   │   └── sentiment/         # Sentiment analysis
│   │       └── route.js       # GET: Global Twitter sentiment
│   │
│   ├── bot/                   # Bot control page
│   │   └── page.js            # Bot management interface
│   ├── crypto/                # Crypto details pages
│   │   └── [id]/
│   │       └── page.js        # Individual crypto page
│   ├── market/                # Market view page
│   │   └── page.js            # All cryptocurrencies table
│   ├── sentiment/             # Sentiment analysis page
│   │   └── page.js            # Global Twitter trends
│   │
│   ├── layout.js              # Main layout with Sidebar
│   ├── page.js                # Home page (Overview)
│   └── globals.css            # Global styles
│
├── components/                # Reusable React components
│   ├── charts/
│   │   └── MultiChart.jsx     # Technical charts (Recharts)
│   ├── layout/
│   │   └── Sidebar.jsx        # Side navigation
│   └── ui/
│       ├── HotTweets.jsx      # Trending tweets display
│       └── SentimentSection.jsx # Sentiment UI section
│
└── lib/
    └── db.js                  # PostgreSQL connection (pg)
```

## ✨ Features

### 📊 Overview (Homepage)
- **Global Statistics**: Number of tracked cryptos, average sentiment, 24h volume
- **Multi-indicator Charts**: Price, volume, RSI, sentiment
- **Top Cryptos**: Best daily performers
- **Alerts**: Trading signal notifications

### 💹 Market Page
- **Complete List**: All tracked cryptocurrencies
- **Technical Indicators**: RSI, MACD, EMA, SMA
- **Sort & Filter**: By price, volume, 24h change, market cap
- **Real-time Data**: Automatic updates

### 🪙 Crypto Details
- **Interactive Charts**: Historical price with technical indicators
- **Complete Metrics**: Price, volume, market cap, supply
- **Twitter Sentiment**: Sentiment score and recent tweets
- **Trading Signals**: Calculated technical indicators
- **Hot Tweets**: Most influential tweets about the crypto

### 💬 Sentiment Analysis
- **Global Sentiment**: Overall crypto market trend on Twitter
- **Top Cryptos by Sentiment**: Ranking by sentiment score
- **Influential Tweets**: Tweets with highest engagement
- **Temporal Evolution**: Sentiment evolution charts

### 🤖 Trading Bot
- **Control**: Start/Stop the bot
- **Configuration**: Trading parameters and risk management
- **Performance**: Realized/unrealized PnL
- **History**: List of executed trades
- **Open Positions**: Real-time monitoring

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
// Returns: { cryptos: [...], total: 100, avgSentiment: 0.65 }

GET /api/crypto/[id]
// Returns: { crypto: {...}, historicalData: [...], indicators: {...} }
```

### Sentiment Analysis
```javascript
GET /api/sentiment
// Returns: { globalSentiment: 0.68, topCryptos: [...], trends: [...] }

GET /api/crypto/[id]/tweets
// Returns: { tweets: [...], sentimentScore: 0.72, tweetCount: 150 }
```

### Trading Bot
```javascript
GET /api/bot
// Returns: { status: "running", pnl: 1250, positions: [...], config: {...} }

POST /api/bot
// Body: { action: "start" | "stop", config: {...} }
// Returns: { success: true, status: "started" }
```

### Trading History
```javascript
GET /api/history/[id]
// Returns: { trades: [...], totalPnl: 500, winRate: 0.65 }
```

## 🎨 Technologies Used

- **Next.js 14+**: React framework with App Router and Server Components
- **React 18**: UI library with hooks and server components
- **Recharts**: Chart library for data visualization
- **PostgreSQL (pg)**: PostgreSQL client for Node.js
- **Tailwind CSS**: Utility-first CSS framework (if configured)
- **Geist Font**: Optimized font from Vercel

## 🔐 Database Configuration

Ensure your PostgreSQL database contains the following tables:
- `cryptos`: Cryptocurrency metadata
- `crypto_ranks`: Rankings and scores
- `cyptos_data_base`: Current market data
- `cyptos_data_details`: Detailed historical data
- `tweets`: Collected tweets
- `sentiment_scores`: Sentiment scores

## 📦 Available Scripts

```bash
# Development
npm run dev          # Start dev server on port 3000

# Production
npm run build        # Build the application
npm run start        # Start production server

# Linting
npm run lint         # Check code with ESLint
```

## 🌐 Deployment

### Vercel (Recommended)
1. Push code to GitHub
2. Import project on [Vercel](https://vercel.com)
3. Configure environment variables
4. Deploy automatically

### Other Platforms
- **Docker**: Create an image with `Dockerfile`
- **VPS**: Use `pm2` to manage Node.js process
- **AWS/Azure**: Deploy on cloud services

## 📝 Important Notes

- The frontend requires the Python backend to be running to collect data
- Data is stored in PostgreSQL, no frontend caching
- API routes use server-side connections only
- Trading bot must be launched via Python backend script

## 🔗 Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Recharts Documentation](https://recharts.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## 📄 License

See [LICENSE](../../LICENSE) file at the project root.
