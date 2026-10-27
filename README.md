# Stock Digest

A daily email with the previous day's company news and the latest price change for a handful of stock tickers. It runs every morning on GitHub Actions.

- **News:** headlines from [Finnhub](https://finnhub.io) for the previous calendar day (Europe/Zagreb), up to 5 per ticker.
- **Prices:** last close and % change from Yahoo Finance (via yfinance). On weekends this is the last trading day's close, and the email says so.
- **Delivery:** an HTML email (with a plain-text fallback) sent through Gmail SMTP.

## Setup

1. **Finnhub key:** sign up at https://finnhub.io and copy your API key. The free tier is enough.
2. **Gmail app password:**
   1. Turn on 2-Step Verification for your Google account.
   2. Create an app password at https://myaccount.google.com/apppasswords.
   3. Use these 16 letters as the password, not your normal Google password.
3. **Local config:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate            # Windows
   source .venv/bin/activate         # macOS/Linux
   pip install -r requirements.txt
   cp .env.example .env              # then fill in the values
   ```
   | Var | What it is |
   |---|---|
   | `FINNHUB_KEY` | Finnhub API key |
   | `GMAIL_USER` | Gmail address that sends the email |
   | `GMAIL_APP_PASSWORD` | The app password from step 2 |
   | `EMAIL_TO` | Where the digest is sent |
4. **GitHub secrets:** add the same four variables under **Settings → Secrets and variables → Actions → New repository secret**. With the GitHub CLI you can instead run `gh secret set -f .env`.

## Commands

```bash
python main.py --dry-run   # build the email and write preview.html (open it in a browser); nothing is sent
python main.py             # build and send the email

gh workflow run daily.yml  # run the GitHub Actions job now
gh run watch               # follow it
```

You can also start a run from GitHub: **Actions → Daily stock digest → Run workflow**.

## Customizing

- **Tickers / headline count:** edit `TICKERS` and `MAX_HEADLINES` in `digest/config.py`.
- **Send time:** edit the `cron` line in `.github/workflows/daily.yml`.
  - Cron is in UTC. The default `13 6 * * *` is 07:13 Zagreb in winter and 08:13 in summer.
  - Avoid minute `0`, because GitHub often delays top-of-hour runs.
  - Scheduled runs can be a few minutes late.
- **Email look:** edit `templates/email.html`. Use inline CSS only, because Gmail strips `<style>` blocks.
