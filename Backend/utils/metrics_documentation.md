# Metrics Documentation

This document provides detailed explanations of all metrics and technical analysis functions used in the cryptocurrency analysis system.

---

## Table of Contents

1. [Volume Metrics](#volume-metrics)
2. [Price Variation Metrics](#price-variation-metrics)
3. [Supply Metrics](#supply-metrics)
4. [Pivot Points](#pivot-points)
5. [RSI (Relative Strength Index)](#rsi-relative-strength-index)
6. [MACD (Moving Average Convergence Divergence)](#macd-moving-average-convergence-divergence)
7. [Moving Averages](#moving-averages)
8. [POC (Point of Control)](#poc-point-of-control)
9. [Market Dominance](#market-dominance)
10. [Fibonacci Retracement Levels](#fibonacci-retracement-levels)

---

## Volume Metrics

### Function: `volume_data(data)`

**Purpose**: Analyzes trading volume changes over different time periods (1 day, 7 days, 30 days) and compares current volume to historical averages.

**Parameters**:
- `data`: Dictionary containing `total_volumes` array with timestamps and volume values

**Returns**: Dictionary with the following keys:
- `volume_actuel`: Current trading volume
- `volume_1j`, `volume_7j`, `volume_30j`: Volume at 1, 7, and 30 days ago
- `variation_1j`, `variation_7j`, `variation_30j`: Percentage change from historical points
- `volume_moyen_1j`, `volume_moyen_7j`, `volume_moyen_30j`: Average volumes over periods
- `variation_moyenne_1j`, `variation_moyenne_7j`, `variation_moyenne_30j`: % change vs averages

**Interpretation**:

| Range | Interpretation |
|-------|---------------|
| **Variation > +50%** | Very high volume spike - strong interest, potential breakout or news event |
| **+20% to +50%** | Elevated volume - increased trading activity, growing momentum |
| **-20% to +20%** | Normal volume - stable trading conditions |
| **-50% to -20%** | Low volume - reduced interest, consolidation phase |
| **< -50%** | Very low volume - weak interest, low liquidity, avoid trading |

**Trading Signals**:
- High volume + price increase = Strong bullish signal
- High volume + price decrease = Strong bearish signal
- Low volume + price movement = Weak signal, likely false breakout

---

## Price Variation Metrics

### Functions: `variation_1j()`, `variation_7j()`, `variation_14j()`, `variation_30j()`

**Purpose**: Calculate price changes over different time horizons and compare current price to period averages.

**Parameters**:
- `data`: Dictionary containing `prices` array with timestamps and price values

**Returns**: Tuple of:
1. Percentage change from period start
2. Absolute value change
3. Percentage vs period average
4. Current price or period average

### Function: `calcul_variation_price(data_all, crypto)`

**Purpose**: Aggregates all price variations into a single comprehensive report.

**Returns**: Dictionary with nested structure:
```json
{
  "current_price": 45000,
  "1d": {"percentage": 2.5, "value": 1100, "vs_avg": 1.2, "mean": 44500},
  "7d": {"percentage": 8.3, "value": 3500, "vs_avg": 4.1, "mean": 43200},
  "14d": {"percentage": 12.1, "value": 4900, "vs_avg": 5.8, "mean": 42500},
  "30d": {"percentage": 15.7, "value": 6100, "vs_avg": 7.2, "mean": 41900}
}
```

**Interpretation**:

| Period | Range | Interpretation |
|--------|-------|---------------|
| **1-Day** | > +5% | Strong daily gain, high volatility |
| | +2% to +5% | Moderate bullish movement |
| | -2% to +2% | Consolidation, sideways movement |
| | -5% to -2% | Moderate bearish movement |
| | < -5% | Strong daily loss, high risk |
| **7-Day** | > +15% | Strong weekly rally, momentum building |
| | +5% to +15% | Healthy uptrend |
| | -5% to +5% | Neutral, range-bound |
| | -15% to -5% | Corrective phase |
| | < -15% | Significant downtrend, bear market |
| **30-Day** | > +30% | Parabolic move, potential overextension |
| | +10% to +30% | Strong monthly performance |
| | -10% to +10% | Stable market conditions |
| | -30% to -10% | Bear market territory |
| | < -30% | Severe decline, high risk |

**Trading Insights**:
- `vs_avg` above 0: Price trading above period average (bullish)
- `vs_avg` below 0: Price trading below period average (bearish)
- Large divergence between short and long-term variations indicates trend change

---

## Supply Metrics

### Function: `get_supply(crypto_id, data)`

**Purpose**: Extract supply data to understand token economics and inflation dynamics.

**Returns**: Tuple of:
1. `circulating_supply`: Tokens currently in circulation
2. `total_supply`: Total tokens currently existing
3. `max_supply`: Maximum tokens that will ever exist (can be None)

**Interpretation**:

| Metric | Formula | Interpretation |
|--------|---------|---------------|
| **Circulating Ratio** | circulating / max_supply | **> 90%**: Low inflation risk, mature project |
| | | **50-90%**: Moderate emission schedule |
| | | **< 50%**: High inflation risk, early stage |
| **Supply Overhang** | (total - circulating) / circulating | **> 50%**: Large unlocked supply risk |
| | | **20-50%**: Moderate future dilution |
| | | **< 20%**: Low dilution risk |
| **Max Supply** | None | Unlimited supply (inflationary like ETH) |
| | Fixed number | Deflationary model (like BTC 21M cap) |

**Investment Considerations**:
- High circulating ratio = Less dilution risk
- Low max supply = Scarcity premium potential
- No max supply = Requires strong demand to offset inflation

---

## Pivot Points

### Function: `calculer_pivot_support_resistance(crypto_id, data)`

**Purpose**: Calculate classical pivot points for intraday support and resistance levels.

**Formula**:
```
Pivot Point (PP) = (High + Low + Close) / 3
R1 = (2 × PP) - Low
R2 = PP + (High - Low)
S1 = (2 × PP) - High
S2 = PP - (High - Low)
```

**Returns**: Tuple of (PP, R1, R2, S1, S2)

**Interpretation**:

| Level | Purpose | Action |
|-------|---------|--------|
| **R2** | Strong resistance | Take profit target for longs |
| **R1** | First resistance | Partial profit taking zone |
| **PP** | Equilibrium point | Trend indicator (above = bullish, below = bearish) |
| **S1** | First support | Initial buy zone |
| **S2** | Strong support | Deep value buy zone |

**Price Range Analysis**:
- **Above PP + closer to R1**: Bullish bias, look for breakout above R1
- **Between PP and R1**: Mild bullish, watch for PP support
- **At PP**: Neutral zone, wait for direction
- **Between PP and S1**: Mild bearish, watch for PP resistance
- **Below PP + closer to S1**: Bearish bias, look for breakdown below S1

**Trading Strategy**:
1. Buy near S1/S2 with stop below next support
2. Sell near R1/R2 with stop above next resistance
3. Breakout above R2 or below S2 signals strong trend

---

## RSI (Relative Strength Index)

### Function: `calcul_rsi(data, period=168)`

**Purpose**: Momentum oscillator measuring speed and magnitude of price changes to identify overbought/oversold conditions.

**Parameters**:
- `data`: Price data dictionary
- `period`: Lookback window (default 168 hours = 7 days)

**Formula**:
```
RSI = 100 - (100 / (1 + RS))
RS = Average Gain / Average Loss
```

**Returns**: Pandas Series with RSI values ranging from 0 to 100

**Interpretation**:

| RSI Value | Condition | Action |
|-----------|-----------|--------|
| **> 80** | Extremely overbought | Strong sell signal, expect correction |
| **70-80** | Overbought | Consider taking profits, bearish divergence likely |
| **50-70** | Bullish momentum | Uptrend intact, hold long positions |
| **40-50** | Neutral/Weak | Consolidation, wait for confirmation |
| **30-40** | Oversold zone | Early buy signal, wait for reversal confirmation |
| **20-30** | Deeply oversold | Strong buy signal, bounce likely |
| **< 20** | Extremely oversold | Capitulation, excellent buy opportunity |

**Advanced Signals**:
- **Bullish Divergence**: Price makes lower low, RSI makes higher low → Reversal up
- **Bearish Divergence**: Price makes higher high, RSI makes lower high → Reversal down
- **RSI crossing 50**: Confirms trend direction (above 50 = bullish, below 50 = bearish)

**Trading Rules**:
- **Buy**: RSI < 30 + bullish divergence + price support
- **Sell**: RSI > 70 + bearish divergence + price resistance
- **Trend Following**: Stay long when RSI > 50, short when RSI < 50

---

## MACD (Moving Average Convergence Divergence)

### Function: `calcul_macd(data, fast_period=12, slow_period=26, signal_period=9)`

**Purpose**: Trend-following momentum indicator showing relationship between two moving averages.

**Parameters**:
- `fast_period`: Fast EMA period (default 12)
- `slow_period`: Slow EMA period (default 26)
- `signal_period`: Signal line period (default 9)

**Formula**:
```
MACD Line = EMA(12) - EMA(26)
Signal Line = EMA(9) of MACD Line
Histogram = MACD Line - Signal Line
```

**Returns**: Tuple of (macd, signal_line, histogram) as Pandas Series

**Interpretation**:

| Component | Range | Interpretation |
|-----------|-------|---------------|
| **MACD Line** | > 0 | Bullish momentum (12 EMA above 26 EMA) |
| | < 0 | Bearish momentum (12 EMA below 26 EMA) |
| | Increasing | Momentum accelerating |
| | Decreasing | Momentum slowing |
| **Signal Line** | MACD crosses above | **Golden Cross** - Buy signal |
| | MACD crosses below | **Death Cross** - Sell signal |
| **Histogram** | > 0 | MACD above signal (bullish) |
| | < 0 | MACD below signal (bearish) |
| | Expanding | Trend strengthening |
| | Contracting | Trend weakening |

**Trading Signals**:

| Signal Type | Condition | Strength | Action |
|-------------|-----------|----------|--------|
| **Strong Buy** | MACD crosses above signal + histogram growing + both positive | High | Enter long position |
| **Buy** | MACD crosses above signal + histogram negative but growing | Medium | Consider long entry |
| **Strong Sell** | MACD crosses below signal + histogram shrinking + both negative | High | Enter short position |
| **Sell** | MACD crosses below signal + histogram positive but shrinking | Medium | Consider short entry |

**Divergence Signals**:
- **Bullish**: Price lower low + MACD higher low = Upward reversal coming
- **Bearish**: Price higher high + MACD lower high = Downward reversal coming

**Histogram Analysis**:
- Histogram peaking = Momentum exhaustion, prepare for reversal
- Histogram widening = Strong trend, ride the momentum
- Histogram near zero = Indecision, wait for breakout

---

## Moving Averages

### Function: `moving_averages(data, short_period=50, long_period=200)`

**Purpose**: Calculate Simple Moving Averages (SMA) and Exponential Moving Averages (EMA) to identify trend direction and dynamic support/resistance.

**Parameters**:
- `short_period`: Short-term period (default 50)
- `long_period`: Long-term period (default 200)

**Returns**: DataFrame with columns:
- `Close`: Original prices
- `SMA_50`, `SMA_200`: Simple moving averages
- `EMA_50`, `EMA_200`: Exponential moving averages

**Interpretation**:

### SMA vs EMA
- **SMA**: Equal weight to all prices, smoother but slower
- **EMA**: More weight to recent prices, more responsive to changes

### Moving Average Crossovers

| Cross Type | Description | Signal Strength |
|------------|-------------|-----------------|
| **Golden Cross** | MA 50 crosses above MA 200 | Very bullish - Major buy signal |
| **Death Cross** | MA 50 crosses below MA 200 | Very bearish - Major sell signal |
| **Price above both MAs** | Uptrend confirmed | Strong bullish, hold long |
| **Price below both MAs** | Downtrend confirmed | Strong bearish, stay short |
| **Price between MAs** | Transition phase | Neutral, wait for clarity |

### Price Distance from MA

| Distance from MA 200 | Interpretation |
|---------------------|----------------|
| **> +20%** | Extremely extended, correction likely |
| **+10% to +20%** | Strong uptrend, overbought risk |
| **-5% to +10%** | Healthy uptrend |
| **-5% to +5%** | Near equilibrium, consolidation |
| **-10% to -5%** | Healthy downtrend |
| **-20% to -10%** | Strong downtrend, oversold potential |
| **< -20%** | Extremely oversold, bounce likely |

### MA Slope Analysis
- **Rising MA**: Uptrend in progress
- **Flat MA**: Consolidation/range-bound
- **Falling MA**: Downtrend in progress

### Support/Resistance
- MAs act as dynamic support in uptrends
- MAs act as dynamic resistance in downtrends
- MA 200 is strongest support/resistance level

**Trading Strategy**:
1. **Trend Following**: Buy when price > MA 50 > MA 200, sell when price < MA 50 < MA 200
2. **Pullback Entry**: Buy dips to MA 50 in uptrends, sell rallies to MA 50 in downtrends
3. **Crossover Trading**: Enter on golden cross, exit on death cross

---

## POC (Point of Control)

### Function: `calculate_poc(data, period=14, nb_bins=50)`

**Purpose**: Identify the price level with the highest trading volume (most accepted price) using volume profile analysis.

**Parameters**:
- `data`: Price and volume data
- `period`: Days to analyze (default 14)
- `nb_bins`: Number of price bins (default 50)

**Methodology**:
1. Divide price range into 50 equal bins
2. Sum volume traded at each price level
3. Identify bin with maximum volume = POC

**Returns**: Single price value representing the POC

**Interpretation**:

| Current Price vs POC | Market State | Action |
|---------------------|--------------|--------|
| **> +5% above POC** | Trading above value | Overbought, expect pullback to POC |
| **+2% to +5% above** | Slight premium | Monitor for resistance |
| **Within ±2% of POC** | Fair value zone | Equilibrium, consolidation likely |
| **-2% to -5% below** | Slight discount | Monitor for support |
| **> -5% below POC** | Trading below value | Oversold, expect rally to POC |

**Trading Applications**:

| Scenario | Interpretation | Strategy |
|----------|---------------|----------|
| **POC Rising** | Accumulation phase, higher value | Bullish - Buy dips |
| **POC Falling** | Distribution phase, lower value | Bearish - Sell rallies |
| **POC Flat** | Range-bound market | Range trade between POC ± 5% |
| **Price returns to POC** | Magnet effect | Strong support/resistance, expect bounce/rejection |

**Volume Profile Context**:
- POC acts as a magnet - price tends to return to it
- High volume areas = Support/resistance zones
- Low volume areas = Price moves through quickly
- Breaking above/below POC with volume = Trend change

**Best Use**:
- Combine with other indicators (RSI, MACD) for confirmation
- Use POC as target for mean reversion trades
- Identify breakout levels (POC + high volume zones)

---

## Market Dominance

### Function: `get_crypto_dominance(data_global, market_cap, crypto_id="bitcoin")`

**Purpose**: Calculate a cryptocurrency's market share relative to total crypto market cap.

**Formula**:
```
Dominance = (Crypto Market Cap / Total Crypto Market Cap) × 100
```

**Parameters**:
- `data_global`: Global crypto market data
- `market_cap`: Specific crypto's market cap
- `crypto_id`: Cryptocurrency identifier

**Returns**: Percentage value (0-100)

**Interpretation**:

### Bitcoin Dominance

| BTC Dominance | Market Phase | Investment Strategy |
|---------------|--------------|---------------------|
| **> 65%** | Bitcoin dominance | Alt season unlikely, focus on BTC |
| **55-65%** | BTC strength | Some alt opportunities, BTC-heavy portfolio |
| **45-55%** | Balanced market | Diversify between BTC and major alts |
| **35-45%** | Alt season starting | Increase alt exposure, BTC losing steam |
| **< 35%** | Peak alt season | Maximum alt allocation, BTC weak |

### Altcoin Dominance

| Dominance Level | For Top 10 Coins | For Smaller Caps |
|-----------------|------------------|------------------|
| **> 5%** | Major player (ETH) | Mega-cap altcoin |
| **2-5%** | Large cap strong position | Large cap |
| **0.5-2%** | Mid cap | Mid cap with potential |
| **0.1-0.5%** | Smaller position | Small cap |
| **< 0.1%** | Niche coin | Micro cap, high risk |

**Market Cycle Indicators**:

1. **Rising BTC Dominance**:
   - Flight to safety
   - Bear market or correction
   - Risk-off sentiment
   - Alts underperforming

2. **Falling BTC Dominance**:
   - Risk-on environment
   - Bull market for alts
   - Capital flowing to alts
   - Speculation increasing

3. **Stable Dominance**:
   - Market equilibrium
   - Sector rotation
   - Transitional phase

**Trading Insights**:
- **BTC dominance rising + BTC price falling** = Bear market, stay in cash
- **BTC dominance rising + BTC price rising** = BTC-only rally, wait for alt season
- **BTC dominance falling + BTC price rising** = Best scenario, buy quality alts
- **BTC dominance falling + BTC price falling** = Alt bleed, extreme risk

---

## Fibonacci Retracement Levels

### Function: `fibonacci_levels(data)`

**Purpose**: Calculate Fibonacci retracement levels to identify potential support/resistance zones based on natural mathematical ratios.

**Parameters**:
- `data`: Price data with historical prices

**Formula**:
```
Level 0% = High (most recent swing high)
Level 23.6% = High - (High - Low) × 0.236
Level 38.2% = High - (High - Low) × 0.382
Level 50.0% = High - (High - Low) × 0.5
Level 61.8% = High - (High - Low) × 0.618 (Golden ratio)
Level 78.6% = High - (High - Low) × 0.786
Level 100% = Low (most recent swing low)
```

**Returns**: Tuple of 7 values (fib_levels_1 through fib_levels_7)

**Interpretation**:

| Level | Ratio | Support/Resistance Strength | Use Case |
|-------|-------|---------------------------|----------|
| **0%** | 1.000 | Highest | Recent high, strong resistance |
| **23.6%** | 0.764 | Weak | Shallow retracement, trend continuation likely |
| **38.2%** | 0.618 | Moderate | Common pullback level in strong trends |
| **50%0%** | 0.500 | Strong | Psychological level, half-back retracement |
| **61.8%** | 0.382 | Very Strong | Golden ratio, most important Fibonacci level |
| **78.6%** | 0.214 | Strong | Deep retracement, trend validity test |
| **100%** | 0.000 | Highest | Recent low, strong support |

### Retracement Depth Analysis

**In an Uptrend**:

| Pullback to Level | Trend Strength | Action |
|-------------------|----------------|--------|
| **0-23.6%** | Very strong | Minor correction, strong buy |
| **23.6-38.2%** | Strong | Healthy pullback, buy opportunity |
| **38.2-50%** | Moderate | Normal correction, consider buying |
| **50-61.8%** | Weakening | Deep retracement, wait for confirmation |
| **61.8-78.6%** | Weak | Trend in danger, cautious buy only |
| **78.6-100%** | Failed | Trend likely reversed, avoid |

**In a Downtrend (inverted)**:

| Bounce to Level | Trend Strength | Action |
|-----------------|----------------|--------|
| **0-23.6%** | Very strong | Minor bounce, strong sell |
| **23.6-38.2%** | Strong | Healthy retracement, sell opportunity |
| **38.2-50%** | Moderate | Normal bounce, consider selling |
| **50-61.8%** | Weakening | Deep bounce, wait for confirmation |
| **61.8-78.6%** | Weak | Downtrend in danger, cautious sell only |
| **78.6-100%** | Failed | Downtrend likely reversed, avoid |

### Trading Strategy

**Entry Points**:
1. **Conservative**: Enter at 38.2% retracement with stop below 50%
2. **Moderate**: Enter at 50% retracement with stop below 61.8%
3. **Aggressive**: Enter at 61.8% retracement (golden ratio) with stop below 78.6%

**Extension Targets**:
- **161.8%**: First profit target beyond recent high/low
- **261.8%**: Second profit target for strong trends
- **423.6%**: Third target for parabolic moves

**Confluence Zones**:
Strongest signals occur when Fibonacci levels align with:
- Pivot points (S1, S2, R1, R2)
- Moving averages (MA 50, MA 200)
- POC (Point of Control)
- Round psychological numbers

**Example Trade Setup**:
```
Uptrend scenario:
- Price rallies from $30,000 to $50,000
- Retraces to 61.8% level ($37,640)
- RSI oversold + MACD bullish cross + at MA 50
- Buy at $37,640 with stop at $35,710 (below 78.6%)
- Target: Previous high $50,000 or 161.8% extension $62,360
```

---

## Combined Analysis Framework

### Multi-Indicator Confluence

For strongest trading signals, look for alignment across multiple categories:

**Strong Buy Signal Example**:
- Price: -15% from 30d average (oversold)
- Volume: +80% above average (strong interest)
- RSI: 25 (oversold)
- MACD: Bullish crossover below zero
- Price: At 61.8% Fibonacci level
- Price: Near S1 pivot support
- Price: Above POC (trading below value)
- Dominance: Stable or rising (not bleeding to other coins)

**Strong Sell Signal Example**:
- Price: +20% from 7d average (overbought)
- Volume: +100% spike (climax volume)
- RSI: 78 (overbought)
- MACD: Bearish crossover above zero
- Price: At 23.6% Fibonacci retracement (weak bounce)
- Price: Near R1 pivot resistance
- Price: Far above POC (trading at premium)
- Dominance: Falling rapidly (money leaving)

### Risk Management

Use metrics to determine position size:
- **High confidence** (5+ indicators align): 5-10% of portfolio
- **Medium confidence** (3-4 indicators): 2-5% of portfolio
- **Low confidence** (1-2 indicators): 1-2% of portfolio or avoid

### Time Frame Considerations

- **1-day metrics**: Day trading, scalping (high risk)
- **7-day metrics**: Swing trading (moderate risk)
- **30-day metrics**: Position trading (lower risk)
- **Multi-month**: Long-term investing (lowest risk)

---

## Glossary

- **EMA**: Exponential Moving Average - weighted average favoring recent prices
- **SMA**: Simple Moving Average - arithmetic mean of prices
- **Support**: Price level where buying pressure prevents further decline
- **Resistance**: Price level where selling pressure prevents further rise
- **Divergence**: When price and indicator move in opposite directions
- **Confluence**: Multiple indicators/levels aligning at same price
- **Momentum**: Rate of price change over time
- **Volatility**: Degree of price fluctuation
- **Liquidity**: Ease of buying/selling without affecting price

---

## Important Disclaimers

1. **No Single Indicator**: Never trade based on one metric alone
2. **Context Matters**: Market conditions affect indicator reliability
3. **Backtesting**: Always test strategies on historical data first
4. **Risk Management**: Use stop losses and position sizing
5. **Market Regime**: Bull/bear markets behave differently
6. **False Signals**: All indicators produce false signals occasionally
7. **Adaptation**: Adjust parameters based on asset volatility and timeframe

---

*This documentation is for educational purposes only and does not constitute financial advice.*
