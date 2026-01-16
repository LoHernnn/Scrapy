import { query } from '@/lib/db';
import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const res = await query(`
      WITH 
      -- Configuration TP weights
      tp_weights AS (
        SELECT 0.70 as tp1_weight, 0.20 as tp2_weight, 0.10 as runner_weight
      ),
      -- Trades actifs (non complètement fermés)
      active_trades AS (
        SELECT 
          t.*,
          c.symbol,
          c.name,
          -- Calculer quelle partie est encore active
          CASE WHEN t.status_1 = 0 THEN true ELSE false END as tp1_active,
          CASE WHEN t.status_1 != 0 AND t.status_2 = 0 THEN true ELSE false END as tp2_active,
          CASE WHEN t.status_2 != 0 AND t.status = 0 THEN true ELSE false END as runner_active,
          -- Calculer combien a été récupéré (basé sur les status) avec les poids config
          CASE 
            WHEN t.status_1 != 0 AND t.status_2 = 0 THEN (SELECT tp1_weight FROM tp_weights)
            WHEN t.status_2 != 0 AND t.status = 0 THEN (SELECT tp1_weight + tp2_weight FROM tp_weights)
            ELSE 0.0
          END as portion_recovered,
          -- Valeur totale de la position
          t.position_size as total_position_value,
          -- Prix actuel pour calcul PnL latent
          (SELECT b.price FROM cyptos_data_base b WHERE b.crypto_id = t.crypto_id ORDER BY b.timestamp DESC LIMIT 1) as current_price
        FROM crypto_trade_data t
        JOIN cryptos c ON t.crypto_id = c.id
        WHERE t.status = 0  -- Trade pas complètement fermé
      ),
      -- Trades complètement clôturés
      closed_trades AS (
        SELECT 
          t.*,
          c.symbol,
          c.name,
          -- Déterminer si c'était un gain ou une perte basé sur les status
          CASE 
            WHEN t.status = 1 THEN 'WIN'
            WHEN t.status = -1 THEN 'LOSS'
            WHEN t.status_1 = 1 OR t.status_2 = 1 THEN 'PARTIAL_WIN'
            ELSE 'CLOSED'
          END as result
        FROM crypto_trade_data t
        JOIN cryptos c ON t.crypto_id = c.id
        WHERE t.status != 0  -- Trade complètement fermé
        ORDER BY t.timestamp DESC
        LIMIT 50
      ),
      -- Statistiques des trades clôturés
      closed_stats AS (
        SELECT 
          COUNT(*) as total_closed,
          COUNT(CASE WHEN status = 1 THEN 1 END) as wins,
          COUNT(CASE WHEN status = -1 THEN 1 END) as losses
        FROM crypto_trade_data
        WHERE status != 0
      ),
      -- Calcul du portfolio réel
      portfolio_calc AS (
        SELECT
          -- Capital investi en positions actives (partie non encore récupérée)
          COALESCE(SUM(
            CASE WHEN status = 0 THEN 
              position_size * (1 - CASE 
                WHEN status_1 != 0 AND status_2 = 0 THEN 0.70
                WHEN status_2 != 0 THEN 0.90
                ELSE 0.0
              END)
            ELSE 0 
            END
          ), 0) as total_in_crypto,
          -- Nombre de positions actives
          COUNT(CASE WHEN status = 0 THEN 1 END) as active_count
        FROM crypto_trade_data
      ),
      -- Dernière performance enregistrée (pour le free_cash)
      latest_perf AS (
        SELECT * FROM portfolio_performance ORDER BY timestamp DESC LIMIT 1
      ),
      -- Historique du portfolio pour le graphique (dernières 24h)
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
      -- Signaux actuels
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
    
    // Calcul du portfolio correct
    const rawPerf = rawData.raw_performance || {};
    const portfolioCalc = rawData.portfolio_calc || {};
    const closedStats = rawData.closed_stats || {};
    const activePositions = rawData.active_positions || [];
    const closedPositions = rawData.closed_positions || [];
    
    // Capital en cash = free_cash de la dernière perf
    const freeCash = parseFloat(rawPerf.free_cash) || 0;
    // Capital en crypto = somme des positions actives (partie non récupérée)
    const totalInCrypto = parseFloat(portfolioCalc.total_in_crypto) || 0;
    // Capital total = cash + crypto
    const totalCapital = freeCash + totalInCrypto;
    
    // Calcul du PnL latent réel pour chaque position active
    let totalUnrealizedPnl = 0;
    if (activePositions) {
      for (const pos of activePositions) {
        if (pos.current_price && pos.entry_price) {
          const currentPrice = parseFloat(pos.current_price);
          const entryPrice = parseFloat(pos.entry_price);
          const positionSize = parseFloat(pos.position_size);
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
    
    // Capital total avec PnL latent
    const totalWithPnl = freeCash + totalInCrypto + totalUnrealizedPnl;
    
    // Vérification de cohérence
    const initialCapital = 10000;
    const expectedTotal = parseFloat(rawPerf.total_balance) || initialCapital;
    const discrepancy = Math.abs(totalWithPnl - expectedTotal);
    const hasDiscrepancy = discrepancy > 1; // Tolérance de 1$
    
    // Win rate
    const totalClosed = closedStats.total_closed || 0;
    const wins = closedStats.wins || 0;
    const winRate = totalClosed > 0 ? ((wins / totalClosed) * 100).toFixed(1) : 0;
    
    // Construire l'objet performance corrigé
    const performance = {
      total_balance: totalWithPnl,
      free_cash: freeCash,
      total_in_crypto: totalInCrypto,
      unrealized_pnl: totalUnrealizedPnl,
      active_positions_count: portfolioCalc.active_count || 0,
      // Stats trades
      total_closed_trades: totalClosed,
      wins: wins,
      losses: closedStats.losses || 0,
      win_rate: winRate,
      // Vérification
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
    console.error("Erreur API Bot:", error);
    return NextResponse.json(
      { error: "Failed to fetch bot data", details: error.message }, 
      { status: 500 }
    );
  }
}