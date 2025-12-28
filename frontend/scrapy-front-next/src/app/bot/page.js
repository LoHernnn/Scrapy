'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

export default function BotPage() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  // Data recovery function
  const refreshData = async () => {
    try {
      const res = await fetch('/api/bot');
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
  
  // DATA EXTRACTION (Correction of the name all_signals)
  const perf = data?.performance || {};
  const positions = data?.active_positions || [];
  const signals = data?.all_signals || []; // <--- Changed from top_signals to all_signals

  return (
    <div className="max-w-[1600px] mx-auto p-6 space-y-8 min-h-screen text-slate-200">
      
      {/* HEADER : CAPITAL STATUS */}
      <header className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="col-span-1 md:col-span-2 p-6 bg-blue-600 rounded-2xl shadow-lg shadow-blue-900/20">
          <p className="text-blue-100 text-xs font-bold uppercase tracking-widest">Total Balance</p>
          <h2 className="text-4xl font-black text-white">${perf.total_balance?.toLocaleString() || '0.00'}</h2>
          <div className="mt-4 flex gap-4 text-xs font-bold text-blue-100 uppercase">
            <span>Cash: ${perf.free_cash?.toLocaleString()}</span>
            <span>PnL Latent: <span className={perf.unrealized_pnl >= 0 ? 'text-emerald-300' : 'text-rose-300'}>
              {perf.unrealized_pnl >= 0 ? '+' : ''}{perf.unrealized_pnl}$
            </span></span>
          </div>
        </div>
        
        <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl">
          <p className="text-slate-500 text-[10px] font-black uppercase tracking-widest">Statut du Bot</p>
          <div className="flex items-center gap-2 mt-2">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
            </span>
            <h3 className="text-xl font-bold text-white uppercase italic">Active & Scanning</h3>
          </div>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* COLUMNS 1 & 2: CURRENT POSITIONS */}
        <section className="lg:col-span-2 space-y-4">
          <h3 className="text-sm font-black text-slate-500 uppercase tracking-widest flex items-center gap-2">
            <span className="w-4 h-[1px] bg-slate-700"></span> Active Positions ({positions.length})
          </h3>
          
          <div className="grid grid-cols-1 gap-4">
            {positions.length > 0 ? positions.map((trade) => (
              <div key={trade.id_trade} className="bg-slate-900 border border-slate-800 p-5 rounded-xl flex items-center justify-between group hover:border-slate-600 transition-colors">
                <div>
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-black ${trade.direction === 1 ? 'bg-emerald-500/10 text-emerald-500' : 'bg-rose-500/10 text-rose-500'}`}>
                      {trade.direction === 1 ? 'LONG' : 'SHORT'}
                    </span>
                    <h4 className="font-black text-white text-lg uppercase tracking-tight">{trade.symbol}</h4>
                  </div>
                  <p className="text-[10px] text-slate-500 font-mono mt-1">Entry: ${trade.entry_price?.toLocaleString()}</p>
                </div>

                <div className="flex gap-8 text-right">
                  <div>
                    <p className="text-[9px] font-bold text-slate-600 uppercase">Take Profit</p>
                    <p className="text-xs font-bold text-emerald-400 font-mono">${trade.take_profit_1}</p>
                  </div>
                  <div>
                    <p className="text-[9px] font-bold text-slate-600 uppercase">Stop Loss</p>
                    <p className="text-xs font-bold text-rose-500 font-mono">${trade.stop_loss_1}</p>
                  </div>
                </div>

                <div className="ml-4 border-l border-slate-800 pl-6 text-right min-w-[100px]">
                  <p className="text-[9px] font-bold text-slate-500 uppercase">Risk/Reward</p>
                  <p className="text-sm font-black text-white">{trade.risk_reward_ratio}</p>
                </div>
              </div>
            )) : (
              <div className="p-10 border border-dashed border-slate-800 rounded-2xl text-center text-slate-600 italic">
                Aucune position ouverte actuellement.
              </div>
            )}
          </div>
        </section>

        {/* COLUMN 3: SIGNALS (NO FRILLS) */}
        <section className="space-y-4">
          <h3 className="text-sm font-black text-slate-500 uppercase tracking-widest flex items-center gap-2">
            <span className="w-4 h-[1px] bg-slate-700"></span> Algorithm Scanner ({signals.length})
          </h3>
          
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl">
            {signals.map((sig) => (
                <div key={sig.crypto_id} className="p-4 hover:bg-slate-800/50 transition-all group relative">
                    <div className="flex justify-between items-center">
                    <div>
                        <div className="flex items-center gap-2">
                        <span className="font-black text-white text-sm uppercase">{sig.symbol}</span>
                        {/* Button to details - Appears on hover or remains discreet */}
                        <a 
                            href={`/crypto/${sig.crypto_id}`}
                            className="opacity-0 group-hover:opacity-100 transition-opacity bg-blue-600 hover:bg-blue-500 p-1 rounded text-[9px] font-black text-white flex items-center gap-1"
                        >
                            DETAILS →
                        </a>
                        </div>
                        <div className="flex gap-2 mt-1">
                        <span className="text-[9px] text-slate-500 font-bold uppercase tracking-tighter">
                            Trend: <span className={sig.trend > 0 ? 'text-emerald-500' : 'text-rose-500'}>
                            {sig.trend?.toFixed(4)}
                            </span>
                        </span>
                        </div>
                    </div>
                    
                    <div className="text-right">
                        <span className={`text-xl font-black font-mono ${sig.score_total > 0 ? 'text-blue-400' : 'text-slate-600'}`}>
                        {Number(sig.score_total).toFixed(2)}%
                        </span>
                        <p className="text-[9px] text-slate-600 font-mono italic">
                        {new Date(sig.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </p>
                    </div>
                    </div>
                </div>
                ))}
          </div>
        </section>

      </div>
    </div>
  );
}