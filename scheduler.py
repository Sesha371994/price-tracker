"""
Auto-refresh scheduler — runs independently of the Streamlit dashboard,
checking all tracked product prices on a schedule and sending email
alerts when targets are hit.

Run this in the background (separate terminal, or as a system service):
    python scheduler.py

It will check prices immediately on start, then every day at the time
set below (default 09:00).
"""
import time
import schedule

import db
from scraper import scrape_product
from emailer import send_price_alert, is_email_configured

CHECK_TIME = "09:00"  # 24-hour format, runs once daily at this time


def check_all_prices():
    print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Checking all tracked prices...")
    products = db.get_products()

    if not products:
        print("  No products tracked yet.")
        return

    for pid, name, url, site, target in products:
        result = scrape_product(url)
        if result.get("error"):
            print(f"  ❌ {name}: {result['error']}")
            continue

        price = result.get("price")
        if price is None:
            print(f"  ⚠️  {name}: price not found (selectors may need updating)")
            continue

        db.add_price_record(pid, price)
        print(f"  ✅ {name}: ₹{price:,.2f}")

        if target and price <= target:
            if is_email_configured():
                success, message = send_price_alert(name, price, target, url)
                print(f"     🔔 Target hit! {message}")
            else:
                print(f"     🔔 Target hit! (set up email alerts in emailer.py to get notified)")


if __name__ == "__main__":
    db.init_db()
    print(f"Price tracker scheduler started. Checking daily at {CHECK_TIME}.")
    print("Press Ctrl+C to stop.\n")

    # Run once immediately on startup
    check_all_prices()

    schedule.every().day.at(CHECK_TIME).do(check_all_prices)

    while True:
        schedule.run_pending()
        time.sleep(60)
