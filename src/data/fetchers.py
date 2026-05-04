#!/usr/bin/env python3
"""Data fetching services for cryptocurrency and market data."""

import requests
import yfinance as yf
from datetime import datetime
from typing import List, Dict, Any, Optional

from .models import BitcoinData, EthereumData, FearGreedData, HalvingData, ETFData, BlockchainData
from ..config.settings import APIConfig


class DataFetchError(Exception):
    """Exception raised when data fetching fails."""
    pass


class BitcoinFetcher:
    """Fetches Bitcoin-related data."""
    
    @staticmethod
    def fetch_btc_data() -> BitcoinData:
        """Fetch Bitcoin price and market data."""
        try:
            response = requests.get(APIConfig.BTC_API_URL)
            response.raise_for_status()
            data = response.json()
            
            return BitcoinData(
                price=float(data["lastPrice"]),
                change_24h=float(data["priceChange"]),
                change_percent_24h=float(data["priceChangePercent"]),
                high_24h=float(data["highPrice"]),
                low_24h=float(data["lowPrice"]),
                volume=float(data["volume"]),
                timestamp=datetime.utcnow()
            )
        except (requests.RequestException, KeyError, ValueError) as e:
            raise DataFetchError(f"Failed to fetch Bitcoin data: {e}")


class EthereumFetcher:
    """Fetches Ethereum-related data."""
    
    @staticmethod
    def fetch_eth_data() -> EthereumData:
        """Fetch Ethereum price data in both USD and BTC."""
        try:
            # Get ETH/BTC pair
            response = requests.get(APIConfig.ETHBTC_API_URL)
            response.raise_for_status()
            eth_btc_data = response.json()
            
            # Get USD prices through price API
            eth_price_response = requests.get(
                f"{APIConfig.PRICE_API_URL}?symbol=ETHUSDT"
            )
            eth_price_response.raise_for_status()
            eth_usd_data = eth_price_response.json()
            
            return EthereumData(
                price=float(eth_usd_data["price"]),
                btc_price=float(eth_btc_data["lastPrice"]),
                change_24h=float(eth_btc_data["priceChange"]),
                change_percent_24h=float(eth_btc_data["priceChangePercent"]),
                high_24h=float(eth_btc_data["highPrice"]),
                low_24h=float(eth_btc_data["lowPrice"]),
                volume=float(eth_btc_data["volume"]),
                timestamp=datetime.utcnow()
            )
        except (requests.RequestException, KeyError, ValueError) as e:
            raise DataFetchError(f"Failed to fetch Ethereum data: {e}")


class FearGreedFetcher:
    """Fetches Fear & Greed Index data."""
    
    @staticmethod
    def fetch_fear_greed_data() -> FearGreedData:
        """Fetch current Fear & Greed Index."""
        try:
            response = requests.get(APIConfig.FNG_API_URL)
            response.raise_for_status()
            data = response.json()
            
            fng_data = data["data"][0]
            return FearGreedData(
                value=int(fng_data["value"]),
                classification=fng_data["value_classification"],
                timestamp=datetime.fromtimestamp(int(fng_data["timestamp"]))
            )
        except (requests.RequestException, KeyError, ValueError) as e:
            raise DataFetchError(f"Failed to fetch Fear & Greed data: {e}")


class BlockchainFetcher:
    """Fetches blockchain data like block height and fees."""
    
    @staticmethod
    def fetch_blockchain_data() -> BlockchainData:
        """Fetch current blockchain height and fee information."""
        try:
            response = requests.get(APIConfig.BLOCK_HEIGHT_URL)
            response.raise_for_status()
            data = response.json()
            
            return BlockchainData(
                current_height=int(data["current_block_height"]),
                priority_fee=float(data["fee_by_block_target"]["1"]) / 1000,
                timestamp=datetime.utcnow()
            )
        except (requests.RequestException, KeyError, ValueError) as e:
            raise DataFetchError(f"Failed to fetch blockchain data: {e}")


class HalvingFetcher:
    """Fetches Bitcoin halving information."""
    
    @staticmethod
    def fetch_halving_data() -> HalvingData:
        """Calculate Bitcoin halving information."""
        try:
            blockchain_data = BlockchainFetcher.fetch_blockchain_data()
            current_height = blockchain_data.current_height
            
            # Bitcoin halving occurs every 210,000 blocks
            HALVING_INTERVAL = 210000
            next_halving_block = ((current_height // HALVING_INTERVAL) + 1) * HALVING_INTERVAL
            blocks_remaining = next_halving_block - current_height
            
            # Estimate days (average 10 minutes per block)
            estimated_days = (blocks_remaining * 10) // (60 * 24)
            completion_percentage = (current_height % HALVING_INTERVAL) / HALVING_INTERVAL * 100
            
            return HalvingData(
                current_block_height=current_height,
                next_halving_block=next_halving_block,
                blocks_remaining=blocks_remaining,
                estimated_days=estimated_days,
                completion_percentage=completion_percentage,
                timestamp=datetime.utcnow()
            )
        except DataFetchError:
            raise
        except Exception as e:
            raise DataFetchError(f"Failed to calculate halving data: {e}")


class ETFFetcher:
    """Fetches ETF market data."""
    
    ETF_SYMBOLS = [
        "IBIT", "FBTC", "BITB", "ARKB", "BTCO", 
        "EZBC", "BRRR", "HODL", "BTCW", "GBTC", "BTC"
    ]
    
    @classmethod
    def fetch_etf_data(cls) -> List[ETFData]:
        """Fetch ETF data for Bitcoin-related funds."""
        try:
            etf_data = []
            
            # Use yfinance to get multiple tickers at once
            tickers = yf.Tickers(" ".join(cls.ETF_SYMBOLS))
            
            for symbol in cls.ETF_SYMBOLS:
                try:
                    ticker = tickers.tickers[symbol]
                    info = ticker.info
                    hist = ticker.history(period="2d")
                    
                    if len(hist) < 2:
                        continue
                        
                    current_price = hist['Close'].iloc[-1]
                    prev_price = hist['Close'].iloc[-2]
                    change = current_price - prev_price
                    change_percent = (change / prev_price) * 100
                    
                    etf_data.append(ETFData(
                        symbol=symbol,
                        name=info.get("longName", symbol),
                        price=float(current_price),
                        change=float(change),
                        change_percent=float(change_percent),
                        market_cap=float(info.get("marketCap", 0)),
                        volume=float(hist['Volume'].iloc[-1]) if 'Volume' in hist else None
                    ))
                except Exception as e:
                    print(f"Warning: Failed to fetch data for {symbol}: {e}")
                    continue
            
            # Sort by market cap descending
            return sorted(etf_data, key=lambda x: x.market_cap, reverse=True)
            
        except Exception as e:
            raise DataFetchError(f"Failed to fetch ETF data: {e}")
