#!/usr/bin/env python3
"""
Polymarket Trading Bot - Main Entry Point

Usage:
    python -m src.main              # Run scanner
    python -m src.main --paper      # Paper trading mode
    python -m src.main --scan-once  # Single scan then exit
"""

import asyncio
import argparse
import sys
from datetime import datetime
from typing import Optional

from loguru import logger

from src.core.config import settings
from src.core.types import Order, Side, Outcome
from src.data.polymarket import PolymarketClient, MarketScanner
from src.modules.arbitrage import ArbitrageDetector, format_opportunity
from src.execution.paper import PaperExecutor


# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
    level=settings.log_level
)


class TradingEngine:
    """
    Main trading engine orchestrating all components.
    """
    
    def __init__(self, paper_trade: bool = True):
        """
        Initialize trading engine.
        
        Args:
            paper_trade: Whether to use paper trading (default True)
        """
        self.paper_trade = paper_trade
        
        # Initialize components
        self.client = PolymarketClient()
        self.scanner = MarketScanner(self.client)
        self.arb_detector = ArbitrageDetector()
        
        # Executor
        if paper_trade:
            self.executor = PaperExecutor(initial_balance=settings.bankroll)
            logger.info("📝 Paper trading mode enabled")
        else:
            # TODO: Real executor with py-clob-client
            raise NotImplementedError("Real trading not yet implemented")
        
        self._running = False
        self._scan_count = 0
        self._opportunities_found = 0
    
    async def scan_once(self) -> int:
        """
        Perform a single market scan.
        
        Returns:
            Number of arbitrage opportunities found
        """
        self._scan_count += 1
        logger.info(f"🔍 Scan #{self._scan_count} starting...")
        
        # Fetch all active markets
        markets = await self.scanner.scan_all_markets(
            min_volume=settings.min_market_volume,
            fetch_prices=True
        )
        
        if not markets:
            logger.warning("No markets found")
            return 0
        
        # Detect arbitrage opportunities
        opportunities = self.arb_detector.detect(markets)
        
        if opportunities:
            self._opportunities_found += len(opportunities)
            logger.info(f"🎯 Found {len(opportunities)} arbitrage opportunities!")
            
            for opp in opportunities[:5]:  # Show top 5
                print(format_opportunity(opp))
                
                # Execute if paper trading
                if self.paper_trade:
                    await self._execute_arbitrage(opp)
        else:
            logger.info("No arbitrage opportunities found this scan")
        
        return len(opportunities)
    
    async def _execute_arbitrage(self, opp):
        """Execute arbitrage opportunity."""
        # Calculate shares to buy
        shares_per_side = opp.suggested_size / opp.total_cost
        
        yes_order = Order(
            market_id=opp.market.id,
            token_id=opp.market.yes_token_id,
            side=Side.BUY,
            outcome=Outcome.YES,
            price=opp.yes_price,
            size=shares_per_side
        )
        
        no_order = Order(
            market_id=opp.market.id,
            token_id=opp.market.no_token_id,
            side=Side.BUY,
            outcome=Outcome.NO,
            price=opp.no_price,
            size=shares_per_side
        )
        
        await self.executor.execute_arbitrage_pair(yes_order, no_order)
    
    async def run(self, single_scan: bool = False):
        """
        Run the trading engine.
        
        Args:
            single_scan: If True, run one scan and exit
        """
        self._running = True
        
        print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║   ██████╗  ██████╗ ██╗  ██╗   ██╗███╗   ███╗ █████╗ ██████╗ ██╗  ██╗███████╗████████╗   ║
║   ██╔══██╗██╔═══██╗██║  ╚██╗ ██╔╝████╗ ████║██╔══██╗██╔══██╗██║ ██╔╝██╔════╝╚══██╔══╝   ║
║   ██████╔╝██║   ██║██║   ╚████╔╝ ██╔████╔██║███████║██████╔╝█████╔╝ █████╗     ██║      ║
║   ██╔═══╝ ██║   ██║██║    ╚██╔╝  ██║╚██╔╝██║██╔══██║██╔══██╗██╔═██╗ ██╔══╝     ██║      ║
║   ██║     ╚██████╔╝███████╗██║   ██║ ╚═╝ ██║██║  ██║██║  ██║██║  ██╗███████╗   ██║      ║
║   ╚═╝      ╚═════╝ ╚══════╝╚═╝   ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝   ╚═╝      ║
║                                                                               ║
║                    ⚡ ARBITRAGE BOT v0.1.0 ⚡                                  ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
        """)
        
        logger.info(f"Mode: {'PAPER TRADING' if self.paper_trade else 'LIVE TRADING'}")
        logger.info(f"Bankroll: ${settings.bankroll:,.2f}")
        logger.info(f"Min arbitrage spread: {settings.min_arbitrage_spread:.1%}")
        logger.info(f"Min market volume: ${settings.min_market_volume:,.0f}")
        logger.info(f"Scan interval: {settings.scan_interval}s")
        print()
        
        try:
            if single_scan:
                await self.scan_once()
            else:
                while self._running:
                    await self.scan_once()
                    
                    # Show account status
                    if self.paper_trade:
                        print(self.executor.get_status())
                    
                    logger.info(f"💤 Sleeping {settings.scan_interval}s until next scan...")
                    await asyncio.sleep(settings.scan_interval)
                    
        except KeyboardInterrupt:
            logger.info("🛑 Shutting down...")
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Clean shutdown."""
        self._running = False
        await self.client.close()
        
        # Final summary
        print("\n" + "="*60)
        print("📊 SESSION SUMMARY")
        print("="*60)
        print(f"Total scans: {self._scan_count}")
        print(f"Opportunities found: {self._opportunities_found}")
        
        if self.paper_trade:
            print(f"Final P&L: ${self.executor.account.pnl:+,.2f} ({self.executor.account.pnl_pct:+.2%})")
            print(f"Trades executed: {len(self.executor.account.trades)}")
        
        print("="*60)


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Polymarket Arbitrage Bot")
    parser.add_argument(
        "--paper", 
        action="store_true", 
        default=True,
        help="Run in paper trading mode (default)"
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Run in live trading mode (NOT IMPLEMENTED)"
    )
    parser.add_argument(
        "--scan-once",
        action="store_true",
        help="Run a single scan and exit"
    )
    
    args = parser.parse_args()
    
    paper_trade = not args.live
    
    engine = TradingEngine(paper_trade=paper_trade)
    await engine.run(single_scan=args.scan_once)


if __name__ == "__main__":
    asyncio.run(main())
