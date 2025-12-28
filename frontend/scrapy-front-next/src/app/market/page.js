'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

export default function MarketPage() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  // Data recovery function
  const refreshData = async () => {
    try {
      const res = await fetch('/api/market');
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

  const formatPrice = (p) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 4 }).format(p);
  const formatCompact = (v) => new Intl.NumberFormat('en-US', { notation: 'compact' }).format(v);

  return (
    <div className="max-w-7xl mx-auto p-6 min-h-screen text-slate-200">
      <header className="mb-10 border-b border-slate-800 pb-6">
        <h1 className="text-4xl font-black tracking-tighter text-white uppercase italic">Quant Terminal</h1>
        <p className="text-slate-500 text-xs font-bold tracking-widest uppercase">Market Efficiency & Technical Indicators</p>
      </header>

      <div className="space-y-4">
        {data?.map((coin) => (
          <div key={coin.crypto_id} className="bg-[#0f172a] border border-slate-800 rounded-xl p-5 hover:border-blue-500/50 transition-all group shadow-xl">
            
            {/* LINE 1: IDENTITY AND PRICE  */}
            <div className="flex flex-wrap items-center justify-between gap-6 mb-4">
              <div className="flex items-center gap-4 min-w-[200px]">
                <span className="text-slate-700 font-black text-2xl italic">#{coin.market_rank || '--'}</span>
                <div>
                  <h2 className="text-xl font-black text-white leading-none">{coin.name}</h2>
                  <span className="text-blue-500 font-mono text-sm uppercase font-bold">{coin.symbol}</span>
                </div>
              </div>

              <div className="text-right">
                <div className="text-2xl font-black text-white font-mono">{formatPrice(coin.price)}</div>
                <div className={`text-sm font-bold ${Number(coin.variation24h_pst) >= 0 ? 'text-emerald-400' : 'text-rose-500'}`}>
                  {Number(coin.variation24h_pst) >= 0 ? '▲' : '▼'} {Math.abs(coin.variation24h_pst).toFixed(2)}%
                </div>
              </div>

              {/* RSI & MACD */}
              <div className="flex gap-8 border-l border-slate-800 pl-8">
                <div className="text-center">
                  <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">RSI (14)</p>
                  <div className={`text-xl font-black font-mono ${coin.rsi_values > 70 ? 'text-rose-500' : coin.rsi_values < 30 ? 'text-emerald-500' : 'text-blue-400'}`}>
                    {Number(coin.rsi_values)?.toFixed(1)}
                  </div>
                </div>
              </div>

              <Link href={`/crypto/${coin.crypto_id}`} className="ml-auto bg-blue-600 hover:bg-blue-500 text-white px-6 py-2 rounded-lg font-black text-xs uppercase transition-colors">
                Analysis
              </Link>
            </div>

            {/* LINE 2: TECHNICAL METRICS */}
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-6 pt-4 border-t border-slate-800/50">
              
              <div>
                <p className="text-[9px] font-bold text-slate-600 uppercase mb-1">Performance</p>
                <div className="flex gap-3 text-[11px] font-mono">
                  <span title="1D" className={coin.d1_percentage >= 0 ? 'text-emerald-500' : 'text-rose-500'}>1D: {Number(coin.d1_percentage).toFixed(1)}%</span>
                  <span title="7D" className={coin.d7_percentage >= 0 ? 'text-emerald-500' : 'text-rose-500'}>7D: {Number(coin.d7_percentage).toFixed(1)}%</span>
                  <span title="30D" className={coin.d30_percentage >= 0 ? 'text-emerald-500' : 'text-rose-500'}>30D: {Number(coin.d30_percentage).toFixed(1)}%</span>
                </div>
              </div>

              {/* Moving Averages */}
              <div>
                <p className="text-[9px] font-bold text-slate-600 uppercase mb-1">Trend (SMA/EMA 50-200)</p>
                <div className="text-[10px] text-slate-400 grid grid-cols-2 gap-x-2">
                  <span>S50: {formatCompact(coin.sma_50)}</span>
                  <span>E50: {formatCompact(coin.ema_50)}</span>
                  <span>S200: {formatCompact(coin.sma_200)}</span>
                  <span>E200: {formatCompact(coin.ema_200)}</span>
                </div>
              </div>

              {/* Market Data */}
              <div>
                <p className="text-[9px] font-bold text-slate-600 uppercase mb-1">Market Cap</p>
                <p className="text-xs font-bold text-slate-300 font-mono">${formatCompact(coin.market_cap)}</p>
              </div>

              {/* Volatility Range */}
              <div>
                <p className="text-[9px] font-bold text-slate-600 uppercase mb-1">24h Range (L/H)</p>
                <p className="text-[10px] font-mono text-slate-400">
                  {formatCompact(coin.low_24h)} — {formatCompact(coin.high_24h)}
                </p>
              </div>

              {/* MACD Details */}
              <div className="lg:col-span-2">
                <p className="text-[9px] font-bold text-slate-600 uppercase mb-1">Signal vs MACD Line</p>
                <div className="flex flex-col gap-1.5 border-l border-slate-800/50 pl-4">
                    <div className="flex items-center gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-slate-500"></span>
                        <span className="text-slate-400 text-[10px] font-mono uppercase">
                        Signal: <b className="text-slate-200">{Number(coin.signal_line_h).toFixed(3)}</b>
                        </span>
                    </div>
                    
                    <div className="flex items-center gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
                        <span className="text-slate-400 text-[10px] font-mono uppercase">
                        MACD: <b className="text-slate-200">{Number(coin.macd_h).toFixed(3)}</b>
                        </span>
                    </div>

                    <div className="flex items-center gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
                        <span className="text-slate-400 text-[10px] font-mono uppercase">
                        HIST: <b className="text-slate-200">{Number(coin.histogram_h).toFixed(3)}</b>
                        </span>
                    </div>
                </div>
              </div>

            </div>
          </div>
        ))}
      </div>
    </div>
  );
}