import SentimentSection from "@/components/ui/SentimentSection";
import MultiChart from "@/components/charts/MultiChart";

async function getCryptoData(id) {
  const res = await fetch(`http://localhost:3000/api/crypto/${id}`, { cache: 'no-store' });
  if (!res.ok) return null;
  return res.json();
}

async function getTweets(id) {
  const res = await fetch(`http://localhost:3000/api/crypto/${id}/tweets`, { cache: 'no-store' });
  if (!res.ok) return null;
  return res.json();
}

async function getHistory(id, range = '24h') {
  const res = await fetch(`http://localhost:3000/api/history/${id}?range=${range}`, { cache: 'no-store' });
  if (!res.ok) return [];
  return res.json();
}



export default async function CryptoDetail({ params, searchParams }) {
  const { id } = await params;
  const { range } = await searchParams || '24h';


  const [data, sentimentData, historyData] = await Promise.all([
    getCryptoData(id),
    getTweets(id),
    getHistory(id, range)
  ]);

  if (!data) {
    return (
      <div className="p-10 text-center">
        <h1 className="text-2xl font-bold text-white">Crypto non trouvée...</h1>
        <p className="text-slate-400">L'ID {id} n'existe pas dans la base de données.</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header: Name, Price, and Change */}
      <div className="flex justify-between items-end border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-4xl font-bold text-white">{data.crypto.name}</h1>
            <span className="text-xl text-slate-500 font-mono uppercase tracking-widest">{data.crypto.symbol}</span>
          </div>
          <p className="text-slate-400 font-medium">Market Rank: <span className="text-blue-400">#{data.rank}</span></p>
        </div>
        
        <div className="text-right">
          <p className="text-sm text-slate-500 uppercase font-bold tracking-tighter mb-1">Current Price</p>
          <p className="text-4xl font-mono font-bold text-white">
            {parseFloat(data.base?.price).toLocaleString('en-US', { style: 'currency', currency: 'USD' })}
          </p>
          <p className={`text-lg font-bold mt-1 ${data.base?.variation24h_pst >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
            {data.base?.variation24h_pst >= 0 ? '▲' : '▼'} {Math.abs(data.base?.variation24h_pst).toFixed(2)}%
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column (2/3): Chart and Technical Indicators */}
        <div className="lg:col-span-2 space-y-6">
            {/* Advanced Chart Card */}
            <div className="glass-card h-[550px] flex flex-col">
                <div className="flex justify-between items-start mb-6">
                <div>
                    <h3 className="text-lg font-bold text-white uppercase tracking-tighter">Advanced Analytics</h3>
                    <div className="flex items-center gap-2 mt-1">
                    <span className="relative flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
                    </span>
                    <span className="text-[10px] text-blue-400 uppercase font-bold tracking-widest">Live Terminal</span>
                    </div>
                </div>

                {/* Range Selector */}
                <div className="flex bg-slate-900/80 p-1 rounded-xl border border-slate-700/50 shadow-inner">
                    {[
                    { label: '12H', val: '12h' },
                    { label: '24H', val: '24h' },
                    { label: '7J', val: '7j' },
                    { label: '30J', val: '30j' },
                    { label: 'ALL', val: 'all' }
                    ].map((r) => (
                    <a
                        key={r.val}
                        href={`?range=${r.val}`}
                        className={`px-3 py-1.5 rounded-lg text-[10px] font-black transition-all duration-200 ${
                        (range || '24h') === r.val 
                        ? 'bg-blue-600 text-white shadow-md shadow-blue-900/40' 
                        : 'text-slate-500 hover:text-slate-300 hover:bg-slate-800'
                        }`}
                    >
                        {r.label}
                    </a>
                    ))}
                </div>
                </div>
                
                {/* New multi-data component */}
                <div className="flex-1 w-full min-h-0">
                <MultiChart data={historyData} />
                </div>
            </div>

            {/* Impactful Widgets Grid (Data from your new tables) */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                
                {/* 1. Liquidity & Order Book (Binance Table) */}
                <div className="glass-card border-t-2 border-orange-500/50">
                <span className="text-slate-500 text-[10px] uppercase font-bold">Binance Liquidity</span>
                <div className="mt-3 space-y-2">
                    <div className="flex justify-between text-sm font-mono">
                    <span className="text-emerald-400">Best Bid</span>
                    <span className="text-white">${parseFloat(data.binance?.bids_price_1 || 0).toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between text-sm font-mono">
                    <span className="text-rose-400">Best Ask</span>
                    <span className="text-white">${parseFloat(data.binance?.asks_price_1 || 0).toFixed(2)}</span>
                    </div>
                    <div className="mt-3 pt-2 border-t border-slate-800">
                    <span className="text-[10px] text-slate-500 block">Open Interest</span>
                    <p className="text-white font-bold">${(data.binance?.open_interest / 1e6 || 0).toFixed(2)}M</p>
                    </div>
                </div>
                </div>

                {/* 2. Potential & ATH (Base Table) */}
                <div className="glass-card border-t-2 border-purple-500/50">
                <span className="text-slate-500 text-[10px] uppercase font-bold">ATH Performance</span>
                <div className="mt-2">
                    <p className="text-2xl font-bold text-white">${parseFloat(data.base?.all_time_high || 0).toFixed(2)}</p>
                    <p className="text-rose-400 text-xs font-bold">
                    -{Math.abs(data.base?.all_time_high_pst || 0).toFixed(2)}% <span className="text-slate-500 font-normal text-[10px]">depuis le pic</span>
                    </p>
                    <div className="mt-4 flex items-center gap-2">
                        <div className="flex-1 bg-slate-800 h-1 rounded-full">
                            <div className="bg-purple-500 h-full rounded-full" style={{ width: `${100 - Math.abs(data.base?.all_time_high_pst || 0)}%` }}></div>
                        </div>
                    </div>
                </div>
                </div>

                {/* 3. Technical Levels (Detail Table) */}
                <div className="glass-card border-t-2 border-blue-500/50">
                <span className="text-slate-500 text-[10px] uppercase font-bold">Support & Résistance</span>
                <div className="grid grid-cols-1 gap-3 mt-2">
                    <div className="flex justify-between items-center">
                    <span className="text-[10px] text-slate-400 italic">Resist. (R1)</span>
                    <span className="text-rose-400 font-mono font-bold">${parseFloat(data.details?.r1 || 0).toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between items-center">
                    <span className="text-[10px] text-slate-400 italic">Pivot (PP)</span>
                    <span className="text-yellow-500 font-mono font-bold">${parseFloat(data.details?.pp || 0).toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between items-center">
                    <span className="text-[10px] text-slate-400 italic">Support (S1)</span>
                    <span className="text-emerald-400 font-mono font-bold">${parseFloat(data.details?.s1 || 0).toFixed(2)}</span>
                    </div>
                </div>
                </div>

            </div>
            </div>

        {/* Right Column (1/3): Sentiment & Social Signal */}
        <div className="lg:col-span-1">
          {sentimentData && <SentimentSection sentimentData={sentimentData} />}
        </div>
      </div>
    </div>
  );
}