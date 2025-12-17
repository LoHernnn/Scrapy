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
    const result = await pool.query(`
      SELECT DISTINCT ON (c.id)
        c.*,
        cr.rank,
        css.score_24h as grade24h,
        css.count_24h as count24h,
        css.score_12h as grade12h,
        css.count_12h as count12h,
        cdb.price as current_price,
        cdb.market_cap,
        cdb.variation24h_pst as price_change_24h_pct
      FROM cryptos c
      LEFT JOIN crypto_ranks cr ON c.id = cr.crypto_id
      LEFT JOIN crypto_sentiment_scores css ON c.id = css.crypto_id
      LEFT JOIN LATERAL (
        SELECT price, market_cap, variation24h_pst
        FROM cyptos_data_base
        WHERE crypto_id = c.id
        ORDER BY timestamp DESC
        LIMIT 1
      ) cdb ON true
      ORDER BY c.id
    `);
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

    const cryptograde = await pool.query(
      `SELECT score_24h, count_24h, score_12h, count_12h
        FROM crypto_sentiment_scores 
        WHERE crypto_id = $1`,
      [cryptoId]
    );
    
    res.json({
      crypto: cryptoInfo.rows[0],
      base: baseData.rows[0] || null,
      details: detailsData.rows[0] || null,
      binance: binanceData.rows[0] || null,
      rank: rankData.rows[0]?.rank || null,
      grade24h: cryptograde.rows[0]?.score_24h || null,
      count24h: cryptograde.rows[0]?.count_24h || null,
      grade12h: cryptograde.rows[0]?.score_12h || null,
      count12h: cryptograde.rows[0]?.count_12h || null,
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

// Route to retrieve the last 3 tweets for a crypto
app.get("/tweets/:id", async (req, res) => {
  try {
    const cryptoId = req.params.id;
    
    const tweets = await pool.query(
      `SELECT 
        ts.tweet_id as id,
        ts.account,
        to_timestamp(ts.timestamp) as tweet_date,
        ts.tweet_content as content,
        tc.sentiment_score
       FROM tweet_sentiments ts
       INNER JOIN tweet_crypto tc ON ts.tweet_id = tc.tweet_id
       WHERE tc.crypto_id = $1
       ORDER BY ts.timestamp DESC
       LIMIT 3`,
      [cryptoId]
    );
    
    res.json(tweets.rows);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(3001, () => {
  console.log("API backend OK sur http://localhost:3001");
});
