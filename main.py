"""Daily stock news email digest.

Fetches yesterday's company news (Finnhub) and daily % price change (yfinance)
for a list of tickers, builds a simple HTML email, and sends it via Gmail SMTP.
Runs on weekdays via GitHub Actions.
"""
