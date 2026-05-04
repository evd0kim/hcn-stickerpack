#!/usr/bin/env python3
"""Sticker renderers for different data types."""

import math
import io
from datetime import datetime
from typing import List
import cairocffi as cairo

from ..data.models import BitcoinData, EthereumData, FearGreedData, HalvingData, ETFData
from .base import (
    create_surface, draw_text, draw_triangle, draw_grid, 
    load_svg, get_color_for_value, format_large_number, draw_rounded_rectangle
)


class BitcoinRenderer:
    """Renders Bitcoin price stickers."""
    
    @staticmethod
    def render(data: BitcoinData) -> cairo.ImageSurface:
        """Render Bitcoin price sticker."""
        surface, ctx = create_surface()
        
        # Load Bitcoin SVG
        bitcoin_svg = load_svg("bitcoin.svg")
        ctx.set_source_surface(bitcoin_svg, 20, 20)
        ctx.paint()
        
        # Price
        price_text = f"${data.price:,.0f}"
        draw_text(ctx, (50, 50), (1, 1, 1), 48, price_text)
        
        # 24h change
        change_color = get_color_for_value(data.change_percent_24h)
        change_text = f"{data.change_percent_24h:+.1f}%"
        draw_text(ctx, (50, 100), change_color, 24, change_text)
        
        # Triangle indicator
        direction = "up" if data.change_percent_24h >= 0 else "down"
        draw_triangle(ctx, (30, 105), change_color, direction)
        
        return surface


class EthereumRenderer:
    """Renders Ethereum price stickers."""
    
    @staticmethod
    def render(data: EthereumData) -> cairo.ImageSurface:
        """Render Ethereum price sticker."""
        surface, ctx = create_surface()
        
        # Load Ethereum SVG
        eth_svg = load_svg("ethereum.svg")
        ctx.set_source_surface(eth_svg, 20, 20)
        ctx.paint()
        
        # USD Price
        price_text = f"${data.price:,.0f}"
        draw_text(ctx, (50, 50), (1, 1, 1), 36, price_text)
        
        # BTC Price
        btc_price_text = f"₿{data.btc_price:.6f}"
        draw_text(ctx, (50, 90), (0.8, 0.8, 0.8), 20, btc_price_text)
        
        # 24h change
        change_color = get_color_for_value(data.change_percent_24h)
        change_text = f"{data.change_percent_24h:+.1f}%"
        draw_text(ctx, (50, 120), change_color, 24, change_text)
        
        return surface


class FearGreedRenderer:
    """Renders Fear & Greed Index stickers."""
    
    @staticmethod
    def get_fear_color(value: int) -> tuple:
        """Get color based on Fear & Greed value."""
        if value <= 25:  # Extreme Fear
            return (1, 0, 0)  # Red
        elif value <= 45:  # Fear
            return (1, 0.5, 0)  # Orange
        elif value <= 55:  # Neutral
            return (1, 1, 0)  # Yellow
        elif value <= 75:  # Greed
            return (0.5, 1, 0)  # Light Green
        else:  # Extreme Greed
            return (0, 1, 0)  # Green
    
    @staticmethod
    def render_regular(data: FearGreedData) -> cairo.ImageSurface:
        """Render regular Fear & Greed sticker."""
        surface, ctx = create_surface()
        draw_grid(ctx)
        
        color = FearGreedRenderer.get_fear_color(data.value)
        
        # Draw gauge background
        center_x, center_y = 256, 200
        radius = 120
        
        ctx.set_line_width(20)
        ctx.set_source_rgb(0.2, 0.2, 0.2)
        ctx.arc(center_x, center_y, radius, math.pi, 2 * math.pi)
        ctx.stroke()
        
        # Draw gauge value
        angle = math.pi + (data.value / 100) * math.pi
        ctx.set_source_rgb(*color)
        ctx.arc(center_x, center_y, radius, math.pi, angle)
        ctx.stroke()
        
        # Value text
        draw_text(ctx, (center_x, center_y), (1, 1, 1), 48, str(data.value), 
                 center=(center_x, center_y))
        
        # Classification text
        draw_text(ctx, (center_x, center_y + 60), color, 20, data.classification,
                 center=(center_x, center_y + 60))
        
        return surface
    
    @staticmethod
    def render_troll(data: FearGreedData) -> cairo.ImageSurface:
        """Render troll version of Fear & Greed sticker."""
        surface, ctx = create_surface()
        draw_grid(ctx)
        
        # Inverted colors for troll mode
        troll_value = 100 - data.value
        color = FearGreedRenderer.get_fear_color(troll_value)
        
        # Similar rendering but with troll text
        center_x, center_y = 256, 200
        draw_text(ctx, (center_x, center_y), color, 48, "🤡", 
                 center=(center_x, center_y - 50))
        draw_text(ctx, (center_x, center_y), (1, 1, 1), 36, str(troll_value),
                 center=(center_x, center_y))
        draw_text(ctx, (center_x, center_y + 40), color, 16, "TROLL MODE",
                 center=(center_x, center_y + 40))
        
        return surface


class HalvingRenderer:
    """Renders Bitcoin halving countdown stickers."""
    
    @staticmethod
    def render(data: HalvingData) -> cairo.ImageSurface:
        """Render halving countdown sticker."""
        surface, ctx = create_surface()
        draw_grid(ctx)
        
        center_x, center_y = 256, 200
        
        # Progress bar
        bar_width = 300
        bar_height = 30
        bar_x = center_x - bar_width // 2
        bar_y = center_y - 50
        
        # Background bar
        draw_rounded_rectangle(ctx, bar_x, bar_y, bar_width, bar_height, 15)
        ctx.set_source_rgb(0.2, 0.2, 0.2)
        ctx.fill()
        
        # Progress fill
        progress_width = bar_width * (data.completion_percentage / 100)
        draw_rounded_rectangle(ctx, bar_x, bar_y, progress_width, bar_height, 15)
        ctx.set_source_rgb(1, 0.5, 0)  # Orange
        ctx.fill()
        
        # Chain emoji
        draw_text(ctx, (center_x, center_y - 100), (1, 1, 1), 48, "⛓️",
                 center=(center_x, center_y - 100))
        
        # Progress percentage
        draw_text(ctx, (center_x, center_y), (1, 1, 1), 32, 
                 f"{data.completion_percentage:.1f}%",
                 center=(center_x, center_y))
        
        # Days remaining
        draw_text(ctx, (center_x, center_y + 40), (0.8, 0.8, 0.8), 20,
                 f"{data.estimated_days} days left",
                 center=(center_x, center_y + 40))
        
        # Blocks remaining
        draw_text(ctx, (center_x, center_y + 70), (0.6, 0.6, 0.6), 16,
                 f"{data.blocks_remaining:,} blocks",
                 center=(center_x, center_y + 70))
        
        return surface


class ETFRenderer:
    """Renders ETF data stickers."""
    
    @staticmethod
    def render(etf_data: List[ETFData]) -> cairo.ImageSurface:
        """Render ETF overview sticker."""
        surface, ctx = create_surface()
        
        # Load bank SVG
        bank_svg = load_svg("bank.svg")
        ctx.set_source_surface(bank_svg, 20, 20)
        ctx.paint()
        
        # Title
        draw_text(ctx, (50, 50), (1, 1, 1), 32, "BTC ETFs")
        
        # Show top 5 ETFs
        y_offset = 100
        for i, etf in enumerate(etf_data[:5]):
            color = get_color_for_value(etf.change_percent)
            
            # Symbol and price
            symbol_text = f"{etf.symbol}: ${etf.price:.2f}"
            draw_text(ctx, (50, y_offset), (1, 1, 1), 18, symbol_text)
            
            # Change
            change_text = f"{etf.change_percent:+.1f}%"
            draw_text(ctx, (350, y_offset), color, 18, change_text)
            
            # Market cap
            if etf.market_cap > 0:
                mcap_text = format_large_number(etf.market_cap)
                draw_text(ctx, (450, y_offset), (0.7, 0.7, 0.7), 14, mcap_text)
            
            y_offset += 35
        
        return surface
