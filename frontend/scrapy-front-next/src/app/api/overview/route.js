import { query } from '@/lib/db';
import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const marketRes = await query(`
      SELECT DISTINCT ON (c.id)
        c.id, c.name, c.symbol,
        b.price, b.variation24h_pst, b.market_cap,
        s.score_24h as sentiment
      FROM cryptos c
      LEFT JOIN cyptos_data_base b ON c.id = b.crypto_id
      LEFT JOIN crypto_sentiment_scores s ON c.id = s.crypto_id
      ORDER BY c.id, b.timestamp DESC
    `);

    const tweetsRes = await query(`
      SELECT t.tweet_content, t.account, tc.sentiment_score, c.symbol
      FROM tweet_sentiments t
      JOIN tweet_crypto tc ON t.tweet_id = tc.tweet_id
      JOIN cryptos c ON tc.crypto_id = c.id
      WHERE ABS(tc.sentiment_score) >= 0.7
      ORDER BY t.timestamp DESC 
      LIMIT 6
    `);

    return NextResponse.json({ 
      market: marketRes.rows, 
      hotTweets: tweetsRes.rows 
    });

  } catch (error) {
    console.error("Erreur API Overview:", error);
    return NextResponse.json(
      { error: "Erreur lors de la récupération de l'overview", details: error.message },
      { status: 500 }
    );
  }
}