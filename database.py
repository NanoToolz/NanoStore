"""NanoStore database module — aiosqlite, all tables, all queries."""

import json
import logging
from datetime import datetime
from typing import Any, Optional

import aiosqlite

from config import DB_PATH

logger = logging.getLogger(__name__)

_db: Optional[aiosqlite.Connection] = None


async def get_db() -> aiosqlite.Connection:
    """Get or create DB connection."""
    global _db
    if _db is None:
        _db = await aiosqlite.connect(DB_PATH)
        _db.row_factory = aiosqlite.Row
        await _db.execute("PRAGMA journal_mode=WAL")
        await _db.execute("PRAGMA foreign_keys=ON")
    return _db


def _row_to_dict(row) -> dict:
    """Convert aiosqlite.Row to dict."""
    if row is None:
        return None
    return dict(row)


def _rows_to_list(rows) -> list:
    """Convert list of rows to list of dicts."""
    return [dict(r) for r in rows]


# ======================== INIT ========================

async def init_db() -> None:
    """Create all tables."""
    db = await get_db()

    await db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id     INTEGER PRIMARY KEY,
            full_name   TEXT DEFAULT '',
            username    TEXT DEFAULT '',
            balance     REAL DEFAULT 0.0,
            banned      INTEGER DEFAULT 0,
            joined_at   TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS categories (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            emoji       TEXT DEFAULT '',
            image_id    TEXT DEFAULT NULL,
            sort_order  INTEGER DEFAULT 0,
            active      INTEGER DEFAULT 1,
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS products (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            name        TEXT NOT NULL,
            description TEXT DEFAULT '',
            price       REAL NOT NULL DEFAULT 0,
            stock       INTEGER DEFAULT -1,
            image_id    TEXT DEFAULT NULL,
            active      INTEGER DEFAULT 1,
            created_at  TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS product_faqs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id  INTEGER NOT NULL,
            question    TEXT NOT NULL,
            answer      TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS product_media (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id  INTEGER NOT NULL,
            media_type  TEXT NOT NULL DEFAULT 'file',
            file_id     TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS cart (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            product_id  INTEGER NOT NULL,
            quantity    INTEGER DEFAULT 1,
            added_at    TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS orders (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL,
            items_json      TEXT DEFAULT '[]',
            total           REAL DEFAULT 0,
            status          TEXT DEFAULT 'pending',
            payment_status  TEXT DEFAULT 'unpaid',
            payment_method_id INTEGER DEFAULT NULL,
            payment_proof_id  INTEGER DEFAULT NULL,
            coupon_code     TEXT DEFAULT NULL,
            created_at      TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS payment_methods (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name    TEXT NOT NULL,
            details TEXT DEFAULT '',
            emoji   TEXT DEFAULT '',
            active  INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS payment_proofs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            order_id    INTEGER NOT NULL,
            method_id   INTEGER DEFAULT 0,
            file_id     TEXT NOT NULL,
            status      TEXT DEFAULT 'pending_review',
            reviewed_by INTEGER DEFAULT NULL,
            admin_note  TEXT DEFAULT NULL,
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS coupons (
            code            TEXT PRIMARY KEY,
            discount_percent INTEGER DEFAULT 0,
            max_uses        INTEGER DEFAULT 0,
            used_count      INTEGER DEFAULT 0,
            active          INTEGER DEFAULT 1,
            created_at      TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS settings (
            key     TEXT PRIMARY KEY,
            value   TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS force_join_channels (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id  TEXT NOT NULL,
            name        TEXT NOT NULL,
            invite_link TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS tickets (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            subject     TEXT NOT NULL,
            message     TEXT DEFAULT '',
            status      TEXT DEFAULT 'open',
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS ticket_replies (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id   INTEGER NOT NULL,
            sender      TEXT DEFAULT 'user',
            message     TEXT NOT NULL,
            created_at  TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS action_logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            action      TEXT NOT NULL,
            user_id     INTEGER DEFAULT 0,
            details     TEXT DEFAULT '',
            created_at  TEXT DEFAULT (datetime('now'))
        );
    """)

    # Default settings
    defaults = {
        "currency": "Rs",
        "bot_name": "NanoStore",
        "welcome_text": "Welcome to NanoStore!",
        "welcome_image_id": "",
        "min_order": "0",
    }
    for key, value in defaults.items():
        await db.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
            (key, value),
        )

    await db.commit()
    logger.info("Database initialized with all tables.")


# ... rest of database.py unchanged ...
