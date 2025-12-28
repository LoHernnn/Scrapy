import { query } from '@/lib/db';
import { NextResponse } from 'next/server';

export async function GET(request, { params }) {
  const resolvedParams = await params;
  const id = resolvedParams.id;

  try {
    const [info, base, details, binance, rank, grade] = await Promise.all([
      query("SELECT * FROM cryptos WHERE id = $1", [id]),
      query("SELECT * FROM cyptos_data_base WHERE crypto_id = $1 ORDER BY timestamp DESC LIMIT 1", [id]),
      query("SELECT * FROM cyptos_data_details WHERE crypto_id = $1 ORDER BY timestamp DESC LIMIT 1", [id]),
      query("SELECT * FROM cyptos_data_binance WHERE crypto_id = $1 ORDER BY timestamp DESC LIMIT 1", [id]),
      query("SELECT rank FROM crypto_ranks WHERE crypto_id = $1", [id]),
      query("SELECT score_24h, count_24h FROM crypto_sentiment_scores WHERE crypto_id = $1", [id])
    ]);

    if (info.rows.length === 0) {
      return NextResponse.json({ error: "Crypto non trouvée" }, { status: 404 });
    }

    return NextResponse.json({
      crypto: info.rows[0],
      base: base.rows[0] || null,
      details: details.rows[0] || null,
      binance: binance.rows[0] || null,
      rank: rank.rows[0]?.rank || null,
      sentiment: grade.rows[0] || null
    });
  } catch (error) {
    console.error("Database Error:", error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}