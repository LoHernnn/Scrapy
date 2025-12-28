'use client'; 

import { useState, useEffect } from 'react';
import Link from 'next/link';

export default function SentimentPage() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  // Data recovery function
  const refreshData = async () => {
    try {
      const res = await fetch('/api/sentiment');
      const json = await res.json();
      setData(json);
      setLoading(false);
    } catch (err) {
      console.error("Erreur de rafraîchissement:", err);
    }
  };

  // Interval setup
  useEffect(() => {
    refreshData(); 
    const interval = setInterval(refreshData, 10000); 
    return () => clearInterval(interval); 
  }, []);

  if (loading && data.length === 0) {
    return <div className="p-10 text-slate-500 font-mono text-center">INITIALIZING SOCIAL SCANNER...</div>;
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-10 min-h-screen text-slate-200">
      <header className="border-b border-slate-800 pb-6 flex justify-between items-end">
        <div>
          <h1 className="text-4xl font-black text-white italic tracking-tighter uppercase">Social Signals</h1>
          <p className="text-orange-500 text-xs font-bold tracking-[0.3em] uppercase">Aggregated X Intelligence</p>
        </div>
        <div className="flex items-center gap-2 mb-1">
          <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Live Feed</span>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {data.map((coin) => {
          const score24 = Number(coin.score_24h || 0);
          const score12 = Number(coin.score_12h || 0);
          const trendUp = score12 > score24;

          return (
            <div key={coin.id} className="flex flex-col p-5 border border-slate-800 hover:border-blue-500/30 transition-all bg-[#0f172a]/50 shadow-xl rounded-2xl relative overflow-hidden group">
              
              {/* HEADER: Identity & Volume */}
              <div className="flex justify-between items-start mb-6">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-slate-800 flex items-center justify-center font-black text-blue-400 border border-slate-700">
                    {coin.symbol.substring(0, 2)}
                  </div>
                  <div>
                    <h3 className="text-lg font-black text-white leading-none group-hover:text-blue-400 transition-colors">{coin.name}</h3>
                    <span className="text-xs text-slate-500 font-mono uppercase tracking-widest">{coin.symbol}</span>
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-[9px] font-black text-slate-500 uppercase block tracking-tighter">Mentions 24h</span>
                  <span className="text-xl font-black text-white font-mono">{coin.count_24h || 0}</span>
                </div>
              </div>

              {/* RAW SCORES (12h vs 24h) */}
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="bg-slate-900/50 p-3 rounded-lg border border-slate-800/50">
                  <p className="text-[9px] font-bold text-slate-500 uppercase mb-1">Score 24h</p>
                  <span className={`text-lg font-black font-mono ${score24 > 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {score24 > 0 ? '+' : ''}{score24.toFixed(3)}
                  </span>
                </div>
                <div className="bg-slate-900/50 p-3 rounded-lg border border-slate-800/50 relative overflow-hidden">
                  <p className="text-[9px] font-bold text-slate-500 uppercase mb-1">Score 12h</p>
                  <div className="flex items-baseline gap-2">
                    <span className={`text-lg font-black font-mono ${score12 > 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {score12 > 0 ? '+' : ''}{score12.toFixed(3)}
                    </span>
                    <span className={`text-[10px] font-bold ${trendUp ? 'text-emerald-500' : 'text-rose-500'}`}>
                      {trendUp ? '↑' : '↓'}
                    </span>
                  </div>
                </div>
              </div>

              {/* VISUAL GAUGE */}
              <div className="space-y-2 mb-6">
                <div className="h-1 w-full bg-slate-800 rounded-full overflow-hidden relative">
                  <div 
                    className={`absolute h-full transition-all duration-1000 ${score24 > 0 ? 'bg-emerald-500 shadow-[0_0_8px_#10b981]' : 'bg-rose-500 shadow-[0_0_8px_#f43f5e]'}`}
                    style={{ 
                      width: `${Math.min(Math.abs(score24 * 100), 50)}%`,
                      left: score24 > 0 ? '50%' : `${50 - Math.min(Math.abs(score24 * 100), 50)}%`
                    }}
                  />
                </div>
                <div className="flex justify-between text-[7px] font-black text-slate-600 uppercase tracking-tighter">
                  <span>Extreme Fear</span>
                  <span>Neutral</span>
                  <span>Extreme Greed</span>
                </div>
              </div>

              {/* FOOTER: Last Tweet & Action */}
              <div className="mt-auto space-y-4">
                {coin.last_tweet && (
                  <div className="bg-blue-500/5 p-3 rounded-lg border border-blue-500/10 min-h-[50px]">
                    <p className="text-[10px] text-slate-400 italic line-clamp-2 leading-relaxed font-serif">
                      "{coin.last_tweet}"
                    </p>
                  </div>
                )}
                
                <Link 
                  href={`/crypto/${coin.id}`}
                  className="w-full py-3 bg-slate-800 hover:bg-blue-600 text-white text-[10px] font-black uppercase tracking-[0.2em] rounded-xl transition-all border border-slate-700 hover:border-blue-400 text-center block"
                >
                  Analysis
                </Link>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}