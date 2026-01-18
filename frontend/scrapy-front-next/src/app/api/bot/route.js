import { query } from '@/lib/db';
import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const res = await query(`
      WITH 
      tp_weights AS (
        SELECT 0.70 as tp1_weight, 0.20 as tp2_weight, 0.10 as runner_weight
      ),
      active_trades AS (
        SELECT 
          t.*,
          c.symbol,
          c.name,
          CASE WHEN t.status_1 = 0 THEN true ELSE false END as tp1_active,
          CASE WHEN t.status_1 != 0 AND t.status_2 = 0 THEN true ELSE false END as tp2_active,
          CASE WHEN t.status_2 != 0 AND t.status = 0 THEN true ELSE false END as runner_active,
          CASE 
            WHEN t.status_1 != 0 AND t.status_2 = 0 THEN (SELECT tp1_weight FROM tp_weights)
            WHEN t.status_2 != 0 AND t.status = 0 THEN (SELECT tp1_weight + tp2_weight FROM tp_weights)
            ELSE 0.0
          END as portion_recovered,
          COALESCE(t.total_injected, 0) + t.position_size as total_position_value,
          COALESCE(t.average_entry_price, t.entry_price) as effective_entry_price,
          (SELECT b.price FROM cyptos_data_base b WHERE b.crypto_id = t.crypto_id ORDER BY b.timestamp DESC LIMIT 1) as current_price
        FROM crypto_trade_data t
        JOIN cryptos c ON t.crypto_id = c.id
        WHERE t.status = 0 
      ),
      closed_trades AS (
        SELECT 
          t.*,
          c.symbol,
          c.name,
          COALESCE(t.total_injected, 0) + t.position_size as total_position_value,
          CASE 
            WHEN t.status = 1 THEN 'WIN'
            WHEN t.status = -1 THEN 'LOSS'
            WHEN t.status = 2 THEN 'INERTIA'
            WHEN t.status_1 = 1 OR t.status_2 = 1 THEN 'PARTIAL_WIN'
            ELSE 'CLOSED'
          END as result
        FROM crypto_trade_data t
        JOIN cryptos c ON t.crypto_id = c.id
        WHERE t.status != 0  
        ORDER BY t.timestamp DESC
        LIMIT 50
      ),
      
      closed_stats AS (
        SELECT 
          COUNT(*) as total_closed,
          COUNT(CASE WHEN status = 1 THEN 1 END) as wins,
          COUNT(CASE WHEN status = -1 THEN 1 END) as losses,
          COUNT(CASE WHEN status = 2 THEN 1 END) as inertia_exits
        FROM crypto_trade_data
        WHERE status != 0
      ),
      portfolio_calc AS (
        SELECT
          
          COALESCE(SUM(
            CASE WHEN status = 0 THEN 
              (position_size + COALESCE(total_injected, 0)) * (1 - CASE 
                WHEN status_1 != 0 AND status_2 = 0 THEN 0.70
                WHEN status_2 != 0 THEN 0.90
                ELSE 0.0
              END)
            ELSE 0 
            END
          ), 0) as total_in_crypto,
          
          COALESCE(SUM(CASE WHEN status = 0 THEN COALESCE(total_injected, 0) ELSE 0 END), 0) as total_reinjected,
          COALESCE(SUM(CASE WHEN status = 0 THEN reinjection_count ELSE 0 END), 0) as total_reinjection_count,
          
          COUNT(CASE WHEN status = 0 THEN 1 END) as active_count
        FROM crypto_trade_data
      ),
      
      latest_perf AS (
        SELECT * FROM portfolio_performance ORDER BY timestamp DESC LIMIT 1
      ),
      
      portfolio_history AS (
        SELECT 
          timestamp,
          total_balance,
          free_cash,
          unrealized_pnl
        FROM portfolio_performance
        WHERE timestamp > NOW() - INTERVAL '24 hours'
        ORDER BY timestamp DESC
        LIMIT 200
      ),
      
      latest_signals AS (
        SELECT DISTINCT ON (crypto_id) 
          s.crypto_id, 
          s.score_total, 
          s.score_metric, 
          s.trend, 
          s.timestamp,
          c.symbol, c.name 
        FROM crypto_scores s
        JOIN cryptos c ON s.crypto_id = c.id
        ORDER BY crypto_id, s.timestamp DESC
      )
      SELECT 
        (SELECT row_to_json(p) FROM latest_perf p) as raw_performance,
        (SELECT row_to_json(pc) FROM portfolio_calc pc) as portfolio_calc,
        (SELECT row_to_json(cs) FROM closed_stats cs) as closed_stats,
        (SELECT json_agg(sig) FROM (SELECT * FROM latest_signals ORDER BY score_total DESC) sig) as all_signals,
        (SELECT json_agg(a) FROM active_trades a) as active_positions,
        (SELECT json_agg(c) FROM closed_trades c) as closed_positions,
        (SELECT json_agg(h ORDER BY h.timestamp ASC) FROM portfolio_history h) as portfolio_history
    `);

    const rawData = res.rows[0] || {};
    

    const rawPerf = rawData.raw_performance || {};
    const portfolioCalc = rawData.portfolio_calc || {};
    const closedStats = rawData.closed_stats || {};
    const activePositions = rawData.active_positions || [];
    const closedPositions = rawData.closed_positions || [];
    

    const freeCash = parseFloat(rawPerf.free_cash) || 0;
    
    const totalInCrypto = parseFloat(portfolioCalc.total_in_crypto) || 0;
    const totalReinjected = parseFloat(portfolioCalc.total_reinjected) || 0;
    const totalReinjectionCount = parseInt(portfolioCalc.total_reinjection_count) || 0;
    
    const totalCapital = freeCash + totalInCrypto;
    

    let totalUnrealizedPnl = 0;
    if (activePositions) {
      for (const pos of activePositions) {
        if (pos.current_price && pos.entry_price) {
          const currentPrice = parseFloat(pos.current_price);
          // Use effective entry price (considers reinjections)
          const entryPrice = parseFloat(pos.effective_entry_price) || parseFloat(pos.entry_price);
          const positionSize = parseFloat(pos.total_position_value) || parseFloat(pos.position_size);
          const portionRemaining = 1 - (parseFloat(pos.portion_recovered) || 0);
          const remainingSize = positionSize * portionRemaining;
          
          if (pos.direction === 1) { // Long
            totalUnrealizedPnl += (currentPrice - entryPrice) / entryPrice * remainingSize;
          } else { // Short
            totalUnrealizedPnl += (entryPrice - currentPrice) / entryPrice * remainingSize;
          }
        }
      }
    }
    

    const totalWithPnl = freeCash + totalInCrypto + totalUnrealizedPnl;
    

    const initialCapital = 10000;
    const expectedTotal = parseFloat(rawPerf.total_balance) || initialCapital;
    
    // Integrity check - compare DB value with calculated value
    // Allow 1% tolerance or $10 absolute, whichever is greater
    const tolerancePercent = Math.abs(expectedTotal * 0.01);
    const toleranceAbsolute = 10;
    const tolerance = Math.max(tolerancePercent, toleranceAbsolute);
    const discrepancy = Math.abs(totalWithPnl - expectedTotal);
    const hasDiscrepancy = discrepancy > tolerance; 
    

    const totalClosed = closedStats.total_closed || 0;
    const wins = closedStats.wins || 0;
    const inertiaExits = closedStats.inertia_exits || 0;
    const winRate = totalClosed > 0 ? ((wins / totalClosed) * 100).toFixed(1) : 0;
    

    const performance = {
      total_balance: totalWithPnl,
      free_cash: freeCash,
      total_in_crypto: totalInCrypto,
      unrealized_pnl: totalUnrealizedPnl,
      active_positions_count: portfolioCalc.active_count || 0,
      // Reinjection stats
      total_reinjected: totalReinjected,
      total_reinjection_count: totalReinjectionCount,
      // Trade stats
      total_closed_trades: totalClosed,
      wins: wins,
      losses: closedStats.losses || 0,
      inertia_exits: inertiaExits,
      win_rate: winRate,
      check: {
        expected: expectedTotal,
        calculated: totalWithPnl,
        discrepancy: discrepancy,
        status: hasDiscrepancy ? 'WARNING' : 'OK'
      },
      timestamp: rawPerf.timestamp
    };

    const data = {
      performance,
      all_signals: rawData.all_signals || [],
      active_positions: activePositions,
      closed_positions: closedPositions,
      portfolio_history: rawData.portfolio_history || []
    };

    return NextResponse.json(data);
  } catch (error) {
    console.error("Error API Bot:", error);
    return NextResponse.json(
      { error: "Failed to fetch bot data", details: error.message }, 
      { status: 500 }
    );
  }
}