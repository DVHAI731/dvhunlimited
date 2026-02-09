"""
Paper Trading Executor - Simulates trades without real execution.

Use this to test strategies before going live.
"""

from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass, field
import uuid
from loguru import logger

from src.core.types import Order, Trade, Position, Signal, Side, Outcome, OrderStatus


@dataclass
class PaperAccount:
    """Simulated trading account."""
    balance: float  # USDC balance
    initial_balance: float
    positions: Dict[str, Position] = field(default_factory=dict)  # token_id -> Position
    trades: List[Trade] = field(default_factory=list)
    
    @property
    def total_value(self) -> float:
        """Total account value (balance + positions)."""
        position_value = sum(p.current_value for p in self.positions.values())
        return self.balance + position_value
    
    @property
    def pnl(self) -> float:
        """Total P&L since start."""
        return self.total_value - self.initial_balance
    
    @property
    def pnl_pct(self) -> float:
        """P&L as percentage."""
        if self.initial_balance == 0:
            return 0.0
        return self.pnl / self.initial_balance


class PaperExecutor:
    """
    Paper trading executor that simulates order execution.
    
    Features:
    - Tracks positions and P&L
    - Simulates fills at market prices
    - No real money at risk
    """
    
    def __init__(self, initial_balance: float = 1000.0):
        """
        Initialize paper executor.
        
        Args:
            initial_balance: Starting balance in USD
        """
        self.account = PaperAccount(
            balance=initial_balance,
            initial_balance=initial_balance
        )
        self._order_history: List[Order] = []
    
    async def execute_order(self, order: Order) -> Order:
        """
        Execute a paper trade order.
        
        Args:
            order: Order to execute
            
        Returns:
            Order with updated status
        """
        order.order_id = str(uuid.uuid4())[:8]
        
        # Calculate cost
        cost = order.price * order.size
        
        if order.side == Side.BUY:
            # Check balance
            if cost > self.account.balance:
                order.status = OrderStatus.FAILED
                logger.warning(f"❌ Insufficient balance for order: ${cost:.2f} > ${self.account.balance:.2f}")
                return order
            
            # Deduct balance
            self.account.balance -= cost
            
            # Update position
            self._add_to_position(order)
            
        else:  # SELL
            # Check position
            position = self.account.positions.get(order.token_id)
            if not position or position.shares < order.size:
                order.status = OrderStatus.FAILED
                logger.warning(f"❌ Insufficient position for sell order")
                return order
            
            # Add balance
            self.account.balance += cost
            
            # Update position
            self._remove_from_position(order)
        
        # Mark as filled
        order.status = OrderStatus.FILLED
        order.filled_size = order.size
        order.filled_price = order.price
        order.executed_at = datetime.utcnow()
        
        # Record trade
        trade = Trade(
            id=str(uuid.uuid4())[:8],
            market_id=order.market_id,
            token_id=order.token_id,
            side=order.side,
            outcome=order.outcome,
            price=order.price,
            size=order.size,
            cost=cost,
            executed_at=datetime.utcnow(),
            module="paper"
        )
        self.account.trades.append(trade)
        self._order_history.append(order)
        
        action = "BOUGHT" if order.side == Side.BUY else "SOLD"
        logger.info(
            f"📝 Paper Trade: {action} {order.size:.2f} {order.outcome.value} @ ${order.price:.4f} "
            f"(Cost: ${cost:.2f})"
        )
        
        return order
    
    async def execute_arbitrage_pair(
        self,
        yes_order: Order,
        no_order: Order
    ) -> tuple[Order, Order]:
        """
        Execute arbitrage pair (buy YES and NO together).
        
        Both orders must succeed or neither executes.
        """
        total_cost = (yes_order.price * yes_order.size) + (no_order.price * no_order.size)
        
        if total_cost > self.account.balance:
            yes_order.status = OrderStatus.FAILED
            no_order.status = OrderStatus.FAILED
            logger.warning(f"❌ Insufficient balance for arbitrage: ${total_cost:.2f}")
            return yes_order, no_order
        
        # Execute both
        yes_result = await self.execute_order(yes_order)
        no_result = await self.execute_order(no_order)
        
        if yes_result.is_filled and no_result.is_filled:
            profit = (yes_result.size + no_result.size) - total_cost
            logger.info(
                f"✅ Arbitrage executed! Total cost: ${total_cost:.4f} | "
                f"Guaranteed payout: $1.00/share | Profit: ${profit:.4f}"
            )
        
        return yes_result, no_result
    
    def _add_to_position(self, order: Order):
        """Add shares to position."""
        token_id = order.token_id
        
        if token_id in self.account.positions:
            pos = self.account.positions[token_id]
            # Update average price
            total_cost = (pos.shares * pos.avg_price) + (order.size * order.price)
            total_shares = pos.shares + order.size
            pos.avg_price = total_cost / total_shares if total_shares > 0 else 0
            pos.shares = total_shares
            pos.current_price = order.price
        else:
            self.account.positions[token_id] = Position(
                market_id=order.market_id,
                token_id=token_id,
                outcome=order.outcome,
                shares=order.size,
                avg_price=order.price,
                current_price=order.price
            )
    
    def _remove_from_position(self, order: Order):
        """Remove shares from position."""
        token_id = order.token_id
        
        if token_id in self.account.positions:
            pos = self.account.positions[token_id]
            pos.shares -= order.size
            pos.current_price = order.price
            
            if pos.shares <= 0:
                del self.account.positions[token_id]
    
    def get_status(self) -> str:
        """Get formatted account status."""
        return (
            f"\n"
            f"╔═══════════════════════════════════════════════════════════╗\n"
            f"║ 📊 PAPER TRADING ACCOUNT                                  ║\n"
            f"╠═══════════════════════════════════════════════════════════╣\n"
            f"║ Balance:       ${self.account.balance:>12,.2f}                       ║\n"
            f"║ Positions:     ${sum(p.current_value for p in self.account.positions.values()):>12,.2f}                       ║\n"
            f"║ Total Value:   ${self.account.total_value:>12,.2f}                       ║\n"
            f"╠═══════════════════════════════════════════════════════════╣\n"
            f"║ P&L:           ${self.account.pnl:>+12,.2f} ({self.account.pnl_pct:>+.2%})              ║\n"
            f"║ Trades:        {len(self.account.trades):>12}                       ║\n"
            f"╚═══════════════════════════════════════════════════════════╝"
        )
