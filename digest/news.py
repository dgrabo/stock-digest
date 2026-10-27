"""Company news from Finnhub."""

from datetime import datetime, time, timedelta

import requests

from . import config

FINNHUB_URL = "https://finnhub.io/api/v1/company-news"


def news_window(now=None):
    """Return (start, end) datetimes in Zagreb time covering the previous calendar day.

    start is yesterday 00:00, end is today 00:00 (exclusive). The digest runs daily,
    so each day's news appears exactly once, weekends included.
    """
    now = now or datetime.now(config.TZ)
    today = now.astimezone(config.TZ).date()
    # Build from dates (not by subtracting 24h) so DST-change days stay midnight-to-midnight.
    start = datetime.combine(today - timedelta(days=1), time(), config.TZ)
    end = datetime.combine(today, time(), config.TZ)
    return start, end


def fetch_news(ticker):
    start, end = news_window()
    params = {
        "symbol": ticker,
        # Finnhub filters by date only, so query a slightly wider range
        # and filter precisely on each article's timestamp below.
        "from": (start - timedelta(days=1)).date().isoformat(),
        "to": end.date().isoformat(),
        "token": config.FINNHUB_KEY,
    }
    resp = requests.get(FINNHUB_URL, params=params, timeout=config.REQUEST_TIMEOUT)
    resp.raise_for_status()

    start_ts, end_ts = start.timestamp(), end.timestamp()
    seen = set()
    articles = []
    for item in resp.json():
        ts = item.get("datetime", 0)
        headline = (item.get("headline") or "").strip()
        if not (start_ts <= ts < end_ts) or not headline:
            continue
        key = headline.lower()
        if key in seen:
            continue
        seen.add(key)
        articles.append({
            "headline": headline,
            "source": item.get("source", ""),
            "url": item.get("url", ""),
            "datetime": ts,
            "summary": item.get("summary", ""),
        })

    articles.sort(key=lambda a: a["datetime"], reverse=True)
    return articles[:config.MAX_HEADLINES]
