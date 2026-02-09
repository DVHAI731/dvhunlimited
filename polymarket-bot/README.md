# Polymarket Multi-Strategy Trading Bot

**Project Status:** Planning Complete → Ready to Build  
**Last Updated:** 2026-02-09  
**Lead:** Alexia ⚡

## Overview

A multi-strategy automated trading engine for Polymarket prediction markets. Designed to run multiple edges simultaneously—arbitrage, news trading, latency exploitation, and model-driven predictions.

## Why This Wins

- **Multiple edges** — Not dependent on one strategy
- **Always hunting** — Different modules trigger in different market conditions
- **Compounding** — Arbitrage profits (risk-free) fund model bets (higher risk/reward)
- **Paper trade first** — Prove it works before real money

## Proven Market Data

| Metric | Value |
|--------|-------|
| Arbitrage profits extracted (Apr 2024 - Apr 2025) | **$40M+** |
| Polymarket 2025 trading volume | **$10B+** |
| % of retail traders who lose money | **70%** |
| % of addresses capturing 70% of profits | **0.03%** |

## Top Performer Case Studies

| Bot/Trader | Profit | Strategy | Edge |
|------------|--------|----------|------|
| gabagool22 | $313 → $414k (1 month) | Arbitrage | Chainlink latency, maker rebates |
| ilovecircle | $2.2M (2 months) | AI/ML Models | Mispriced niche markets, 74% win rate |
| Esports bot | $900 → $208k (3 months) | Information | Parses live streams faster |
| defiance_cr | $700-800/day | Market Making | Open-sourced poly-maker code |

## Project Structure

```
polymarket-bot/
├── README.md           # This file
├── docs/
│   ├── STRATEGY.md     # Detailed strategy documentation
│   ├── ARCHITECTURE.md # System architecture
│   ├── RESEARCH.md     # Market research findings
│   └── RISKS.md        # Risk assessment
├── src/                # Source code (to be built)
│   ├── core/           # Core engine
│   ├── modules/        # Strategy modules
│   ├── data/           # Data feeds
│   └── execution/      # Order execution
└── config/             # Configuration files
```

## Build Phases

| Phase | Week | Components | Risk Level |
|-------|------|------------|------------|
| **1** | 1 | Scanner + Arbitrage + Paper Trading | Zero |
| **2** | 2-3 | Latency + News + Maker Rebates + Risk Manager | Low |
| **3** | 4+ | Cross-platform + Whale Copy + AI/ML | Scaled |

## Quick Start

```bash
# Coming soon - Phase 1 implementation
cd polymarket-bot
pip install -r requirements.txt
python src/main.py --paper-trade
```

## Requirements (To Be Provided)

- [ ] Polymarket wallet private key (for CLOB trading)
- [ ] Starting capital amount (for position sizing)
- [ ] Binance API key (for latency arbitrage)

## Links

- [Polymarket](https://polymarket.com)
- [Polymarket CLOB Docs](https://docs.polymarket.com/developers/CLOB/introduction)
- [py-clob-client](https://github.com/Polymarket/py-clob-client)
- [Polymarket Analytics](https://polymarketanalytics.com)

---

Built by Alexia ⚡ | Co-founder energy
