#!/usr/bin/python
import cairocffi as cairo
import pangocairocffi as pangocairo
import pangocffi as pango
from cairosvg.parser import Tree
from cairosvg.surface import PNGSurface, SVGSurface
from datetime import datetime, time, timedelta, timezone

import telebot

WIDTH, HEIGHT = 512, 512

def create_pack(png_file, user_id, name, bot):
    sticker = open(png_file, "rb")
    response = bot.create_new_sticker_set(
        user_id,
        name=f"{name}_by_{bot.get_me().username}",
        title=f"Stickers {name}",
        png_sticker=sticker,
        emojis=["😱"],
        tgs_sticker=None,
    )
    print(response)

def load_svg(url) -> cairo.ImageSurface:
    return PNGSurface(Tree(url=f"./assets/{url}"), None, 1).cairo


def draw_text(ctx, pos, c, s, text, center=None):
    PANGO_SCALE = pango.units_from_double(1)

    layout = pangocairo.create_layout(ctx)

    desc = pango.FontDescription()
    desc.size = s * PANGO_SCALE
    desc.family = "Comfortaa"
    layout.font_description = desc

    layout.apply_markup(f"{text}")
    layout.alignment = pango.Alignment.CENTER
    ink_box, log_box = layout.get_extents()

    text_width, text_height = (
        1.0 * log_box.width / PANGO_SCALE,
        1.0 * log_box.height / PANGO_SCALE,
    )
    if center:
        ctx.move_to(
            WIDTH / 2 - text_width / 2 + pos[0], HEIGHT / 2 - text_height / 2 + pos[1]
        )
    else:
        ctx.move_to(*pos)

    ctx.set_source_rgb(*c)
    pangocairo.show_layout(ctx, layout)



def draw_triagle(cr, pos, v):
    c = (0.0, 1.0, 0.0)
    if v < 0:
        c = (1.0, 0, 0)

    cr.save()
    cr.translate(*pos)
    cr.set_source_rgb(*c)

    if v < 0:
        cr.move_to(0, 0)
        cr.line_to(18, 0)
        cr.line_to(9, 10)
        cr.line_to(0, 0)
    else:
        cr.move_to(9, 0)
        cr.line_to(18, 10)
        cr.line_to(0, 10)
        cr.line_to(9, 0)
    # cr.stroke()
    # cr.stroke_preserve()
    cr.fill()

    draw_text(cr, (30, -15), c, 20, str(round(abs(v), 2)) + "%")
    cr.restore()


def update_currency(c):
    c = int(round(c))
    currency ="{:,}".format(c)
    return currency.replace(",", " ").ljust(10)


def update_btc(c):
    currency = "{:,<.4f}".format(c)
    return currency.replace(",", " ")


def fngColouring(c):
    if c >= 90:
        color = (0.396, 0.776, 0.298)
    if c < 90:
        color = (0.475, 0.824, 0.235)
    if c <= 75:
        color = (0.608, 0.745, 0.267)
    if c <= 63:
        color = (0.776, 0.749, 0.133)
    if c <= 54:
        color = (0.875, 0.808, 0.376)
    if c <= 46:
        color = (0.847, 0.737, 0.349)
    if c <= 35:
        color = (0.89, 0.616, 0.392)
    if c <= 25:
        color = (0.82, 0.451, 0.224)
    if c <= 10:
        color = (0.718, 0.302, 0.204)
    return color

def map_interval(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def is_us_market_open_now():
    # US market hours in Eastern Time (ET)
    market_open = time(9, 30, 0)   # 9:30 AM
    market_close = time(16, 0, 0)  # 4:00 PM

    # Current time in UTC
    now_utc = datetime.now(timezone.utc)

    # Convert current UTC time to Eastern Time (ET)
    # Eastern Time is UTC-5 (standard time) or UTC-4 (daylight saving time)
    # Note: This approach does not account for daylight saving time changes
    offset = -5 if now_utc.month < 3 or now_utc.month > 11 else -4
    now_et = now_utc.replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=offset))).time()

    # Check if current ET time is within US market hours
    return market_open <= now_et <= market_close


if __name__ == "__main__":
    from os import getenv

    USER_ID = getenv("TG_USER_ID")
    PACK_NAME = getenv("TG_PACK_NAME")
    TELEGRAM_BOT_TOKEN = getenv("TG_BOT_TOKEN")

    bot = telebot.TeleBot(
        TELEGRAM_BOT_TOKEN, parse_mode=None
    )

    create_pack("example.png", USER_ID, PACK_NAME, bot)
