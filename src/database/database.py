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
    """Get or create DB connection with timeout."""
    global _db
    if _db is None:
        import os
        from pathlib import Path
        db_dir = Path(DB_PATH).parent
        db_dir.mkdir(parents=True, exist_ok=True)

        _db = await aiosqlite.connect(DB_PATH, timeout=10.0)
        _db.row_factory = aiosqlite.Row
        await _db.execute("PRAGMA journal_mode=WAL")
        await _db.execute("PRAGMA foreign_keys=ON")
    return _db


def _row_to_dict(row) -> dict:
    if row is None:
        return None
    return dict(row)


def _rows_to_list(rows) -> list:
    return [dict(r) for r in rows]


# ======================== INIT ========================

async def init_db() -> None:
    """Create all tables."""
    db = await get_db()

    await db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id         INTEGER PRIMARY KEY,
            full_name       TEXT DEFAULT '',
            username        TEXT DEFAULT '',
            balance         REAL DEFAULT 0.0,
            points          INTEGER DEFAULT 0,
            currency        TEXT DEFAULT 'PKR',
            banned          INTEGER DEFAULT 0,
            joined_at       TEXT DEFAULT (datetime('now')),
            last_spin       TEXT DEFAULT NULL,
            referrer_id     INTEGER DEFAULT NULL,
            total_spent     REAL DEFAULT 0.0,
            total_deposited REAL DEFAULT 0.0
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
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id     INTEGER NOT NULL,
            name            TEXT NOT NULL,
            description     TEXT DEFAULT '',
            price           REAL NOT NULL DEFAULT 0,
            base_price      REAL DEFAULT 0,
            current_price   REAL DEFAULT 0,
            min_price       REAL DEFAULT 0,
            plan_days       INTEGER DEFAULT 0,
            warranty_days   INTEGER DEFAULT 0,
            warranty_terms  TEXT DEFAULT '',
            drop_per_day    REAL DEFAULT 0,
            drop_enabled    INTEGER DEFAULT 0,
            listed_at       TEXT DEFAULT (datetime('now')),
            last_drop_at    TEXT DEFAULT NULL,
            stock           INTEGER DEFAULT -1,
            image_id        TEXT DEFAULT NULL,
            active          INTEGER DEFAULT 1,
            created_at      TEXT DEFAULT (datetime('now')),
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
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
            UNIQUE(user_id, product_id)
        );

        CREATE TABLE IF NOT EXISTS orders (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id           INTEGER NOT NULL,
            items_json        TEXT DEFAULT '[]',
            total             REAL DEFAULT 0,
            status            TEXT DEFAULT 'pending',
            payment_status    TEXT DEFAULT 'unpaid',
            payment_method_id INTEGER DEFAULT NULL,
            payment_proof_id  INTEGER DEFAULT NULL,
            coupon_code       TEXT DEFAULT NULL,
            created_at        TEXT DEFAULT (datetime('now'))
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
            code             TEXT PRIMARY KEY,
            discount_percent INTEGER DEFAULT 0,
            max_uses         INTEGER DEFAULT 0,
            used_count       INTEGER DEFAULT 0,
            active           INTEGER DEFAULT 1,
            created_at       TEXT DEFAULT (datetime('now'))
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

        CREATE TABLE IF NOT EXISTS points_history (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            amount      INTEGER NOT NULL,
            reason      TEXT NOT NULL,
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS referrals (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            referrer_id INTEGER NOT NULL,
            referred_id INTEGER NOT NULL,
            created_at  TEXT DEFAULT (datetime('now')),
            UNIQUE(referred_id)
        );

        CREATE TABLE IF NOT EXISTS currency_rates (
            currency    TEXT PRIMARY KEY,
            rate_vs_pkr REAL NOT NULL,
            updated_at  TEXT DEFAULT (datetime('now'))
        );

        -- ==========================================
        -- 🆕 DIGITAL STORE UPGRADE TABLES
        -- ==========================================

        -- Digital Items: Keys, Accounts, Links, Files
        CREATE TABLE IF NOT EXISTS digital_items (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id   INTEGER NOT NULL,
            type         TEXT NOT NULL DEFAULT 'key',
            -- Types: key, account, file_link, tg_link, redeem_code, manual
            content      TEXT NOT NULL,
            -- Actual key/password/link stored here (encrypted recommended)
            instructions TEXT DEFAULT '',
            -- Extra instructions for customer
            status       TEXT DEFAULT 'available',
            -- available, used, reserved, expired
            used_by      INTEGER DEFAULT NULL,
            -- user_id who received this item
            used_at      TEXT DEFAULT NULL,
            -- When it was delivered
            order_id     INTEGER DEFAULT NULL,
            -- Which order used this item
            added_at     TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        );

        -- Order Deliveries: Track every delivery
        CREATE TABLE IF NOT EXISTS order_deliveries (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id         INTEGER NOT NULL,
            user_id          INTEGER NOT NULL,
            product_id       INTEGER NOT NULL,
            item_id          INTEGER DEFAULT NULL,
            -- digital_items id that was delivered
            delivery_type    TEXT NOT NULL DEFAULT 'auto',
            -- auto, manual, semi_auto
            delivery_data    TEXT DEFAULT '',
            -- JSON with delivered content
            delivery_email   TEXT DEFAULT NULL,
            -- For manual deliveries like Canva
            delivery_status  TEXT DEFAULT 'pending',
            -- pending, delivered, failed
            delivered_at     TEXT DEFAULT NULL,
            manual_note      TEXT DEFAULT NULL,
            -- Admin note for manual deliveries
            delivered_by     INTEGER DEFAULT NULL,
            -- Admin id who delivered (for manual)
            created_at       TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        );

        -- Price Drop Log: History of all price changes
        CREATE TABLE IF NOT EXISTS price_drop_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id  INTEGER NOT NULL,
            old_price   REAL NOT NULL,
            new_price   REAL NOT NULL,
            drop_amount REAL NOT NULL,
            day_number  INTEGER DEFAULT 0,
            -- Which day of listing this drop happened
            reason      TEXT DEFAULT 'auto_daily_drop',
            -- auto_daily_drop, manual_admin, min_price_reached
            dropped_at  TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        );

        -- Product Access: Subscription / Time-limited access
        CREATE TABLE IF NOT EXISTS product_access (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            product_id  INTEGER NOT NULL,
            order_id    INTEGER DEFAULT NULL,
            access_type TEXT DEFAULT 'lifetime',
            -- lifetime, subscription, limited
            granted_at  TEXT DEFAULT (datetime('now')),
            expires_at  TEXT DEFAULT NULL,
            -- NULL = lifetime, date = expiry
            is_active   INTEGER DEFAULT 1,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
            UNIQUE(user_id, product_id)
        );

        -- Bulk Import Log: Track bulk key/account imports
        CREATE TABLE IF NOT EXISTS bulk_import_log (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id   INTEGER NOT NULL,
            total_items  INTEGER DEFAULT 0,
            item_type    TEXT DEFAULT 'key',
            imported_by  INTEGER NOT NULL,
            -- Admin user_id
            imported_at  TEXT DEFAULT (datetime('now')),
            notes        TEXT DEFAULT '',
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        );

        -- ==========================================
        -- PERFORMANCE INDEXES
        -- ==========================================
        CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
        CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
        CREATE INDEX IF NOT EXISTS idx_orders_payment_status ON orders(payment_status);
        CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_orders_user_status ON orders(user_id, status, created_at DESC);

        CREATE INDEX IF NOT EXISTS idx_cart_user_id ON cart(user_id);
        CREATE INDEX IF NOT EXISTS idx_cart_product_id ON cart(product_id);

        CREATE INDEX IF NOT EXISTS idx_payment_proofs_status ON payment_proofs(status);
        CREATE INDEX IF NOT EXISTS idx_payment_proofs_order_id ON payment_proofs(order_id);
        CREATE INDEX IF NOT EXISTS idx_payment_proofs_user_id ON payment_proofs(user_id);

        CREATE INDEX IF NOT EXISTS idx_tickets_user_id ON tickets(user_id);
        CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status);
        CREATE INDEX IF NOT EXISTS idx_tickets_created_at ON tickets(created_at DESC);

        CREATE INDEX IF NOT EXISTS idx_products_category_id ON products(category_id);
        CREATE INDEX IF NOT EXISTS idx_products_active ON products(active);
        CREATE INDEX IF NOT EXISTS idx_products_drop_enabled ON products(drop_enabled);

        CREATE INDEX IF NOT EXISTS idx_wallet_topups_user_id ON wallet_topups(user_id);
        CREATE INDEX IF NOT EXISTS idx_wallet_topups_status ON wallet_topups(status);

        CREATE INDEX IF NOT EXISTS idx_points_history_user_id ON points_history(user_id);
        CREATE INDEX IF NOT EXISTS idx_referrals_referrer_id ON referrals(referrer_id);

        CREATE INDEX IF NOT EXISTS idx_digital_items_product_id ON digital_items(product_id);
        CREATE INDEX IF NOT EXISTS idx_digital_items_status ON digital_items(status);
        CREATE INDEX IF NOT EXISTS idx_digital_items_used_by ON digital_items(used_by);

        CREATE INDEX IF NOT EXISTS idx_order_deliveries_order_id ON order_deliveries(order_id);
        CREATE INDEX IF NOT EXISTS idx_order_deliveries_user_id ON order_deliveries(user_id);
        CREATE INDEX IF NOT EXISTS idx_order_deliveries_status ON order_deliveries(delivery_status);

        CREATE INDEX IF NOT EXISTS idx_price_drop_log_product_id ON price_drop_log(product_id);
        CREATE INDEX IF NOT EXISTS idx_product_access_user_id ON product_access(user_id);
        CREATE INDEX IF NOT EXISTS idx_product_access_expires ON product_access(expires_at);
    """)

    # Migrate existing products table (safe — adds columns only if missing)
    await _migrate_products_table(db)

    # Default settings
    defaults = {
        "currency": "Rs",
        "bot_name": "NanoStore",
        "welcome_text": "Welcome to NanoStore!",
        "use_global_image": "on",
        "global_ui_image_id": "",
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
        "global_banner_image_id": "",
        "min_order": "0",
        "topup_enabled": "on",
        "topup_min_amount": "100",
        "topup_max_amount": "10000",
        "topup_bonus_percent": "0",
        "auto_delete": "0",
        "restart_notify_users": "off",
        "last_restart_at": "",
        "price_drop_enabled": "on",
        "price_drop_notify_admin": "on",
        "low_stock_alert_threshold": "5",
    }
    for key, value in defaults.items():
        await db.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
            (key, value),
        )

    await db.commit()
    logger.info("Database initialized with all tables including Digital Store Upgrade.")


async def _migrate_products_table(db) -> None:
    """Safely add new columns to existing products table."""
    new_columns = [
        ("base_price",     "REAL DEFAULT 0"),
        ("current_price",  "REAL DEFAULT 0"),
        ("min_price",      "REAL DEFAULT 0"),
        ("plan_days",      "INTEGER DEFAULT 0"),
        ("warranty_days",  "INTEGER DEFAULT 0"),
        ("warranty_terms", "TEXT DEFAULT ''"),
        ("drop_per_day",   "REAL DEFAULT 0"),
        ("drop_enabled",   "INTEGER DEFAULT 0"),
        ("listed_at",      "TEXT DEFAULT (datetime('now'))"),
        ("last_drop_at",   "TEXT DEFAULT NULL"),
    ]
    cur = await db.execute("PRAGMA table_info(products)")
    existing = {row[1] for row in await cur.fetchall()}
    for col_name, col_def in new_columns:
        if col_name not in existing:
            await db.execute(
                f"ALTER TABLE products ADD COLUMN {col_name} {col_def}"
            )
            logger.info(f"Migrated: Added column '{col_name}' to products table.")
    await db.commit()


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


async def update_user_balance(user_id: int, amount: float, commit: bool = True) -> bool:
    db = await get_db()
    if amount < 0:
        cur = await db.execute(
            """UPDATE users
               SET balance = balance + ?
               WHERE user_id = ? AND balance >= ?
               RETURNING balance""",
            (amount, user_id, abs(amount)),
        )
        row = await cur.fetchone()
        if commit:
            await db.commit()
        return row is not None
    else:
        await db.execute(
            "UPDATE users SET balance = balance + ? WHERE user_id = ?",
            (amount, user_id),
        )
        if commit:
            await db.commit()
        return True


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

async def get_products_by_category(cat_id: int, limit: int = 100, offset: int = 0) -> list:
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
    base_price: float = 0, min_price: float = 0,
    plan_days: int = 0, warranty_days: int = 0,
    warranty_terms: str = "",
    drop_per_day: float = 0, drop_enabled: int = 0,
) -> int:
    db = await get_db()
    now = datetime.utcnow().isoformat()
    effective_base = base_price if base_price > 0 else price
    cur = await db.execute(
        """INSERT INTO products (
               category_id, name, description, price,
               base_price, current_price, min_price,
               plan_days, warranty_days, warranty_terms,
               drop_per_day, drop_enabled, stock, listed_at
           ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            cat_id, name, description, price,
            effective_base, price, min_price,
            plan_days, warranty_days, warranty_terms,
            drop_per_day, drop_enabled, stock, now
        ),
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


async def decrement_stock(product_id: int, quantity: int, commit: bool = True) -> bool:
    db = await get_db()
    cur = await db.execute(
        """UPDATE products SET stock = stock - ?
           WHERE id = ? AND stock >= ?
           RETURNING stock""",
        (quantity, product_id, quantity),
    )
    row = await cur.fetchone()
    if commit:
        await db.commit()
    return row is not None


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
    db = await get_db()
    cur = await db.execute(
        """SELECT c.id as cart_id, c.product_id, c.quantity,
                  p.name, p.price, p.current_price, p.base_price, p.stock, p.image_id
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
        """SELECT COALESCE(SUM(c.quantity * COALESCE(NULLIF(p.current_price,0), p.price)), 0) as total
           FROM cart c JOIN products p ON c.product_id = p.id
           WHERE c.user_id = ?""",
        (user_id,),
    )
    row = await cur.fetchone()
    return row["total"] if row else 0.0


async def get_cart_item(cart_id: int) -> Optional[dict]:
    db = await get_db()
    cur = await db.execute(
        """SELECT c.id as cart_id, c.product_id, c.quantity,
                  p.name, p.price, p.current_price, p.base_price, p.stock
           FROM cart c JOIN products p ON c.product_id = p.id
           WHERE c.id = ?""",
        (cart_id,),
    )
    return _row_to_dict(await cur.fetchone())


async def add_to_cart(user_id: int, product_id: int, quantity: int = 1) -> int:
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


async def get_user_orders(user_id: int, limit: int = 10, offset: int = 0) -> list:
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


# ======================== DIGITAL ITEMS ========================

async def add_digital_item(
    product_id: int, content: str,
    item_type: str = 'key', instructions: str = ''
) -> int:
    """Add a single digital item (key/account/link) to a product."""
    db = await get_db()
    cur = await db.execute(
        """INSERT INTO digital_items (product_id, type, content, instructions)
           VALUES (?, ?, ?, ?)""",
        (product_id, item_type, content, instructions),
    )
    await db.commit()
    # Update product stock count
    await _sync_product_stock(product_id)
    return cur.lastrowid


async def bulk_add_digital_items(
    product_id: int, items: list[str],
    item_type: str = 'key', instructions: str = ''
) -> int:
    """Bulk add digital items. items = list of content strings.
    Returns count of items added."""
    db = await get_db()
    data = [
        (product_id, item_type, item.strip(), instructions)
        for item in items if item.strip()
    ]
    await db.executemany(
        "INSERT INTO digital_items (product_id, type, content, instructions) VALUES (?, ?, ?, ?)",
        data,
    )
    await db.commit()
    await _sync_product_stock(product_id)
    return len(data)


async def get_available_digital_item(product_id: int) -> Optional[dict]:
    """Get one available digital item for delivery (FIFO)."""
    db = await get_db()
    cur = await db.execute(
        """SELECT * FROM digital_items
           WHERE product_id = ? AND status = 'available'
           ORDER BY id ASC LIMIT 1""",
        (product_id,),
    )
    return _row_to_dict(await cur.fetchone())


async def mark_digital_item_used(
    item_id: int, user_id: int, order_id: int, commit: bool = True
) -> None:
    """Mark a digital item as used after delivery."""
    db = await get_db()
    now = datetime.utcnow().isoformat()
    await db.execute(
        """UPDATE digital_items
           SET status = 'used', used_by = ?, used_at = ?, order_id = ?
           WHERE id = ?""",
        (user_id, now, order_id, item_id),
    )
    if commit:
        await db.commit()


async def get_digital_items_by_product(product_id: int, limit: int = 50) -> list:
    """Get all digital items for a product (admin view)."""
    db = await get_db()
    cur = await db.execute(
        """SELECT * FROM digital_items
           WHERE product_id = ?
           ORDER BY status ASC, id ASC LIMIT ?""",
        (product_id, limit),
    )
    return _rows_to_list(await cur.fetchall())


async def get_available_items_count(product_id: int) -> int:
    """Count available digital items for a product."""
    db = await get_db()
    cur = await db.execute(
        "SELECT COUNT(*) as cnt FROM digital_items WHERE product_id = ? AND status = 'available'",
        (product_id,),
    )
    row = await cur.fetchone()
    return row["cnt"] if row else 0


async def _sync_product_stock(product_id: int) -> None:
    """Sync product stock with available digital items count."""
    db = await get_db()
    cur = await db.execute(
        "SELECT COUNT(*) as cnt FROM digital_items WHERE product_id = ? AND status = 'available'",
        (product_id,),
    )
    row = await cur.fetchone()
    count = row["cnt"] if row else 0
    await db.execute(
        "UPDATE products SET stock = ? WHERE id = ?",
        (count, product_id),
    )
    await db.commit()


async def deliver_digital_item(
    order_id: int, user_id: int, product_id: int
) -> Optional[dict]:
    """Full delivery flow: get item → mark used → create delivery record.
    Returns delivered item dict or None if out of stock."""
    item = await get_available_digital_item(product_id)
    if not item:
        return None
    db = await get_db()
    now = datetime.utcnow().isoformat()
    # Mark item used
    await db.execute(
        """UPDATE digital_items
           SET status='used', used_by=?, used_at=?, order_id=?
           WHERE id=?""",
        (user_id, now, order_id, item["id"]),
    )
    # Create delivery record
    await db.execute(
        """INSERT INTO order_deliveries
           (order_id, user_id, product_id, item_id, delivery_type, delivery_data, delivery_status, delivered_at)
           VALUES (?, ?, ?, ?, 'auto', ?, 'delivered', ?)""",
        (order_id, user_id, product_id, item["id"], item["content"], now),
    )
    await db.commit()
    # Sync stock
    await _sync_product_stock(product_id)
    return item


async def create_manual_delivery(
    order_id: int, user_id: int, product_id: int,
    delivery_email: str = None
) -> int:
    """Create a manual delivery record (e.g. Canva invite)."""
    db = await get_db()
    cur = await db.execute(
        """INSERT INTO order_deliveries
           (order_id, user_id, product_id, delivery_type, delivery_email, delivery_status)
           VALUES (?, ?, ?, 'manual', ?, 'pending')""",
        (order_id, user_id, product_id, delivery_email),
    )
    await db.commit()
    return cur.lastrowid


async def complete_manual_delivery(
    delivery_id: int, admin_id: int, note: str = ''
) -> None:
    """Mark a manual delivery as completed by admin."""
    db = await get_db()
    now = datetime.utcnow().isoformat()
    await db.execute(
        """UPDATE order_deliveries
           SET delivery_status='delivered', delivered_at=?, delivered_by=?, manual_note=?
           WHERE id=?""",
        (now, admin_id, note, delivery_id),
    )
    await db.commit()


async def get_pending_manual_deliveries() -> list:
    """Get all pending manual deliveries for admin."""
    db = await get_db()
    cur = await db.execute(
        """SELECT od.*, p.name as product_name, u.full_name, u.username
           FROM order_deliveries od
           JOIN products p ON od.product_id = p.id
           JOIN users u ON od.user_id = u.user_id
           WHERE od.delivery_type = 'manual' AND od.delivery_status = 'pending'
           ORDER BY od.created_at ASC"""
    )
    return _rows_to_list(await cur.fetchall())


async def get_order_delivery(order_id: int) -> Optional[dict]:
    """Get delivery info for an order."""
    db = await get_db()
    cur = await db.execute(
        "SELECT * FROM order_deliveries WHERE order_id = ? ORDER BY id DESC LIMIT 1",
        (order_id,),
    )
    return _row_to_dict(await cur.fetchone())


# ======================== PRICE DROP ========================

async def get_products_due_for_drop() -> list:
    """Get all products where price drop is due today."""
    db = await get_db()
    today = datetime.utcnow().date().isoformat()
    cur = await db.execute(
        """SELECT * FROM products
           WHERE drop_enabled = 1
             AND active = 1
             AND current_price > min_price
             AND (last_drop_at IS NULL OR date(last_drop_at) < ?)
             AND listed_at IS NOT NULL""",
        (today,),
    )
    return _rows_to_list(await cur.fetchall())


async def apply_price_drop(product_id: int) -> Optional[dict]:
    """Apply daily price drop to a product.
    Returns dict with old/new price or None if not applicable."""
    db = await get_db()
    cur = await db.execute(
        "SELECT * FROM products WHERE id = ?", (product_id,)
    )
    product = _row_to_dict(await cur.fetchone())
    if not product:
        return None
    old_price = product["current_price"] or product["price"]
    drop = product["drop_per_day"] or 0
    min_p = product["min_price"] or 0
    if old_price <= min_p or drop <= 0:
        return None
    new_price = max(round(old_price - drop, 2), min_p)
    now = datetime.utcnow().isoformat()
    # Calculate day number
    try:
        listed = datetime.fromisoformat(product["listed_at"])
        day_num = (datetime.utcnow() - listed).days
    except Exception:
        day_num = 0
    # Update product
    await db.execute(
        "UPDATE products SET current_price = ?, price = ?, last_drop_at = ? WHERE id = ?",
        (new_price, new_price, now, product_id),
    )
    # Log the drop
    await db.execute(
        """INSERT INTO price_drop_log (product_id, old_price, new_price, drop_amount, day_number, reason)
           VALUES (?, ?, ?, ?, ?, 'auto_daily_drop')""",
        (product_id, old_price, new_price, round(old_price - new_price, 2), day_num),
    )
    await db.commit()
    return {
        "product_id": product_id,
        "product_name": product["name"],
        "old_price": old_price,
        "new_price": new_price,
        "drop_amount": round(old_price - new_price, 2),
        "day_number": day_num,
    }


async def run_daily_price_drops() -> list:
    """Run price drop for ALL eligible products. Call this at midnight.
    Returns list of products that had price drops."""
    products = await get_products_due_for_drop()
    results = []
    for product in products:
        result = await apply_price_drop(product["id"])
        if result:
            results.append(result)
    logger.info(f"Daily price drop: {len(results)} products updated.")
    return results


async def get_price_drop_history(product_id: int, limit: int = 30) -> list:
    """Get price drop history for a product."""
    db = await get_db()
    cur = await db.execute(
        """SELECT * FROM price_drop_log
           WHERE product_id = ?
           ORDER BY dropped_at DESC LIMIT ?""",
        (product_id, limit),
    )
    return _rows_to_list(await cur.fetchall())


async def reset_product_price(product_id: int) -> None:
    """Reset product price back to base_price (admin action)."""
    db = await get_db()
    cur = await db.execute(
        "SELECT base_price FROM products WHERE id = ?", (product_id,)
    )
    row = await cur.fetchone()
    if row and row["base_price"]:
        now = datetime.utcnow().isoformat()
        await db.execute(
            "UPDATE products SET current_price = base_price, price = base_price, last_drop_at = NULL WHERE id = ?",
            (product_id,),
        )
        await db.execute(
            """INSERT INTO price_drop_log (product_id, old_price, new_price, drop_amount, reason)
               SELECT current_price, base_price, current_price - base_price, 'manual_admin_reset'
               FROM products WHERE id = ?""",
            (product_id,),
        )
        await db.commit()


# ======================== PRODUCT ACCESS ========================

async def grant_product_access(
    user_id: int, product_id: int, order_id: int,
    access_type: str = 'lifetime', expires_at: str = None
) -> None:
    """Grant user access to a product after purchase."""
    db = await get_db()
    await db.execute(
        """INSERT INTO product_access (user_id, product_id, order_id, access_type, expires_at)
           VALUES (?, ?, ?, ?, ?)
           ON CONFLICT(user_id, product_id) DO UPDATE SET
             access_type = excluded.access_type,
             expires_at  = excluded.expires_at,
             is_active   = 1,
             granted_at  = datetime('now')""",
        (user_id, product_id, order_id, access_type, expires_at),
    )
    await db.commit()


async def check_product_access(user_id: int, product_id: int) -> bool:
    """Check if user has active access to a product."""
    db = await get_db()
    now = datetime.utcnow().isoformat()
    cur = await db.execute(
        """SELECT * FROM product_access
           WHERE user_id = ? AND product_id = ? AND is_active = 1
             AND (expires_at IS NULL OR expires_at > ?)""",
        (user_id, product_id, now),
    )
    return (await cur.fetchone()) is not None


async def get_user_purchases(user_id: int) -> list:
    """Get all products a user has purchased/has access to."""
    db = await get_db()
    cur = await db.execute(
        """SELECT pa.*, p.name, p.description, p.image_id
           FROM product_access pa
           JOIN products p ON pa.product_id = p.id
           WHERE pa.user_id = ? AND pa.is_active = 1
           ORDER BY pa.granted_at DESC""",
        (user_id,),
    )
    return _rows_to_list(await cur.fetchall())


async def revoke_expired_access() -> int:
    """Revoke access for expired subscriptions. Returns count revoked."""
    db = await get_db()
    now = datetime.utcnow().isoformat()
    cur = await db.execute(
        """UPDATE product_access SET is_active = 0
           WHERE expires_at IS NOT NULL AND expires_at <= ? AND is_active = 1""",
        (now,),
    )
    await db.commit()
    return cur.rowcount


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


async def use_coupon(code: str, commit: bool = True) -> bool:
    db = await get_db()
    cur = await db.execute(
        """UPDATE coupons
           SET used_count = used_count + 1
           WHERE code = ? AND active = 1
             AND (max_uses = 0 OR used_count < max_uses)
           RETURNING used_count""",
        (code,),
    )
    row = await cur.fetchone()
    if commit:
        await db.commit()
    return row is not None


async def get_all_coupons() -> list:
    db = await get_db()
    cur = await db.execute("SELECT * FROM coupons ORDER BY created_at DESC")
    return _rows_to_list(await cur.fetchall())


async def create_coupon(code: str, discount_percent: int, max_uses: int = 0) -> None:
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


async def add_payment_method(name: str, details: str, emoji: str = "") -> int:
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

async def create_payment_proof(user_id: int, order_id: int, method_id: int, file_id: str) -> int:
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
        "SELECT * FROM payment_proofs WHERE status = 'pending_review' ORDER BY created_at DESC"
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
    old_value = await get_setting(key, None)
    db = await get_db()
    await db.execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
        (key, value),
    )
    await db.commit()
    from utils.activity_logger import log_db_action
    if key == "global_ui_image_id":
        logger.warning(f"GLOBAL IMAGE CHANGED: '{old_value}' -> '{value}'")
        log_db_action("UPDATE", f"GLOBAL_IMAGE: {old_value[:20] if old_value else 'None'} -> {value[:20] if value else 'None'}")
    else:
        log_db_action("UPDATE", f"Setting: {key} = {str(value)[:50]}")


async def get_all_settings() -> list:
    db = await get_db()
    cur = await db.execute("SELECT * FROM settings ORDER BY key")
    return _rows_to_list(await cur.fetchall())


# ======================== FORCE JOIN ========================

async def get_force_join_channels() -> list:
    db = await get_db()
    cur = await db.execute("SELECT * FROM force_join_channels ORDER BY id")
    return _rows_to_list(await cur.fetchall())


async def add_force_join_channel(channel_id: str, name: str, invite_link: str) -> int:
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

async def create_ticket(user_id: int, subject: str, message: str) -> int:
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


async def add_ticket_reply(ticket_id: int, sender: str, message: str) -> int:
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

async def add_action_log(action: str, user_id: int = 0, details: str = "") -> None:
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
    users    = await db.execute("SELECT COUNT(*) as c FROM users")
    cats     = await db.execute("SELECT COUNT(*) as c FROM categories")
    prods    = await db.execute("SELECT COUNT(*) as c FROM products")
    orders   = await db.execute("SELECT COUNT(*) as c FROM orders")
    revenue  = await db.execute(
        "SELECT COALESCE(SUM(total), 0) as r FROM orders WHERE payment_status = 'paid'"
    )
    proofs   = await db.execute(
        "SELECT COUNT(*) as c FROM payment_proofs WHERE status = 'pending_review'"
    )
    tickets  = await db.execute(
        "SELECT COUNT(*) as c FROM tickets WHERE status = 'open'"
    )
    topups   = await db.execute(
        "SELECT COUNT(*) as c FROM wallet_topups WHERE status = 'pending'"
    )
    manual_del = await db.execute(
        "SELECT COUNT(*) as c FROM order_deliveries WHERE delivery_type='manual' AND delivery_status='pending'"
    )
    total_items = await db.execute(
        "SELECT COUNT(*) as c FROM digital_items WHERE status='available'"
    )
    return {
        "users":             (await users.fetchone())["c"],
        "categories":        (await cats.fetchone())["c"],
        "products":          (await prods.fetchone())["c"],
        "orders":            (await orders.fetchone())["c"],
        "revenue":           (await revenue.fetchone())["r"],
        "pending_proofs":    (await proofs.fetchone())["c"],
        "open_tickets":      (await tickets.fetchone())["c"],
        "pending_topups":    (await topups.fetchone())["c"],
        "pending_deliveries":(await manual_del.fetchone())["c"],
        "available_items":   (await total_items.fetchone())["c"],
    }


# ======================== POINTS SYSTEM ========================

async def get_user_points(user_id: int) -> int:
    db = await get_db()
    cur = await db.execute(
        "SELECT points FROM users WHERE user_id = ?", (user_id,)
    )
    row = await cur.fetchone()
    return row["points"] if row else 0


async def add_points(user_id: int, amount: int, reason: str) -> None:
    db = await get_db()
    await db.execute(
        "UPDATE users SET points = points + ? WHERE user_id = ?",
        (amount, user_id),
    )
    await db.execute(
        "INSERT INTO points_history (user_id, amount, reason) VALUES (?, ?, ?)",
        (user_id, amount, reason),
    )
    await db.commit()


async def deduct_points(user_id: int, amount: int) -> bool:
    db = await get_db()
    cur = await db.execute(
        "SELECT points FROM users WHERE user_id = ?", (user_id,)
    )
    row = await cur.fetchone()
    if not row or row["points"] < amount:
        return False
    await db.execute(
        "UPDATE users SET points = points - ? WHERE user_id = ?",
        (amount, user_id),
    )
    await db.execute(
        "INSERT INTO points_history (user_id, amount, reason) VALUES (?, ?, ?)",
        (user_id, -amount, "Used for order payment"),
    )
    await db.commit()
    return True


async def get_points_history(user_id: int, limit: int = 20) -> list:
    db = await get_db()
    cur = await db.execute(
        "SELECT * FROM points_history WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
        (user_id, limit),
    )
    return _rows_to_list(await cur.fetchall())


# ======================== DAILY SPIN ========================

async def can_spin(user_id: int) -> bool:
    from datetime import timedelta
    db = await get_db()
    cur = await db.execute(
        "SELECT last_spin FROM users WHERE user_id = ?", (user_id,)
    )
    row = await cur.fetchone()
    if not row or not row["last_spin"]:
        return True
    try:
        last_spin = datetime.fromisoformat(row["last_spin"])
        return (datetime.utcnow() - last_spin) >= timedelta(hours=24)
    except Exception:
        return True


async def get_next_spin_time(user_id: int) -> Optional[str]:
    from datetime import timedelta
    db = await get_db()
    cur = await db.execute(
        "SELECT last_spin FROM users WHERE user_id = ?", (user_id,)
    )
    row = await cur.fetchone()
    if not row or not row["last_spin"]:
        return None
    try:
        last_spin = datetime.fromisoformat(row["last_spin"])
        next_spin = last_spin + timedelta(hours=24)
        now = datetime.utcnow()
        if now >= next_spin:
            return None
        diff = next_spin - now
        hours = int(diff.total_seconds() // 3600)
        minutes = int((diff.total_seconds() % 3600) // 60)
        return f"{hours}h {minutes}m"
    except Exception:
        return None


async def record_spin(user_id: int, points_won: int) -> None:
    db = await get_db()
    now = datetime.utcnow().isoformat()
    await db.execute(
        "UPDATE users SET last_spin = ?, points = points + ? WHERE user_id = ?",
        (now, points_won, user_id),
    )
    await db.execute(
        "INSERT INTO points_history (user_id, amount, reason) VALUES (?, ?, ?)",
        (user_id, points_won, "Daily Spin"),
    )
    await db.commit()


# ======================== REFERRAL SYSTEM ========================

async def create_referral(referrer_id: int, referred_id: int) -> bool:
    db = await get_db()
    try:
        await db.execute(
            "INSERT INTO referrals (referrer_id, referred_id) VALUES (?, ?)",
            (referrer_id, referred_id),
        )
        await db.commit()
        return True
    except Exception:
        return False


async def get_referral_stats(user_id: int) -> dict:
    db = await get_db()
    cur = await db.execute(
        "SELECT COUNT(*) as cnt FROM referrals WHERE referrer_id = ?",
        (user_id,),
    )
    row = await cur.fetchone()
    total = row["cnt"] if row else 0
    return {
        "total_referrals": total,
        "points_earned": total * 1000,
        "active_referrals": total,
    }


async def get_referral_history(user_id: int, limit: int = 20) -> list:
    db = await get_db()
    cur = await db.execute(
        """SELECT r.*, u.full_name, u.username, u.joined_at
           FROM referrals r
           JOIN users u ON r.referred_id = u.user_id
           WHERE r.referrer_id = ?
           ORDER BY r.created_at DESC LIMIT ?""",
        (user_id, limit),
    )
    return _rows_to_list(await cur.fetchall())


async def get_referrer(user_id: int) -> Optional[int]:
    db = await get_db()
    cur = await db.execute(
        "SELECT referrer_id FROM referrals WHERE referred_id = ?",
        (user_id,),
    )
    row = await cur.fetchone()
    return row["referrer_id"] if row else None


# ======================== MULTI-CURRENCY ========================

async def get_user_currency(user_id: int) -> str:
    db = await get_db()
    cur = await db.execute(
        "SELECT currency FROM users WHERE user_id = ?", (user_id,)
    )
    row = await cur.fetchone()
    return row["currency"] if row else "PKR"


async def set_user_currency(user_id: int, currency_code: str) -> None:
    db = await get_db()
    await db.execute(
        "UPDATE users SET currency = ? WHERE user_id = ?",
        (currency_code, user_id),
    )
    await db.commit()


async def get_currency_rate(currency: str) -> float:
    db = await get_db()
    cur = await db.execute(
        "SELECT rate_vs_pkr FROM currency_rates WHERE currency = ?",
        (currency,),
    )
    row = await cur.fetchone()
    return row["rate_vs_pkr"] if row else 1.0


async def update_currency_rate(currency: str, rate_vs_pkr: float) -> None:
    db = await get_db()
    now = datetime.utcnow().isoformat()
    await db.execute(
        """INSERT OR REPLACE INTO currency_rates (currency, rate_vs_pkr, updated_at)
           VALUES (?, ?, ?)""",
        (currency, rate_vs_pkr, now),
    )
    await db.commit()


# ======================== USER STATS ========================

async def get_user_stats(user_id: int) -> dict:
    db = await get_db()
    cur = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = await cur.fetchone()
    if not user:
        return {}
    cur = await db.execute(
        """SELECT
            COUNT(*) as total,
            SUM(CASE WHEN status IN ('completed','delivered') THEN 1 ELSE 0 END) as completed,
            SUM(CASE WHEN status IN ('pending','confirmed','processing','shipped') THEN 1 ELSE 0 END) as pending
           FROM orders WHERE user_id = ?""",
        (user_id,),
    )
    orders = await cur.fetchone()
    cur = await db.execute(
        "SELECT COUNT(*) as cnt FROM referrals WHERE referrer_id = ?",
        (user_id,),
    )
    ref_row = await cur.fetchone()
    return {
        "user_id":          user["user_id"],
        "full_name":        user["full_name"],
        "username":         user["username"],
        "balance":          user["balance"],
        "points":           user["points"],
        "currency":         user["currency"],
        "joined_at":        user["joined_at"],
        "total_spent":      user["total_spent"],
        "total_deposited":  user["total_deposited"],
        "total_orders":     orders["total"] if orders else 0,
        "completed_orders": orders["completed"] if orders else 0,
        "pending_orders":   orders["pending"] if orders else 0,
        "referral_count":   ref_row["cnt"] if ref_row else 0,
    }


async def update_user_spent(user_id: int, amount: float) -> None:
    db = await get_db()
    await db.execute(
        "UPDATE users SET total_spent = total_spent + ? WHERE user_id = ?",
        (amount, user_id),
    )
    await db.commit()


async def update_user_deposited(user_id: int, amount: float) -> None:
    db = await get_db()
    await db.execute(
        "UPDATE users SET total_deposited = total_deposited + ? WHERE user_id = ?",
        (amount, user_id),
    )
    await db.commit()


async def get_user_total_spent(user_id: int) -> float:
    db = await get_db()
    cur = await db.execute(
        "SELECT COALESCE(SUM(total), 0) as total FROM orders WHERE user_id = ? AND status = 'completed'",
        (user_id,)
    )
    row = await cur.fetchone()
    return row["total"] if row else 0.0


async def get_user_total_deposited(user_id: int) -> float:
    db = await get_db()
    cur = await db.execute(
        "SELECT COALESCE(SUM(amount), 0) as total FROM wallet_topups WHERE user_id = ? AND status = 'approved'",
        (user_id,)
    )
    row = await cur.fetchone()
    return row["total"] if row else 0.0


async def get_user_join_date(user_id: int) -> str:
    db = await get_db()
    cur = await db.execute(
        "SELECT joined_at FROM users WHERE user_id = ?", (user_id,)
    )
    row = await cur.fetchone()
    if not row or not row["joined_at"]:
        return "Unknown"
    try:
        dt = datetime.fromisoformat(row["joined_at"])
        return dt.strftime("%b %Y")
    except Exception:
        return "Unknown"


async def get_user_pending_orders(user_id: int) -> int:
    db = await get_db()
    cur = await db.execute(
        "SELECT COUNT(*) as cnt FROM orders WHERE user_id = ? AND status IN ('pending','confirmed','processing')",
        (user_id,)
    )
    row = await cur.fetchone()
    return row["cnt"] if row else 0


async def get_user_completed_orders(user_id: int) -> int:
    db = await get_db()
    cur = await db.execute(
        "SELECT COUNT(*) as cnt FROM orders WHERE user_id = ? AND status = 'completed'",
        (user_id,)
    )
    row = await cur.fetchone()
    return row["cnt"] if row else 0


async def get_user_referral_count(user_id: int) -> int:
    try:
        db = await get_db()
        cur = await db.execute(
            "SELECT COUNT(*) as cnt FROM referrals WHERE referrer_id = ?",
            (user_id,)
        )
        row = await cur.fetchone()
        return row["cnt"] if row else 0
    except Exception:
        return 0


async def get_spin_status(user_id: int) -> dict:
    from datetime import timedelta
    try:
        db = await get_db()
        cur = await db.execute(
            "SELECT last_spin FROM users WHERE user_id = ?", (user_id,)
        )
        row = await cur.fetchone()
        if not row or not row["last_spin"]:
            return {"available": True, "hours_left": 0, "mins_left": 0}
        last_spin = datetime.fromisoformat(row["last_spin"])
        now = datetime.utcnow()
        next_spin = last_spin + timedelta(hours=24)
        if now >= next_spin:
            return {"available": True, "hours_left": 0, "mins_left": 0}
        diff = next_spin - now
        hours = int(diff.total_seconds() // 3600)
        mins  = int((diff.total_seconds() % 3600) // 60)
        return {"available": False, "hours_left": hours, "mins_left": mins}
    except Exception:
        return {"available": True, "hours_left": 0, "mins_left": 0}
