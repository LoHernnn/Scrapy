import { query } from '@/lib/db';
import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const res = await query(`
      WITH LatestSentiment AS (
        SELECT DISTINCT ON (crypto_id) * FROM crypto_sentiment_scores 
        ORDER BY crypto_id, timestamp DESC
      )
      SELECT 
        c.name, c.symbol, c.id,
        s.score_24h, s.count_24h, s.score_12h,
        (SELECT tweet_content FROM tweet_sentiments ts 
         JOIN tweet_crypto tc ON ts.tweet_id = tc.tweet_id 
         WHERE tc.crypto_id = c.id 
         ORDER BY ts.timestamp DESC LIMIT 1) as last_tweet
      FROM cryptos c
      JOIN LatestSentiment s ON c.id = s.crypto_id
      ORDER BY s.count_24h DESC NULLS LAST
    `);
    return NextResponse.json(res.rows);
  } catch (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}