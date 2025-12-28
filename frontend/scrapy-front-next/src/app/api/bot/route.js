import { query } from '@/lib/db';
import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const res = await query(`
      WITH latest_perf AS (
        SELECT * FROM portfolio_performance ORDER BY timestamp DESC LIMIT 1
      ),
      latest_signals AS (
        SELECT DISTINCT ON (crypto_id) 
          s.crypto_id, 
          s.score_total, 
          s.score_metric, 
          s.trend, 
          s.timestamp,
          c.symbol, c.name 
        FROM crypto_scores s
        JOIN cryptos c ON s.crypto_id = c.id
        ORDER BY crypto_id, s.timestamp DESC
      ),
      active_trades AS (
        SELECT t.*, c.symbol 
        FROM crypto_trade_data t
        JOIN cryptos c ON t.crypto_id = c.id
        WHERE t.status = 0
      )
      SELECT 
        (SELECT row_to_json(p) FROM latest_perf p) as performance,
        (SELECT json_agg(sig) FROM (SELECT * FROM latest_signals ORDER BY score_total DESC) sig) as all_signals,
        (SELECT json_agg(a) FROM active_trades a) as active_positions
    `);

    const data = res.rows[0] || { performance: {}, all_signals: [], active_positions: [] };

    return NextResponse.json(data);
  } catch (error) {
    console.error("Erreur API Bot:", error);
    return NextResponse.json(
      { error: "Failed to fetch bot data", details: error.message }, 
      { status: 500 }
    );
  }
}