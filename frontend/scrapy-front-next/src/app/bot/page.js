'use client';

import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';

export default function BotPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const refreshData = async () => {
    try {
      const res = await fetch('/api/bot');
      const json = await res.json();
      console.log('Data received:', json);
      setData(json);
      setLoading(false);
    } catch (err) {
      console.error("Refresh error:", err);
    }
  };

  useEffect(() => {
    refreshData();
    const interval = setInterval(refreshData, 10000);
    return () => clearInterval(interval);
  }, []);

  if (loading || !data) {
    return <div className="p-10 text-slate-500 font-mono text-center">INITIALIZING BOT DASHBOARD...</div>;
  }

  const perf = data?.performance || {};
  const positions = data?.active_positions || [];
  const closedPositions = data?.closed_positions || [];
  const signals = data?.all_signals || [];
  const portfolioHistory = data?.portfolio_history || [];

  // Prepare chart data
  const chartData = portfolioHistory.map(p => ({
    time: new Date(p.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    fullTime: new Date(p.timestamp).toLocaleString(),
    balance: p.total_balance,
    cash: p.free_cash
  }));

  const initialCapital = 10000;
  const totalPnL = perf.total_balance - initialCapital;
  const pnlPercent = ((totalPnL / initialCapital) * 100).toFixed(2);

  return (
    <div className="max-w-[1800px] mx-auto p-6 space-y-6 min-h-screen text-slate-200">
      
      {/* HEADER: CAPITAL STATUS */}
      <header className="grid grid-cols-1 md:grid-cols-6 gap-4">
        {/* Total Balance */}
        <div className="col-span-1 md:col-span-2 p-6 bg-gradient-to-br from-blue-600 to-blue-800 rounded-2xl shadow-lg shadow-blue-900/30">
          <p className="text-blue-200 text-xs font-bold uppercase tracking-widest">💰 Total Capital</p>
          <h2 className="text-4xl font-black text-white">${perf.total_balance?.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) || '0.00'}</h2>
          <div className="mt-3 grid grid-cols-3 gap-4 text-sm">
            <div>
              <span className="text-blue-300 text-xs">Cash</span>
              <p className="font-bold text-white">${perf.free_cash?.toLocaleString(undefined, {minimumFractionDigits: 2}) || '0'}</p>
            </div>
            <div>
              <span className="text-blue-300 text-xs">In positions</span>
              <p className="font-bold text-yellow-300">${perf.total_in_crypto?.toLocaleString(undefined, {minimumFractionDigits: 2}) || '0'}</p>
            </div>
            <div>
              <span className="text-blue-300 text-xs">Unrealized PnL</span>
              <p className={`font-bold ${perf.unrealized_pnl >= 0 ? 'text-emerald-300' : 'text-rose-300'}`}>
                {perf.unrealized_pnl >= 0 ? '+' : ''}{perf.unrealized_pnl?.toFixed(2) || '0'}$
              </p>
            </div>
          </div>
        </div>
        
        {/* PnL Total */}
        <div className={`p-6 rounded-2xl border ${totalPnL >= 0 ? 'bg-emerald-900/20 border-emerald-800' : 'bg-rose-900/20 border-rose-800'}`}>
          <p className="text-slate-400 text-xs font-bold uppercase tracking-widest">📈 Total P&L</p>
          <h3 className={`text-3xl font-black ${totalPnL >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
            {totalPnL >= 0 ? '+' : ''}{totalPnL.toFixed(2)}$
          </h3>
          <p className={`text-sm font-bold ${totalPnL >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
            ({totalPnL >= 0 ? '+' : ''}{pnlPercent}%)
          </p>
        </div>

        {/* Win Rate */}
        <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl">
          <p className="text-slate-500 text-xs font-bold uppercase tracking-widest">🎯 Win Rate</p>
          <h3 className={`text-3xl font-black ${parseFloat(perf.win_rate) >= 50 ? 'text-emerald-400' : 'text-rose-400'}`}>
            {perf.win_rate || 0}%
          </h3>
          <p className="text-xs text-slate-500 mt-1">
            <span className="text-emerald-400">{perf.wins || 0}W</span> / <span className="text-rose-400">{perf.losses || 0}L</span>
            <span className="text-slate-600 ml-1">({perf.total_closed_trades || 0} trades)</span>
          </p>
        </div>

        {/* Bot Status */}
        <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl">
          <p className="text-slate-500 text-xs font-bold uppercase tracking-widest">🤖 Bot Status</p>
          <div className="flex items-center gap-2 mt-2">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
            </span>
            <span className="text-lg font-bold text-white">ACTIVE</span>
          </div>
          <p className="text-xs text-slate-500 mt-1">{perf.active_positions_count || 0} open positions</p>
        </div>

        {/* Verification */}
        <div className={`p-6 rounded-2xl border ${perf.check?.status === 'OK' ? 'bg-slate-900 border-slate-800' : 'bg-amber-900/20 border-amber-700'}`}>
          <p className="text-slate-500 text-xs font-bold uppercase tracking-widest">✅ Integrity</p>
          <div className="flex items-center gap-2 mt-2">
            {perf.check?.status === 'OK' ? (
              <span className="text-emerald-400 font-bold text-lg">✓ OK</span>
            ) : (
              <span className="text-amber-400 font-bold">⚠ Gap: {perf.check?.discrepancy?.toFixed(2)}$</span>
            )}
          </div>
          <p className="text-[10px] text-slate-600 mt-1">
            DB: ${perf.check?.expected?.toFixed(2)} | Calc: ${perf.check?.calculated?.toFixed(2)}
          </p>
        </div>
      </header>

      {/* PORTFOLIO CHART */}
      {chartData.length > 1 && (
        <section className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
          <h3 className="text-sm font-black text-slate-500 uppercase tracking-widest mb-4">
            📊 Portfolio Evolution
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis 
                  dataKey="time" 
                  stroke="#64748b" 
                  tick={{ fontSize: 10 }}
                  interval="preserveStartEnd"
                />
                <YAxis 
                  stroke="#64748b" 
                  tick={{ fontSize: 10 }}
                  domain={['dataMin - 100', 'dataMax + 100']}
                  tickFormatter={(v) => `$${v.toLocaleString()}`}
                />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                  labelStyle={{ color: '#94a3b8' }}
                  formatter={(value) => [`$${value.toLocaleString(undefined, {minimumFractionDigits: 2})}`, 'Balance']}
                  labelFormatter={(label, payload) => payload[0]?.payload?.fullTime || label}
                />
                <ReferenceLine y={initialCapital} stroke="#f59e0b" strokeDasharray="5 5" label={{ value: 'Initial', fill: '#f59e0b', fontSize: 10 }} />
                <Line 
                  type="monotone" 
                  dataKey="balance" 
                  stroke="#3b82f6" 
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 4, fill: '#3b82f6' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </section>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* COLUMN 1 & 2: POSITIONS */}
        <section className="lg:col-span-2 space-y-6">
          
          {/* ACTIVE POSITIONS */}
          <div className="space-y-4">
            <h3 className="text-sm font-black text-slate-500 uppercase tracking-widest flex items-center gap-2">
              <span className="w-4 h-[2px] bg-emerald-500"></span> Active Positions ({positions.length})
            </h3>
            
            <div className="grid grid-cols-1 gap-3">
              {positions.length > 0 ? positions.map((trade) => {
                // Calculate unrealized PnL for this position
                const currentPrice = parseFloat(trade.current_price) || 0;
                const entryPrice = parseFloat(trade.entry_price) || 0;
                const positionSize = parseFloat(trade.total_position_value) || 0;
                const portionRemaining = 1 - (parseFloat(trade.portion_recovered) || 0);
                const remainingSize = positionSize * portionRemaining;
                
                let positionPnl = 0;
                if (currentPrice && entryPrice) {
                  if (trade.direction === 1) { // Long
                    positionPnl = (currentPrice - entryPrice) / entryPrice * remainingSize;
                  } else { // Short
                    positionPnl = (entryPrice - currentPrice) / entryPrice * remainingSize;
                  }
                }
                const pnlPercent = entryPrice > 0 ? ((currentPrice - entryPrice) / entryPrice * 100 * trade.direction) : 0;
                
                return (
                <div key={trade.id_trade} className="bg-slate-900 border border-slate-800 p-5 rounded-xl hover:border-slate-600 transition-colors">
                  <div className="flex items-center justify-between flex-wrap gap-4">
                    {/* Main info */}
                    <div className="flex items-center gap-4">
                      <span className={`px-3 py-1 rounded-lg text-xs font-black ${trade.direction === 1 ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'}`}>
                        {trade.direction === 1 ? '🟢 LONG' : '🔴 SHORT'}
                      </span>
                      <div>
                        <h4 className="font-black text-white text-lg uppercase">{trade.symbol}</h4>
                        <p className="text-xs text-slate-500">Entry: ${entryPrice?.toLocaleString()} → Now: ${currentPrice?.toLocaleString()}</p>
                      </div>
                    </div>

                    {/* Position value */}
                    <div className="text-center px-4 border-l border-slate-800">
                      <p className="text-[10px] text-slate-500 uppercase font-bold">Position</p>
                      <p className="text-lg font-black text-yellow-400">${positionSize?.toFixed(2)}</p>
                      <p className="text-xs text-slate-500">Remaining: ${remainingSize?.toFixed(2)}</p>
                    </div>

                    {/* Unrealized PnL */}
                    <div className="text-center px-4 border-l border-slate-800">
                      <p className="text-[10px] text-slate-500 uppercase font-bold">Unrealized PnL</p>
                      <p className={`text-lg font-black ${positionPnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                        {positionPnl >= 0 ? '+' : ''}{positionPnl.toFixed(2)}$
                      </p>
                      <p className={`text-xs ${pnlPercent >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
                        ({pnlPercent >= 0 ? '+' : ''}{pnlPercent.toFixed(2)}%)
                      </p>
                    </div>

                    {/* TP/SL phases */}
                    <div className="flex gap-2">
                      <div className={`px-3 py-2 rounded-lg text-center ${trade.tp1_active ? 'bg-blue-500/20 border border-blue-500/50' : trade.portion_recovered >= 0.70 ? 'bg-emerald-500/20 border border-emerald-500/50' : 'bg-slate-800'}`}>
                        <p className="text-[9px] font-bold text-slate-400">TP1 (70%)</p>
                        <p className={`text-xs font-bold ${trade.tp1_active ? 'text-blue-400' : trade.portion_recovered >= 0.70 ? 'text-emerald-400' : 'text-slate-600'}`}>
                          {trade.tp1_active ? '⏳ Active' : trade.portion_recovered >= 0.70 ? '✓' : '-'}
                        </p>
                      </div>
                      <div className={`px-3 py-2 rounded-lg text-center ${trade.tp2_active ? 'bg-blue-500/20 border border-blue-500/50' : trade.portion_recovered >= 0.90 ? 'bg-emerald-500/20 border border-emerald-500/50' : 'bg-slate-800'}`}>
                        <p className="text-[9px] font-bold text-slate-400">TP2 (20%)</p>
                        <p className={`text-xs font-bold ${trade.tp2_active ? 'text-blue-400' : trade.portion_recovered >= 0.90 ? 'text-emerald-400' : 'text-slate-600'}`}>
                          {trade.tp2_active ? '⏳ Active' : trade.portion_recovered >= 0.90 ? '✓' : '-'}
                        </p>
                      </div>
                      <div className={`px-3 py-2 rounded-lg text-center ${trade.runner_active ? 'bg-purple-500/20 border border-purple-500/50' : 'bg-slate-800'}`}>
                        <p className="text-[9px] font-bold text-slate-400">Runner (10%)</p>
                        <p className={`text-xs font-bold ${trade.runner_active ? 'text-purple-400' : 'text-slate-600'}`}>
                          {trade.runner_active ? '🚀 Active' : '-'}
                        </p>
                      </div>
                    </div>

                    {/* Recovered */}
                    <div className="text-right px-4 border-l border-slate-800">
                      <p className="text-[10px] text-slate-500 uppercase font-bold">Recovered</p>
                      <p className="text-sm font-black text-emerald-400">{(trade.portion_recovered * 100).toFixed(0)}%</p>
                      <p className="text-xs text-slate-500">${(positionSize * trade.portion_recovered).toFixed(2)}</p>
                    </div>
                  </div>

                  {/* TP/SL details */}
                  <div className="mt-3 pt-3 border-t border-slate-800 flex gap-6 text-xs">
                    <span className="text-slate-500">SL1: <span className="text-rose-400">-{trade.stop_loss_1?.toFixed(2)}%</span></span>
                    <span className="text-slate-500">TP1: <span className="text-emerald-400">+{trade.take_profit_1?.toFixed(2)}%</span></span>
                    <span className="text-slate-500">TP2: <span className="text-emerald-400">+{trade.take_profit_2?.toFixed(2)}%</span></span>
                    <span className="text-slate-500">Runner: <span className="text-purple-400">+{trade.runner?.toFixed(2)}%</span></span>
                  </div>
                </div>
              )}) : (
                <div className="p-8 border border-dashed border-slate-800 rounded-2xl text-center text-slate-600 italic">
                  No open positions currently.
                </div>
              )}
            </div>
          </div>

          {/* CLOSED POSITIONS */}
          <div className="space-y-4">
            <h3 className="text-sm font-black text-slate-500 uppercase tracking-widest flex items-center gap-2">
              <span className="w-4 h-[2px] bg-slate-600"></span> Trade History ({closedPositions.length})
            </h3>
            
            <div className="bg-slate-900/50 border border-slate-800 rounded-xl overflow-hidden">
              {closedPositions.length > 0 ? (
                <div className="max-h-64 overflow-y-auto">
                  <table className="w-full text-xs">
                    <thead className="bg-slate-800/50 sticky top-0">
                      <tr className="text-slate-500 uppercase">
                        <th className="p-3 text-left">Crypto</th>
                        <th className="p-3 text-left">Direction</th>
                        <th className="p-3 text-right">Position</th>
                        <th className="p-3 text-right">Entry</th>
                        <th className="p-3 text-center">Result</th>
                        <th className="p-3 text-right">Date</th>
                      </tr>
                    </thead>
                    <tbody>
                      {closedPositions.map((trade, idx) => (
                        <tr key={trade.id_trade || idx} className="border-t border-slate-800/50 hover:bg-slate-800/30">
                          <td className="p-3 font-bold text-white">{trade.symbol}</td>
                          <td className="p-3">
                            <span className={trade.direction === 1 ? 'text-emerald-400' : 'text-rose-400'}>
                              {trade.direction === 1 ? 'LONG' : 'SHORT'}
                            </span>
                          </td>
                          <td className="p-3 text-right text-slate-300">${trade.position_size?.toFixed(2)}</td>
                          <td className="p-3 text-right text-slate-400">${trade.entry_price?.toLocaleString()}</td>
                          <td className="p-3 text-center">
                            <span className={`px-2 py-1 rounded text-[10px] font-bold ${
                              trade.result === 'WIN' ? 'bg-emerald-500/20 text-emerald-400' : 
                              trade.result === 'LOSS' ? 'bg-rose-500/20 text-rose-400' : 
                              'bg-amber-500/20 text-amber-400'
                            }`}>
                              {trade.result}
                            </span>
                          </td>
                          <td className="p-3 text-right text-slate-500">
                            {new Date(trade.timestamp).toLocaleDateString()}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="p-6 text-center text-slate-600 italic">
                  No closed trades.
                </div>
              )}
            </div>
          </div>
        </section>

        {/* COLUMN 3: SIGNALS */}
        <section className="space-y-4">
          <h3 className="text-sm font-black text-slate-500 uppercase tracking-widest flex items-center gap-2">
            <span className="w-4 h-[2px] bg-blue-500"></span> Scanner ({signals.length})
          </h3>
          
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden max-h-[600px] overflow-y-auto">
            {signals.map((sig) => (
              <div key={sig.crypto_id} className="p-4 hover:bg-slate-800/50 transition-all group border-b border-slate-800/50 last:border-0">
                <div className="flex justify-between items-center">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-black text-white text-sm uppercase">{sig.symbol}</span>
                      <a 
                        href={`/crypto/${sig.crypto_id}`}
                        className="opacity-0 group-hover:opacity-100 transition-opacity bg-blue-600 hover:bg-blue-500 px-2 py-0.5 rounded text-[9px] font-bold text-white"
                      >
                        →
                      </a>
                    </div>
                    <div className="flex gap-3 mt-1 text-[10px]">
                      <span className="text-slate-500">
                        Tech: <span className={sig.score_metric > 0 ? 'text-emerald-400' : 'text-rose-400'}>
                          {sig.score_metric?.toFixed(3)}
                        </span>
                      </span>
                      <span className="text-slate-500">
                        Trend: <span className={sig.trend > 0 ? 'text-emerald-400' : 'text-rose-400'}>
                          {sig.trend?.toFixed(3)}
                        </span>
                      </span>
                    </div>
                  </div>
                  
                  <div className="text-right">
                    <span className={`text-xl font-black font-mono ${
                      sig.score_total > 0.6 ? 'text-emerald-400' : 
                      sig.score_total < -0.6 ? 'text-rose-400' : 
                      'text-slate-500'
                    }`}>
                      {Number(sig.score_total).toFixed(2)}
                    </span>
                    <p className="text-[9px] text-slate-600 font-mono">
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