"""
Configuration management using Pydantic Settings.
Loads from environment variables and .env file.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment."""
    
    # Polymarket API
    polymarket_private_key: str = Field(default="", description="Wallet private key")
    polymarket_funder: str = Field(default="", description="Funder address")
    polymarket_chain_id: int = Field(default=137, description="Chain ID (137=Polygon)")
    polymarket_clob_url: str = Field(default="https://clob.polymarket.com")
    polymarket_gamma_url: str = Field(default="https://gamma-api.polymarket.com")
    
    # Trading
    paper_trade: bool = Field(default=True, description="Paper trading mode")
    bankroll: float = Field(default=1000.0, description="Starting bankroll USD")
    max_position_fraction: float = Field(default=0.05, description="Max position as fraction of bankroll")
    min_arbitrage_spread: float = Field(default=0.02, description="Min spread to trigger arb")
    
    # Scanning
    scan_interval: int = Field(default=5, description="Scan interval in seconds")
    min_market_volume: float = Field(default=10000, description="Min market volume USD")
    
    # Notifications
    telegram_bot_token: Optional[str] = Field(default=None)
    telegram_chat_id: Optional[str] = Field(default=None)
    
    # Logging
    log_level: str = Field(default="INFO")
    
    # Binance (Phase 2)
    binance_api_key: Optional[str] = Field(default=None)
    binance_secret: Optional[str] = Field(default=None)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @property
    def max_position_usd(self) -> float:
        """Maximum position size in USD."""
        return self.bankroll * self.max_position_fraction
    
    @property
    def is_configured(self) -> bool:
        """Check if essential settings are configured."""
        if self.paper_trade:
            return True  # Paper trade doesn't need wallet
        return bool(self.polymarket_private_key and self.polymarket_funder)


# Global settings instance
settings = Settings()


def load_settings(env_file: Optional[Path] = None) -> Settings:
    """Load settings from optional custom env file."""
    if env_file:
        return Settings(_env_file=env_file)
    return Settings()
