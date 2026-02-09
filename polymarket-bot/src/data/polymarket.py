"""
Polymarket API client for fetching markets and orderbook data.
Uses both Gamma API (metadata) and CLOB API (trading).
"""

import asyncio
import aiohttp
from typing import List, Optional, Dict, Any
from datetime import datetime
from loguru import logger

from src.core.config import settings
from src.core.types import Market


class PolymarketClient:
    """
    Client for interacting with Polymarket APIs.
    
    - Gamma API: Market metadata, events, categories
    - CLOB API: Orderbooks, trades, order execution
    """
    
    def __init__(self):
        self.gamma_url = settings.polymarket_gamma_url
        self.clob_url = settings.polymarket_clob_url
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
        return self._session
    
    async def close(self):
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def _get(self, url: str, params: Optional[Dict] = None) -> Any:
        """Make GET request with error handling."""
        session = await self._get_session()
        try:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    logger.error(f"API error {resp.status}: {url}")
                    return None
        except Exception as e:
            logger.error(f"Request failed: {url} - {e}")
            return None
    
    # =========================================
    # GAMMA API - Market Metadata
    # =========================================
    
    async def get_markets(
        self,
        active: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """
        Fetch markets from Gamma API.
        
        Returns raw market data from API.
        """
        params = {
            "limit": limit,
            "offset": offset,
            "active": str(active).lower(),
            "closed": "false"
        }
        
        url = f"{self.gamma_url}/markets"
        data = await self._get(url, params)
        
        if data is None:
            return []
        
        return data if isinstance(data, list) else []
    
    async def get_all_active_markets(self) -> List[Dict]:
        """Fetch all active markets (paginated)."""
        all_markets = []
        offset = 0
        limit = 100
        
        while True:
            markets = await self.get_markets(active=True, limit=limit, offset=offset)
            if not markets:
                break
            all_markets.extend(markets)
            if len(markets) < limit:
                break
            offset += limit
            await asyncio.sleep(0.1)  # Rate limiting
        
        logger.info(f"Fetched {len(all_markets)} active markets")
        return all_markets
    
    async def get_market_by_id(self, market_id: str) -> Optional[Dict]:
        """Fetch single market by ID."""
        url = f"{self.gamma_url}/markets/{market_id}"
        return await self._get(url)
    
    # =========================================
    # CLOB API - Orderbooks & Prices
    # =========================================
    
    async def get_orderbook(self, token_id: str) -> Optional[Dict]:
        """
        Fetch orderbook for a token.
        
        Returns:
            {
                "bids": [{"price": "0.45", "size": "100"}, ...],
                "asks": [{"price": "0.47", "size": "50"}, ...]
            }
        """
        url = f"{self.clob_url}/book"
        params = {"token_id": token_id}
        return await self._get(url, params)
    
    async def get_price(self, token_id: str) -> Optional[Dict]:
        """
        Fetch current price for a token.
        
        Returns:
            {"price": "0.45", "timestamp": "..."}
        """
        url = f"{self.clob_url}/price"
        params = {"token_id": token_id}
        return await self._get(url, params)
    
    async def get_midpoint(self, token_id: str) -> Optional[float]:
        """Get midpoint price for a token."""
        url = f"{self.clob_url}/midpoint"
        params = {"token_id": token_id}
        data = await self._get(url, params)
        
        if data and "mid" in data:
            try:
                return float(data["mid"])
            except (ValueError, TypeError):
                return None
        return None
    
    async def get_prices_for_market(self, yes_token: str, no_token: str) -> Dict[str, float]:
        """
        Get prices for both YES and NO tokens.
        
        Returns:
            {"yes": 0.45, "no": 0.55}
        """
        yes_price, no_price = await asyncio.gather(
            self.get_midpoint(yes_token),
            self.get_midpoint(no_token)
        )
        
        return {
            "yes": yes_price or 0.0,
            "no": no_price or 0.0
        }
    
    async def get_last_trade_price(self, token_id: str) -> Optional[float]:
        """Get last trade price for a token."""
        url = f"{self.clob_url}/last-trade-price"
        params = {"token_id": token_id}
        data = await self._get(url, params)
        
        if data and "price" in data:
            try:
                return float(data["price"])
            except (ValueError, TypeError):
                return None
        return None
    
    # =========================================
    # Helper: Parse to Market objects
    # =========================================
    
    def parse_market(self, raw: Dict, prices: Optional[Dict] = None) -> Optional[Market]:
        """
        Parse raw API response to Market object.
        
        Args:
            raw: Raw market data from Gamma API
            prices: Optional price data {"yes": 0.45, "no": 0.55}
        """
        try:
            # Extract token IDs from outcomes
            tokens = raw.get("tokens", [])
            if len(tokens) < 2:
                return None
            
            yes_token = None
            no_token = None
            
            for token in tokens:
                outcome = token.get("outcome", "").upper()
                if outcome == "YES":
                    yes_token = token.get("token_id")
                elif outcome == "NO":
                    no_token = token.get("token_id")
            
            if not yes_token or not no_token:
                return None
            
            # Get prices from tokens if not provided
            yes_price = 0.0
            no_price = 0.0
            
            if prices:
                yes_price = prices.get("yes", 0.0)
                no_price = prices.get("no", 0.0)
            else:
                for token in tokens:
                    outcome = token.get("outcome", "").upper()
                    price = float(token.get("price", 0) or 0)
                    if outcome == "YES":
                        yes_price = price
                    elif outcome == "NO":
                        no_price = price
            
            # Parse end date
            end_date = None
            if raw.get("end_date_iso"):
                try:
                    end_date = datetime.fromisoformat(
                        raw["end_date_iso"].replace("Z", "+00:00")
                    )
                except:
                    pass
            
            return Market(
                id=raw.get("condition_id", raw.get("id", "")),
                question=raw.get("question", ""),
                slug=raw.get("slug", ""),
                yes_token_id=yes_token,
                no_token_id=no_token,
                yes_price=yes_price,
                no_price=no_price,
                volume_24h=float(raw.get("volume_24hr", 0) or 0),
                liquidity=float(raw.get("liquidity", 0) or 0),
                end_date=end_date,
                category=raw.get("category"),
                is_active=raw.get("active", True)
            )
        except Exception as e:
            logger.debug(f"Failed to parse market: {e}")
            return None


class MarketScanner:
    """
    Scans all active markets and enriches with real-time prices.
    """
    
    def __init__(self, client: PolymarketClient):
        self.client = client
        self._market_cache: Dict[str, Market] = {}
        self._last_scan: Optional[datetime] = None
    
    async def scan_all_markets(
        self,
        min_volume: float = 0,
        fetch_prices: bool = True
    ) -> List[Market]:
        """
        Scan all active markets and return Market objects.
        
        Args:
            min_volume: Minimum 24h volume filter
            fetch_prices: Whether to fetch real-time prices (slower but accurate)
        """
        raw_markets = await self.client.get_all_active_markets()
        markets = []
        
        for raw in raw_markets:
            # Apply volume filter early
            volume = float(raw.get("volume_24hr", 0) or 0)
            if volume < min_volume:
                continue
            
            market = self.client.parse_market(raw)
            if not market:
                continue
            
            # Optionally fetch real-time prices
            if fetch_prices and market.yes_token_id and market.no_token_id:
                prices = await self.client.get_prices_for_market(
                    market.yes_token_id,
                    market.no_token_id
                )
                market.yes_price = prices["yes"]
                market.no_price = prices["no"]
                await asyncio.sleep(0.05)  # Rate limiting
            
            markets.append(market)
            self._market_cache[market.id] = market
        
        self._last_scan = datetime.utcnow()
        logger.info(f"Scanned {len(markets)} markets (min_volume: ${min_volume})")
        
        return markets
    
    async def get_market(self, market_id: str) -> Optional[Market]:
        """Get market from cache or fetch."""
        if market_id in self._market_cache:
            return self._market_cache[market_id]
        
        raw = await self.client.get_market_by_id(market_id)
        if raw:
            market = self.client.parse_market(raw)
            if market:
                self._market_cache[market_id] = market
                return market
        return None
    
    def find_arbitrage_opportunities(
        self,
        markets: List[Market],
        min_spread: float = 0.01
    ) -> List[Market]:
        """
        Find markets where YES + NO < 1.0 (arbitrage opportunity).
        
        Args:
            markets: List of markets to scan
            min_spread: Minimum spread (1.0 - sum) to consider
        """
        opportunities = []
        
        for market in markets:
            if market.yes_price <= 0 or market.no_price <= 0:
                continue
            
            spread = market.arbitrage_spread
            if spread >= min_spread:
                opportunities.append(market)
                logger.info(
                    f"🎯 Arbitrage found: {market.question[:50]}... "
                    f"| YES: {market.yes_price:.3f} NO: {market.no_price:.3f} "
                    f"| Spread: {spread:.2%}"
                )
        
        return sorted(opportunities, key=lambda m: m.arbitrage_spread, reverse=True)
