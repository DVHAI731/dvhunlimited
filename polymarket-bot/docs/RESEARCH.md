# Market Research Findings

**Research Date:** 2026-02-09  
**Sources:** Brave Search, X/Twitter, Reddit, GitHub, DeFiPrime

---

## Market Overview

### Polymarket Stats (as of Feb 2026)
- **Valuation:** $9 billion (after $2B ICE investment)
- **2025 Trading Volume:** $10B+
- **Arbitrage Profits Extracted:** $40M+ (Apr 2024 - Apr 2025)
- **Ecosystem Tools:** 170+ third-party products

### User Distribution
- **70%** of retail traders lose money
- **0.03%** of addresses capture **70%** of total profits
- **0.51%** of wallets achieved significant profits

---

## Top Performer Analysis

### Gabagool22 — The BTC 15-Min King
- **Results:** $313 → $414,000 in ~1 month
- **Strategy:** Pure arbitrage on BTC 15-minute markets
- **Edge:** Exploits Chainlink price feed latency from Binance
- **Method:**
  - Never predicts direction
  - Buys YES and NO at different times
  - Waits for combined cost < $1.00
  - Profit locked in regardless of outcome
- **Additional Income:** $1,700+/day in maker rebates alone
- **Tech:** Ultra-low latency, likely colocated with Binance + Polymarket

### ilovecircle — The AI/ML Trader
- **Results:** $2.2M in 60 days
- **Win Rate:** 74%
- **Strategy:** Data models finding mispriced niche markets
- **Method:**
  - No gambling or gut feeling
  - AI-powered probability estimation
  - High volume across many markets
  - Small edge compounded over thousands of trades

### Defiance_cr — The Market Maker
- **Results:** $700-800/day consistently
- **Strategy:** Market making (spread capture)
- **Open Source:** poly-maker code available

### Jane Street-linked Bot (Account88888)
- **Strategy:** Dutch book arbitrage + latency
- **Method:** Identifies when sum of probabilities < 100%
- **Tech:** Dedicated Binance endpoint, sub-150ms execution

---

## Strategy Deep Dives

### 1. Single-Market Arbitrage
**How it works:**
```
YES price + NO price < $1.00
Buy both → Guaranteed profit
```

**Stats:**
- Generated $39.5M+ since 2024
- Most common in volatile markets
- Opportunities are rare but pure profit

**Tools:**
- GitHub: gabagool222/15min-btc-polymarket-trading-bot
- Features: auto-discovery, depth-aware sizing, paired execution

### 2. Latency Arbitrage (Binance → Chainlink)
**How it works:**
- Chainlink aggregates prices from multiple sources
- Binance price spikes propagate with 200-500ms delay
- Bot detects spike on Binance, trades on Polymarket before Chainlink updates

**Requirements:**
- Binance WebSocket feed (dedicated endpoint for large traders)
- Colocation with both Binance and Polymarket
- Sub-200ms total execution time

**Reality Check:**
- Highly competitive space
- gabagool likely has infrastructure advantages
- Still possible to capture some edge without colocation

### 3. Cross-Platform Arbitrage (Polymarket vs Kalshi)
**How it works:**
```
Same event, different prices:
- Polymarket: YES at 55¢
- Kalshi: NO at 40¢
- Buy both: 95¢ → Payout $1.00 = 5.3% profit
```

**Tools:**
- EventArb.com — Real-time calculator
- GitHub: ImMike/polymarket-arbitrage
- GitHub: CarlosIbCu/polymarket-kalshi-btc-arbitrage-bot

**Challenges:**
- Settlement timing differences
- Liquidity varies between platforms
- 78% of opportunities fail due to execution inefficiencies (2025 study)

### 4. Maker Rebates Program (NEW as of Jan 2026)
**How it works:**
- Polymarket added taker fees on 15-min crypto markets
- Fees pooled into daily USDC rebates for makers
- Distributed based on liquidity provided that got taken

**Key Details:**
- Highest fees at 50% probability
- Fees decrease toward extremes (0% and 100%)
- Daily distribution in USDC
- gabagool earns $1,700+/day in rebates alone

---

## Resolution & Oracle Risks

### UMA Oracle System
- Polymarket uses UMA for dispute resolution
- Proposers stake $750 USDC to submit outcomes
- 2-hour challenge period
- Disputes resolved by UMA token holder votes

### Known Incidents

**Zelenskyy Suit Controversy (July 2025):**
- Subjective market about what Zelenskyy wore
- UMA whale with 5M tokens (25% of votes) manipulated outcome
- Honest voters were slashed
- Polymarket promised improvements

**Oracle Manipulation (March 2025):**
- Low-volume market had fake settlement
- UMA tycoon swung vote with concentrated tokens
- $7M scandal

### Mitigation Strategies
1. **Avoid low-volume subjective markets**
2. **Stick to objective, verifiable outcomes** (BTC price, election results)
3. **Monitor UMA dispute activity** (Betmoar has UMA dashboard)
4. **Don't over-concentrate** in any single market

---

## Ecosystem Tools

### Top Trading Terminals
| Tool | Volume | Features |
|------|--------|----------|
| Betmoar | $110M+ | Analytics, UMA dashboard, execution |
| Stand.trade | — | Professional terminal, automations |
| NexusTools | — | Wallet tracking, discovery |

### AI/Research Tools
| Tool | Focus |
|------|-------|
| PolyBro | Autonomous research agent |
| Polyseer | Open-source AI research |
| PolyRadar | Multi-model consensus |
| Inside Edge | Mispricing detection |

### Arbitrage Tools
| Tool | Focus |
|------|-------|
| EventArb.com | Cross-platform calculator |
| polymarket-arbitrage (GitHub) | Polymarket + Kalshi bot |
| PolyTrack | Arbitrage guide + alerts |

### Data & Analytics
| Tool | Focus |
|------|-------|
| polymarketanalytics.com | Leaderboard, whale tracking |
| Polymarket Leaderboard | Official top traders |

---

## Fee Structure

### Most Markets: ZERO FEES
- No deposit fees
- No withdrawal fees
- No trading fees

### 15-Minute Crypto Markets: TAKER FEES
- Introduced January 2026
- Fees fund maker rebates program
- Highest fees at 50% probability
- Lower fees at extremes

### Gas Costs
- Polygon network fees (minimal)
- ~$0.01-0.10 per transaction

---

## API & Technical Resources

### Official Polymarket
- CLOB API: `https://clob.polymarket.com`
- Gamma API: `https://gamma-api.polymarket.com`
- Docs: `https://docs.polymarket.com`
- py-clob-client: `https://github.com/Polymarket/py-clob-client`

### Community SDKs
- @polybased/sdk (TypeScript): Full SDK with CLOB integration
- NautilusTrader: Professional trading framework integration

### Batch Limits
- 2024: 5 orders per batch
- 2025+: 15 orders per batch
