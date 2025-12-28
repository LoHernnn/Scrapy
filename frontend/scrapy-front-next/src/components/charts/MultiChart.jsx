"use client";
import { useState } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, 
  CartesianGrid, ReferenceLine, Legend 
} from 'recharts';

const METRICS = [
  { id: 'price', label: 'Prix', color: '#3b82f6', yAxisId: 'left', unit: '$' },
  { id: 'rsi', label: 'RSI', color: '#fbbf24', yAxisId: 'right', unit: '' },
  { id: 'sentiment', label: 'Sentiment', color: '#10b981', yAxisId: 'right', unit: '' },
  { id: 'funding', label: 'Funding', color: '#f43f5e', yAxisId: 'right', unit: '%' },
];

export default function MultiChart({ data }) {
  const [activeMetrics, setActiveMetrics] = useState(['price']);

  const toggleMetric = (id) => {
    setActiveMetrics(prev => 
      prev.includes(id) ? prev.filter(m => m !== id) : [...prev, id]
    );
  };

  return (
    <div className="flex flex-col h-full w-full">
      {/* Stylized Buttons Menu */}
      <div className="flex flex-wrap gap-2 mb-6">
        {METRICS.map(m => (
          <button
            key={m.id}
            onClick={() => toggleMetric(m.id)}
            className={`px-3 py-1.5 rounded-lg text-[10px] font-bold border transition-all flex items-center gap-2 ${
              activeMetrics.includes(m.id) 
              ? 'bg-blue-600/10 border-blue-500 text-blue-400 shadow-[0_0_10px_rgba(59,130,246,0.1)]' 
              : 'bg-slate-900 border-slate-800 text-slate-500 opacity-60'
            }`}
          >
            <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: m.color }} />
            {m.label}
          </button>
        ))}
      </div>

      <div className="flex-1 w-full min-h-0">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
            {/* Discrete Grid */}
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} opacity={0.4} />
            
            {/* X Axis with dates */}
            <XAxis 
              dataKey="fullDate" 
              stroke="#475569" 
              fontSize={10} 
              tickLine={false} 
              axisLine={false}
              minTickGap={40}
            />

            {/* Left Axis: Price */}
            <YAxis 
              yAxisId="left"
              orientation="left"
              stroke="#3b82f6"
              fontSize={10}
              tickLine={false}
              axisLine={false}
              domain={['auto', 'auto']}
              tickFormatter={(val) => `$${val.toLocaleString()}`}
              width={60}
            />

            {/* Right Axis: Indicators (0-100) */}
            {activeMetrics.some(m => m !== 'price') && (
              <YAxis 
                yAxisId="right"
                orientation="right"
                stroke="#64748b"
                fontSize={10}
                tickLine={false}
                axisLine={false}
                domain={[0, 100]}
                width={30}
              />
            )}

            {/* RSI reference lines (appear if RSI is active) */}
            {activeMetrics.includes('rsi') && (
              <>
                <ReferenceLine yAxisId="right" y={70} stroke="#f43f5e" strokeDasharray="3 3" label={{ position: 'right', value: '70', fill: '#f43f5e', fontSize: 10 }} />
                <ReferenceLine yAxisId="right" y={30} stroke="#10b981" strokeDasharray="3 3" label={{ position: 'right', value: '30', fill: '#10b981', fontSize: 10 }} />
              </>
            )}

            <Tooltip 
              contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px' }}
              labelStyle={{ color: '#94a3b8', fontSize: '11px', fontWeight: 'bold' }}
              itemStyle={{ fontSize: '12px', padding: '0px' }}
              labelFormatter={(label, payload) => payload[0]?.payload?.fullDate || label}
            />

            {activeMetrics.map(mId => {
              const config = METRICS.find(m => m.id === mId);
              return (
                <Line
                  key={mId}
                  yAxisId={config.yAxisId}
                  type="monotone"
                  dataKey={mId}
                  stroke={config.color}
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 4, strokeWidth: 0 }}
                  animationDuration={1000}
                />
              );
            })}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}