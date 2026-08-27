import io
import streamlit as st
import pandas as pd

from db import (
    init_db,
    add_product,
    get_products,
    delete_product,
    add_price_record,
    get_price_history,
    get_latest_price,
)
from scraper import scrape_product, detect_site
from emailer import send_price_alert, is_email_configured

st.set_page_config(page_title="Price Tracker", layout="wide", page_icon="🛒")
init_db()

# ---------- Dark mode toggle ----------
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

with st.sidebar:
    st.header("⚙️ Settings")
    st.session_state.dark_mode = st.toggle("🌙 Dark mode", value=st.session_state.dark_mode)

    st.divider()
    st.subheader("📧 Email alerts")
    if is_email_configured():
        st.success("Email alerts are configured")
    else:
        st.info(
            "Not configured. Set these environment variables before "
            "launching the app to enable email alerts:\n\n"
            "`EMAIL_SENDER`, `EMAIL_APP_PASSWORD`, `EMAIL_RECEIVER`"
        )

if st.session_state.dark_mode:
    st.markdown(
        """
        <style>
        .stApp { background-color: #0e1117; color: #fafafa; }
        .stApp [data-testid="stMetricValue"] { color: #fafafa; }
        div[data-testid="stExpander"] { background-color: #1a1d24; border-radius: 8px; }
        div[data-testid="stVerticalBlock"] div[data-testid="stMarkdownContainer"] p { color: #e0e0e0; }
        </style>
        """,
        unsafe_allow_html=True,
    )

st.title("🛒 Amazon / Flipkart Price Tracker")

# ---------- Add product ----------
with st.expander("➕ Add a product to track", expanded=True):
    with st.form("add_product_form"):
        url = st.text_input("Product URL (Amazon or Flipkart)")
        target_price = st.number_input("Target price (optional, for alerts)", min_value=0.0, value=0.0)
        submitted = st.form_submit_button("Add & fetch price")

        if submitted and url:
            site = detect_site(url)
            if site == "unknown":
                st.error("URL should be from amazon.* or flipkart.*")
            else:
                with st.spinner("Fetching product info..."):
                    result = scrape_product(url)
                if result.get("error"):
                    st.error(f"Could not fetch product: {result['error']}")
                else:
                    add_product(result["name"], url, site, target_price or None)
                    products = get_products()
                    prod_id = [p[0] for p in products if p[2] == url][0]
                    if result["price"]:
                        add_price_record(prod_id, result["price"])
                    st.success(f"Added: {result['name']} — ₹{result['price']}")
                    st.rerun()

st.divider()

# ---------- Refresh all ----------
col1, col2 = st.columns([1, 5])
with col1:
    if st.button("🔄 Refresh all prices"):
        products = get_products()
        progress = st.progress(0)
        for i, (pid, name, url, site, target) in enumerate(products):
            result = scrape_product(url)
            if result.get("price"):
                add_price_record(pid, result["price"])
                # Check target and send email alert
                if target and result["price"] <= target and is_email_configured():
                    success, message = send_price_alert(name, result["price"], target, url)
                    if success:
                        st.toast(f"📧 Alert sent for {name}!")
            progress.progress((i + 1) / max(len(products), 1))
        st.success("Prices refreshed!")
        st.rerun()

st.divider()

# ---------- Product list ----------
products = get_products()

if not products:
    st.info("No products tracked yet. Add one above to get started.")
else:
    for pid, name, url, site, target in products:
        latest = get_latest_price(pid)
        history = get_price_history(pid)

        cols = st.columns([3, 1, 1, 1, 1])
        cols[0].markdown(f"**{name}**  \n[{url}]({url})  \n`{site}`")

        if latest:
            price, checked_at = latest
            cols[1].metric("Latest price", f"₹{price:,.2f}")
            if target:
                if price <= target:
                    cols[2].success(f"✅ Below target ₹{target:,.2f}")
                else:
                    cols[2].warning(f"Target ₹{target:,.2f}")
        else:
            cols[1].write("No data yet")

        # CSV export button
        if history:
            df = pd.DataFrame(history, columns=["price", "checked_at"])
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            cols[3].download_button(
                "⬇️ CSV",
                data=csv_buffer.getvalue(),
                file_name=f"{name.replace(' ', '_')}_price_history.csv",
                mime="text/csv",
                key=f"csv_{pid}",
            )

        if cols[4].button("🗑️ Remove", key=f"del_{pid}"):
            delete_product(pid)
            st.rerun()

        if len(history) > 1:
            df = pd.DataFrame(history, columns=["price", "checked_at"])
            df["checked_at"] = pd.to_datetime(df["checked_at"])
            st.line_chart(df.set_index("checked_at")["price"])

        st.divider()

st.caption(
    "Note: Amazon/Flipkart change their page structure often and may block "
    "automated requests. If scraping fails, the site likely updated its HTML — "
    "the CSS selectors in scraper.py will need updating. "
    "Run `python scheduler.py` separately for automatic daily price checks + email alerts."
)
