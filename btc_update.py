#!/usr/bin/python
import sys

import cairocffi as cairo
import io
import math
import requests
from datetime import datetime
import yfinance as yf
from time import sleep

import telebot

from utils import *

# Globals
FNG_API_URL = "https://api.alternative.me/fng/"
AUD_API_URL = "https://www.coinspot.com.au/pubapi/v2/latest"
BTC_API_URL = "https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT"
ETHBTC_API_URL = "https://api.binance.com/api/v3/ticker/24hr?symbol=ETHBTC"
PRICE_API_URL = "https://api.binance.com/api/v3/ticker/price"
RUB_PRICE_API_URL = "https://blockchain.info/ticker"
BLOCK_HEIGHT_URL = "https://mempool.space/api/blocks/tip/height"

date_now = datetime.utcnow()
resp = requests.get(url=BLOCK_HEIGHT_URL)
BTC_HEIGHT = int(resp.text)

def load_fear():
    resp = requests.get(url=FNG_API_URL)
    j = resp.json()
    print(j["data"][0])
    data = j["data"][0]
    value = int(data["value"])
    value_class = data["value_classification"]
    timestamp = date_now.strftime("%Y-%m-%d")
    return value, value_class, timestamp


def load_halving():
    halving = 210000
    blocks_to_halving = (210000 - BTC_HEIGHT % halving)
    done_percent = int((1 - blocks_to_halving / halving)*100)
    days_to_halving = int(blocks_to_halving / 144)
    timestamp = date_now.strftime("%Y-%m-%d")
    print("{} - {}, {}, {}".format(blocks_to_halving, done_percent, days_to_halving, timestamp))
    return done_percent, blocks_to_halving, days_to_halving, timestamp


def draw_fear_gear():
    value, value_class, timestamp = load_fear()

    surface2 = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
    cr2 = cairo.Context(surface2)

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
    cr = cairo.Context(surface)

    cr.rectangle(0, 0, WIDTH, HEIGHT)
    cr.set_source_rgb(0, 0, 0)
    cr.fill()

    draw_arc(cr, value)

    draw_text(cr, (62, 76), (1, 1, 1), 24, "<b>" + value_class + "</b>")
    draw_text(
        cr,
        (150, -125),
        fngColouring(value),
        54,
        "<b>" + str(value) + "</b>",
        center=True,
    )
    draw_text(cr, (0, 150), (1, 1, 1), 20, "<b>Fear &amp; Greed Index</b>", center=True)
    draw_text(cr, (0, 190), (1, 1, 1), 16, "<b>" + timestamp + "</b>", center=True)

    print(fngColouring(value))
    cr2.set_source_surface(surface, 1, 1)

    draw_arrow(cr, value)

    w = 472 - 60
    h = 448 - 60
    print((WIDTH - w) / 2, (HEIGHT - h) / 2, w, h)
    cr2.set_line_width(60)
    cr2.rectangle((WIDTH - w) / 2, (HEIGHT - h) / 2, w, h)
    cr2.set_line_join(cairo.LINE_JOIN_ROUND)
    cr2.stroke_preserve()

    cr2.clip()
    cr2.paint()

    return surface2

def draw_halving_gear():
    done_percent, blocks_to_halving, days_to_halving, timestamp = load_halving()
    color = (247 / 255.0, 69 / 255.0, 226 / 255.0)

    surface2 = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
    cr2 = cairo.Context(surface2)

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
    cr = cairo.Context(surface)

    cr.rectangle(0, 0, WIDTH, HEIGHT)
    cr.set_source_rgb(0, 0, 0)
    cr.fill()

    draw_arc(cr, done_percent, color)

    draw_text(cr, (62, 76), (1, 1, 1), 24, "<b> Blocks " + str(blocks_to_halving) + "</b>")
    draw_text(
        cr,
        (150, -125),
        color,
        42,
        "<b>" + str(done_percent) + "%</b>",
        center=True,
    )
    draw_text(cr, (0, 150), (1, 1, 1), 20, "<b>≅" + str(days_to_halving) + " days</b>", center=True)
    draw_text(cr, (0, 190), (1, 1, 1), 16, "<b>" + timestamp + "</b>", center=True)

    cr2.set_source_surface(surface, 1, 1)

    draw_arrow(cr, done_percent, color)

    w = 472 - 60
    h = 448 - 60
    print((WIDTH - w) / 2, (HEIGHT - h) / 2, w, h)
    cr2.set_line_width(60)
    cr2.rectangle((WIDTH - w) / 2, (HEIGHT - h) / 2, w, h)
    cr2.set_line_join(cairo.LINE_JOIN_ROUND)
    cr2.stroke_preserve()

    cr2.clip()
    cr2.paint()

    return surface2

def draw_arc(cr, value, color=None):
    # main arc
    cr.set_source_rgb(45 / 255.0, 7 / 255.0, 1 / 255.0)
    cr.set_line_width(20)
    # cr.set_line_join(cairo.LINE_JOIN_ROUND)
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.arc(WIDTH / 2, HEIGHT / 2, 100, 3 * math.pi / 4, math.pi / 4)
    cr.stroke()
    # cope arc
    if color:
        cr.set_source_rgb(*color)
    else:
        cr.set_source_rgb(*fngColouring(value))
    cr.set_line_width(20)
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    angle = map_interval(value, 0.0, 100.0, 0, 3 * math.pi / 2)
    cr.arc(
        WIDTH / 2, HEIGHT / 2, 100, 3 * math.pi / 4, angle + math.pi / 2 + math.pi / 4
    )
    cr.stroke()


def draw_arrow(cr, v, color=None):
    cr.move_to(WIDTH / 2 + 10, HEIGHT / 2)
    if color:
        cr.set_source_rgb(*color)
    else:
        cr.set_source_rgb(*fngColouring(v))
    cr.set_line_width(1)
    cr.arc(WIDTH / 2, HEIGHT / 2, 10, 0, math.pi * 2)
    angle = map_interval(v, 0.0, 100.0, 0, 3 * math.pi / 2)
    cr.move_to(
        WIDTH / 2 - 10 * math.cos(angle - math.pi / 2 - math.pi / 4),
        HEIGHT / 2 - 10 * math.sin(angle - math.pi / 2 - math.pi / 4),
    )
    cr.line_to(
        WIDTH / 2 - 50 * math.cos(angle - math.pi / 4),
        HEIGHT / 2 - 50 * math.sin(angle - math.pi / 4),
    )
    cr.line_to(
        WIDTH / 2 + 10 * math.cos(angle - math.pi / 2 - math.pi / 4),
        HEIGHT / 2 + 10 * math.sin(angle - math.pi / 2 - math.pi / 4),
    )
    cr.stroke_preserve()
    cr.fill()


fear_png = draw_fear_gear()
fear_png.write_to_png("fear.png")

halving_png = draw_halving_gear()
halving_png.write_to_png("halving.png")

def load_btc():
    out = {}
    resp = requests.get(url=AUD_API_URL)
    j = resp.json()
    out["btc_aud_price"] = next(
        (
            update_currency(float(v["last"]))
            for k, v in j["prices"].items()
            if k == "btc"
        ),
        None,
    )
    out["eth_aud_price"] = next(
        (
            update_currency(float(v["last"]))
            for k, v in j["prices"].items()
            if k == "eth"
        ),
        None,
    )

    resp = requests.get(url=BTC_API_URL)
    j = resp.json()
    # print(j)
    out["btc_usd_price"] = update_currency(float(j["lastPrice"]))
    out["btc_percent"] = float(j["priceChangePercent"])

    resp = requests.get(url=ETHBTC_API_URL)
    j = resp.json()
    # print(j)
    out["eth_btc_price"] = update_btc(float(j["lastPrice"]))
    out["eth_percent"] = float(j["priceChangePercent"])

    resp = requests.get(url=PRICE_API_URL)
    j = resp.json()
    out["btc_eur_price"] = next(
        (
            update_currency(float(item["price"]))
            for item in j
            if item["symbol"] == "BTCEUR"
        ),
        None,
    )
    out["btc_uah_price"] = next(
        (
            update_currency(float(item["price"]))
            for item in j
            if item["symbol"] == "BTCUAH"
        ),
        None,
    )

    out["eth_usd_price"] = next(
        (
            update_currency(float(item["price"]))
            for item in j
            if item["symbol"] == "ETHUSDT"
        ),
        None,
    )
    out["eth_eur_price"] = next(
        (
            update_currency(float(item["price"]))
            for item in j
            if item["symbol"] == "ETHEUR"
        ),
        None,
    )
    out["eth_rub_price"] = next(
        (
            update_currency(float(item["price"]))
            for item in j
            if item["symbol"] == "ETHRUB"
        ),
        None,
    )
    out["eth_uah_price"] = next(
        (
            update_currency(float(item["price"]))
            for item in j
            if item["symbol"] == "ETHUAH"
        ),
        None,
    )

    resp = requests.get(url=RUB_PRICE_API_URL)
    j = resp.json()
    out["btc_rub_price"] = update_currency(float(j["RUB"]["last"]))

    out["btc_height"] = str(BTC_HEIGHT)
    return out


def load_etf():
    out = {}
    etfs = {
        # Asset per share may be n/a for some etfs
        "BITB": 0.009823183,
        "HODL": 0.001132,
        "GBTC": 0.00089404,
        "FBTC": 0.00896861,
        "IBIT": 0.00498008,
        "ARKB": 0.061728395,
        #"BTCO": 1,
        #"BTCW": 1,
        #"BRRR": 1,
        #"PBTC": 1,
    }

    tickers = yf.Tickers(' '.join(etfs.keys()))

    for t in etfs.keys():
        try:
            etf = tickers.tickers[t]
            if is_us_market_open_now() and etf.info.get("bid") and etf.info.get("ask") and etf.info.get("open"):
                out[t] =((etf.info.get("bid") + etf.info.get("ask")) * 0.5 - etf.info.get("open"))/etf.info.get("open")*100.
            elif not is_us_market_open_now() and etf.info.get("close"):
                out[t] = (etf.info.get("close") - etf.info.get("previousClose")) / etf.info.get("close") * 100.
            else:
                out[t] = (etf.info.get("open") - etf.info.get("previousClose")) / etf.info.get("open") * 100.
        except Exception as etf_exception:
            raise etf_exception

    return out


def draw_btc_price(data):
    surface2 = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
    cr2 = cairo.Context(surface2)

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
    cr = cairo.Context(surface)

    r2 = cairo.LinearGradient(270.7, 129.3, 129.3, 270.7)

    r2.add_color_stop_rgb(0, 254 / 255.0, 67 / 255.0, 0)
    r2.add_color_stop_rgb(1, 255 / 255.0, 109 / 255.0, 0)

    cr.set_source(r2)
    cr.rectangle(0, 0, WIDTH, HEIGHT)
    cr.fill()

    cr.save()
    cr.translate(WIDTH / 2 + 20, 0)
    btc = load_svg("bitcoin.svg")
    cr.set_source_surface(btc)
    cr.rectangle(0, 0, WIDTH, HEIGHT)
    cr.fill()
    cr.restore()

    cr.rectangle(0, HEIGHT - 180, WIDTH, HEIGHT)
    cr.set_source_rgb(0, 0, 0)
    cr.fill()

    dt = date_now.strftime("%H:%M %a, %d.%m.%y (UTC%z)")
    draw_text(cr, (70, 360), (1, 1, 1), 20, "<b>BTC</b>  Bitcoin")
    draw_text(cr, (70, 360 + 40), (1, 1, 1), 16, dt)
    draw_text(cr, (70, 360 + 70), (1, 1, 1), 16, data["btc_height"])

    draw_text(cr, (70, 65), (1, 1, 1), 50, "<b>$" + data["btc_usd_price"] + "</b>")
    draw_text(cr, (70, 65 + 80), (1, 1, 1), 25, data["btc_eur_price"])
    draw_text(cr, (240, 65 + 80), (1, 1, 1), 25, "€")

    draw_text(
        cr,
        (70, 65 + 80 + 25 + 15),
        (1, 1, 1),
        25,
        data["btc_aud_price"],
    )
    draw_text(
        cr,
        (240, 65 + 80 + 25 + 15),
        (1, 1, 1),
        25,
        "$A",
    )
    draw_text(cr, (70, 65 + 80 + 25 * 2 + 15 * 2), (1, 1, 1), 25, data["btc_uah_price"])
    draw_text(cr, (240, 65 + 80 + 25 * 2 + 15 * 2), (1, 1, 1), 25, "₴")
    draw_text(cr, (70, 65 + 80 + 25 * 3 + 15 * 3), (1, 1, 1), 25, data["btc_rub_price"])
    draw_text(cr, (240, 65 + 80 + 25 * 3 + 15 * 3), (1, 1, 1), 25, "₽")

    draw_triagle(cr, (350, 375), data["btc_percent"])

    cr2.set_source_surface(surface, 1, 1)

    w = 472 - 60
    h = 448 - 60
    cr2.set_line_width(60)
    cr2.rectangle((WIDTH - w) / 2, (HEIGHT - h) / 2, w, h)
    cr2.set_line_join(cairo.LINE_JOIN_ROUND)
    cr2.stroke_preserve()

    cr2.clip()
    cr2.paint()

    return surface2


def draw_etf_price(data):
    surface2 = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
    cr2 = cairo.Context(surface2)

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
    cr = cairo.Context(surface)

    r2 = cairo.LinearGradient(270.7, 129.3, 129.3, 270.7)

    r2.add_color_stop_rgb(0, 72 / 255.0, 78 / 255.0, 83 / 255.0)
    r2.add_color_stop_rgb(1, 91 / 255.0, 95 / 255.0, 100 / 255.0)

    cr.set_source(r2)
    cr.rectangle(0, 0, WIDTH, HEIGHT)
    cr.fill()

    cr.save()
    cr.translate(WIDTH / 2 + 50, 50)
    btc = load_svg("bank.svg")
    cr.set_source_surface(btc)
    cr.rectangle(0, 0, WIDTH, HEIGHT)
    cr.fill()
    cr.restore()

    cr.rectangle(0, HEIGHT - 180, WIDTH, HEIGHT)
    cr.set_source_rgb(0, 0, 0)
    cr.fill()

    space = 0
    for ticker, delta in data.items():
        draw_text(cr, (70, 65 + space), (1, 1, 1), 20, ticker)
        draw_triagle(cr, (70 + 110, 80 + space), delta, True)
        space += 40

    status = "Closed 🔴"
    if is_us_market_open_now():
        status = "Open 🟢"

    draw_text(cr, (70, 360), (1, 1, 1), 20, "<b>ETF</b>  Bitcoin, spot")
    dt = date_now.strftime("%H:%M %a, %d.%m.%y (UTC%z)")
    draw_text(cr, (70, 360 + 40), (1, 1, 1), 16, dt + " " + status )
    draw_text(cr, (70, 360 + 70), (1, 1, 1), 16, "🇺🇸")

    cr2.set_source_surface(surface, 1, 1)

    w = 472 - 60
    h = 448 - 60
    cr2.set_line_width(60)
    cr2.rectangle((WIDTH - w) / 2, (HEIGHT - h) / 2, w, h)
    cr2.set_line_join(cairo.LINE_JOIN_ROUND)
    cr2.stroke_preserve()

    cr2.clip()
    cr2.paint()

    return surface2


def draw_eth_price(data):
    # value, value_class, timestamp = load_fear()

    surface2 = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
    cr2 = cairo.Context(surface2)

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
    cr = cairo.Context(surface)

    r2 = cairo.LinearGradient(270.7, 129.3, 129.3, 270.7)

    r2.add_color_stop_rgb(0, 72 / 255.0, 78 / 255.0, 83 / 255.0)
    r2.add_color_stop_rgb(1, 91 / 255.0, 95 / 255.0, 100 / 255.0)

    cr.set_source(r2)
    cr.rectangle(0, 0, WIDTH, HEIGHT)
    cr.fill()

    cr.save()
    cr.translate(WIDTH / 2 + 20, 0)
    eth = load_svg("ethereum.svg")
    cr.set_source_surface(eth)
    cr.rectangle(0, 0, WIDTH, HEIGHT)
    cr.fill()
    cr.restore()

    cr.rectangle(0, HEIGHT - 180, WIDTH, HEIGHT)
    cr.set_source_rgb(0, 0, 0)
    cr.fill()

    dt = date_now.strftime("%H:%M %a, %d.%m.%y (UTC%z)")

    draw_text(cr, (70, 360), (1, 1, 1), 20, "<b>ETH</b>  Ethereum")
    draw_triagle(cr, (350, 375), data["eth_percent"])
    draw_text(cr, (70, 360 + 40), (1, 1, 1), 16, dt)
    draw_text(cr, (70, 360 + 70), (1, 1, 1), 16, "💩")

    draw_text(cr, (70, 65), (1, 1, 1), 50, "<b>" + data["eth_btc_price"] + " BTC</b>")
    draw_text(cr, (70, 65 + 90), (1, 1, 1), 25, data["eth_usd_price"])
    draw_text(cr, (230, 65 + 90), (1, 1, 1), 25, "$")
    draw_text(cr, (70, 65 + 90 + 25 + 15), (1, 1, 1), 25, data["eth_eur_price"])
    draw_text(cr, (230, 65 + 90 + 25 + 15), (1, 1, 1), 25, "€")
    draw_text(cr, (70, 65 + 90 + 25 * 2 + 15 * 2), (1, 1, 1), 25, data["eth_uah_price"])
    draw_text(cr, (230, 65 + 90 + 25 * 2 + 15 * 2), (1, 1, 1), 25, "₴")
    draw_text(cr, (70, 65 + 90 + 25 * 3 + 15 * 3), (1, 1, 1), 25, data["eth_rub_price"])
    draw_text(cr, (230, 65 + 90 + 25 * 3 + 15 * 3), (1, 1, 1), 25, "₽")

    cr2.set_source_surface(surface, 1, 1)

    w = 472 - 60
    h = 448 - 60
    cr2.set_line_width(60)
    cr2.rectangle((WIDTH - w) / 2, (HEIGHT - h) / 2, w, h)
    cr2.set_line_join(cairo.LINE_JOIN_ROUND)
    cr2.stroke_preserve()

    cr2.clip()
    cr2.paint()

    return surface2


if __name__ == "__main__":
    from os import getenv

    USER_ID = getenv("TG_USER_ID")
    PACK_NAME = getenv("TG_PACK_NAME")
    TELEGRAM_BOT_TOKEN = getenv("TG_BOT_TOKEN")

    bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, parse_mode=None)

    try:
        btc_data = load_btc()
        btc_png = draw_btc_price(btc_data)
        btc_png.write_to_png("btc.png")

        eth_png = draw_eth_price(btc_data)
        eth_png.write_to_png("eth.png")

        etf_data = load_etf()
        etf_png = draw_etf_price(etf_data)
        etf_png.write_to_png("etf.png")

        old_pack = bot.get_sticker_set(PACK_NAME)
        old_emojis = [s.emoji for s in old_pack.stickers]

        files = {
            "💸": "btc.png",
            "💩": "eth.png",
            "🏦": "etf.png",
            "😱": "fear.png",
            "⛓": "halving.png",
            "🙏": f"./assets/donate.png",
        }

        for emoji, png_file in files.items():
            if emoji == "🙏":
                continue
            if emoji == "⛓" and emoji in old_emojis and BTC_HEIGHT % 144 > 2:
                continue
            with open(png_file, "rb") as sticker:
                try:
                    req = bot.add_sticker_to_set(
                        USER_ID,
                        name=PACK_NAME,
                        png_sticker=sticker,
                        emojis=emoji,
                        tgs_sticker=None,
                    )
                    sleep(5)
                    for s in old_pack.stickers:
                        if s.emoji == emoji:
                            req = bot.delete_sticker_from_set(s.file_id)
                    sleep(5)
                except Exception as e:
                    bot.send_message(USER_ID, f"Sticker pack upload is getting rate limited by Telegram: {e}")
                    sleep(55)

    except Exception as e:
        bot.send_message(USER_ID, f"Sticker pack update, exception caught: {e}")