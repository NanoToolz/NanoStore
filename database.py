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

        CREATE TABLE IF NOT EXISTS wallet_topups (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL,
            amount          REAL NOT NULL,
            method_id       INTEGER DEFAULT NULL,
            proof_file_id   TEXT DEFAULT NULL,
            status          TEXT DEFAULT 'pending',
            admin_note      TEXT DEFAULT NULL,
            reviewed_by     INTEGER DEFAULT NULL,
            created_at      TEXT DEFAULT (datetime('now'))
        );
    """)

    # Default settings
    defaults = {
        "currency": "Rs",
        "bot_name": "NanoStore",
        "welcome_text": "Welcome to NanoStore!",
        "welcome_image_id": "",
        "ui_images_enabled": "on",
        "shop_image_id": "",
        "shop_text": "",
        "cart_image_id": "",
        "cart_text": "",
        "orders_image_id": "",
        "orders_text": "",
        "wallet_image_id": "",
        "wallet_text": "",
        "support_image_id": "",
        "support_text": "",
        "admin_panel_image_id": "",
        "admin_panel_text": "",
        "min_order": "0",
        "topup_enabled": "on",
        "topup_min_amount": "100",
        "topup_max_amount": "10000",
        "topup_bonus_percent": "0",
        "auto_delete": "0",
        "restart_notify_users": "off",
        "last_restart_at": "",
    }
    for key, value in defaults.items():
        await db.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
            (key, value),
        )

    await db.commit()
    logger.info("Database initialized with all tables.")


# ======================== USERS ========================

async def ensure_user(user_id: int, full_name: str = "", username: str = "") -> None:
    db = await get_db()
    await db.execute(
        """INSERT INTO users (user_id, full_name, username)
           VALUES (?, ?, ?)
           ON CONFLICT(user_id) DO UPDATE SET
             full_name = excluded.full_name,
             username  = excluded.username""",
        (user_id, full_name, username),
    )
    await db.commit()


async def get_user(user_id: int) -> Optional[dict]:
    db = await get_db()
    cur = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    return _row_to_dict(await cur.fetchone())


async def get_all_users(limit: int = 20) -> list:
    db = await get_db()
    cur = await db.execute(
        "SELECT * FROM users ORDER BY joined_at DESC LIMIT ?", (limit,)
    )
    return _rows_to_list(await cur.fetchall())


async def get_all_user_ids() -> list[int]:
    """Return IDs of all non-banned users for broadcast, etc."""
    db = await get_db()
    cur = await db.execute(
        "SELECT user_id FROM users WHERE banned = 0 ORDER BY joined_at DESC"
    )
    rows = await cur.fetchall()
    return [row["user_id"] for row in rows]


async def get_user_count() -> int:
    db = await get_db()
    cur = await db.execute("SELECT COUNT(*) as cnt FROM users")
    row = await cur.fetchone()
    return row["cnt"] if row else 0


async def is_user_banned(user_id: int) -> bool:
    db = await get_db()
    cur = await db.execute(
        "SELECT banned FROM users WHERE user_id = ?", (user_id,)
    )
    row = await cur.fetchone()
    return bool(row["banned"]) if row else False


async def ban_user(user_id: int) -> None:
    db = await get_db()
    await db.execute("UPDATE users SET banned = 1 WHERE user_id = ?", (user_id,))
    await db.commit()


async def unban_user(user_id: int) -> None:
    db = await get_db()
    await db.execute("UPDATE users SET banned = 0 WHERE user_id = ?", (user_id,))
    await db.commit()


async def get_user_balance(user_id: int) -> float:
    db = await get_db()
    cur = await db.execute(
        "SELECT balance FROM users WHERE user_id = ?", (user_id,)
    )
    row = await cur.fetchone()
    return row["balance"] if row else 0.0


async def update_user_balance(user_id: int, amount: float) -> None:
    db = await get_db()
    await db.execute(
        "UPDATE users SET balance = MAX(0, balance + ?) WHERE user_id = ?",
        (amount, user_id),
    )
    await db.commit()


# ======================== CATEGORIES ========================

async def get_active_categories() -> list:
    db = await get_db()
    cur = await db.execute(
        "SELECT * FROM categories WHERE active = 1 ORDER BY sort_order, id"
    )
    return _rows_to_list(await cur.fetchall())


async def get_all_categories() -> list:
    db = await get_db()
    cur = await db.execute("SELECT * FROM categories ORDER BY sort_order, id")
    return _rows_to_list(await cur.fetchall())


async def get_category(cat_id: int) -> Optional[dict]:
    db = await get_db()
    cur = await db.execute("SELECT * FROM categories WHERE id = ?", (cat_id,))
    return _row_to_dict(await cur.fetchone())


async def add_category(name: str, emoji: str = "", sort_order: int = 0) -> int:
    db = await get_db()
    cur = await db.execute(
        "INSERT INTO categories (name, emoji, sort_order) VALUES (?, ?, ?)",
        (name, emoji, sort_order),
    )
    await db.commit()
    return cur.lastrowid


async def update_category(cat_id: int, **kwargs) -> None:
    db = await get_db()
    fields = []
    values = []
    for k, v in kwargs.items():
        fields.append(f"{k} = ?")
        values.append(v)
    if not fields:
        return
    values.append(cat_id)
    await db.execute(
        f"UPDATE categories SET {', '.join(fields)} WHERE id = ?", values
    )
    await db.commit()


async def delete_category(cat_id: int) -> None:
    db = await get_db()
    await db.execute("DELETE FROM categories WHERE id = ?", (cat_id,))
    await db.commit()


async def get_product_count_in_category(cat_id: int) -> int:
    db = await get_db()
    cur = await db.execute(
        "SELECT COUNT(*) as cnt FROM products WHERE category_id = ?", (cat_id,)
    )
    row = await cur.fetchone()
    return row["cnt"] if row else 0


# ======================== PRODUCTS ========================

async def get_products_by_category(
    cat_id: int, limit: int = 100, offset: int = 0
) -> list:
    db = await get_db()
    cur = await db.execute(
        """SELECT * FROM products
           WHERE category_id = ? AND active = 1
           ORDER BY id LIMIT ? OFFSET ?""",
        (cat_id, limit, offset),
    )
    return _rows_to_list(await cur.fetchall())


async def get_product(prod_id: int) -> Optional[dict]:
    db = await get_db()
    cur = await db.execute("SELECT * FROM products WHERE id = ?", (prod_id,))
    return _row_to_dict(await cur.fetchone())


async def add_product(
    cat_id: int, name: str, description: str = "",
    price: float = 0, stock: int = -1,
) -> int:
    db = await get_db()
    cur = await db.execute(
        """INSERT INTO products (category_id, name, description, price, stock)
           VALUES (?, ?, ?, ?, ?)""",
        (cat_id, name, description, price, stock),
    )
    await db.commit()
    return cur.lastrowid


async def update_product(prod_id: int, **kwargs) -> None:
    db = await get_db()
    fields = []
    values = []
    for k, v in kwargs.items():
        fields.append(f"{k} = ?")
        values.append(v)
    if not fields:
        return
    values.append(prod_id)
    await db.execute(
        f"UPDATE products SET {', '.join(fields)} WHERE id = ?", values
    )
    await db.commit()


async def delete_product(prod_id: int) -> None:
    db = await get_db()
    await db.execute("DELETE FROM products WHERE id = ?", (prod_id,))
    await db.commit()


async def search_products(query: str) -> list:
    db = await get_db()
    pattern = f"%{query}%"
    cur = await db.execute(
        """SELECT * FROM products
           WHERE active = 1 AND (name LIKE ? OR description LIKE ?)
           ORDER BY name LIMIT 50""",
        (pattern, pattern),
    )
    return _rows_to_list(await cur.fetchall())


async def decrement_stock(product_id: int, quantity: int) -> None:
    db = await get_db()
    await db.execute(
        """UPDATE products SET stock = stock - ?
           WHERE id = ? AND stock > 0""",
        (quantity, product_id),
    )
    await db.commit()


# ======================== PRODUCT FAQ & MEDIA ========================

async def get_product_faqs(prod_id: int) -> list:
    db = await get_db()
    cur = await db.execute(
        "SELECT * FROM product_faqs WHERE product_id = ?", (prod_id,)
    )
    return _rows_to_list(await cur.fetchall())


async def add_product_faq(prod_id: int, question: str, answer: str) -> int:
    db = await get_db()
    cur = await db.execute(
        "INSERT INTO product_faqs (product_id, question, answer) VALUES (?, ?, ?)",
        (prod_id, question, answer),
    )
    await db.commit()
    return cur.lastrowid


async def delete_product_faq(faq_id: int) -> None:
    db = await get_db()
    await db.execute("DELETE FROM product_faqs WHERE id = ?", (faq_id,))
    await db.commit()


async def get_product_media(prod_id: int) -> list:
    db = await get_db()
    cur = await db.execute(
        "SELECT * FROM product_media WHERE product_id = ?", (prod_id,)
    )
    return _rows_to_list(await cur.fetchall())


async def add_product_media(prod_id: int, media_type: str, file_id: str) -> int:
    db = await get_db()
    cur = await db.execute(
        "INSERT INTO product_media (product_id, media_type, file_id) VALUES (?, ?, ?)",
        (prod_id, media_type, file_id),
    )
    await db.commit()
    return cur.lastrowid


async def delete_product_media(mid: int) -> None:
    db = await get_db()
    await db.execute("DELETE FROM product_media WHERE id = ?", (mid,))
    await db.commit()


# ======================== CART ========================

async def get_cart(user_id: int) -> list:
    """Get cart items with product details."""
    db = await get_db()
    cur = await db.execute(
        """SELECT c.id as cart_id, c.product_id, c.quantity,
                  p.name, p.price, p.stock, p.image_id
           FROM cart c JOIN products p ON c.product_id = p.id
           WHERE c.user_id = ?
           ORDER BY c.added_at""",
        (user_id,),
    )
    return _rows_to_list(await cur.fetchall())


async def get_cart_count(user_id: int) -> int:
    db = await get_db()
    cur = await db.execute(
        "SELECT COALESCE(SUM(quantity), 0) as cnt FROM cart WHERE user_id = ?",
        (user_id,),
    )
    row = await cur.fetchone()
    return row["cnt"] if row else 0


async def get_cart_total(user_id: int) -> float:
    db = await get_db()
    cur = await db.execute(
        """SELECT COALESCE(SUM(c.quantity * p.price), 0) as total
           FROM cart c JOIN products p ON c.product_id = p.id
           WHERE c.user_id = ?""",
        (user_id,),
    )
    row = await cur.fetchone()
    return row["total"] if row else 0.0


async def get_cart_item(cart_id: int) -> Optional[dict]:
    """Get a single cart item with product info."""
    db = await get_db()
    cur = await db.execute(
        """SELECT c.id as cart_id, c.product_id, c.quantity,
                  p.name, p.price, p.stock
           FROM cart c JOIN products p ON c.product_id = p.id
           WHERE c.id = ?""",
        (cart_id,),
    )
    return _row_to_dict(await cur.fetchone())


async def add_to_cart(user_id: int, product_id: int, quantity: int = 1) -> int:
    """Add product to cart or increment quantity."""
    db = await get_db()
    cur = await db.execute(
        "SELECT id, quantity FROM cart WHERE user_id = ? AND product_id = ?",
        (user_id, product_id),
    )
    existing = await cur.fetchone()

    if existing:
        new_qty = existing["quantity"] + quantity
        await db.execute(
            "UPDATE cart SET quantity = ? WHERE id = ?",
            (new_qty, existing["id"]),
        )
        await db.commit()
        return existing["id"]
    else:
        cur = await db.execute(
            "INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?)",
            (user_id, product_id, quantity),
        )
        await db.commit()
        return cur.lastrowid


async def update_cart_qty(cart_id: int, quantity: int) -> None:
    db = await get_db()
    if quantity <= 0:
        await db.execute("DELETE FROM cart WHERE id = ?", (cart_id,))
    else:
        await db.execute(
            "UPDATE cart SET quantity = ? WHERE id = ?", (quantity, cart_id)
        )
    await db.commit()


async def remove_from_cart_by_id(cart_id: int) -> None:
    db = await get_db()
    await db.execute("DELETE FROM cart WHERE id = ?", (cart_id,))
    await db.commit()


async def clear_cart(user_id: int) -> None:
    db = await get_db()
    await db.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
    await db.commit()


# ======================== ORDERS ========================

async def create_order(user_id: int, items: list, total: float) -> int:
    db = await get_db()
    cur = await db.execute(
        """INSERT INTO orders (user_id, items_json, total)
           VALUES (?, ?, ?)""",
        (user_id, json.dumps(items), total),
    )
    await db.commit()
    return cur.lastrowid


async def get_order(order_id: int) -> Optional[dict]:
    db = await get_db()
    cur = await db.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    return _row_to_dict(await cur.fetchone())


async def get_user_orders(
    user_id: int, limit: int = 10, offset: int = 0
) -> list:
    db = await get_db()
    cur = await db.execute(
        """SELECT * FROM orders WHERE user_id = ?
           ORDER BY created_at DESC LIMIT ? OFFSET ?""",
        (user_id, limit, offset),
    )
    return _rows_to_list(await cur.fetchall())


async def get_user_order_count(user_id: int) -> int:
    db = await get_db()
    cur = await db.execute(
        "SELECT COUNT(*) as cnt FROM orders WHERE user_id = ?", (user_id,)
    )
    row = await cur.fetchone()
    return row["cnt"] if row else 0


async def get_all_orders(limit: int = 20) -> list:
    db = await get_db()
    cur = await db.execute(
        "SELECT * FROM orders ORDER BY created_at DESC LIMIT ?", (limit,)
    )
    return _rows_to_list(await cur.fetchall())


async def update_order(order_id: int, **kwargs) -> None:
    db = await get_db()
    fields = []
    values = []
    for k, v in kwargs.items():
        fields.append(f"{k} = ?")
        values.append(v)
    if not fields:
        return
    values.append(order_id)
    await db.execute(
        f"UPDATE orders SET {', '.join(fields)} WHERE id = ?", values
    )
    await db.commit()


# ======================== COUPONS ========================

async def validate_coupon(code: str) -> Optional[dict]:
    db = await get_db()
    cur = await db.execute(
        """SELECT * FROM coupons
           WHERE code = ? AND active = 1
             AND (max_uses = 0 OR used_count < max_uses)""",
        (code,),
    )
    return _row_to_dict(await cur.fetchone())


async def use_coupon(code: str) -> None:
    db = await get_db()
    await db.execute(
        "UPDATE coupons SET used_count = used_count + 1 WHERE code = ?",
        (code,),
    )
    await db.commit()


async def get_all_coupons() -> list:
    db = await get_db()
    cur = await db.execute("SELECT * FROM coupons ORDER BY created_at DESC")
    return _rows_to_list(await cur.fetchall())


async def create_coupon(
    code: str, discount_percent: int, max_uses: int = 0
) -> None:
    db = await get_db()
    await db.execute(
        """INSERT OR REPLACE INTO coupons (code, discount_percent, max_uses)
           VALUES (?, ?, ?)""",
        (code, discount_percent, max_uses),
    )
    await db.commit()


async def delete_coupon(code: str) -> None:
    db = await get_db()
    await db.execute("DELETE FROM coupons WHERE code = ?", (code,))
    await db.commit()


async def toggle_coupon(code: str) -> None:
    db = await get_db()
    await db.execute(
        "UPDATE coupons SET active = CASE WHEN active = 1 THEN 0 ELSE 1 END WHERE code = ?",
        (code,),
    )
    await db.commit()


# ======================== PAYMENT METHODS ========================

async def get_payment_methods() -> list:
    db = await get_db()
    cur = await db.execute(
        "SELECT * FROM payment_methods WHERE active = 1 ORDER BY id"
    )
    return _rows_to_list(await cur.fetchall())


async def get_all_payment_methods() -> list:
    db = await get_db()
    cur = await db.execute("SELECT * FROM payment_methods ORDER BY id")
    return _rows_to_list(await cur.fetchall())


async def get_payment_method(method_id: int) -> Optional[dict]:
    db = await get_db()
    cur = await db.execute(
        "SELECT * FROM payment_methods WHERE id = ?", (method_id,)
    )
    return _row_to_dict(await cur.fetchone())


async def add_payment_method(
    name: str, details: str, emoji: str = ""
) -> int:
    db = await get_db()
    cur = await db.execute(
        "INSERT INTO payment_methods (name, details, emoji) VALUES (?, ?, ?)",
        (name, details, emoji),
    )
    await db.commit()
    return cur.lastrowid


async def delete_payment_method(method_id: int) -> None:
    db = await get_db()
    await db.execute("DELETE FROM payment_methods WHERE id = ?", (method_id,))
    await db.commit()


# ======================== PAYMENT PROOFS ========================

async def create_payment_proof(
    user_id: int, order_id: int, method_id: int, file_id: str
) -> int:
    db = await get_db()
    cur = await db.execute(
        """INSERT INTO payment_proofs (user_id, order_id, method_id, file_id)
           VALUES (?, ?, ?, ?)""",
        (user_id, order_id, method_id, file_id),
    )
    await db.commit()
    return cur.lastrowid


async def get_payment_proof(proof_id: int) -> Optional[dict]:
    db = await get_db()
    cur = await db.execute(
        "SELECT * FROM payment_proofs WHERE id = ?", (proof_id,)
    )
    return _row_to_dict(await cur.fetchone())


async def get_pending_proofs() -> list:
    db = await get_db()
    cur = await db.execute(
        """SELECT * FROM payment_proofs
           WHERE status = 'pending_review'
           ORDER BY created_at DESC"""
    )
    return _rows_to_list(await cur.fetchall())


async def get_pending_proof_count() -> int:
    db = await get_db()
    cur = await db.execute(
        "SELECT COUNT(*) as cnt FROM payment_proofs WHERE status = 'pending_review'"
    )
    row = await cur.fetchone()
    return row["cnt"] if row else 0


async def update_proof(proof_id: int, **kwargs) -> None:
    db = await get_db()
    fields = []
    values = []
    for k, v in kwargs.items():
        fields.append(f"{k} = ?")
        values.append(v)
    if not fields:
        return
    values.append(proof_id)
    await db.execute(
        f"UPDATE payment_proofs SET {', '.join(fields)} WHERE id = ?", values
    )
    await db.commit()


# ======================== SETTINGS ========================

async def get_setting(key: str, default: str = "") -> str:
    db = await get_db()
    cur = await db.execute(
        "SELECT value FROM settings WHERE key = ?", (key,),
    )
    row = await cur.fetchone()
    return row["value"] if row else default


async def set_setting(key: str, value: str) -> None:
    db = await get_db()
    await db.execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
        (key, value),
    )
    await db.commit()


async def get_all_settings() -> list:
    db = await get_db()
    cur = await db.execute("SELECT * FROM settings ORDER BY key")
    return _rows_to_list(await cur.fetchall())


# ======================== FORCE JOIN ========================

async def get_force_join_channels() -> list:
    db = await get_db()
    cur = await db.execute("SELECT * FROM force_join_channels ORDER BY id")
    return _rows_to_list(await cur.fetchall())


async def add_force_join_channel(
    channel_id: str, name: str, invite_link: str
) -> int:
    db = await get_db()
    cur = await db.execute(
        "INSERT INTO force_join_channels (channel_id, name, invite_link) VALUES (?, ?, ?)",
        (channel_id, name, invite_link),
    )
    await db.commit()
    return cur.lastrowid


async def delete_force_join_channel(fj_id: int) -> None:
    db = await get_db()
    await db.execute("DELETE FROM force_join_channels WHERE id = ?", (fj_id,))
    await db.commit()


# ======================== TICKETS ========================

async def create_ticket(
    user_id: int, subject: str, message: str
) -> int:
    db = await get_db()
    cur = await db.execute(
        "INSERT INTO tickets (user_id, subject, message) VALUES (?, ?, ?)",
        (user_id, subject, message),
    )
    await db.commit()
    return cur.lastrowid


async def get_ticket(ticket_id: int) -> Optional[dict]:
    db = await get_db()
    cur = await db.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    return _row_to_dict(await cur.fetchone())


async def get_user_tickets(user_id: int, limit: int = 20) -> list:
    db = await get_db()
    cur = await db.execute(
        "SELECT * FROM tickets WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
        (user_id, limit),
    )
    return _rows_to_list(await cur.fetchall())


async def get_open_tickets(limit: int = 20) -> list:
    db = await get_db()
    cur = await db.execute(
        "SELECT * FROM tickets WHERE status = 'open' ORDER BY created_at DESC LIMIT ?",
        (limit,),
    )
    return _rows_to_list(await cur.fetchall())


async def get_all_tickets(limit: int = 30) -> list:
    db = await get_db()
    cur = await db.execute(
        "SELECT * FROM tickets ORDER BY created_at DESC LIMIT ?", (limit,),
    )
    return _rows_to_list(await cur.fetchall())


async def get_open_ticket_count() -> int:
    db = await get_db()
    cur = await db.execute(
        "SELECT COUNT(*) as cnt FROM tickets WHERE status = 'open'",
    )
    row = await cur.fetchone()
    return row["cnt"] if row else 0


async def close_ticket(ticket_id: int) -> None:
    db = await get_db()
    await db.execute(
        "UPDATE tickets SET status = 'closed' WHERE id = ?", (ticket_id,),
    )
    await db.commit()


async def reopen_ticket(ticket_id: int) -> None:
    db = await get_db()
    await db.execute(
        "UPDATE tickets SET status = 'open' WHERE id = ?", (ticket_id,),
    )
    await db.commit()


async def add_ticket_reply(
    ticket_id: int, sender: str, message: str
) -> int:
    db = await get_db()
    cur = await db.execute(
        "INSERT INTO ticket_replies (ticket_id, sender, message) VALUES (?, ?, ?)",
        (ticket_id, sender, message),
    )
    await db.commit()
    return cur.lastrowid


async def get_ticket_replies(ticket_id: int) -> list:
    db = await get_db()
    cur = await db.execute(
        "SELECT * FROM ticket_replies WHERE ticket_id = ? ORDER BY created_at",
        (ticket_id,),
    )
    return _rows_to_list(await cur.fetchall())


# ======================== ACTION LOGS ========================

async def add_action_log(
    action: str, user_id: int = 0, details: str = ""
) -> None:
    db = await get_db()
    await db.execute(
        "INSERT INTO action_logs (action, user_id, details) VALUES (?, ?, ?)",
        (action, user_id, details),
    )
    await db.commit()


# ======================== WALLET TOPUPS ========================

async def create_topup(user_id: int, amount: float, method_id: int) -> int:
    db = await get_db()
    cur = await db.execute(
        "INSERT INTO wallet_topups (user_id, amount, method_id) VALUES (?, ?, ?)",
        (user_id, amount, method_id),
    )
    await db.commit()
    return cur.lastrowid


async def get_topup(topup_id: int) -> Optional[dict]:
    db = await get_db()
    cur = await db.execute(
        "SELECT * FROM wallet_topups WHERE id = ?", (topup_id,)
    )
    return _row_to_dict(await cur.fetchone())


async def get_pending_topups() -> list:
    db = await get_db()
    cur = await db.execute(
        "SELECT * FROM wallet_topups WHERE status = 'pending' ORDER BY created_at DESC"
    )
    return _rows_to_list(await cur.fetchall())


async def get_user_topups(user_id: int, limit: int = 10) -> list:
    db = await get_db()
    cur = await db.execute(
        "SELECT * FROM wallet_topups WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
        (user_id, limit),
    )
    return _rows_to_list(await cur.fetchall())


async def update_topup(topup_id: int, **kwargs) -> None:
    db = await get_db()
    fields = []
    values = []
    for k, v in kwargs.items():
        fields.append(f"{k} = ?")
        values.append(v)
    if not fields:
        return
    values.append(topup_id)
    await db.execute(
        f"UPDATE wallet_topups SET {', '.join(fields)} WHERE id = ?", values
    )
    await db.commit()


async def get_pending_topup_count() -> int:
    db = await get_db()
    cur = await db.execute(
        "SELECT COUNT(*) as cnt FROM wallet_topups WHERE status = 'pending'"
    )
    row = await cur.fetchone()
    return row["cnt"] if row else 0


# ======================== DASHBOARD STATS ========================

async def get_dashboard_stats() -> dict:
    db = await get_db()

    users = await db.execute("SELECT COUNT(*) as c FROM users")
    users_row = await users.fetchone()

    cats = await db.execute("SELECT COUNT(*) as c FROM categories")
    cats_row = await cats.fetchone()

    prods = await db.execute("SELECT COUNT(*) as c FROM products")
    prods_row = await prods.fetchone()

    orders = await db.execute("SELECT COUNT(*) as c FROM orders")
    orders_row = await orders.fetchone()

    revenue = await db.execute(
        "SELECT COALESCE(SUM(total), 0) as r FROM orders WHERE payment_status = 'paid'",
    )
    rev_row = await revenue.fetchone()

    proofs = await db.execute(
        "SELECT COUNT(*) as c FROM payment_proofs WHERE status = 'pending_review'",
    )
    proofs_row = await proofs.fetchone()

    tickets = await db.execute(
        "SELECT COUNT(*) as c FROM tickets WHERE status = 'open'",
    )
    tickets_row = await tickets.fetchone()

    topups = await db.execute(
        "SELECT COUNT(*) as c FROM wallet_topups WHERE status = 'pending'",
    )
    topups_row = await topups.fetchone()

    return {
        "users": users_row["c"],
        "categories": cats_row["c"],
        "products": prods_row["c"],
        "orders": orders_row["c"],
        "revenue": rev_row["r"],
        "pending_proofs": proofs_row["c"],
        "open_tickets": tickets_row["c"],
        "pending_topups": topups_row["c"],
    }
