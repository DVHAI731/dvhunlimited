# System Architecture

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    POLYMARKET ENGINE v2                     │
├─────────────────────────────────────────────────────────────┤
│  DATA LAYER                                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ Binance  │ │Polymarket│ │  Kalshi  │ │   News   │       │
│  │WebSocket │ │ CLOB API │ │   API    │ │ (Brave)  │       │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘       │
│       └────────────┼───────────┼────────────┘              │
│                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────┐│
│  │              SIGNAL GENERATORS                          ││
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       ││
│  │  │Arbitrage│ │ Latency │ │  News   │ │  Model  │       ││
│  │  │YES+NO<1 │ │Binance→ │ │Reactive │ │  (AI)   │       ││
│  │  │         │ │Chainlink│ │         │ │         │       ││
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘       ││
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       ││
│  │  │  Whale  │ │Hi-Prob  │ │Cross-   │ │ Maker   │       ││
│  │  │  Copy   │ │  Bonds  │ │Platform │ │ Rebates │       ││
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘       ││
│  └─────────────────────────────────────────────────────────┘│
│                           │                                 │
│                           ▼                                 │
│  ┌─────────────────────────────────────────────────────────┐│
│  │              SIGNAL AGGREGATOR                          ││
│  │  • Combines signals from all modules                    ││
│  │  • Ranks opportunities by expected value                ││
│  │  • Deduplicates conflicting signals                     ││
│  └─────────────────────────────────────────────────────────┘│
│                           │                                 │
│                           ▼                                 │
│  ┌─────────────────────────────────────────────────────────┐│
│  │              RISK MANAGER                               ││
│  │  • Position limits per market                           ││
│  │  • Max drawdown controls                                ││
│  │  • Resolution risk scoring                              ││
│  │  • Liquidity depth checks                               ││
│  │  • Correlation limits (avoid overexposure)              ││
│  └─────────────────────────────────────────────────────────┘│
│                           │                                 │
│                           ▼                                 │
│  ┌─────────────────────────────────────────────────────────┐│
│  │              EXECUTION ENGINE                           ││
│  │  • FOK orders for arbitrage                             ││
│  │  • Depth-aware sizing (walk the ask book)               ││
│  │  • Paired execution verification                        ││
│  │  • Sub-150ms target latency                             ││
│  │  • Retry logic with backoff                             ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

---

## Component Details

### Data Layer

#### Polymarket CLOB API
- **Endpoint:** `https://clob.polymarket.com`
- **Chain:** Polygon (137)
- **Client:** `py-clob-client` (official Python SDK)
- **Features:**
  - Real-time orderbook data
  - Historical trades
  - Batch orders (up to 15 per call as of 2025)
  - WebSocket for live updates

#### Gamma API (Market Metadata)
- **Endpoint:** `https://gamma-api.polymarket.com`
- **Purpose:** Market metadata, event details, resolution info

#### Binance WebSocket
- **Purpose:** Real-time BTC/ETH/SOL prices for latency arbitrage
- **Latency target:** <50ms from Binance to our system

#### News Feeds
- **Brave Search API:** Real-time web search
- **RSS Feeds:** Major news sources
- **Twitter/X:** Social sentiment (future)

---

### Signal Generators (Modules)

Each module is a pluggable component that:
1. Subscribes to relevant data feeds
2. Analyzes for opportunities
3. Emits standardized `Signal` objects

```python
@dataclass
class Signal:
    module: str           # "arbitrage", "news", "latency", etc.
    market_id: str        # Polymarket market ID
    token_id: str         # YES or NO token
    action: str           # "BUY" or "SELL"
    confidence: float     # 0.0 - 1.0
    expected_value: float # Expected profit in USD
    size_suggestion: float # Suggested position size
    urgency: str          # "immediate", "normal", "low"
    metadata: dict        # Module-specific data
```

---

### Risk Manager

**Position Limits:**
```python
MAX_POSITION_PER_MARKET = 0.05  # 5% of bankroll
MAX_TOTAL_EXPOSURE = 0.50       # 50% of bankroll at risk
MAX_CORRELATED_EXPOSURE = 0.15  # 15% on correlated markets
```

**Resolution Risk Scoring:**
- Objective markets (BTC price) → Low risk
- Subjective markets (opinions) → High risk
- Low-volume markets → Higher manipulation risk

**Liquidity Checks:**
- Verify orderbook depth before sizing
- Reject trades that would move price >1%

---

### Execution Engine

**Order Types:**
- **FOK (Fill or Kill):** For arbitrage (must fill both legs)
- **Limit:** For maker rebates (provide liquidity)
- **Market:** For urgent news trades

**Paired Execution:**
```python
# For arbitrage, both legs must fill or neither
async def execute_arbitrage(yes_order, no_order):
    yes_result = await place_fok_order(yes_order)
    if not yes_result.filled:
        return None
    
    no_result = await place_fok_order(no_order)
    if not no_result.filled:
        # Unwind the YES position
        await unwind_position(yes_result)
        return None
    
    return ArbitrageResult(yes_result, no_result)
```

---

## Data Flow

```
1. Market Scanner polls all active markets (every 1s)
2. Data feeds stream real-time prices
3. Signal modules analyze for opportunities
4. Signals aggregated and ranked
5. Risk manager filters/sizes positions
6. Execution engine places orders
7. Results logged for analysis
```

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.11+ |
| Async | asyncio, aiohttp |
| Polymarket | py-clob-client |
| Database | SQLite (local), PostgreSQL (production) |
| Caching | Redis (optional) |
| Monitoring | Prometheus + Grafana |
| Alerts | Telegram bot |

---

## File Structure

```
src/
├── main.py                 # Entry point
├── core/
│   ├── engine.py           # Main orchestrator
│   ├── config.py           # Configuration
│   └── types.py            # Data types (Signal, Order, etc.)
├── data/
│   ├── polymarket.py       # Polymarket CLOB client
│   ├── binance.py          # Binance WebSocket
│   ├── news.py             # News feed aggregator
│   └── cache.py            # Data caching
├── modules/
│   ├── base.py             # Base module class
│   ├── arbitrage.py        # Single-market arbitrage
│   ├── latency.py          # Binance→Chainlink latency
│   ├── news.py             # News reactive trading
│   ├── bonds.py            # High-probability bonds
│   ├── rebates.py          # Maker rebates
│   └── whale.py            # Whale copy trading
├── risk/
│   ├── manager.py          # Risk management
│   ├── limits.py           # Position limits
│   └── scoring.py          # Resolution risk scoring
├── execution/
│   ├── executor.py         # Order execution
│   ├── orders.py           # Order types
│   └── verification.py     # Fill verification
└── utils/
    ├── logging.py          # Logging setup
    ├── metrics.py          # Prometheus metrics
    └── alerts.py           # Telegram alerts
```
