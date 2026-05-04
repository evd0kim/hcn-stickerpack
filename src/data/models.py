#!/usr/bin/env python3
"""Data models for the sticker pack bot."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional


@dataclass
class BitcoinData:
    """Bitcoin price and market data."""
    price: float
    change_24h: float
    change_percent_24h: float
    high_24h: float
    low_24h: float
    volume: float
    market_cap: Optional[float] = None
    timestamp: Optional[datetime] = None


@dataclass
class EthereumData:
    """Ethereum price and market data."""
    price: float
    btc_price: float
    change_24h: float
    change_percent_24h: float
    high_24h: float
    low_24h: float
    volume: float
    timestamp: Optional[datetime] = None


@dataclass
class FearGreedData:
    """Fear & Greed Index data."""
    value: int
    classification: str
    timestamp: datetime


@dataclass
class HalvingData:
    """Bitcoin halving information."""
    current_block_height: int
    next_halving_block: int
    blocks_remaining: int
    estimated_days: int
    completion_percentage: float
    timestamp: datetime


@dataclass
class ETFData:
    """ETF market data."""
    symbol: str
    name: str
    price: float
    change: float
    change_percent: float
    market_cap: float
    volume: Optional[float] = None


@dataclass
class BlockchainData:
    """Blockchain fee and height data."""
    current_height: int
    priority_fee: float  # sats per vByte
    timestamp: datetime
