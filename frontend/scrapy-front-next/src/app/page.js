'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import HotTweets from '@/components/ui/HotTweets';

export default function OverviewPage() {
  const [data, setData] = useState({ market: [], hotTweets: [] });
  const [loading, setLoading] = useState(true);

  // Data recovery function
  const refreshData = async () => {
    try {
      const res = await fetch('/api/overview');
      const json = await res.json();
      console.log('Data received:', json);
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

  if (!data || data.length === 0) {
    return <div className="p-10 text-slate-500 font-mono text-center">NO MARKET DATA AVAILABLE</div>;
  }

  // We secure the sorting of winners
  const winners = [...data.market]
      .sort((a, b) => Number(b.variation24h_pst) - Number(a.variation24h_pst))
      .slice(0, 3);

  return (
    <div className="max-w-7xl mx-auto space-y-8 p-6">
      
      {/* HEADER SECTION */}
      <div className="flex justify-between items-center border-b border-slate-800 pb-8">
        <div>
          <h1 className="text-4xl font-black text-white tracking-tighter italic">TERMINAL OVERVIEW</h1>
          <p className="text-slate-500 text-[10px] mt-1 uppercase tracking-[0.3em] font-bold">Real-time Market Analytics & Social Intelligence</p>
        </div>
        <div className="hidden md:flex gap-4">
          {winners.map(w => (
            <div key={w.id} className="bg-emerald-500/5 border border-emerald-500/20 px-4 py-2 rounded-xl backdrop-blur-sm">
              <span className="text-[10px] text-emerald-500 font-black uppercase tracking-widest">{w.symbol}</span>
              <p className="text-white font-mono text-sm font-bold">
                +{w.variation24h_pst ? Number(w.variation24h_pst).toFixed(2) : '0.00'}%
              </p>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        
        {/* LEFT COLUMN: Tweet Alerts */}
        <div className="lg:col-span-1 space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-[10px] font-black text-orange-500 uppercase tracking-widest flex items-center gap-2">
               <span className="w-2 h-2 bg-orange-500 rounded-full animate-pulse"></span>
               Live Social Signals
            </h3>
          </div>
          <div className="space-y-4">
            {data.hotTweets.map((t, i) => (
              <div key={i} className="glass-card p-4 border-l-2 border-orange-500/50 hover:bg-slate-800/40 transition-all cursor-default">
                <div className="flex justify-between text-[10px] mb-3 font-black uppercase tracking-tighter">
                  <span className="text-blue-400">@{t.account}</span>
                  <span className={t.sentiment_score > 0 ? 'text-emerald-400' : 'text-rose-400'}>{t.symbol}</span>
                </div>
                <p className="text-xs text-slate-300 italic leading-relaxed">"{t.tweet_content}"</p>
              </div>
            ))}
          </div>
        </div>

        {/* RIGHT COLUMN: Market Table */}
        <div className="lg:col-span-3">
          <div className="glass-card overflow-hidden border-slate-800/50 shadow-2xl">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-900/80 border-b border-slate-800">
                  <th className="p-4 text-[10px] font-black text-slate-500 uppercase tracking-widest">Asset</th>
                  <th className="p-4 text-[10px] font-black text-slate-500 uppercase tracking-widest text-right">Price</th>
                  <th className="p-4 text-[10px] font-black text-slate-500 uppercase tracking-widest text-right">24h Change</th>
                  <th className="p-4 text-[10px] font-black text-slate-500 uppercase tracking-widest text-center">Sentiment Score</th>
                  <th className="p-4 text-[10px] font-black text-slate-500 uppercase tracking-widest"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50">
                {data.market.map((coin) => {
                  const change = Number(coin.variation24h_pst || 0);
                  const sentiment = Number(coin.sentiment || 0);
                  
                  return (
                    <tr key={coin.id} className="hover:bg-blue-500/[0.03] transition-colors group">
                      <td className="p-4">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-lg bg-slate-800 flex items-center justify-center font-black text-xs text-slate-400 group-hover:text-blue-400 transition-colors border border-slate-700">
                            {coin.symbol[0]}
                          </div>
                          <div className="flex flex-col">
                            <span className="text-sm font-bold text-white tracking-tight">{coin.name}</span>
                            <span className="text-[10px] text-slate-500 font-mono uppercase tracking-widest">{coin.symbol}</span>
                          </div>
                        </div>
                      </td>
                      <td className="p-4 text-right font-mono text-sm text-white font-bold">
                        ${Number(coin.price).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                      </td>
                      <td className={`p-4 text-right font-mono text-sm font-bold ${change >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                        {change > 0 ? '+' : ''}{change.toFixed(2)}%
                      </td>
                      <td className="p-4">
                        <div className="flex flex-col items-center gap-1">
                          <div className="h-1 w-24 rounded-full bg-slate-800 overflow-hidden relative shadow-inner">
                              <div 
                                className={`absolute h-full transition-all duration-1000 ${sentiment > 0 ? 'bg-emerald-500 shadow-[0_0_8px_#10b981]' : 'bg-rose-500 shadow-[0_0_8px_#f43f5e]'}`}
                                style={{ 
                                  width: `${Math.abs(sentiment * 100)}%`,
                                  left: sentiment > 0 ? '50%' : `${50 - Math.abs(sentiment * 100)}%`
                                }}
                              ></div>
                          </div>
                          <span className="text-[9px] font-bold text-slate-600 uppercase tracking-tighter">
                            {sentiment > 0.2 ? 'Bullish' : sentiment < -0.2 ? 'Bearish' : 'Neutral'}
                          </span>
                        </div>
                      </td>
                      <td className="p-4 text-right">
                        <Link href={`/crypto/${coin.id}`} className="inline-flex items-center px-4 py-2 bg-slate-800 hover:bg-blue-600 text-white text-[10px] font-black rounded-lg transition-all uppercase tracking-widest border border-slate-700 hover:border-blue-400">
                          Analyze
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </div>
  );
}