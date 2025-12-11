import { useEffect, useState } from "react";
import "./App.css";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

function App() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCrypto, setSelectedCrypto] = useState(null);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [history, setHistory] = useState(null);
  const [selectedMetrics, setSelectedMetrics] = useState({
    price: true,
    market_cap: false,
    total_volume: false,
    rsi_values: false,
    sma_50: false,
    sma_200: false,
    funding_rate: false,
  });

  useEffect(() => {
    fetch("http://localhost:3001/data")
      .then(res => {
        if (!res.ok) throw new Error("API connection error");
        return res.json();
      })
      .then(result => {
        setData(result);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  // Function to load crypto details
  const loadCryptoDetails = async (cryptoId) => {
    setDetailsLoading(true);
    try {
      const [detailsRes, historyRes] = await Promise.all([
        fetch(`http://localhost:3001/crypto/${cryptoId}`),
        fetch(`http://localhost:3001/history/${cryptoId}?limit=50`)
      ]);
      
      if (!detailsRes.ok) throw new Error("Error loading details");
      const details = await detailsRes.json();
      const historyData = await historyRes.json();
      
      setSelectedCrypto(details);
      setHistory(historyData);
    } catch (err) {
      console.error(err);
      alert("Unable to load details");
    } finally {
      setDetailsLoading(false);
    }
  };

  // Function to close the modal
  const closeModal = () => {
    setSelectedCrypto(null);
    setHistory(null);
    setSelectedMetrics({
      price: true,
      market_cap: false,
      total_volume: false,
      rsi_values: false,
      sma_50: false,
      sma_200: false,
      funding_rate: false,
    });
  };

  // Handle checkboxes
  const toggleMetric = (metric) => {
    setSelectedMetrics(prev => ({
      ...prev,
      [metric]: !prev[metric]
    }));
  };

  // Prepare chart data
  const prepareChartData = () => {
    if (!history || (!history.base?.length && !history.details?.length && !history.binance?.length)) {
      return null;
    }

    const timestamps = history.base?.map(item => 
      new Date(item.timestamp).toLocaleString('fr-FR', { 
        month: 'short', 
        day: 'numeric', 
        hour: '2-digit' 
      })
    ) || [];

    const datasets = [];
    const colors = [
      '#667eea', '#764ba2', '#f093fb', '#4facfe',
      '#43e97b', '#fa709a', '#fee140', '#30cfd0'
    ];
    let colorIndex = 0;

    // Price
    if (selectedMetrics.price && history.base) {
      datasets.push({
        label: 'Prix ($)',
        data: history.base.map(item => item.price),
        borderColor: colors[colorIndex++ % colors.length],
        backgroundColor: 'transparent',
        tension: 0.4,
        yAxisID: 'y',
      });
    }

    // Market Cap
    if (selectedMetrics.market_cap && history.base) {
      datasets.push({
        label: 'Market Cap ($)',
        data: history.base.map(item => item.market_cap),
        borderColor: colors[colorIndex++ % colors.length],
        backgroundColor: 'transparent',
        tension: 0.4,
        yAxisID: 'y1',
      });
    }

    // Volume
    if (selectedMetrics.total_volume && history.base) {
      datasets.push({
        label: 'Volume ($)',
        data: history.base.map(item => item.total_volume),
        borderColor: colors[colorIndex++ % colors.length],
        backgroundColor: 'transparent',
        tension: 0.4,
        yAxisID: 'y1',
      });
    }

    // RSI
    if (selectedMetrics.rsi_values && history.details) {
      datasets.push({
        label: 'RSI',
        data: history.details.map(item => item.rsi_values),
        borderColor: colors[colorIndex++ % colors.length],
        backgroundColor: 'transparent',
        tension: 0.4,
        yAxisID: 'y2',
      });
    }

    // SMA 50
    if (selectedMetrics.sma_50 && history.details) {
      datasets.push({
        label: 'SMA 50',
        data: history.details.map(item => item.sma_50),
        borderColor: colors[colorIndex++ % colors.length],
        backgroundColor: 'transparent',
        tension: 0.4,
        yAxisID: 'y',
      });
    }

    // SMA 200
    if (selectedMetrics.sma_200 && history.details) {
      datasets.push({
        label: 'SMA 200',
        data: history.details.map(item => item.sma_200),
        borderColor: colors[colorIndex++ % colors.length],
        backgroundColor: 'transparent',
        tension: 0.4,
        yAxisID: 'y',
      });
    }

    // Funding Rate
    if (selectedMetrics.funding_rate && history.binance) {
      datasets.push({
        label: 'Funding Rate (%)',
        data: history.binance.map(item => item.funding_rate),
        borderColor: colors[colorIndex++ % colors.length],
        backgroundColor: 'transparent',
        tension: 0.4,
        yAxisID: 'y2',
      });
    }

    return {
      labels: timestamps,
      datasets: datasets
    };
  };

  const chartOptions = {
    responsive: true,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Data History',
      },
    },
    scales: {
      y: {
        type: 'linear',
        display: true,
        position: 'left',
      },
      y1: {
        type: 'linear',
        display: true,
        position: 'right',
        grid: {
          drawOnChartArea: false,
        },
      },
      y2: {
        type: 'linear',
        display: false,
        position: 'right',
      },
    },
  };

  // Filter cryptos based on search
  const filteredData = data.filter(crypto => 
    crypto.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    crypto.symbol?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="app">
        <div className="loading">
          <h2>Loading data...</h2>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="app">
        <div className="error">
          <h2>Error</h2>
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>
            🔄 Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="header">
        <h1> Crypto Dashboard</h1>
        <p>{data.length} cryptocurrencies available</p>
      </header>

      <div className="search-bar">
        <input
          type="text"
          placeholder="🔍 Search crypto (name or symbol)..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      <div className="crypto-grid">
        {filteredData.length === 0 ? (
          <p className="no-results">No crypto found</p>
        ) : (
          filteredData.map((crypto, index) => (
            <div 
              key={index} 
              className="crypto-card"
              onClick={() => loadCryptoDetails(crypto.id)}
            >
              <div className="crypto-header">
                <h3>{crypto.name || "N/A"}</h3>
                <span className="symbol">{crypto.symbol || "N/A"}</span>
              </div>
              
              <div className="crypto-info">
                {crypto.rank && (
                  <div className="info-row">
                    <span className="label">Rank:</span>
                    <span className="value">#{crypto.rank}</span>
                  </div>
                )}
                
                {crypto.current_price && (
                  <div className="info-row">
                    <span className="label">Price:</span>
                    <span className="value price">${crypto.current_price.toLocaleString()}</span>
                  </div>
                )}
                
                {crypto.market_cap && (
                  <div className="info-row">
                    <span className="label">Market Cap:</span>
                    <span className="value">${(crypto.market_cap / 1e9).toFixed(2)}B</span>
                  </div>
                )}
                
                {crypto.price_change_24h_pct && (
                  <div className="info-row">
                    <span className="label">24h:</span>
                    <span className={`value ${crypto.price_change_24h_pct >= 0 ? 'positive' : 'negative'}`}>
                      {crypto.price_change_24h_pct >= 0 ? '↑' : '↓'} 
                      {Math.abs(crypto.price_change_24h_pct).toFixed(2)}%
                    </span>
                  </div>
                )}

                {crypto.symbol_binance && (
                  <div className="info-row">
                    <span className="label">Binance:</span>
                    <span className="value">{crypto.symbol_binance}</span>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Details modal */}
      {selectedCrypto && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={closeModal}>✕</button>
            
            {detailsLoading ? (
              <div className="modal-loading">Loading...</div>
            ) : (
              <>
                <div className="modal-header">
                  <h2>{selectedCrypto.crypto.name}</h2>
                  <span className="modal-symbol">{selectedCrypto.crypto.symbol}</span>
                </div>

                {selectedCrypto.rank && (
                  <div className="modal-rank">Rank: #{selectedCrypto.rank}</div>
                )}

                {/* Base data */}
                {selectedCrypto.base && (
                  <div className="modal-section">
                    <h3>📊 Market Data</h3>
                    <div className="details-grid">
                      {selectedCrypto.base.price && <div><strong>Prix:</strong> ${Number(selectedCrypto.base.price).toLocaleString()}</div>}
                      {selectedCrypto.base.high_24h && <div><strong>High 24h:</strong> ${Number(selectedCrypto.base.high_24h).toLocaleString()}</div>}
                      {selectedCrypto.base.low_24h && <div><strong>Low 24h:</strong> ${Number(selectedCrypto.base.low_24h).toLocaleString()}</div>}
                      {selectedCrypto.base.market_cap && <div><strong>Market Cap:</strong> ${(Number(selectedCrypto.base.market_cap) / 1e9).toFixed(2)}B</div>}
                      {selectedCrypto.base.total_volume && <div><strong>Volume 24h:</strong> ${(Number(selectedCrypto.base.total_volume) / 1e6).toFixed(2)}M</div>}
                      {selectedCrypto.base.dominance && <div><strong>Dominance:</strong> {Number(selectedCrypto.base.dominance).toFixed(2)}%</div>}
                      {selectedCrypto.base.variation24h_pst && <div><strong>Var 24h:</strong> <span className={Number(selectedCrypto.base.variation24h_pst) >= 0 ? 'positive' : 'negative'}>{Number(selectedCrypto.base.variation24h_pst).toFixed(2)}%</span></div>}
                      {selectedCrypto.base.all_time_high && <div><strong>ATH:</strong> ${Number(selectedCrypto.base.all_time_high).toLocaleString()}</div>}
                    </div>
                  </div>
                )}

                {/* Detailed data */}
                {selectedCrypto.details && (
                  <>
                    <div className="modal-section">
                      <h3>📈 Technical Indicators</h3>
                      <div className="details-grid">
                        {selectedCrypto.details.rsi_values && <div><strong>RSI:</strong> {Number(selectedCrypto.details.rsi_values).toFixed(2)}</div>}
                        {selectedCrypto.details.sma_50 && <div><strong>SMA 50:</strong> ${Number(selectedCrypto.details.sma_50).toFixed(2)}</div>}
                        {selectedCrypto.details.sma_200 && <div><strong>SMA 200:</strong> ${Number(selectedCrypto.details.sma_200).toFixed(2)}</div>}
                        {selectedCrypto.details.ema_50 && <div><strong>EMA 50:</strong> ${Number(selectedCrypto.details.ema_50).toFixed(2)}</div>}
                        {selectedCrypto.details.ema_200 && <div><strong>EMA 200:</strong> ${Number(selectedCrypto.details.ema_200).toFixed(2)}</div>}
                      </div>
                    </div>

                    <div className="modal-section">
                      <h3>💹 MACD</h3>
                      <div className="details-grid">
                        {selectedCrypto.details.macd_h && <div><strong>MACD (H):</strong> {Number(selectedCrypto.details.macd_h).toFixed(4)}</div>}
                        {selectedCrypto.details.signal_line_h && <div><strong>Signal (H):</strong> {Number(selectedCrypto.details.signal_line_h).toFixed(4)}</div>}
                        {selectedCrypto.details.histogram_h && <div><strong>Histogram (H):</strong> {Number(selectedCrypto.details.histogram_h).toFixed(4)}</div>}
                      </div>
                    </div>

                    <div className="modal-section">
                      <h3>🎯 Pivot Points</h3>
                      <div className="details-grid">
                        {selectedCrypto.details.pp && <div><strong>PP:</strong> ${Number(selectedCrypto.details.pp).toFixed(2)}</div>}
                        {selectedCrypto.details.r1 && <div><strong>R1:</strong> ${Number(selectedCrypto.details.r1).toFixed(2)}</div>}
                        {selectedCrypto.details.r2 && <div><strong>R2:</strong> ${Number(selectedCrypto.details.r2).toFixed(2)}</div>}
                        {selectedCrypto.details.s1 && <div><strong>S1:</strong> ${Number(selectedCrypto.details.s1).toFixed(2)}</div>}
                        {selectedCrypto.details.s2 && <div><strong>S2:</strong> ${Number(selectedCrypto.details.s2).toFixed(2)}</div>}
                      </div>
                    </div>
                  </>
                )}

                {/* Binance data */}
                {selectedCrypto.binance && (
                  <div className="modal-section">
                    <h3>Binance</h3>
                    <div className="details-grid">
                      {selectedCrypto.binance.funding_rate && <div><strong>Funding Rate:</strong> {Number(selectedCrypto.binance.funding_rate).toFixed(4)}%</div>}
                      {selectedCrypto.binance.open_interest && <div><strong>Open Interest:</strong> ${Number(selectedCrypto.binance.open_interest).toLocaleString()}</div>}
                    </div>
                    
                    <div className="orderbook">
                      <div className="orderbook-side">
                        <h4>Bids</h4>
                        {selectedCrypto.binance.bids_price_1 && (
                          <div><strong>${Number(selectedCrypto.binance.bids_price_1).toFixed(4)}</strong> × {Number(selectedCrypto.binance.bids_quantity_1).toFixed(2)}</div>
                        )}
                        {selectedCrypto.binance.bids_price_2 && (
                          <div><strong>${Number(selectedCrypto.binance.bids_price_2).toFixed(4)}</strong> × {Number(selectedCrypto.binance.bids_quantity_2).toFixed(2)}</div>
                        )}
                        {selectedCrypto.binance.bids_price_3 && (
                          <div><strong>${Number(selectedCrypto.binance.bids_price_3).toFixed(4)}</strong> × {Number(selectedCrypto.binance.bids_quantity_3).toFixed(2)}</div>
                        )}
                      </div>
                      <div className="orderbook-side">
                        <h4>Asks</h4>
                        {selectedCrypto.binance.asks_price_1 && (
                          <div><strong>${Number(selectedCrypto.binance.asks_price_1).toFixed(4)}</strong> × {Number(selectedCrypto.binance.asks_quantity_1).toFixed(2)}</div>
                        )}
                        {selectedCrypto.binance.asks_price_2 && (
                          <div><strong>${Number(selectedCrypto.binance.asks_price_2).toFixed(4)}</strong> × {Number(selectedCrypto.binance.asks_quantity_2).toFixed(2)}</div>
                        )}
                        {selectedCrypto.binance.asks_price_3 && (
                          <div><strong>${Number(selectedCrypto.binance.asks_price_3).toFixed(4)}</strong> × {Number(selectedCrypto.binance.asks_quantity_3).toFixed(2)}</div>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {/* Chart section */}
                {history && (
                  <div className="modal-section">
                    <h3>📈 Historical Chart</h3>
                    
                    {/* Checkboxes */}
                    <div className="metrics-checkboxes">
                      <label>
                        <input
                          type="checkbox"
                          checked={selectedMetrics.price}
                          onChange={() => toggleMetric('price')}
                        />
                          Price
                        </label>
                      <label>
                        <input
                          type="checkbox"
                          checked={selectedMetrics.market_cap}
                          onChange={() => toggleMetric('market_cap')}
                        />
                        Market Cap
                        </label>
                      <label>
                        <input
                          type="checkbox"
                          checked={selectedMetrics.total_volume}
                          onChange={() => toggleMetric('total_volume')}
                        />
                        Volume
                      </label>
                      <label>
                        <input
                          type="checkbox"
                          checked={selectedMetrics.rsi_values}
                          onChange={() => toggleMetric('rsi_values')}
                        />
                        RSI
                      </label>
                      <label>
                        <input
                          type="checkbox"
                          checked={selectedMetrics.sma_50}
                          onChange={() => toggleMetric('sma_50')}
                        />
                        SMA 50
                      </label>
                      <label>
                        <input
                          type="checkbox"
                          checked={selectedMetrics.sma_200}
                          onChange={() => toggleMetric('sma_200')}
                        />
                        SMA 200
                      </label>
                      <label>
                        <input
                          type="checkbox"
                          checked={selectedMetrics.funding_rate}
                          onChange={() => toggleMetric('funding_rate')}
                        />
                        Funding Rate
                      </label>
                    </div>

                    {/* Chart */}
                    <div className="chart-container">
                      {prepareChartData() ? (
                        <Line data={prepareChartData()} options={chartOptions} />
                      ) : (
                        <p>No historical data available</p>
                      )}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
