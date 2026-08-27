import re
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-IN,en;q=0.9",
}


def detect_site(url: str) -> str:
    if "amazon." in url:
        return "amazon"
    if "flipkart." in url:
        return "flipkart"
    return "unknown"


def clean_price(text: str):
    """Extract a float price from messy text like '₹1,299.00'."""
    if not text:
        return None
    match = re.search(r"[\d,]+(?:\.\d+)?", text.replace(",", ""))
    return float(match.group()) if match else None


def scrape_amazon(url: str):
    resp = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(resp.text, "html.parser")

    name_tag = soup.select_one("#productTitle")
    name = name_tag.get_text(strip=True) if name_tag else "Unknown Product"

    price = None
    for selector in [
        "span.a-price-whole",
        "#priceblock_ourprice",
        "#priceblock_dealprice",
        "span.a-offscreen",
    ]:
        tag = soup.select_one(selector)
        if tag:
            price = clean_price(tag.get_text())
            if price:
                break

    return {"name": name, "price": price}


def scrape_flipkart(url: str):
    resp = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(resp.text, "html.parser")

    name = "Unknown Product"
    for selector in ["span.B_NuCI", "span.VU-ZEz", "h1"]:
        tag = soup.select_one(selector)
        if tag:
            name = tag.get_text(strip=True)
            break

    price = None
    for selector in ["div._30jeq3._16Jk6d", "div._30jeq3", "div.Nx9bqj"]:
        tag = soup.select_one(selector)
        if tag:
            price = clean_price(tag.get_text())
            if price:
                break

    return {"name": name, "price": price}


def scrape_product(url: str):
    site = detect_site(url)
    try:
        if site == "amazon":
            result = scrape_amazon(url)
        elif site == "flipkart":
            result = scrape_flipkart(url)
        else:
            return {"name": None, "price": None, "error": "Unsupported site"}
        result["site"] = site
        return result
    except Exception as e:
        return {"name": None, "price": None, "site": site, "error": str(e)}
