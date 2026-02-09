"""
Core data types for the trading engine.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum


class Side(Enum):
    """Order side."""
    BUY = "BUY"
    SELL = "SELL"


class Outcome(Enum):
    """Market outcome."""
    YES = "YES"
    NO = "NO"


class SignalUrgency(Enum):
    """Signal urgency level."""
    IMMEDIATE = "immediate"  # Execute now
    NORMAL = "normal"        # Execute within scan cycle
    LOW = "low"              # Can wait


class OrderStatus(Enum):
    """Order execution status."""
    PENDING = "pending"
    FILLED = "filled"
    PARTIAL = "partial"
    CANCELLED = "cancelled"
    FAILED = "failed"


@dataclass
class Market:
    """Polymarket market data."""
    id: str
    question: str
    slug: str
    
    # Tokens
    yes_token_id: str
    no_token_id: str
    
    # Prices (0.0 - 1.0)
    yes_price: float
    no_price: float
    
    # Volume and liquidity
    volume_24h: float
    liquidity: float
    
    # Metadata
    end_date: Optional[datetime] = None
    category: Optional[str] = None
    is_active: bool = True
    
    # Orderbook depth (optional)
    yes_best_bid: Optional[float] = None
    yes_best_ask: Optional[float] = None
    no_best_bid: Optional[float] = None
    no_best_ask: Optional[float] = None
    
    @property
    def spread_sum(self) -> float:
        """Sum of YES and NO prices. If < 1.0, arbitrage opportunity exists."""
        return self.yes_price + self.no_price
    
    @property
    def arbitrage_spread(self) -> float:
        """Arbitrage profit margin if buying both sides."""
        return 1.0 - self.spread_sum
    
    @property
    def has_arbitrage(self) -> bool:
        """Check if arbitrage opportunity exists (spread_sum < 1)."""
        return self.spread_sum < 1.0


@dataclass
class Signal:
    """Trading signal from a strategy module."""
    module: str              # "arbitrage", "news", "latency", etc.
    market_id: str           # Polymarket market ID
    token_id: str            # Token to trade
    action: Side             # BUY or SELL
    outcome: Outcome         # YES or NO
    
    confidence: float        # 0.0 - 1.0
    expected_value: float    # Expected profit in USD
    size_suggestion: float   # Suggested position size in USD
    urgency: SignalUrgency   # Execution priority
    
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        return f"Signal({self.module}: {self.action.value} {self.outcome.value} @ {self.market_id[:8]}... EV=${self.expected_value:.2f})"


@dataclass
class ArbitrageOpportunity:
    """Detected arbitrage opportunity."""
    market: Market
    
    yes_price: float  # Price to buy YES
    no_price: float   # Price to buy NO
    total_cost: float # Total cost to buy both
    profit: float     # Guaranteed profit (1.0 - total_cost)
    profit_pct: float # Profit as percentage
    
    # Sizing
    max_size: float   # Maximum size based on liquidity
    suggested_size: float  # Suggested size based on bankroll
    
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def __str__(self) -> str:
        return f"Arb({self.market.question[:30]}... | Cost: ${self.total_cost:.4f} | Profit: {self.profit_pct:.2%})"


@dataclass 
class Order:
    """Order to be executed."""
    market_id: str
    token_id: str
    side: Side
    outcome: Outcome
    
    price: float      # Limit price
    size: float       # Size in shares
    
    order_type: str = "limit"  # "limit", "market", "fok"
    
    # Execution details
    order_id: Optional[str] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_size: float = 0.0
    filled_price: float = 0.0
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    executed_at: Optional[datetime] = None
    
    @property
    def is_filled(self) -> bool:
        return self.status == OrderStatus.FILLED
    
    @property
    def fill_pct(self) -> float:
        if self.size == 0:
            return 0.0
        return self.filled_size / self.size


@dataclass
class Trade:
    """Executed trade record."""
    id: str
    market_id: str
    token_id: str
    side: Side
    outcome: Outcome
    
    price: float
    size: float
    cost: float  # Total cost in USD
    
    executed_at: datetime
    module: str  # Which module generated this trade
    
    # For arbitrage pairs
    paired_trade_id: Optional[str] = None
    
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Position:
    """Current position in a market."""
    market_id: str
    token_id: str
    outcome: Outcome
    
    shares: float
    avg_price: float
    current_price: float
    
    @property
    def cost_basis(self) -> float:
        return self.shares * self.avg_price
    
    @property
    def current_value(self) -> float:
        return self.shares * self.current_price
    
    @property
    def pnl(self) -> float:
        return self.current_value - self.cost_basis
    
    @property
    def pnl_pct(self) -> float:
        if self.cost_basis == 0:
            return 0.0
        return self.pnl / self.cost_basis
