# Stock Digest

A small Python app that runs once each weekday via GitHub Actions. It fetches yesterday's company news for a list of tickers from the Finnhub `/company-news` API and gets each ticker's daily % price change with yfinance. Then it builds a simple HTML email and sends it through Gmail SMTP (`smtplib.SMTP_SSL`, port 465, Gmail app password). v1 has no database, no dedupe and no LLM summary.

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
.github/workflows/daily.yml   # scheduled run (planned)
```

## Environment variables
| Var | Purpose |
|---|---|
| `FINNHUB_KEY` | Finnhub API key for `/company-news` |
| `GMAIL_USER` | Gmail address that sends the email (SMTP login) |
| `GMAIL_APP_PASSWORD` | Gmail app password (not the normal account password) |
| `EMAIL_TO` | Recipient address for the digest |

Locally these come from `.env`. In GitHub Actions they come from repository secrets.

## Commands
```bash
# activate venv
.venv\Scripts\activate          # Windows (PowerShell/cmd)
source .venv/bin/activate       # macOS/Linux

pip install -r requirements.txt # install deps
python main.py --dry-run        # build report, write preview.html, don't send
python main.py                  # build and send the email
```

## v1 roadmap
- [x] Setup (venv, deps, env files, scaffold)
- [x] Fetch news (Finnhub) + price change (yfinance)
- [x] Build & send HTML email
- [ ] Schedule with GitHub Actions (cron runs in UTC: `0 6 * * 1-5` = 07:00 Zagreb in winter, 08:00 in summer)

**v2 ideas:** dedupe, Claude API summary, retries/error handling.

## Rules
- Never commit or print secrets. To check that one is set, print only True/False for whether it's present.
- Keep the `digest/` package flat and small; add a module only when there's a real reason.
- Filter news to "yesterday" instead of storing state.
