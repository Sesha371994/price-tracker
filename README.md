# Price Tracker — Amazon / Flipkart

Track product prices over time with a Streamlit dashboard.

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
streamlit run dashboard.py
```

This opens a local web dashboard where you can:
- Paste an Amazon or Flipkart product URL to start tracking it
- Set an optional target price for alerts
- Click "Refresh all prices" to re-check every tracked product
- See a price-history line chart for each product

## How it works

- `scraper.py` — fetches the product page with `requests` + `BeautifulSoup`
  and pulls out the name and price using CSS selectors.
- `db.py` — stores products and price history in a local SQLite file
  (`price_tracker.db`, created automatically).
- `dashboard.py` — the Streamlit UI tying it together.

## Features

- **📧 Email alerts** — get emailed when a product hits your target price.
  Set these environment variables before launching (Gmail example):
  ```bash
  export EMAIL_SENDER="youraddress@gmail.com"
  export EMAIL_APP_PASSWORD="your-16-char-app-password"   # Google Account -> Security -> App passwords
  export EMAIL_RECEIVER="whereyouwantalerts@gmail.com"
  ```
  Then run the dashboard or scheduler as normal — alerts fire automatically.

- **⬇️ CSV export** — each tracked product has a "CSV" download button next
  to it in the dashboard, exporting its full price history.

- **🌙 Dark mode** — toggle in the sidebar.

- **⏰ Auto-refresh scheduler** — `scheduler.py` runs independently of the
  dashboard, checking all prices once daily (default 09:00, edit `CHECK_TIME`
  in the file to change) and sending email alerts on target hits:
  ```bash
  python scheduler.py
  ```
  Leave this running in a separate terminal, or set it up as a background
  service (e.g. `nohup python scheduler.py &` on Linux/Mac, or Task
  Scheduler on Windows) so it keeps checking even when the dashboard is closed.

## Important notes

- **Selectors break often.** Amazon and Flipkart change their HTML regularly,
  and both sites actively try to block scrapers. If a price stops showing up,
  open the product page in a browser, inspect the price element, and update
  the CSS selectors in `scraper.py`.
- **Rate limiting.** Don't refresh too frequently — sites may temporarily
  block your IP if you hit them too often. For real automation (e.g. a cron
  job checking hourly), add delays between requests.
- **Terms of service.** Scraping is a gray area legally; this is intended for
  personal, low-volume price tracking, not commercial use or high-frequency
  polling.
- **For production robustness**, consider:
  - Rotating proxies / user agents
  - Using Selenium or Playwright if pages are JavaScript-rendered
  - Official APIs where available (e.g. Amazon Product Advertising API)
  - Sending email/SMS alerts when target price is hit (e.g. via `smtplib` or Twilio)

## Extending

Ideas to build on this:
- Add a scheduler (`schedule` library or a cron job) to auto-refresh daily
- Email/Telegram bot alert when target price is reached
- Support more sites by adding a new `scrape_<site>()` function in `scraper.py`
