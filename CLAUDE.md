# Stock Digest

A Python script that runs once each weekday via GitHub Actions. It fetches yesterday's company news for a list of tickers from the Finnhub `/company-news` API and gets each ticker's daily % price change with yfinance. Then it builds a simple HTML email and sends it through Gmail SMTP (`smtplib.SMTP_SSL`, port 465, Gmail app password). v1 has no database, no dedupe and no LLM summary.

## Stack
Python 3 · requests · yfinance · python-dotenv · smtplib (stdlib) · GitHub Actions

## File structure (planned)
```
main.py                       # the whole script
requirements.txt              # requests, yfinance, python-dotenv
.env / .env.example           # secrets (local only) / template (committed)
.github/workflows/daily.yml   # scheduled run
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
python main.py                  # run the script
```

## v1 roadmap
- [x] Setup (venv, deps, env files, scaffold)
- [ ] Fetch news (Finnhub) + price change (yfinance)
- [ ] Build & send HTML email
- [ ] Schedule with GitHub Actions (cron runs in UTC: `0 6 * * 1-5` = 07:00 Zagreb in winter, 08:00 in summer)

**v2 ideas:** dedupe, Claude API summary, retries/error handling.

## Rules
- Never commit or print secrets. To check that one is set, print only True/False for whether it's present.
- Keep it a single file until there's a real reason to split.
- Filter news to "yesterday" instead of storing state.

## Working style
I'm learning by building, and I write the core logic myself. Act as a mentor: explain concepts, give hints and small snippets, review my code and point out bugs. Don't write full implementations unless I explicitly ask.
