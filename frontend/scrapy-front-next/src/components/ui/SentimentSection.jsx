export default function SentimentSection({ sentimentData }) {
  const { summary, tweets } = sentimentData;

  return (
    <div className="space-y-6">
      {/* Global Summary */}
      <div className="grid grid-cols-2 gap-4">
        <div className="glass-card flex flex-col items-center">
          <span className="text-slate-400 text-xs uppercase">Score 24h</span>
          <span className={`text-3xl font-bold ${summary.score_24h > 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
            {summary.score_24h?.toFixed(2)}
          </span>
          <span className="text-slate-500 text-xs">{summary.count_24h} Tweets analyzed</span>
        </div>
        <div className="glass-card flex flex-col items-center">
          <span className="text-slate-400 text-xs uppercase">Score 12h</span>
          <span className={`text-3xl font-bold ${summary.score_12h > 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
            {summary.score_12h?.toFixed(2)}
          </span>
          <span className="text-slate-500 text-xs">{summary.count_12h} Tweets analyzed</span>
        </div>
      </div>

      {/* List of Extreme Tweets */}
      <div className="glass-card">
        <h3 className="text-lg font-bold mb-4">Extreme Social Signals</h3>
        <div className="space-y-3">
          {tweets.map((tweet) => (
            <div key={tweet.tweet_id} className="p-3 bg-slate-800/50 rounded-lg border-l-4 border-slate-700" 
                 style={{ borderLeftColor: tweet.sentiment_score > 0 ? '#10b981' : '#f43f5e' }}>
              <div className="flex justify-between items-start mb-1">
                <span className="font-bold text-blue-400 text-sm">@{tweet.account}</span>
                <span className={`text-xs font-mono px-2 py-0.5 rounded ${tweet.sentiment_score > 0 ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
                  Score: {tweet.sentiment_score}
                </span>
              </div>
              <p className="text-slate-300 text-sm line-clamp-2 italic">"{tweet.tweet_content}"</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}