"""Turn the report dict into an email subject, HTML body and plain-text body."""

from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from . import config
from .news import news_window

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
COLORS = {"up": "#1a7f37", "down": "#cf222e", "flat": "#57606a"}

_env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(["html"]),
)


def _fmt_date(d):
    # "Tue 27 Oct 2026" -- d.day avoids a zero-padded day (%-d doesn't work on Windows)
    return f"{d:%a} {d.day} {d:%b %Y}"


def _fmt_window(start, end):
    return f"{start:%a %d.%m. %H:%M} – {end:%a %d.%m. %H:%M} ({config.TIMEZONE})"


def subject(now=None):
    now = now or datetime.now(config.TZ)
    return f"Stock digest — {_fmt_date(now)}"


def _context(report, now=None):
    """Shared view model for both HTML and text, so they always show the same content."""
    now = now or datetime.now(config.TZ)
    start, end = news_window(now)
    tickers = []
    counts = {"up": 0, "down": 0, "flat": 0}
    for symbol, data in report.items():
        price = data["price"]
        direction = None
        if price:
            pct = price["change_pct"]
            direction = "up" if pct > 0 else "down" if pct < 0 else "flat"
            counts[direction] += 1
        tickers.append({
            "symbol": symbol,
            "price": price,
            "direction": direction,
            "color": COLORS.get(direction, COLORS["flat"]),
            "error": data["error"],
            "news": [
                {**a, "time": f"{datetime.fromtimestamp(a['datetime'], config.TZ):%d.%m. %H:%M}"}
                for a in data["news"]
            ],
        })

    parts = [f"{n} {label}" for label, n in counts.items() if n]
    no_price = sum(1 for d in report.values() if d["price"] is None)
    if no_price:
        parts.append(f"{no_price} no price")
    return {
        "date": _fmt_date(now),
        "overview": ", ".join(parts) or "No data",
        "window": _fmt_window(start, end),
        "tickers": tickers,
        "generated": f"{now:%d.%m.%Y %H:%M} {config.TIMEZONE}",
    }


def render_html(report, now=None):
    return _env.get_template("email.html").render(**_context(report, now))


def render_text(report, now=None):
    ctx = _context(report, now)
    lines = [f"Stock digest — {ctx['date']}", ctx["overview"], f"News window: {ctx['window']}", ""]
    for t in ctx["tickers"]:
        if t["price"]:
            p = t["price"]
            lines.append(f"{t['symbol']}  {p['last_close']:.2f}  ({p['change_pct']:+.2f}%)")
        else:
            lines.append(t["symbol"])
        if t["error"]:
            lines.append(f"  Error: {t['error']}")
        if not t["news"]:
            lines.append("  No new articles")
        for a in t["news"]:
            lines.append(f"  - {a['headline']} ({a['source']}, {a['time']})")
            if a["url"]:
                lines.append(f"    {a['url']}")
        lines.append("")
    lines.append(f"Data: Finnhub (news), Yahoo Finance (prices). Generated {ctx['generated']}.")
    return "\n".join(lines)
