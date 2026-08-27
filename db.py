import sqlite3
from datetime import datetime

DB_NAME = "price_tracker.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
            site TEXT NOT NULL,
            target_price REAL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            price REAL,
            checked_at TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    """)
    conn.commit()
    conn.close()


def add_product(name, url, site, target_price=None):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO products (name, url, site, target_price) VALUES (?, ?, ?, ?)",
        (name, url, site, target_price),
    )
    conn.commit()
    conn.close()


def get_products():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id, name, url, site, target_price FROM products")
    rows = cur.fetchall()
    conn.close()
    return rows


def delete_product(product_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("DELETE FROM price_history WHERE product_id = ?", (product_id,))
    cur.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()


def add_price_record(product_id, price):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO price_history (product_id, price, checked_at) VALUES (?, ?, ?)",
        (product_id, price, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_price_history(product_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "SELECT price, checked_at FROM price_history WHERE product_id = ? ORDER BY checked_at",
        (product_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_latest_price(product_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "SELECT price, checked_at FROM price_history WHERE product_id = ? ORDER BY checked_at DESC LIMIT 1",
        (product_id,),
    )
    row = cur.fetchone()
    conn.close()
    return row
