import { query } from '@/lib/db';
import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const res = await query(`
      WITH LatestBase AS (
        SELECT DISTINCT ON (crypto_id) * FROM cyptos_data_base 
        ORDER BY crypto_id, timestamp DESC
      ),
      LatestDetails AS (
        SELECT DISTINCT ON (crypto_id) * FROM cyptos_data_details
        ORDER BY crypto_id, timestamp DESC
      )
      SELECT 
        c.id as crypto_id, 
        c.name, 
        c.symbol,
        r.rank as market_rank,
        b.price, 
        b.high_24h, 
        b.low_24h, 
        b.variation24h_pst, 
        b.market_cap, 
        b.mc_variation24h_pst,
        d.rsi_values, 
        d.macd_h, 
        d.signal_line_h, 
        d.histogram_h,
        d.sma_50, 
        d.sma_200, 
        d.ema_50, 
        d.ema_200,
        d.d1_percentage, 
        d.d7_percentage, 
        d.d30_percentage,
        d.d1_vs_avg
      FROM cryptos c
      LEFT JOIN crypto_ranks r ON c.id = r.crypto_id
      JOIN LatestBase b ON c.id = b.crypto_id
      LEFT JOIN LatestDetails d ON c.id = d.crypto_id
      ORDER BY r.rank ASC NULLS LAST
    `);
    return NextResponse.json(res.rows);
  } catch (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}