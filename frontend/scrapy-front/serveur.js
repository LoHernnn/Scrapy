import express from "express";
import pkg from "pg";
const { Pool } = pkg;
import cors from "cors";

const app = express();
app.use(cors());
app.use(express.json());

const pool = new Pool({
  user: "crypto",
  host: "localhost",
  database: "crypto",
  password: "crypto",
  port: 5432,
});

// route: GET /data
app.get("/data", async (req, res) => {
  try {
    const result = await pool.query("SELECT * FROM cryptos");
    res.json(result.rows);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Route to retrieve all details of a cryptocurrency
app.get("/crypto/:id", async (req, res) => {
  try {
    const cryptoId = req.params.id;
    
    // Récupérer les infos de base
    const cryptoInfo = await pool.query(
      "SELECT * FROM cryptos WHERE id = $1",
      [cryptoId]
    );
    
    if (cryptoInfo.rows.length === 0) {
      return res.status(404).json({ error: "Crypto non trouvée" });
    }
    
    // Retrieve the latest master data
    const baseData = await pool.query(
      `SELECT * FROM cyptos_data_base 
       WHERE crypto_id = $1 
       ORDER BY timestamp DESC 
       LIMIT 1`,
      [cryptoId]
    );
    
    // Retrieve the latest detailed data
    const detailsData = await pool.query(
      `SELECT * FROM cyptos_data_details 
       WHERE crypto_id = $1 
       ORDER BY timestamp DESC 
       LIMIT 1`,
      [cryptoId]
    );
    
    // Retrieve the latest Binance data
    const binanceData = await pool.query(
      `SELECT * FROM cyptos_data_binance 
       WHERE crypto_id = $1 
       ORDER BY timestamp DESC 
       LIMIT 1`,
      [cryptoId]
    );
    
    // Recover rank
    const rankData = await pool.query(
      "SELECT rank FROM crypto_ranks WHERE crypto_id = $1",
      [cryptoId]
    );
    
    res.json({
      crypto: cryptoInfo.rows[0],
      base: baseData.rows[0] || null,
      details: detailsData.rows[0] || null,
      binance: binanceData.rows[0] || null,
      rank: rankData.rows[0]?.rank || null
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Path to retrieve historical data
app.get("/history/:id", async (req, res) => {
  try {
    const cryptoId = req.params.id;
    const limit = req.query.limit || 100;
    
    // Retrieve history from the 3 tables
    const baseHistory = await pool.query(
      `SELECT timestamp, price, market_cap, total_volume, high_24h, low_24h, 
              variation24h_pst, dominance
       FROM cyptos_data_base 
       WHERE crypto_id = $1 
       ORDER BY timestamp DESC 
       LIMIT $2`,
      [cryptoId, limit]
    );
    
    const detailsHistory = await pool.query(
      `SELECT timestamp, rsi_values, sma_50, sma_200, ema_50, ema_200,
              macd_h, signal_line_h, histogram_h
       FROM cyptos_data_details 
       WHERE crypto_id = $1 
       ORDER BY timestamp DESC 
       LIMIT $2`,
      [cryptoId, limit]
    );
    
    const binanceHistory = await pool.query(
      `SELECT timestamp, funding_rate, open_interest
       FROM cyptos_data_binance 
       WHERE crypto_id = $1 
       ORDER BY timestamp DESC 
       LIMIT $2`,
      [cryptoId, limit]
    );
    
    res.json({
      base: baseHistory.rows.reverse(),
      details: detailsHistory.rows.reverse(),
      binance: binanceHistory.rows.reverse()
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(3001, () => {
  console.log("API backend OK sur http://localhost:3001");
});
