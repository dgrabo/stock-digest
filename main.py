"""Daily stock news email digest.

Fetches yesterday's company news (Finnhub) and daily % price change (yfinance)
for a list of tickers, builds a simple HTML email, and sends it via Gmail SMTP.
Runs on weekdays via GitHub Actions.

Usage:
    python main.py            # build and send
    python main.py --dry-run  # build and write preview.html, don't send
"""

import argparse
import logging
import sys
from pathlib import Path

from digest import config, render
from digest.mailer import send_email
from digest.report import build_report

PREVIEW_PATH = Path(__file__).resolve().parent / "preview.html"

log = logging.getLogger("digest")


def main():
    parser = argparse.ArgumentParser(description="Daily stock news email digest")
    parser.add_argument("--dry-run", action="store_true", help="write preview.html instead of sending")
    args = parser.parse_args()

    # Windows consoles default to a legacy codepage; curly quotes etc. would print as garbage.
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    config.require("FINNHUB_KEY")

    report = build_report(config.TICKERS)
    subject = render.subject()
    html = render.render_html(report)
    text = render.render_text(report)

    if args.dry_run:
        PREVIEW_PATH.write_text(html, encoding="utf-8")
        log.info("Dry run: wrote %s (subject: %s)", PREVIEW_PATH.name, subject)
        print(text)
        return

    send_email(subject, html, text)


if __name__ == "__main__":
    main()
