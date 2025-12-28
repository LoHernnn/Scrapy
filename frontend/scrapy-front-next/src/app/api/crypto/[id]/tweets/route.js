import { query } from '@/lib/db';
import { NextResponse } from 'next/server';

export async function GET(request, { params }) {
  const resolvedParams = await params;
  const id = resolvedParams.id;

  try {
    const [globalSentiment, extremeTweets] = await Promise.all([
      query(`
        SELECT score_12h, count_12h, score_24h, count_24h 
        FROM crypto_sentiment_scores 
        WHERE crypto_id = $1
      `, [id]),

      query(`
        (SELECT 
          ts.tweet_id, ts.account, ts.tweet_content, ts.timestamp, tc.sentiment_score
         FROM tweet_sentiments ts
         JOIN tweet_crypto tc ON ts.tweet_id = tc.tweet_id
         WHERE tc.crypto_id = $1
         ORDER BY tc.sentiment_score DESC
         LIMIT 5)
        UNION ALL
        (SELECT 
          ts.tweet_id, ts.account, ts.tweet_content, ts.timestamp, tc.sentiment_score
         FROM tweet_sentiments ts
         JOIN tweet_crypto tc ON ts.tweet_id = tc.tweet_id
         WHERE tc.crypto_id = $1
         ORDER BY tc.sentiment_score ASC
         LIMIT 5)
        ORDER BY sentiment_score DESC
      `, [id])
    ]);

    return NextResponse.json({
      summary: globalSentiment.rows[0] || { score_12h: 0, score_24h: 0, count_12h: 0, count_24h: 0 },
      tweets: extremeTweets.rows
    });

  } catch (error) {
    console.error("Erreur Tweets:", error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}