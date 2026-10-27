"""Settings and secrets, loaded from .env / environment."""

import logging
import os
import sys
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv()

TICKERS = ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN"]
MAX_HEADLINES = 5
TIMEZONE = "Europe/Zagreb"
TZ = ZoneInfo(TIMEZONE)
REQUEST_TIMEOUT = 10

FINNHUB_KEY = os.getenv("FINNHUB_KEY")
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
EMAIL_TO = os.getenv("EMAIL_TO")

log = logging.getLogger(__name__)


def require(*names):
    """Exit with a clear error if any named env var is missing (names only, never values)."""
    missing = [n for n in names if not os.getenv(n)]
    if missing:
        log.error("Missing required env vars: %s. Add them to .env (or the environment).", ", ".join(missing))
        sys.exit(1)
