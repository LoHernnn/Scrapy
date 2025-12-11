# Crypto Dashboard - Frontend

A modern React application for displaying and analyzing cryptocurrency data in real-time with interactive charts and detailed technical indicators.

## Technology Stack

- **React 18** - JavaScript library for building user interfaces
- **Vite** - Next-generation frontend build tool
- **Chart.js 4** - Powerful charting library for data visualization
- **react-chartjs-2** - React wrapper for Chart.js
- **Express.js** - Backend API middleware server
- **PostgreSQL** - Database for storing crypto data

## Installation

### Prerequisites

- Node.js 18+ and npm
- PostgreSQL database running (from backend)
- Backend crypto collector service running

### Setup

```bash
# Install dependencies
npm install

# Start the API middleware server
node serveur.js

# In another terminal, start the React development server
npm run dev
```

The application will be available at `http://localhost:5173` (Vite default port).

## Core Files Documentation

### `serveur.js` - Express API Middleware

**Purpose**: Acts as a bridge between the React frontend and the PostgreSQL database, providing REST API endpoints.

**Configuration**:
```javascript
const pool = new Pool({
  user: "crypto",
  host: "localhost",
  database: "crypto",
  password: "crypto",
  port: 5432,
});
```

**API Endpoints**:

#### 1. `GET /data`
- **Purpose**: Retrieve the list of all cryptocurrencies
- **Response**: Array of crypto objects with basic information
- **Query**: `SELECT * FROM cryptos`
- **Used by**: Main dashboard grid view

#### 2. `GET /crypto/:id`
- **Purpose**: Retrieve complete details for a specific cryptocurrency
- **Parameters**: 
  - `id` (number) - Crypto database ID
- **Response Structure**:
  ```json
  {
    "crypto": {/* Basic crypto info */},
    "base": {/* Market data (price, volume, market_cap) */},
    "details": {/* Technical indicators (RSI, MACD, SMA) */},
    "binance": {/* Binance data (funding rate, orderbook) */},
    "rank": 1
  }
  ```
- **Queries**:
  - Latest record from `cyptos_data_base` (market data)
  - Latest record from `cyptos_data_details` (technical analysis)
  - Latest record from `cyptos_data_binance` (exchange data)
  - Rank from `crypto_ranks`
- **Used by**: Modal detail view when clicking on a crypto card

#### 3. `GET /history/:id`
- **Purpose**: Retrieve time-series historical data for charts
- **Parameters**:
  - `id` (number) - Crypto database ID
  - `limit` (query param, default: 100) - Number of historical points
- **Response Structure**:
  ```json
  {
    "base": [{timestamp, price, market_cap, volume, ...}, ...],
    "details": [{timestamp, rsi_values, sma_50, sma_200, ...}, ...],
    "binance": [{timestamp, funding_rate, open_interest}, ...]
  }
  ```
- **Data Order**: Reversed chronologically (oldest to newest for Chart.js)
- **Used by**: Chart.js visualization in modal

**Features**:
- CORS enabled for cross-origin requests
- Error handling with 500/404 status codes
- Connection pooling for efficient database queries
- Timestamp-based sorting for historical accuracy

---

### `App.jsx` - Main React Component

**Purpose**: Core application component managing the entire cryptocurrency dashboard interface, including data fetching, filtering, modal display, and interactive charts.

#### State Management

```javascript
const [data, setData] = useState([]);                    // All cryptocurrencies list
const [loading, setLoading] = useState(true);            // Initial loading state
const [error, setError] = useState(null);                // Error messages
const [searchTerm, setSearchTerm] = useState("");        // Search filter
const [selectedCrypto, setSelectedCrypto] = useState(null);  // Modal crypto details
const [detailsLoading, setDetailsLoading] = useState(false); // Modal loading state
const [history, setHistory] = useState(null);            // Historical data for charts
const [selectedMetrics, setSelectedMetrics] = useState({ // Chart metric toggles
  price: true,
  market_cap: false,
  total_volume: false,
  rsi_values: false,
  sma_50: false,
  sma_200: false,
  funding_rate: false,
});
```

#### Core Functions

##### `useEffect()` - Data Loading
- **Trigger**: Component mount
- **Action**: Fetches all cryptocurrencies from `/data` endpoint
- **Updates**: `data`, `loading`, `error` states
- **Error Handling**: Catches connection errors and displays message

##### `loadCryptoDetails(cryptoId)`
- **Purpose**: Load complete cryptocurrency details when user clicks a card
- **Parameters**: `cryptoId` (number) - Database ID
- **Process**:
  1. Sets `detailsLoading` to true
  2. Parallel fetch using `Promise.all()`:
     - `/crypto/:id` for current data
     - `/history/:id?limit=50` for time-series data
  3. Updates `selectedCrypto` and `history` states
  4. Opens modal automatically
- **Error Handling**: Alert displayed if fetch fails

##### `closeModal()`
- **Purpose**: Close detail modal and reset states
- **Actions**:
  - Clears `selectedCrypto` and `history`
  - Resets `selectedMetrics` to default (only price enabled)
- **Trigger**: Close button click or overlay click

##### `toggleMetric(metric)`
- **Purpose**: Toggle chart data series visibility
- **Parameters**: `metric` (string) - Metric key name
- **Action**: Updates `selectedMetrics` state by toggling boolean value
- **Effect**: Chart re-renders with updated datasets

##### `prepareChartData()`
- **Purpose**: Transform raw historical data into Chart.js format
- **Returns**: Chart.js data object or `null` if no data
- **Process**:
  1. Extract timestamps and format as readable labels
  2. Create dataset array based on `selectedMetrics`
  3. Assign colors from predefined palette
  4. Map each metric to appropriate Y-axis (`y`, `y1`, or `y2`)
- **Metrics Mapping**:
  - **Y-axis (left)**: Price, SMA 50, SMA 200
  - **Y1-axis (right)**: Market Cap, Volume
  - **Y2-axis (hidden)**: RSI, Funding Rate
- **Color System**: Cycling through 8 gradient colors

#### UI Components

##### Header Section
```jsx
<header className="header">
  <h1>Crypto Dashboard</h1>
  <p>{data.length} cryptocurrencies available</p>
</header>
```
- Displays total cryptocurrency count
- Static branding

##### Search Bar
```jsx
<input
  type="text"
  placeholder="🔍 Search crypto (name or symbol)..."
  value={searchTerm}
  onChange={(e) => setSearchTerm(e.target.value)}
/>
```
- Real-time filtering
- Case-insensitive search
- Searches both name and symbol fields

##### Crypto Grid
- **Layout**: Responsive grid of crypto cards
- **Filtering**: Uses `filteredData` based on search term
- **Click Handler**: Calls `loadCryptoDetails()` on card click
- **Displayed Data per Card**:
  - Name and symbol
  - Rank (if available)
  - Current price
  - Market capitalization
  - 24h price change with color indicator (green/red)
  - Binance symbol

##### Modal Detail View
- **Trigger**: Clicking any crypto card
- **Structure**: Overlay with centered content box
- **Close Methods**:
  - Click overlay background
  - Click close button (✕)
  - `stopPropagation()` on content prevents closing when clicking inside

**Modal Sections**:

1. **Header**:
   - Crypto name and symbol
   - Current rank

2. **Market Data** (`base` table):
   - Price, High/Low 24h
   - Market Cap, Volume
   - Dominance percentage
   - 24h variation (colored)
   - All-time high (ATH)

3. **Technical Indicators** (`details` table):
   - RSI (Relative Strength Index)
   - SMA 50 & 200 (Simple Moving Averages)
   - EMA 50 & 200 (Exponential Moving Averages)

4. **MACD Section** (`details` table):
   - MACD histogram value
   - Signal line value
   - Histogram value

5. **Pivot Points** (`details` table):
   - PP (Pivot Point)
   - R1, R2 (Resistance levels)
   - S1, S2 (Support levels)

6. **Binance Data** (`binance` table):
   - Funding rate
   - Open interest
   - Orderbook display:
     - **Bids**: Top 3 buy orders (price × quantity)
     - **Asks**: Top 3 sell orders (price × quantity)

7. **Historical Chart Section**:
   - **Checkboxes**: 7 metrics to toggle visibility
   - **Chart Display**: Line chart with multi-axis support
   - **Fallback**: "No historical data available" message

#### Chart Configuration

**Chart.js Setup**:
```javascript
ChartJS.register(
  CategoryScale,    // X-axis (time)
  LinearScale,      // Y-axes (values)
  PointElement,     // Data points
  LineElement,      // Lines connecting points
  Title,            // Chart title
  Tooltip,          // Hover tooltips
  Legend            // Dataset legend
);
```

**Chart Options**:
- **Responsive**: Auto-resize with container
- **Interaction Mode**: Index-based (shows all values at X position)
- **Legend**: Top position
- **Title**: "Data History"
- **Axes**:
  - **Y (left)**: Price and moving averages
  - **Y1 (right)**: Market Cap and Volume
  - **Y2 (hidden)**: RSI and Funding Rate (0-100 scale)

#### Conditional Rendering

**Loading State**:
```jsx
if (loading) return <div>Loading data...</div>
```

**Error State**:
```jsx
if (error) return (
  <div>Error
    <p>{error}</p>
    <button onClick={reload}>🔄 Retry</button>
  </div>
)
```

**Empty Search Results**:
```jsx
{filteredData.length === 0 && <p>No crypto found</p>}
```

**Modal Loading**:
```jsx
{detailsLoading ? <div>Loading...</div> : <DetailedContent />}
```

#### Performance Optimizations

1. **Parallel API Calls**: `Promise.all()` for simultaneous fetches
2. **Conditional Rendering**: Only render modal when `selectedCrypto` exists
3. **Lazy Chart Rendering**: Chart only created when data available
4. **Event Delegation**: Single click handler on overlay
5. **Filtered Data**: Computed on render, no extra state

#### Data Flow

```
App Mount
   ↓
Fetch /data → setData → Render Grid
   ↓
User clicks card
   ↓
loadCryptoDetails(id)
   ↓
Parallel fetch:
   - /crypto/:id
   - /history/:id
   ↓
setSelectedCrypto + setHistory
   ↓
Modal renders with details
   ↓
User toggles metrics
   ↓
prepareChartData() recalculates
   ↓
Chart re-renders with new datasets
```

#### Key Features

- **Real-time Search**: Instant filtering without API calls
- **Interactive Charts**: User-controlled metric visibility
- **Multi-axis Charts**: Different scales for different data types
- **Responsive Design**: Mobile-friendly grid and modal
- **Error Recovery**: Retry mechanism for failed requests
- **Data Completeness**: Handles missing data gracefully (null checks)
- **Color Coding**: Visual indicators for positive/negative changes
- **Orderbook Visualization**: Real-time bid/ask display

---

## Data Sources

All data is sourced from the backend PostgreSQL database with 5 tables:

1. **cryptos**: Basic cryptocurrency information
2. **crypto_ranks**: Market cap rankings
3. **cyptos_data_base**: Market data (price, volume, market cap)
4. **cyptos_data_details**: Technical indicators (RSI, MACD, MAs)
5. **cyptos_data_binance**: Exchange data (funding rate, orderbook)

## API Flow

```
React App (Port 5173)
    ↓ HTTP Request
Express API (Port 3001)
    ↓ SQL Query
PostgreSQL Database
    ↓ Result
Express API
    ↓ JSON Response
React App (Renders UI)
```

## Development

### Available Scripts

```bash
# Development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Start API server
node serveur.js
```

### Key Dependencies

```json
{
  "react": "^18.3.1",
  "react-dom": "^18.3.1",
  "chart.js": "^4.4.8",
  "react-chartjs-2": "^5.3.0",
  "express": "^4.21.2",
  "pg": "^8.13.1",
  "cors": "^2.8.5"
}
```

## License

This project is for educational purposes. Not financial advice.

