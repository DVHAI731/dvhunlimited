# Risk Assessment

## Risk Matrix

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Oracle manipulation | Medium | High | Avoid low-volume subjective markets |
| Execution slippage | High | Medium | Depth-aware sizing, walk the book |
| Latency competition | High | Medium | Accept we won't win all races |
| Resolution ambiguity | Medium | High | Stick to objective outcomes |
| Smart contract bug | Low | Critical | Use official SDK, small positions initially |
| API rate limits | Medium | Low | Implement backoff, caching |
| Regulatory action | Low | High | Monitor news, have exit strategy |
| Capital loss | Variable | Variable | Position limits, max drawdown |

---

## Detailed Risk Analysis

### 1. Oracle Manipulation Risk
**What:** UMA token holders can manipulate market resolutions  
**Evidence:** Zelenskyy suit case (July 2025), $7M manipulation (March 2025)  
**Mitigation:**
- Avoid markets with <$100k volume
- Avoid subjective/opinion-based markets
- Stick to verifiable outcomes (BTC price, election results, sports scores)
- Monitor UMA dispute activity via Betmoar dashboard

### 2. Execution Risk
**What:** Orders don't fill at expected prices  
**Causes:**
- Thin orderbooks
- High volatility
- Competing bots

**Mitigation:**
- Use FOK (Fill or Kill) orders for arbitrage
- Walk the orderbook to verify depth before sizing
- Implement paired execution verification
- Accept partial fills only when profitable

### 3. Latency Competition
**What:** Faster bots capture opportunities before us  
**Reality:**
- gabagool likely has colocation advantages
- Sub-150ms execution needed to compete in 15-min markets
- Most retail can't match HFT infrastructure

**Mitigation:**
- Accept we won't win every race
- Focus on opportunities with longer windows
- Diversify across multiple strategies
- Target less competitive markets

### 4. Resolution Ambiguity
**What:** Market rules are unclear, leading to unexpected outcomes  
**Example:** "Will X happen by Y date?" — timezone issues, edge cases

**Mitigation:**
- Read market rules carefully before trading
- Avoid markets with ambiguous resolution criteria
- Prefer markets with clear, objective triggers

### 5. Smart Contract Risk
**What:** Bug in Polymarket contracts causes loss  
**Reality:** Polymarket has been running since 2020, battle-tested

**Mitigation:**
- Use official py-clob-client SDK
- Start with small positions
- Don't put all capital on platform

### 6. Regulatory Risk
**What:** US government action against Polymarket  
**Reality:**
- Polymarket settled with CFTC in 2022 ($1.4M fine)
- Currently blocks US users (but VPN usage common)
- Growing legitimacy with ICE investment

**Mitigation:**
- Stay informed on regulatory developments
- Have exit strategy ready
- Consider non-US entity structure

---

## Position Sizing Rules

### Per-Market Limits
```python
MAX_POSITION_PER_MARKET = 0.05  # 5% of bankroll per market
MAX_SINGLE_TRADE = 0.02         # 2% of bankroll per trade
```

### Total Exposure Limits
```python
MAX_TOTAL_EXPOSURE = 0.50       # 50% of bankroll at risk
MAX_CORRELATED_EXPOSURE = 0.15  # 15% on correlated outcomes
```

### Drawdown Controls
```python
DAILY_LOSS_LIMIT = 0.05         # Stop trading after 5% daily loss
MAX_DRAWDOWN = 0.15             # Reduce size after 15% drawdown
CRITICAL_DRAWDOWN = 0.25        # Pause all trading
```

---

## Risk-Adjusted Strategy Selection

| Strategy | Risk Level | When to Use |
|----------|------------|-------------|
| Single-market arbitrage | Zero | Always (core strategy) |
| Maker rebates | Zero | Always (passive income) |
| High-prob bonds | Very Low | When opportunities exist |
| Latency arbitrage | Low | When infrastructure ready |
| News trading | Medium | On high-confidence events |
| Model-driven | Medium | After backtesting |
| Whale copy | Medium | Selectively |
| Cross-platform | Low-Medium | After Kalshi integration |

---

## Emergency Procedures

### Market Manipulation Detected
1. Immediately close all positions in affected market
2. Document evidence (screenshots, timestamps)
3. Report to Polymarket support
4. Review all open positions for similar exposure

### Unexpected Resolution
1. Do not panic sell
2. Review market rules
3. Check if dispute is possible (2-hour window)
4. Consider UMA dispute if clearly incorrect

### API Outage
1. Check Polymarket status page
2. Do not retry aggressively (rate limits)
3. Monitor positions via web interface
4. Pause automated trading until resolved

### Large Unexpected Loss
1. Stop all automated trading
2. Review what happened
3. Check for bugs in code
4. Adjust risk parameters before resuming

---

## Pre-Launch Checklist

- [ ] Paper trade for minimum 48 hours
- [ ] Verify all position limits are enforced
- [ ] Test emergency stop functionality
- [ ] Confirm API credentials are valid
- [ ] Set up monitoring and alerts
- [ ] Document expected behavior
- [ ] Have manual intervention plan ready
