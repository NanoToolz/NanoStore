"""NanoStore database — 16 tables, all CRUD functions, seed data."""

import aiosqlite
import json
import logging
from datetime import datetime, timedelta
from config import DB_PATH

logger = logging.getLogger(__name__)


# ════════════════════════ INIT + SCHEMA ════════════════════════

async def init_db() -> None:
    """Create all 16 tables and seed default data."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                banned INTEGER DEFAULT 0,
                balance REAL DEFAULT 0,
                joined_at TEXT
            );

            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            );

            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                emoji TEXT DEFAULT '',
                image_id TEXT,
                sort_order INTEGER DEFAULT 0,
                active INTEGER DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                price REAL DEFAULT 0,
                image_id TEXT,
                stock INTEGER DEFAULT -1,
                active INTEGER DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS cart (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                product_id INTEGER,
                quantity INTEGER DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                items_json TEXT,
                total REAL DEFAULT 0,
                status TEXT DEFAULT 'pending',
                coupon_code TEXT,
                payment_status TEXT DEFAULT 'unpaid',
                payment_method_id INTEGER,
                payment_proof_id INTEGER,
                created_at TEXT
            );

            CREATE TABLE IF NOT EXISTS coupons (
                code TEXT PRIMARY KEY,
                discount_percent INTEGER DEFAULT 0,
                max_uses INTEGER DEFAULT 0,
                used_count INTEGER DEFAULT 0,
                active INTEGER DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS payment_methods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                details TEXT NOT NULL,
                emoji TEXT DEFAULT '',
                active INTEGER DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS payment_proofs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                order_id INTEGER,
                method_id INTEGER,
                file_id TEXT,
                status TEXT DEFAULT 'pending',
                reviewed_by INTEGER,
                admin_note TEXT,
                created_at TEXT
            );

            CREATE TABLE IF NOT EXISTS force_join_channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id TEXT,
                channel_name TEXT,
                channel_link TEXT
            );

            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                subject TEXT,
                status TEXT DEFAULT 'open',
                created_at TEXT,
                closed_at TEXT
            );

            CREATE TABLE IF NOT EXISTS ticket_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id INTEGER,
                sender_id INTEGER,
                sender_type TEXT,
                message TEXT,
                created_at TEXT
            );

            CREATE TABLE IF NOT EXISTS product_faqs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                question TEXT,
                answer TEXT,
                sort_order INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS product_media (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                media_type TEXT,
                file_id TEXT,
                caption TEXT
            );

            CREATE TABLE IF NOT EXISTS daily_rewards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                claimed_date TEXT,
                reward_amount REAL,
                streak INTEGER
            );

            CREATE TABLE IF NOT EXISTS action_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT,
                user_id INTEGER,
                details TEXT,
                created_at TEXT
            );
        """)
        await db.commit()

    await _seed_settings()
    await _seed_categories()
    await _seed_payment_methods()
    logger.info("Database initialized successfully.")


async def _seed_settings() -> None:
    """Seed default settings if not present."""
    defaults = {
        "store_name": "NanoStore",
        "currency": "Rs",
        "min_order": "0",
        "contact": "@NanoToolz",
        "welcome_message": "",
        "welcome_image": "",
    }
    async with aiosqlite.connect(DB_PATH) as db:
        for key, value in defaults.items():
            await db.execute(
                "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
                (key, value),
            )
        await db.commit()


async def _seed_categories() -> None:
    """Seed 12 default categories if table is empty."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM categories")
        count = (await cursor.fetchone())[0]
        if count > 0:
            return
        cats = [
            ("eBooks", "📚", 1),
            ("Templates", "📝", 2),
            ("Online Courses", "🎓", 3),
            ("Software & Tools", "💻", 4),
            ("Graphics & Design", "🎨", 5),
            ("Music & Audio", "🎵", 6),
            ("Video & Film", "🎬", 7),
            ("WordPress Themes", "🌐", 8),
            ("Mobile Apps", "📱", 9),
            ("Gaming Assets", "🎮", 10),
            ("Photography", "📷", 11),
            ("Business & Finance", "💼", 12),
        ]
        await db.executemany(
            "INSERT INTO categories (name, emoji, sort_order) VALUES (?, ?, ?)", cats
        )
        await db.commit()
        logger.info("Seeded 12 default categories.")


async def _seed_payment_methods() -> None:
    """Seed 3 default payment methods if table is empty."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM payment_methods")
        count = (await cursor.fetchone())[0]
        if count > 0:
            return
        methods = [
            ("Bank Transfer", "Bank: HBL\nAccount: 1234567890\nTitle: NanoToolz", "🏦"),
            ("JazzCash / EasyPaisa", "JazzCash: 03001234567\nName: NanoToolz", "📱"),
            ("Crypto USDT (TRC20)", "Wallet: TXxxxxxxxxxxxxxxxxxxx\nNetwork: TRC20", "₿"),
        ]
        await db.executemany(
            "INSERT INTO payment_methods (name, details, emoji) VALUES (?, ?, ?)", methods
        )
        await db.commit()
        logger.info("Seeded 3 default payment methods.")


# ════════════════════════ SETTINGS ════════════════════════

async def get_setting(key: str, default: str = "") -> str:
    """Get a single setting value by key."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = await cursor.fetchone()
        return row[0] if row else default


async def set_setting(key: str, value: str) -> None:
    """Set a single setting value."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, str(value)),
        )
        await db.commit()


async def get_all_settings() -> dict:
    """Get all settings as a dict."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT key, value FROM settings")
        rows = await cursor.fetchall()
        return {r[0]: r[1] for r in rows}


# ════════════════════════ USERS ════════════════════════

async def add_user(user_id: int, username: str, full_name: str) -> None:
    """Register a new user (ignored if already exists)."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, username, full_name, joined_at) VALUES (?, ?, ?, ?)",
            (user_id, username, full_name, datetime.utcnow().isoformat()),
        )
        await db.commit()


async def get_user(user_id: int) -> dict | None:
    """Get user by Telegram user ID."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def get_all_users(limit: int = 50, offset: int = 0) -> list[dict]:
    """Get all users with pagination."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM users ORDER BY joined_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        )
        return [dict(r) for r in await cursor.fetchall()]


async def get_user_count() -> int:
    """Get total user count."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM users")
        return (await cursor.fetchone())[0]


async def ban_user(user_id: int) -> None:
    """Ban a user."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET banned = 1 WHERE user_id = ?", (user_id,))
        await db.commit()


async def unban_user(user_id: int) -> None:
    """Unban a user."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET banned = 0 WHERE user_id = ?", (user_id,))
        await db.commit()


async def is_banned(user_id: int) -> bool:
    """Check if a user is banned."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT banned FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        return bool(row and row[0] == 1)


async def get_user_balance(user_id: int) -> float:
    """Get user wallet balance."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        return float(row[0]) if row else 0.0


async def update_user_balance(user_id: int, amount: float) -> None:
    """Add (or subtract with negative) amount to user balance."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET balance = balance + ? WHERE user_id = ?",
            (amount, user_id),
        )
        await db.commit()


async def set_user_balance(user_id: int, balance: float) -> None:
    """Set user balance to exact value."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET balance = ? WHERE user_id = ?",
            (balance, user_id),
        )
        await db.commit()


# ════════════════════════ CATEGORIES ════════════════════════

async def get_categories() -> list[dict]:
    """Get active categories sorted by sort_order."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM categories WHERE active = 1 ORDER BY sort_order, name"
        )
        return [dict(r) for r in await cursor.fetchall()]


async def get_all_categories() -> list[dict]:
    """Get all categories including inactive."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM categories ORDER BY sort_order, name")
        return [dict(r) for r in await cursor.fetchall()]


async def get_category(cat_id: int) -> dict | None:
    """Get single category by ID."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM categories WHERE id = ?", (cat_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def add_category(name: str, emoji: str = "📦") -> int:
    """Add a new category. Returns new ID."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO categories (name, emoji) VALUES (?, ?)",
            (name, emoji),
        )
        await db.commit()
        return cursor.lastrowid


async def update_category(cat_id: int, **kwargs) -> None:
    """Update category fields dynamically."""
    allowed = {"name", "emoji", "image_id", "sort_order", "active"}
    fields = {k: v for k, v in kwargs.items() if k in allowed}
    if not fields:
        return
    set_clause = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [cat_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE categories SET {set_clause} WHERE id = ?", values)
        await db.commit()


async def delete_category(cat_id: int) -> None:
    """Delete category and deactivate its products."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM categories WHERE id = ?", (cat_id,))
        await db.execute("UPDATE products SET active = 0 WHERE category_id = ?", (cat_id,))
        await db.commit()


async def get_category_count() -> int:
    """Get count of active categories."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM categories WHERE active = 1")
        return (await cursor.fetchone())[0]


# ════════════════════════ PRODUCTS ════════════════════════

async def get_products_by_category(cat_id: int, limit: int = 20, offset: int = 0) -> list[dict]:
    """Get products in a category with pagination."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM products WHERE category_id = ? AND active = 1 ORDER BY name LIMIT ? OFFSET ?",
            (cat_id, limit, offset),
        )
        return [dict(r) for r in await cursor.fetchall()]


async def get_product_count_in_category(cat_id: int) -> int:
    """Count active products in a category."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT COUNT(*) FROM products WHERE category_id = ? AND active = 1",
            (cat_id,),
        )
        return (await cursor.fetchone())[0]


async def get_product(product_id: int) -> dict | None:
    """Get single product by ID."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def get_all_products() -> list[dict]:
    """Get all active products."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM products WHERE active = 1 ORDER BY name")
        return [dict(r) for r in await cursor.fetchall()]


async def add_product(category_id: int, name: str, description: str = "", price: float = 0, stock: int = -1) -> int:
    """Add a new product. Returns new ID."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO products (category_id, name, description, price, stock) VALUES (?, ?, ?, ?, ?)",
            (category_id, name, description, price, stock),
        )
        await db.commit()
        return cursor.lastrowid


async def update_product(product_id: int, **kwargs) -> None:
    """Update product fields dynamically."""
    allowed = {"name", "description", "price", "image_id", "category_id", "stock", "active"}
    fields = {k: v for k, v in kwargs.items() if k in allowed}
    if not fields:
        return
    set_clause = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [product_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE products SET {set_clause} WHERE id = ?", values)
        await db.commit()


async def delete_product(product_id: int) -> None:
    """Delete product and all related data."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM products WHERE id = ?", (product_id,))
        await db.execute("DELETE FROM cart WHERE product_id = ?", (product_id,))
        await db.execute("DELETE FROM product_faqs WHERE product_id = ?", (product_id,))
        await db.execute("DELETE FROM product_media WHERE product_id = ?", (product_id,))
        await db.commit()


async def search_products(query: str) -> list[dict]:
    """Search products by name or description."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        q = f"%{query}%"
        cursor = await db.execute(
            "SELECT * FROM products WHERE active = 1 AND (name LIKE ? OR description LIKE ?)",
            (q, q),
        )
        return [dict(r) for r in await cursor.fetchall()]


async def get_product_count() -> int:
    """Get count of active products."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM products WHERE active = 1")
        return (await cursor.fetchone())[0]


async def decrement_stock(product_id: int, qty: int = 1) -> bool:
    """Decrement stock. Returns False if insufficient. Ignores unlimited (-1)."""
    p = await get_product(product_id)
    if not p:
        return False
    if p["stock"] == -1:
        return True
    if p["stock"] < qty:
        return False
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE products SET stock = stock - ? WHERE id = ? AND stock >= ?",
            (qty, product_id, qty),
        )
        await db.commit()
    return True


# ════════════════════════ CART ════════════════════════

async def add_to_cart(user_id: int, product_id: int) -> None:
    """Add product to cart (increment if exists)."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT id, quantity FROM cart WHERE user_id = ? AND product_id = ?",
            (user_id, product_id),
        )
        row = await cursor.fetchone()
        if row:
            await db.execute("UPDATE cart SET quantity = quantity + 1 WHERE id = ?", (row[0],))
        else:
            await db.execute(
                "INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, 1)",
                (user_id, product_id),
            )
        await db.commit()


async def get_cart(user_id: int) -> list[dict]:
    """Get user cart with product details."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """SELECT c.id, c.quantity, p.id AS product_id, p.name, p.price, p.stock, p.image_id
               FROM cart c JOIN products p ON c.product_id = p.id
               WHERE c.user_id = ?""",
            (user_id,),
        )
        return [dict(r) for r in await cursor.fetchall()]


async def get_cart_total(user_id: int) -> float:
    """Get total cart value."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """SELECT SUM(p.price * c.quantity)
               FROM cart c JOIN products p ON c.product_id = p.id
               WHERE c.user_id = ?""",
            (user_id,),
        )
        row = await cursor.fetchone()
        return float(row[0]) if row and row[0] else 0.0


async def get_cart_count(user_id: int) -> int:
    """Get total number of items in cart."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT COALESCE(SUM(quantity), 0) FROM cart WHERE user_id = ?",
            (user_id,),
        )
        return (await cursor.fetchone())[0]


async def update_cart_qty(cart_id: int, qty: int) -> None:
    """Update cart item quantity. Removes if qty <= 0."""
    async with aiosqlite.connect(DB_PATH) as db:
        if qty <= 0:
            await db.execute("DELETE FROM cart WHERE id = ?", (cart_id,))
        else:
            await db.execute("UPDATE cart SET quantity = ? WHERE id = ?", (qty, cart_id))
        await db.commit()


async def remove_from_cart_by_id(cart_id: int) -> None:
    """Remove a cart item by its cart row ID."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM cart WHERE id = ?", (cart_id,))
        await db.commit()


async def clear_cart(user_id: int) -> None:
    """Clear all items from user cart."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
        await db.commit()


async def get_cart_item(cart_id: int) -> dict | None:
    """Get a specific cart item with product details."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """SELECT c.id, c.quantity, c.user_id, c.product_id, p.name, p.price, p.stock
               FROM cart c JOIN products p ON c.product_id = p.id
               WHERE c.id = ?""",
            (cart_id,),
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


# ════════════════════════ ORDERS ════════════════════════

async def create_order(user_id: int, items: list, total: float, coupon_code: str | None = None) -> int:
    """Create a new order. Returns order ID."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """INSERT INTO orders (user_id, items_json, total, coupon_code, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, json.dumps(items), total, coupon_code, datetime.utcnow().isoformat()),
        )
        await db.commit()
        return cursor.lastrowid


async def get_order(order_id: int) -> dict | None:
    """Get single order by ID."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def get_user_orders(user_id: int, limit: int = 20, offset: int = 0) -> list[dict]:
    """Get orders for a user with pagination."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (user_id, limit, offset),
        )
        return [dict(r) for r in await cursor.fetchall()]


async def get_all_orders(limit: int = 50, offset: int = 0) -> list[dict]:
    """Get all orders with pagination."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM orders ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        )
        return [dict(r) for r in await cursor.fetchall()]


async def update_order(order_id: int, **kwargs) -> None:
    """Update order fields dynamically."""
    allowed = {"status", "payment_status", "payment_method_id", "payment_proof_id", "coupon_code"}
    fields = {k: v for k, v in kwargs.items() if k in allowed}
    if not fields:
        return
    set_clause = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [order_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE orders SET {set_clause} WHERE id = ?", values)
        await db.commit()


async def get_order_count() -> int:
    """Get total order count."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM orders")
        return (await cursor.fetchone())[0]


async def get_total_revenue() -> float:
    """Get total revenue excluding cancelled orders."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT COALESCE(SUM(total), 0) FROM orders WHERE status != 'cancelled'"
        )
        return float((await cursor.fetchone())[0])


async def get_user_order_count(user_id: int) -> int:
    """Get total orders for a user."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT COUNT(*) FROM orders WHERE user_id = ?", (user_id,)
        )
        return (await cursor.fetchone())[0]


# ════════════════════════ COUPONS ════════════════════════

async def create_coupon(code: str, discount_percent: int, max_uses: int = 0) -> None:
    """Create a new coupon."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO coupons (code, discount_percent, max_uses) VALUES (?, ?, ?)",
            (code.upper(), discount_percent, max_uses),
        )
        await db.commit()


async def get_coupon(code: str) -> dict | None:
    """Get coupon by code."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM coupons WHERE code = ?", (code.upper(),))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def validate_coupon(code: str) -> dict | None:
    """Validate coupon: returns coupon dict if valid, None otherwise."""
    c = await get_coupon(code)
    if not c or not c["active"]:
        return None
    if c["max_uses"] > 0 and c["used_count"] >= c["max_uses"]:
        return None
    return c


async def use_coupon(code: str) -> None:
    """Increment coupon usage count."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE coupons SET used_count = used_count + 1 WHERE code = ?",
            (code.upper(),),
        )
        await db.commit()


async def delete_coupon(code: str) -> None:
    """Delete a coupon."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM coupons WHERE code = ?", (code.upper(),))
        await db.commit()


async def toggle_coupon(code: str) -> None:
    """Toggle coupon active/inactive."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE coupons SET active = CASE WHEN active = 1 THEN 0 ELSE 1 END WHERE code = ?",
            (code.upper(),),
        )
        await db.commit()


async def get_all_coupons() -> list[dict]:
    """Get all coupons."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM coupons ORDER BY code")
        return [dict(r) for r in await cursor.fetchall()]


# ════════════════════════ PAYMENT METHODS ════════════════════════

async def get_payment_methods() -> list[dict]:
    """Get active payment methods."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM payment_methods WHERE active = 1")
        return [dict(r) for r in await cursor.fetchall()]


async def get_all_payment_methods() -> list[dict]:
    """Get all payment methods."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM payment_methods ORDER BY id")
        return [dict(r) for r in await cursor.fetchall()]


async def get_payment_method(method_id: int) -> dict | None:
    """Get single payment method."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM payment_methods WHERE id = ?", (method_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def add_payment_method(name: str, details: str, emoji: str = "💳") -> int:
    """Add a new payment method. Returns ID."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO payment_methods (name, details, emoji) VALUES (?, ?, ?)",
            (name, details, emoji),
        )
        await db.commit()
        return cursor.lastrowid


async def delete_payment_method(method_id: int) -> None:
    """Delete a payment method."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM payment_methods WHERE id = ?", (method_id,))
        await db.commit()


# ════════════════════════ PAYMENT PROOFS ════════════════════════

async def create_payment_proof(user_id: int, order_id: int, method_id: int, file_id: str) -> int:
    """Save payment proof screenshot. Returns proof ID."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """INSERT INTO payment_proofs (user_id, order_id, method_id, file_id, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, order_id, method_id, file_id, datetime.utcnow().isoformat()),
        )
        await db.commit()
        return cursor.lastrowid


async def get_payment_proof(proof_id: int) -> dict | None:
    """Get single payment proof."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM payment_proofs WHERE id = ?", (proof_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def get_pending_proofs() -> list[dict]:
    """Get all pending payment proofs."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM payment_proofs WHERE status = 'pending' ORDER BY created_at DESC"
        )
        return [dict(r) for r in await cursor.fetchall()]


async def get_pending_proof_count() -> int:
    """Get count of pending proofs."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT COUNT(*) FROM payment_proofs WHERE status = 'pending'"
        )
        return (await cursor.fetchone())[0]


async def update_proof(proof_id: int, **kwargs) -> None:
    """Update proof fields (status, reviewed_by, admin_note)."""
    allowed = {"status", "reviewed_by", "admin_note"}
    fields = {k: v for k, v in kwargs.items() if k in allowed}
    if not fields:
        return
    set_clause = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [proof_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE payment_proofs SET {set_clause} WHERE id = ?", values)
        await db.commit()


# ════════════════════════ FORCE JOIN ════════════════════════

async def get_force_join_channels() -> list[dict]:
    """Get all force join channels."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM force_join_channels ORDER BY id")
        return [dict(r) for r in await cursor.fetchall()]


async def add_force_join_channel(channel_id: str, channel_name: str, channel_link: str) -> int:
    """Add a force join channel. Returns ID."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO force_join_channels (channel_id, channel_name, channel_link) VALUES (?, ?, ?)",
            (channel_id, channel_name, channel_link),
        )
        await db.commit()
        return cursor.lastrowid


async def delete_force_join_channel(fj_id: int) -> None:
    """Delete a force join channel."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM force_join_channels WHERE id = ?", (fj_id,))
        await db.commit()


# ════════════════════════ TICKETS ════════════════════════

async def create_ticket(user_id: int, subject: str) -> int:
    """Create a new support ticket. Returns ticket ID."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO tickets (user_id, subject, created_at) VALUES (?, ?, ?)",
            (user_id, subject, datetime.utcnow().isoformat()),
        )
        await db.commit()
        return cursor.lastrowid


async def get_ticket(ticket_id: int) -> dict | None:
    """Get single ticket by ID."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def get_user_tickets(user_id: int) -> list[dict]:
    """Get all tickets for a user."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM tickets WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        )
        return [dict(r) for r in await cursor.fetchall()]


async def get_all_tickets(status: str | None = None) -> list[dict]:
    """Get all tickets, optionally filtered by status."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if status:
            cursor = await db.execute(
                "SELECT * FROM tickets WHERE status = ? ORDER BY created_at DESC",
                (status,),
            )
        else:
            cursor = await db.execute("SELECT * FROM tickets ORDER BY created_at DESC")
        return [dict(r) for r in await cursor.fetchall()]


async def get_open_ticket_count() -> int:
    """Get count of open tickets."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM tickets WHERE status = 'open'")
        return (await cursor.fetchone())[0]


async def update_ticket(ticket_id: int, **kwargs) -> None:
    """Update ticket fields."""
    allowed = {"status", "closed_at"}
    fields = {k: v for k, v in kwargs.items() if k in allowed}
    if not fields:
        return
    set_clause = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [ticket_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE tickets SET {set_clause} WHERE id = ?", values)
        await db.commit()


async def add_ticket_message(ticket_id: int, sender_id: int, sender_type: str, message: str) -> int:
    """Add a message to a ticket. sender_type: 'user' or 'admin'. Returns message ID."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """INSERT INTO ticket_messages (ticket_id, sender_id, sender_type, message, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (ticket_id, sender_id, sender_type, message, datetime.utcnow().isoformat()),
        )
        await db.commit()
        return cursor.lastrowid


async def get_ticket_messages(ticket_id: int, limit: int = 20) -> list[dict]:
    """Get ticket messages (newest fetched, returned in chronological order)."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM ticket_messages WHERE ticket_id = ? ORDER BY created_at DESC LIMIT ?",
            (ticket_id, limit),
        )
        rows = [dict(r) for r in await cursor.fetchall()]
        return list(reversed(rows))


# ════════════════════════ PRODUCT FAQs ════════════════════════

async def add_product_faq(product_id: int, question: str, answer: str) -> int:
    """Add a FAQ to a product. Returns FAQ ID."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO product_faqs (product_id, question, answer) VALUES (?, ?, ?)",
            (product_id, question, answer),
        )
        await db.commit()
        return cursor.lastrowid


async def get_product_faqs(product_id: int) -> list[dict]:
    """Get all FAQs for a product."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM product_faqs WHERE product_id = ? ORDER BY sort_order, id",
            (product_id,),
        )
        return [dict(r) for r in await cursor.fetchall()]


async def get_faq_count(product_id: int) -> int:
    """Get FAQ count for a product."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT COUNT(*) FROM product_faqs WHERE product_id = ?", (product_id,)
        )
        return (await cursor.fetchone())[0]


async def delete_product_faq(faq_id: int) -> None:
    """Delete a FAQ entry."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM product_faqs WHERE id = ?", (faq_id,))
        await db.commit()


# ════════════════════════ PRODUCT MEDIA ════════════════════════

async def add_product_media(product_id: int, media_type: str, file_id: str, caption: str = "") -> int:
    """Add media to a product. media_type: video, voice, file. Returns ID."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO product_media (product_id, media_type, file_id, caption) VALUES (?, ?, ?, ?)",
            (product_id, media_type, file_id, caption),
        )
        await db.commit()
        return cursor.lastrowid


async def get_product_media(product_id: int, media_type: str | None = None) -> list[dict]:
    """Get media for a product, optionally filtered by type."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if media_type:
            cursor = await db.execute(
                "SELECT * FROM product_media WHERE product_id = ? AND media_type = ? ORDER BY id",
                (product_id, media_type),
            )
        else:
            cursor = await db.execute(
                "SELECT * FROM product_media WHERE product_id = ? ORDER BY id",
                (product_id,),
            )
        return [dict(r) for r in await cursor.fetchall()]


async def get_media_item(media_id: int) -> dict | None:
    """Get single media item."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM product_media WHERE id = ?", (media_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def delete_product_media(media_id: int) -> None:
    """Delete a media item."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM product_media WHERE id = ?", (media_id,))
        await db.commit()


async def get_media_type_counts(product_id: int) -> dict:
    """Get count of each media type for a product. Returns {type: count}."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT media_type, COUNT(*) FROM product_media WHERE product_id = ? GROUP BY media_type",
            (product_id,),
        )
        rows = await cursor.fetchall()
        return {r[0]: r[1] for r in rows}


# ════════════════════════ DAILY REWARDS ════════════════════════

async def get_last_reward(user_id: int) -> dict | None:
    """Get the most recent daily reward claim for a user."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM daily_rewards WHERE user_id = ? ORDER BY claimed_date DESC LIMIT 1",
            (user_id,),
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def claim_daily_reward(user_id: int) -> dict:
    """Claim daily reward. Returns {success, amount, streak, balance, message}."""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")

    last = await get_last_reward(user_id)

    if last and last["claimed_date"] == today:
        return {
            "success": False,
            "amount": last["reward_amount"],
            "streak": last["streak"],
            "balance": await get_user_balance(user_id),
            "message": "already_claimed",
        }

    if last and last["claimed_date"] == yesterday:
        streak = last["streak"] + 1
    else:
        streak = 1

    if streak <= 3:
        amount = 5.0
    elif streak <= 7:
        amount = 8.0
    elif streak <= 14:
        amount = 12.0
    else:
        amount = 20.0

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO daily_rewards (user_id, claimed_date, reward_amount, streak) VALUES (?, ?, ?, ?)",
            (user_id, today, amount, streak),
        )
        await db.commit()

    await update_user_balance(user_id, amount)
    balance = await get_user_balance(user_id)

    return {
        "success": True,
        "amount": amount,
        "streak": streak,
        "balance": balance,
        "message": "claimed",
    }


# ════════════════════════ ACTION LOGS ════════════════════════

async def add_action_log(action: str, user_id: int = 0, details: str = "") -> None:
    """Log an action for auditing."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO action_logs (action, user_id, details, created_at) VALUES (?, ?, ?, ?)",
            (action, user_id, details, datetime.utcnow().isoformat()),
        )
        await db.commit()


async def get_recent_logs(limit: int = 50) -> list[dict]:
    """Get recent action logs."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM action_logs ORDER BY created_at DESC LIMIT ?", (limit,)
        )
        return [dict(r) for r in await cursor.fetchall()]


# ════════════════════════ DASHBOARD ════════════════════════

async def get_dashboard_stats() -> dict:
    """Get all stats for admin dashboard."""
    return {
        "users": await get_user_count(),
        "products": await get_product_count(),
        "categories": await get_category_count(),
        "orders": await get_order_count(),
        "revenue": await get_total_revenue(),
        "pending_proofs": await get_pending_proof_count(),
        "open_tickets": await get_open_ticket_count(),
    }
