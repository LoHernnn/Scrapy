export default function HotTweets({ tweets }) {
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-black text-orange-500 uppercase tracking-widest flex items-center gap-2">
        <span className="relative flex h-3 w-3">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-orange-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-3 w-3 bg-orange-500"></span>
        </span>
        Extreme Social Signals
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {tweets.map((t, i) => (
          <div key={i} className="glass-card border-l-4" style={{ borderColor: t.sentiment_score > 0 ? '#10b981' : '#f43f5e' }}>
            <div className="flex justify-between items-start mb-2">
              <span className="text-blue-400 font-bold text-xs">@{t.account}</span>
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${t.sentiment_score > 0 ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
                {t.symbol} Signal
              </span>
            </div>
            <p className="text-slate-300 text-sm line-clamp-2 italic">"{t.tweet_content}"</p>
          </div>
        ))}
      </div>
    </div>
  );
}