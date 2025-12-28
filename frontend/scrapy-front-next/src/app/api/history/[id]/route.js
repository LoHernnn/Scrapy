import { query } from '@/lib/db';
import { NextResponse } from 'next/server';

export async function GET(request, { params }) {
  const { id } = await params;
  const { searchParams } = new URL(request.url);
  const range = searchParams.get('range') || '24h';

  let interval = "interval '24 hours'";
  if (range === '12h') interval = "interval '12 hours'";
  if (range === '7j') interval = "interval '7 days'";
  if (range === '30j') interval = "interval '30 days'";
  if (range === 'all') interval = "interval '10 years'";

  try {
    const res = await query(`
      SELECT 
        b.timestamp, 
        b.price, 
        b.total_volume as volume,

        (SELECT rsi_values FROM cyptos_data_details d 
         WHERE d.crypto_id = b.crypto_id AND d.timestamp <= b.timestamp 
         ORDER BY d.timestamp DESC LIMIT 1) as rsi,

        (SELECT score_24h FROM crypto_sentiment_scores s 
         WHERE s.crypto_id = b.crypto_id AND s.timestamp <= b.timestamp 
         ORDER BY s.timestamp DESC LIMIT 1) as sentiment,

        (SELECT funding_rate FROM cyptos_data_binance bin 
         WHERE bin.crypto_id = b.crypto_id AND bin.timestamp <= b.timestamp 
         ORDER BY bin.timestamp DESC LIMIT 1) as funding,

        (SELECT open_interest FROM cyptos_data_binance bin 
         WHERE bin.crypto_id = b.crypto_id AND bin.timestamp <= b.timestamp 
         ORDER BY bin.timestamp DESC LIMIT 1) as oi
      FROM cyptos_data_base b
      WHERE b.crypto_id = $1 
      AND b.timestamp > NOW() - ${interval}
      ORDER BY b.timestamp ASC
    `, [id]);

    const formattedData = res.rows.map(row => ({
      time: new Date(row.timestamp).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }),
      fullDate: new Date(row.timestamp).toLocaleString('fr-FR'),
      price: row.price ? parseFloat(row.price) : null,
      rsi: row.rsi ? parseFloat(row.rsi) : null,
      sentiment: row.sentiment ? parseFloat(row.sentiment) : null,
      funding: row.funding ? parseFloat(row.funding) * 100 : null, 
      oi: row.oi ? parseFloat(row.oi) : null,
      volume: row.volume ? parseFloat(row.volume) : null
    }));

    return NextResponse.json(formattedData);
  } catch (error) {
    console.error("Database Error:", error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}