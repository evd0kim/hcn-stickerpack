#!/usr/bin/env python3
"""Configuration module for the sticker pack bot."""

from os import getenv
from typing import Optional


class APIConfig:
    """API endpoint configurations."""
    FNG_API_URL = "https://api.alternative.me/fng/"
    AUD_API_URL = "https://www.coinspot.com.au/pubapi/v2/latest"
    BTC_API_URL = "https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT"
    ETHBTC_API_URL = "https://api.binance.com/api/v3/ticker/24hr?symbol=ETHBTC"
    IDRBTC_API_URL = "https://indodax.com/api/ticker/btcidr"
    PRICE_API_URL = "https://api.binance.com/api/v3/ticker/price"
    RUB_PRICE_API_URL = "https://blockchain.info/ticker"
    BLOCK_HEIGHT_URL = "https://bitcoinchainfees.strike.me/v1/fee-estimates"


class DrawingConfig:
    """Drawing and graphics configurations."""
    # Image dimensions
    WIDTH = 512
    HEIGHT = 512
    
    # Grid settings
    CELL_SIZE = 30
    GRID_SIZE_X = 12
    GRID_SIZE_Y = 7
    SPACING = 3
    CORNER_RADIUS = 3


class TelegramConfig:
    """Telegram bot configurations."""
    USER_ID: Optional[str] = getenv("TG_USER_ID")
    PACK_NAME: Optional[str] = getenv("TG_PACK_NAME")
    BOT_TOKEN: Optional[str] = getenv("TG_BOT_TOKEN")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that all required environment variables are set."""
        return all([cls.USER_ID, cls.PACK_NAME, cls.BOT_TOKEN])


class AppConfig:
    """Main application configuration."""
    api = APIConfig()
    drawing = DrawingConfig()
    telegram = TelegramConfig()
    
    # Asset paths
    ASSETS_DIR = "./assets"
    DONATE_PNG = f"{ASSETS_DIR}/donate.png"
    
    # Emoji mappings
    EMOJI_MAPPING = {
        "💸": "btc",
        "💩": "eth", 
        "🏦": "etf",
        "😱": "fear",
        "⛓": "halving",
        "🙏": "donate",
        "🤡": "fear_troll",
    }
