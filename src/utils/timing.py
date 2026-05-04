#!/usr/bin/env python3
"""Timing and scheduling utilities."""

from datetime import datetime, time, timezone, timedelta


def is_us_market_open() -> bool:
    """Check if US stock market is currently open."""
    # US market hours: 9:30 AM - 4:00 PM ET (weekdays only)
    market_open = time(9, 30)
    market_close = time(16, 0)
    
    # Get current time in ET
    et_offset = timedelta(hours=-5)  # EST (adjust for DST if needed)
    now_utc = datetime.now(timezone.utc)
    now_et = now_utc + et_offset
    
    # Check if it's a weekday and within market hours
    if now_et.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return False
    
    current_time = now_et.time()
    return market_open <= current_time <= market_close


def is_etf_posting_time() -> bool:
    """Determine if it's time to post ETF updates."""
    # Post ETF data during US market hours on weekdays
    market_open = time(9, 30)
    market_close = time(16, 0)
    
    et_offset = timedelta(hours=-5)
    now_utc = datetime.now(timezone.utc)
    now_et = now_utc + et_offset
    
    if now_et.weekday() >= 5:  # Weekend
        return False
    
    current_time = now_et.time()
    return market_open <= current_time <= market_close


def is_fear_greed_posting_time() -> bool:
    """Determine if it's time to post Fear & Greed updates."""
    # Post F&G data once per day
    now_utc = datetime.now(timezone.utc)
    
    # Post at a specific time each day (e.g., 12:00 UTC)
    target_hour = 12
    return now_utc.hour == target_hour


def should_update_sticker_type(sticker_type: str) -> bool:
    """Determine if a specific sticker type should be updated now."""
    update_rules = {
        "btc": True,  # Always update Bitcoin price
        "eth": True,  # Always update Ethereum price
        "etf": is_etf_posting_time(),
        "fear": is_fear_greed_posting_time(),
        "fear_troll": is_fear_greed_posting_time(),
        "halving": is_fear_greed_posting_time(),  # Once per day like F&G
        "donate": False,  # Never auto-update donate sticker
    }
    
    return update_rules.get(sticker_type, False)
