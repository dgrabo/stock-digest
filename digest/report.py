"""Collect price + news for every ticker into one report dict."""

import logging

from .news import fetch_news
from .prices import fetch_price

log = logging.getLogger(__name__)


def build_report(tickers):
    report = {}
    for ticker in tickers:
        log.info("Fetching %s", ticker)
        result = {"price": None, "news": [], "error": None}
        errors = []
        # Separate try blocks so a price failure doesn't also lose the news.
        try:
            result["price"] = fetch_price(ticker)
        except Exception as e:
            log.warning("%s price failed: %s", ticker, e)
            errors.append(f"price: {e}")
        try:
            result["news"] = fetch_news(ticker)
        except Exception as e:
            log.warning("%s news failed: %s", ticker, e)
            errors.append(f"news: {e}")
        result["error"] = "; ".join(errors) or None
        report[ticker] = result
    return report
