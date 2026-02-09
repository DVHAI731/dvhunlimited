# Polymarket Bot Strategy Documentation

## How Polymarket Works

- Every market has **YES** and **NO** shares
- Prices = implied probability (YES at $0.60 = 60% chance)
- If you're right, shares pay out **$1.00**
- If wrong, you lose your stake

---

## Strategy Modules

### 1. Single-Market Arbitrage (Phase 1) — Risk-Free Profit

```
Market: "Will X happen?"
YES price: $0.45
NO price:  $0.52
─────────────────
Total:     $0.97

Buy both for $0.97 → One MUST pay $1.00
Guaranteed $0.03 profit (3.1% return)
```

**Edge:** Math. No prediction needed. Pure market inefficiency.  
**Expected return:** $50-200/day  
**Requirements:** Market scanner, fast execution

---

### 2. Latency Arbitrage (Phase 2) — Binance→Chainlink Lag

```
Binance BTC price spikes →
Chainlink price feed lags 200-500ms →
Polymarket 15-min markets misprice →
We buy the correct side before market catches up
```

**Edge:** Speed advantage over Chainlink oracle updates  
**Expected return:** $500-2,000/day (proven by gabagool)  
**Requirements:** Binance WebSocket, sub-200ms execution

**Gabagool's Method:**
- Never predicts if BTC will go up or down
- Waits for cheap opportunities on either side
- Buys YES and NO asymmetrically when mispriced
- Once Pair Cost < $1.00 → profit is locked in

---

### 3. News Trading (Phase 1-2) — Speed Advantage

```
Breaking: "CEO announces merger"

Market hasn't reacted yet (YES still at $0.30)
We buy YES instantly
Market catches up → YES moves to $0.75
We sell for 150% profit
```

**Edge:** We react faster than humans refreshing Twitter  
**Expected return:** 10-50% per event (event-driven)  
**Requirements:** Brave Search API, RSS feeds, fast parsing

---

### 4. Maker Rebates Mining (Phase 2) — Zero Risk Income

```
Provide liquidity on 15-min crypto markets →
Earn daily USDC rebates from taker fees →
Stack with arbitrage profits
```

**Edge:** Paid to provide liquidity  
**Expected return:** $500-1,700/day documented  
**Requirements:** Understand maker/taker dynamics

---

### 5. High-Probability Bond Strategy (Phase 2) — Near-Certain Returns

```
Find markets at 95-99% probability near resolution →
Buy guaranteed outcomes at slight discount →
Annualized returns: 50-200%+
```

**Example:**
- Market resolves in 2 days
- YES at $0.97
- 3% return in 48h = 547% APY

**Edge:** Time value of near-certain outcomes  
**Risk:** Very low (but resolution risk exists)

---

### 6. Model-Driven Predictions (Phase 3) — Better Probability Estimates

```
Market: "Will Fed raise rates?"
Current price: YES at $0.40 (market says 40%)

Our model (using economic data, Fed speeches, polls):
Estimates 65% probability

We buy YES at $0.40, expecting $0.65+ fair value
```

**Edge:** Better probability estimates than the crowd  
**Expected return:** 5-20% per trade  
**Requirements:** AI/ML models, training data

---

### 7. Whale Copy Trading (Phase 3) — Follow Smart Money

```
Track top 50 profitable addresses →
Mirror their positions with delay →
Piggyback on smart money
```

**Tools:**
- polymarketanalytics.com leaderboard
- Betmoar wallet tracking

**Risk:** Medium (whale could be wrong, or front-running issues)

---

### 8. Cross-Platform Arbitrage (Phase 3) — Polymarket vs Kalshi

```
Same event on Polymarket: YES at $0.55
Same event on Kalshi: NO at $0.40
Buy both → Guaranteed $0.05 profit (5%)
```

**Edge:** Price discrepancies between platforms  
**Complexity:** Higher (two platforms, settlement timing differences)  
**Tools:** EventArb.com, GitHub bots

---

### 9. Market Making (Phase 3) — Spread Capture

```
We post:
  BUY  YES at $0.48
  SELL YES at $0.52

Someone sells to us at $0.48
Someone buys from us at $0.52
We pocket $0.04 spread, no directional risk
```

**Edge:** Providing liquidity, earning the spread  
**Expected return:** $700-800/day (proven by poly-maker bot)  
**Risk:** Inventory risk if market moves against you

---

## Strategy Priority Matrix

| Strategy | Risk | Complexity | Expected Daily Return | Phase |
|----------|------|------------|----------------------|-------|
| Single-market arbitrage | Zero | Low | $50-200 | 1 |
| News reactive | Medium | Medium | Event-driven | 1 |
| Latency arbitrage | Low | High | $500-2,000 | 2 |
| Maker rebates | Zero | Medium | $500-1,700 | 2 |
| High-prob bonds | Very Low | Low | $100-500 | 2 |
| Model-driven | Medium | High | $500-5,000+ | 3 |
| Whale copy | Medium | Medium | Variable | 3 |
| Cross-platform | Low | High | $200-1,000 | 3 |
| Market making | Medium | High | $700-800 | 3 |

---

## Key Insights from Research

1. **70% of retail loses money** — We must be in the 0.03% that wins
2. **Speed matters** — Sub-150ms latency needed for competitive arbitrage
3. **Maker rebates are real** — gabagool earns $1,700+/day just in rebates
4. **AI/ML works** — ilovecircle proved it with $2.2M in 60 days
5. **Diversification wins** — Top bots run multiple strategies simultaneously
