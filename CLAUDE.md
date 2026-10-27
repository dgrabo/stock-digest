# Stock Digest

A small Python app that runs once a day, including weekends, via GitHub Actions. It fetches the previous calendar day's company news (00:00–24:00 Europe/Zagreb) for a list of tickers from the Finnhub `/company-news` API and gets each ticker's last % price change with yfinance. Then it builds a simple HTML email and sends it through Gmail SMTP (`smtplib.SMTP_SSL`, port 465, Gmail app password). On weekends the price is from the last trading day, and the email labels it (e.g. "Close Fri 24 Oct"). v1 has no database, no dedupe and no LLM summary.

## Stack
Python 3 · requests · yfinance · python-dotenv · Jinja2 · smtplib (stdlib) · GitHub Actions

## File structure
```
main.py                       # entry point: parse args, build report, render, send
digest/
  config.py                   # .env loading, TICKERS, MAX_HEADLINES, TIMEZONE, require()
  news.py                     # fetch_news(ticker), news_window()
  prices.py                   # fetch_price(ticker)
  report.py                   # build_report(tickers), per-ticker try/except
  render.py                   # subject(), render_html(report), render_text(report)
  mailer.py                   # send_email(subject, html, text)
templates/email.html          # Jinja2 email template (inline CSS only; Gmail strips <style>)
requirements.txt              # requests, yfinance, python-dotenv, jinja2
.env / .env.example           # secrets (local only) / template (committed)
preview.html                  # --dry-run output (gitignored)
.github/workflows/daily.yml   # daily scheduled run + manual trigger
```

## Environment variables
| Var | Purpose |
|---|---|
| `FINNHUB_KEY` | Finnhub API key for `/company-news` |
| `GMAIL_USER` | Gmail address that sends the email (SMTP login) |
| `GMAIL_APP_PASSWORD` | Gmail app password (not the normal account password) |
| `EMAIL_TO` | Recipient address for the digest |

Locally these come from `.env`. In GitHub Actions they come from repository secrets (Settings → Secrets and variables → Actions). To update the secrets from `.env`, run `gh secret set -f .env`. `.env` is optional; `load_dotenv()` is a no-op without it.

## Commands
```bash
# activate venv
.venv\Scripts\activate          # Windows (PowerShell/cmd)
source .venv/bin/activate       # macOS/Linux

pip install -r requirements.txt # install deps
python main.py --dry-run        # build report, write preview.html, don't send
python main.py                  # build and send the email

gh workflow run daily.yml       # trigger the GitHub Actions run manually
gh run watch                    # follow the run
```

## Schedule
- Cron: `13 6 * * *`, which runs every day at 06:13 UTC.
- Cron is UTC and ignores DST, so that's 07:13 Zagreb in winter (CET) and 08:13 in summer (CEST).
- The schedule avoids `:00` because GitHub delays or drops many top-of-hour runs.
- You can also trigger a run by hand: Actions tab → "Daily stock digest" → "Run workflow", or `gh workflow run daily.yml`.

## v1 roadmap
- [x] Setup (venv, deps, env files, scaffold)
- [x] Fetch news (Finnhub) + price change (yfinance)
- [x] Build & send HTML email
- [x] Schedule with GitHub Actions (daily, 06:13 UTC)

**v2 ideas:** dedupe, Claude API summary, retries/error handling.

## Rules
- Never commit or print secrets. To check that one is set, print only True/False for whether it's present.
- Keep the `digest/` package flat and small; add a module only when there's a real reason.
- Filter news to the previous calendar day instead of storing state.
- Resolve file paths from `__file__`, not the current working directory.
