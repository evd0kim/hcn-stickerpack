#!/usr/bin/env python3
"""Base graphics utilities and common drawing functions."""

import math
import cairocffi as cairo
import pangocairocffi as pangocairo
import pangocffi as pango
from cairosvg.parser import Tree
from cairosvg.surface import PNGSurface
from typing import Tuple, Optional

from ..config.settings import DrawingConfig


def load_svg(filename: str) -> cairo.ImageSurface:
    """Load an SVG file from assets directory."""
    return PNGSurface(Tree(url=f"./assets/{filename}"), None, 1).cairo


def create_surface(width: int = None, height: int = None) -> Tuple[cairo.ImageSurface, cairo.Context]:
    """Create a cairo surface and context with standard dimensions."""
    w = width or DrawingConfig.WIDTH
    h = height or DrawingConfig.HEIGHT
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    ctx = cairo.Context(surface)
    return surface, ctx


def draw_text(ctx: cairo.Context, pos: Tuple[float, float], color: Tuple[float, float, float], 
              size: int, text: str, center: Optional[Tuple[float, float]] = None) -> None:
    """Draw text on the cairo context."""
    PANGO_SCALE = pango.units_from_double(1)
    
    layout = pangocairo.create_layout(ctx)
    
    desc = pango.FontDescription()
    desc.size = size * PANGO_SCALE
    desc.family = "Nunito"
    layout.font_description = desc
    
    layout.apply_markup(f"{text}")
    layout.alignment = pango.Alignment.CENTER
    ink_box, log_box = layout.get_extents()
    
    text_width = 1.0 * log_box.width / PANGO_SCALE
    text_height = 1.0 * log_box.height / PANGO_SCALE
    
    if center:
        ctx.move_to(
            center[0] - text_width / 2,
            center[1] - text_height / 2
        )
    else:
        ctx.move_to(pos[0], pos[1])
    
    ctx.set_source_rgb(*color)
    pangocairo.show_layout(ctx, layout)


def draw_triangle(ctx: cairo.Context, pos: Tuple[float, float], 
                 color: Tuple[float, float, float], direction: str = "up") -> None:
    """Draw a triangular arrow indicator."""
    x, y = pos
    size = 10
    
    ctx.set_source_rgb(*color)
    ctx.move_to(x, y)
    
    if direction == "up":
        ctx.line_to(x - size/2, y + size)
        ctx.line_to(x + size/2, y + size)
    else:  # down
        ctx.line_to(x - size/2, y - size)
        ctx.line_to(x + size/2, y - size)
    
    ctx.close_path()
    ctx.fill()


def draw_rounded_rectangle(ctx: cairo.Context, x: float, y: float, width: float, height: float, 
                          radius: float) -> None:
    """Draw a rounded rectangle path."""
    ctx.move_to(x + radius, y)
    ctx.line_to(x + width - radius, y)
    ctx.arc(x + width - radius, y + radius, radius, -math.pi/2, 0)
    ctx.line_to(x + width, y + height - radius)
    ctx.arc(x + width - radius, y + height - radius, radius, 0, math.pi/2)
    ctx.line_to(x + radius, y + height)
    ctx.arc(x + radius, y + height - radius, radius, math.pi/2, math.pi)
    ctx.line_to(x, y + radius)
    ctx.arc(x + radius, y + radius, radius, math.pi, 3*math.pi/2)
    ctx.close_path()


def draw_grid(ctx: cairo.Context) -> None:
    """Draw a grid background."""
    config = DrawingConfig()
    
    for i in range(config.GRID_SIZE_X):
        for j in range(config.GRID_SIZE_Y):
            x = i * (config.CELL_SIZE + config.SPACING)
            y = j * (config.CELL_SIZE + config.SPACING)
            
            draw_rounded_rectangle(ctx, x, y, config.CELL_SIZE, config.CELL_SIZE, config.CORNER_RADIUS)
            ctx.set_source_rgb(0.1, 0.1, 0.1)  # Dark gray
            ctx.fill()


def get_color_for_value(value: float, is_positive_good: bool = True) -> Tuple[float, float, float]:
    """Get color based on positive/negative value."""
    if is_positive_good:
        return (0, 1, 0) if value >= 0 else (1, 0, 0)  # Green/Red
    else:
        return (1, 0, 0) if value >= 0 else (0, 1, 0)  # Red/Green


def format_large_number(num: float, decimals: int = 2) -> str:
    """Format large numbers with appropriate suffixes (K, M, B, T)."""
    abs_num = abs(num)
    sign = "-" if num < 0 else ""
    
    if abs_num >= 1_000_000_000_000:  # Trillion
        return f"{sign}{abs_num/1_000_000_000_000:.{decimals}f}T"
    elif abs_num >= 1_000_000_000:  # Billion
        return f"{sign}{abs_num/1_000_000_000:.{decimals}f}B"
    elif abs_num >= 1_000_000:  # Million
        return f"{sign}{abs_num/1_000_000:.{decimals}f}M"
    elif abs_num >= 1_000:  # Thousand
        return f"{sign}{abs_num/1_000:.{decimals}f}K"
    else:
        return f"{sign}{abs_num:.{decimals}f}"
