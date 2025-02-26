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
    desc.family = "Nunito"
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


def draw_triagle(cr, pos, v, white=False):
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

    if white:
        draw_text(cr, (30, -15), (1, 1, 1), 20, str(round(abs(v), 2)) + "%")
    else:
        draw_text(cr, (30, -15), c, 20, str(round(abs(v), 2)) + "%")
    cr.restore()


def update_currency(c):
    c = int(round(c))
    currency = "{:,}".format(c)
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


def fngTrollColouring(c):
    # Define gradient color points from blue to pinky
    colors = [
        (90, (0.0, 0.749, 1.0)),  # Deep Sky Blue
        (75, (0.529, 0.808, 0.922)),  # Light Sky Blue
        (63, (0.541, 0.169, 0.886)),  # Blue Violet
        (54, (0.58, 0.439, 0.859)),  # Medium Slate Blue
        (46, (0.729, 0.333, 0.827)),  # Medium Purple
        (35, (0.847, 0.529, 0.945)),  # Medium Violet Red
        (25, (1.0, 0.549, 0.776)),  # Hot Pink
        (10, (1.0, 0.607, 0.835)),  # Pink
        (0, (1.0, 0.752, 0.796))  # Light Pink
    ]

    # Find the appropriate color range
    for i in range(len(colors) - 1):
        if c >= colors[i + 1][0]:
            c1, color1 = colors[i]
            c2, color2 = colors[i + 1]
            break
    else:
        # If c is less than the lowest range, use the lowest color
        return colors[-1][1]

    # Linear interpolation
    t = (c - c2) / (c1 - c2)
    color = tuple(color1[j] * (1 - t) + color2[j] * t for j in range(3))

    return color


def greedToTroll(v):
    if v == "Extreme Fear":
        return "Extreme pussies"
    elif v == "Fear":
        return "Little bitches"
    elif v == "Neutral":
        return "Snowflakes"
    elif v == "Greed":
        return "Diversificatoors"
    elif v == "Extreme Greed":
        return "Yolo Degens"
    else:
        return "Trolldicator"


def map_interval(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def is_us_market_open_now():
    # US market hours in Eastern Time (ET)
    market_open = time(9, 30, 0)  # 9:30 AM
    market_close = time(16, 0, 0)  # 4:00 PM

    # Current time in UTC
    now_utc = datetime.now(timezone.utc)

    # Convert current UTC time to Eastern Time (ET)
    # Eastern Time is UTC-5 (standard time) or UTC-4 (daylight saving time)
    # Note: This approach does not account for daylight saving time changes
    offset = -5 if now_utc.month < 3 or now_utc.month > 11 else -4
    now_et = now_utc.replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=offset)))

    if now_et.weekday() > 4:
        return False

    # Check if current ET time is within US market hours
    return market_open <= now_et.time() <= market_close


def is_etf_posting_time():
    # US market hours in Eastern Time (ET)
    market_open = time(9, 30, 0)  # 9:30 AM
    market_close = time(16, 20, 0)  # added 20 min margin to post "closed" market sticker

    # Current time in UTC
    now_utc = datetime.now(timezone.utc)

    # Convert current UTC time to Eastern Time (ET)
    # Eastern Time is UTC-5 (standard time) or UTC-4 (daylight saving time)
    # Note: This approach does not account for daylight saving time changes
    offset = -5 if now_utc.month < 3 or now_utc.month > 11 else -4
    now_et = now_utc.replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=offset)))

    if now_et.weekday() > 4:
        return False

    # Increase interval, once per hour
    if now_utc.minute > 5:
        return False

    # Check if current ET time is within US market hours
    return market_open <= now_et.time() <= market_close


def is_fng_posting_time():
    now_utc = datetime.now(timezone.utc)

    # Leaving just minutes for a while
    if now_utc.minute > 5:
        return False

    return True


def format_large_number(num, decimal_places=1, use_abbr=True):
    if num is None or not isinstance(num, (int, float)):
        return 'N/A'

    abs_num = abs(num)
    sign = '-' if num < 0 else ''

    # Formatting options
    billion = 1_000_000_000
    million = 1_000_000
    billion_label = 'B' if use_abbr else ' billion'
    million_label = 'M' if use_abbr else ' million'

    if abs_num >= billion:
        return f"{sign}${abs_num / billion:.{decimal_places}f}{billion_label}"
    elif abs_num >= million:
        return f"{sign}${abs_num / million:.{decimal_places}f}{million_label}"
    elif abs_num >= 1000:
        return f"{sign}${abs_num:,.0f}"
    else:
        return f"{sign}${abs_num:.{decimal_places}f}"


def sort_by_market_cap(crypto_etfs, reverse=True):
    etf_list = [(symbol, data['cap'], data['price']) for symbol, data in crypto_etfs.items()]
    sorted_etfs = sorted(etf_list, key=lambda x: x[1], reverse=reverse)
    return sorted_etfs


if __name__ == "__main__":
    print(format_large_number(4272921344))  # "$4.3B"
    print(format_large_number(4272921344, 2))  # "$4.27B"
    print(format_large_number(4272921344, 1, False))  # "$4.3 billion"
    print(format_large_number(27500000))  # "$27.5M"
    print(format_large_number(27500000, 2, False))  # "$27.50 million"
    print(format_large_number(8750))

    from os import getenv

    USER_ID = getenv("TG_USER_ID")
    PACK_NAME = getenv("TG_PACK_NAME")
    TELEGRAM_BOT_TOKEN = getenv("TG_BOT_TOKEN")

    bot = telebot.TeleBot(
        TELEGRAM_BOT_TOKEN, parse_mode=None
    )

    create_pack("example.png", USER_ID, PACK_NAME, bot)
