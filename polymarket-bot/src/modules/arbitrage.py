"""
Arbitrage Module - Detects and executes single-market arbitrage.

Strategy: When YES_price + NO_price < 1.0, buy both sides for guaranteed profit.
"""

from typing import List, Optional
from datetime import datetime
from loguru import logger

from src.core.config import settings
from src.core.types import (
    Market, Signal, ArbitrageOpportunity, 
    Side, Outcome, SignalUrgency
)


class ArbitrageDetector:
    """
    Detects arbitrage opportunities in Polymarket.
    
    An arbitrage exists when:
    - YES_price + NO_price < 1.00
    - The difference (1.0 - sum) is the guaranteed profit
    
    Example:
        YES at $0.45 + NO at $0.52 = $0.97
        Buy both for $0.97, one pays $1.00 = $0.03 profit (3.1%)
    """
    
    def __init__(
        self,
        min_spread: float = None,
        min_volume: float = None,
        max_position: float = None
    ):
        """
        Initialize arbitrage detector.
        
        Args:
            min_spread: Minimum spread to trigger (default from settings)
            min_volume: Minimum market volume (default from settings)
            max_position: Maximum position size (default from settings)
        """
        self.min_spread = min_spread or settings.min_arbitrage_spread
        self.min_volume = min_volume or settings.min_market_volume
        self.max_position = max_position or settings.max_position_usd
    
    def detect(self, markets: List[Market]) -> List[ArbitrageOpportunity]:
        """
        Scan markets for arbitrage opportunities.
        
        Args:
            markets: List of markets to scan
            
        Returns:
            List of ArbitrageOpportunity objects, sorted by profit %
        """
        opportunities = []
        
        for market in markets:
            opp = self._check_market(market)
            if opp:
                opportunities.append(opp)
        
        # Sort by profit percentage (highest first)
        opportunities.sort(key=lambda x: x.profit_pct, reverse=True)
        
        return opportunities
    
    def _check_market(self, market: Market) -> Optional[ArbitrageOpportunity]:
        """Check a single market for arbitrage."""
        
        # Skip if prices are invalid
        if market.yes_price <= 0 or market.no_price <= 0:
            return None
        
        # Skip if below volume threshold
        if market.volume_24h < self.min_volume:
            return None
        
        # Calculate total cost and profit
        total_cost = market.yes_price + market.no_price
        profit = 1.0 - total_cost
        profit_pct = profit / total_cost if total_cost > 0 else 0
        
        # Skip if spread is below threshold
        if profit_pct < self.min_spread:
            return None
        
        # Calculate sizing
        # Max shares = max_position / total_cost_per_share
        max_shares = self.max_position / total_cost if total_cost > 0 else 0
        
        # Also consider liquidity (use lower of the two)
        liquidity_limit = market.liquidity / 2 if market.liquidity > 0 else float('inf')
        suggested_shares = min(max_shares, liquidity_limit)
        
        return ArbitrageOpportunity(
            market=market,
            yes_price=market.yes_price,
            no_price=market.no_price,
            total_cost=total_cost,
            profit=profit,
            profit_pct=profit_pct,
            max_size=max_shares * total_cost,
            suggested_size=suggested_shares * total_cost,
            timestamp=datetime.utcnow()
        )
    
    def generate_signals(
        self, 
        opportunities: List[ArbitrageOpportunity]
    ) -> List[Signal]:
        """
        Convert arbitrage opportunities to trading signals.
        
        Each opportunity generates TWO signals (buy YES and buy NO).
        """
        signals = []
        
        for opp in opportunities:
            # Signal to buy YES
            yes_signal = Signal(
                module="arbitrage",
                market_id=opp.market.id,
                token_id=opp.market.yes_token_id,
                action=Side.BUY,
                outcome=Outcome.YES,
                confidence=1.0,  # Arbitrage is mathematically certain
                expected_value=opp.profit * (opp.suggested_size / opp.total_cost) / 2,
                size_suggestion=opp.suggested_size / 2,
                urgency=SignalUrgency.IMMEDIATE,
                metadata={
                    "type": "arbitrage",
                    "pair_token": opp.market.no_token_id,
                    "total_cost": opp.total_cost,
                    "profit_pct": opp.profit_pct
                }
            )
            
            # Signal to buy NO
            no_signal = Signal(
                module="arbitrage",
                market_id=opp.market.id,
                token_id=opp.market.no_token_id,
                action=Side.BUY,
                outcome=Outcome.NO,
                confidence=1.0,
                expected_value=opp.profit * (opp.suggested_size / opp.total_cost) / 2,
                size_suggestion=opp.suggested_size / 2,
                urgency=SignalUrgency.IMMEDIATE,
                metadata={
                    "type": "arbitrage",
                    "pair_token": opp.market.yes_token_id,
                    "total_cost": opp.total_cost,
                    "profit_pct": opp.profit_pct
                }
            )
            
            signals.extend([yes_signal, no_signal])
        
        return signals


def format_opportunity(opp: ArbitrageOpportunity) -> str:
    """Format opportunity for logging/display."""
    return (
        f"╔═══════════════════════════════════════════════════════════╗\n"
        f"║ 🎯 ARBITRAGE OPPORTUNITY                                  ║\n"
        f"╠═══════════════════════════════════════════════════════════╣\n"
        f"║ Market: {opp.market.question[:50]:<50} ║\n"
        f"╠═══════════════════════════════════════════════════════════╣\n"
        f"║ YES Price: ${opp.yes_price:.4f}                                      ║\n"
        f"║ NO Price:  ${opp.no_price:.4f}                                      ║\n"
        f"║ Total:     ${opp.total_cost:.4f}                                      ║\n"
        f"╠═══════════════════════════════════════════════════════════╣\n"
        f"║ 💰 PROFIT: ${opp.profit:.4f} ({opp.profit_pct:.2%})                         ║\n"
        f"║ 📊 Suggested Size: ${opp.suggested_size:.2f}                        ║\n"
        f"║ 📈 24h Volume: ${opp.market.volume_24h:,.0f}                            ║\n"
        f"╚═══════════════════════════════════════════════════════════╝"
    )
