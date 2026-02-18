import aiosqlite
import json
from config import DATABASE


async def init_db():
    async with aiosqlite.connect(DATABASE) as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                joined TEXT DEFAULT (datetime('now')),
                banned INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                emoji TEXT DEFAULT '📦'
            );
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                image_id TEXT,
                category_id INTEGER,
                active INTEGER DEFAULT 1,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            );
            CREATE TABLE IF NOT EXISTS cart (
                user_id INTEGER,
                product_id INTEGER,
                quantity INTEGER DEFAULT 1,
                PRIMARY KEY (user_id, product_id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            );
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                items TEXT NOT NULL,
                total REAL NOT NULL,
                status TEXT DEFAULT 'pending',
                coupon_code TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS coupons (
                code TEXT PRIMARY KEY,
                discount_percent INTEGER NOT NULL,
                max_uses INTEGER DEFAULT -1,
                used_count INTEGER DEFAULT 0,
                active INTEGER DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            );
        """)
        await db.commit()


# ==================== USERS ====================

async def add_user(user_id, username, full_name):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, username, full_name) VALUES (?, ?, ?)",
            (user_id, username, full_name),
        )
        await db.commit()

async def get_user(user_id):
    async with aiosqlite.connect(DATABASE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cur:
            return await cur.fetchone()

async def get_all_users():
    async with aiosqlite.connect(DATABASE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users ORDER BY joined DESC") as cur:
            return await cur.fetchall()

async def get_user_count():
    async with aiosqlite.connect(DATABASE) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cur:
            return (await cur.fetchone())[0]

async def ban_user(user_id):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("UPDATE users SET banned = 1 WHERE user_id = ?", (user_id,))
        await db.commit()

async def unban_user(user_id):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("UPDATE users SET banned = 0 WHERE user_id = ?", (user_id,))
        await db.commit()

async def is_banned(user_id):
    async with aiosqlite.connect(DATABASE) as db:
        async with db.execute("SELECT banned FROM users WHERE user_id = ?", (user_id,)) as cur:
            row = await cur.fetchone()
            return row and row[0] == 1


# ==================== CATEGORIES ====================

async def add_category(name, emoji="📦"):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("INSERT INTO categories (name, emoji) VALUES (?, ?)", (name, emoji))
        await db.commit()

async def get_categories():
    async with aiosqlite.connect(DATABASE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM categories ORDER BY name") as cur:
            return await cur.fetchall()

async def get_category(cat_id):
    async with aiosqlite.connect(DATABASE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM categories WHERE id = ?", (cat_id,)) as cur:
            return await cur.fetchone()

async def update_category(cat_id, name, emoji):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("UPDATE categories SET name=?, emoji=? WHERE id=?", (name, emoji, cat_id))
        await db.commit()

async def delete_category(cat_id):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("DELETE FROM categories WHERE id = ?", (cat_id,))
        await db.execute("DELETE FROM products WHERE category_id = ?", (cat_id,))
        await db.commit()


# ==================== PRODUCTS ====================

async def add_product(name, description, price, image_id, category_id):
    async with aiosqlite.connect(DATABASE) as db:
        cur = await db.execute(
            "INSERT INTO products (name,description,price,image_id,category_id) VALUES (?,?,?,?,?)",
            (name, description, price, image_id, category_id),
        )
        await db.commit()
        return cur.lastrowid

async def get_product(product_id):
    async with aiosqlite.connect(DATABASE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM products WHERE id = ?", (product_id,)) as cur:
            return await cur.fetchone()

async def get_products_by_category(category_id):
    async with aiosqlite.connect(DATABASE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM products WHERE category_id=? AND active=1", (category_id,)
        ) as cur:
            return await cur.fetchall()

async def get_all_products():
    async with aiosqlite.connect(DATABASE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM products WHERE active=1 ORDER BY name") as cur:
            return await cur.fetchall()

async def update_product_field(product_id, field, value):
    allowed = {"name","description","price","image_id","category_id","active"}
    if field not in allowed:
        return
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute(f"UPDATE products SET {field}=? WHERE id=?", (value, product_id))
        await db.commit()

async def delete_product(product_id):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("DELETE FROM products WHERE id = ?", (product_id,))
        await db.execute("DELETE FROM cart WHERE product_id = ?", (product_id,))
        await db.commit()

async def search_products(query):
    async with aiosqlite.connect(DATABASE) as db:
        db.row_factory = aiosqlite.Row
        q = f"%{query}%"
        async with db.execute(
            "SELECT * FROM products WHERE active=1 AND (name LIKE ? OR description LIKE ?)", (q, q)
        ) as cur:
            return await cur.fetchall()

async def get_product_count():
    async with aiosqlite.connect(DATABASE) as db:
        async with db.execute("SELECT COUNT(*) FROM products WHERE active=1") as cur:
            return (await cur.fetchone())[0]


# ==================== CART ====================

async def add_to_cart(user_id, product_id):
    async with aiosqlite.connect(DATABASE) as db:
        row = await (await db.execute(
            "SELECT quantity FROM cart WHERE user_id=? AND product_id=?", (user_id, product_id)
        )).fetchone()
        if row:
            await db.execute(
                "UPDATE cart SET quantity=quantity+1 WHERE user_id=? AND product_id=?",
                (user_id, product_id),
            )
        else:
            await db.execute(
                "INSERT INTO cart (user_id,product_id,quantity) VALUES (?,?,1)",
                (user_id, product_id),
            )
        await db.commit()

async def decrease_cart_qty(user_id, product_id):
    async with aiosqlite.connect(DATABASE) as db:
        row = await (await db.execute(
            "SELECT quantity FROM cart WHERE user_id=? AND product_id=?", (user_id, product_id)
        )).fetchone()
        if row and row[0] > 1:
            await db.execute(
                "UPDATE cart SET quantity=quantity-1 WHERE user_id=? AND product_id=?",
                (user_id, product_id),
            )
        else:
            await db.execute(
                "DELETE FROM cart WHERE user_id=? AND product_id=?", (user_id, product_id)
            )
        await db.commit()

async def remove_from_cart(user_id, product_id):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("DELETE FROM cart WHERE user_id=? AND product_id=?", (user_id, product_id))
        await db.commit()

async def get_cart(user_id):
    async with aiosqlite.connect(DATABASE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """SELECT c.quantity, p.id, p.name, p.price, p.image_id
               FROM cart c JOIN products p ON c.product_id = p.id
               WHERE c.user_id = ?""", (user_id,)
        ) as cur:
            return await cur.fetchall()

async def clear_cart(user_id):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
        await db.commit()

async def get_cart_total(user_id):
    async with aiosqlite.connect(DATABASE) as db:
        async with db.execute(
            """SELECT SUM(p.price * c.quantity)
               FROM cart c JOIN products p ON c.product_id = p.id
               WHERE c.user_id = ?""", (user_id,)
        ) as cur:
            return (await cur.fetchone())[0] or 0.0

async def get_cart_count(user_id):
    async with aiosqlite.connect(DATABASE) as db:
        async with db.execute(
            "SELECT SUM(quantity) FROM cart WHERE user_id = ?", (user_id,)
        ) as cur:
            return (await cur.fetchone())[0] or 0


# ==================== ORDERS ====================

async def create_order(user_id, items, total, coupon_code=None):
    async with aiosqlite.connect(DATABASE) as db:
        cur = await db.execute(
            "INSERT INTO orders (user_id,items,total,coupon_code) VALUES (?,?,?,?)",
            (user_id, json.dumps(items), total, coupon_code),
        )
        await db.commit()
        return cur.lastrowid

async def get_order(order_id):
    async with aiosqlite.connect(DATABASE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM orders WHERE id = ?", (order_id,)) as cur:
            return await cur.fetchone()

async def get_user_orders(user_id):
    async with aiosqlite.connect(DATABASE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM orders WHERE user_id=? ORDER BY created_at DESC", (user_id,)
        ) as cur:
            return await cur.fetchall()

async def get_all_orders(limit=50):
    async with aiosqlite.connect(DATABASE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM orders ORDER BY created_at DESC LIMIT ?", (limit,)
        ) as cur:
            return await cur.fetchall()

async def update_order_status(order_id, status):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("UPDATE orders SET status=? WHERE id=?", (status, order_id))
        await db.commit()

async def get_order_count():
    async with aiosqlite.connect(DATABASE) as db:
        async with db.execute("SELECT COUNT(*) FROM orders") as cur:
            return (await cur.fetchone())[0]

async def get_total_revenue():
    async with aiosqlite.connect(DATABASE) as db:
        async with db.execute(
            "SELECT SUM(total) FROM orders WHERE status != 'cancelled'"
        ) as cur:
            return (await cur.fetchone())[0] or 0.0


# ==================== COUPONS ====================

async def create_coupon(code, discount_percent, max_uses=-1):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute(
            "INSERT INTO coupons (code,discount_percent,max_uses) VALUES (?,?,?)",
            (code.upper(), discount_percent, max_uses),
        )
        await db.commit()

async def get_coupon(code):
    """Get a single coupon by code."""
    async with aiosqlite.connect(DATABASE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM coupons WHERE code=?", (code.upper(),)) as cur:
            return await cur.fetchone()

async def validate_coupon(code):
    async with aiosqlite.connect(DATABASE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM coupons WHERE code=?", (code.upper(),)) as cur:
            c = await cur.fetchone()
    if not c or not c["active"]:
        return None
    if c["max_uses"] != -1 and c["used_count"] >= c["max_uses"]:
        return None
    return c

async def use_coupon(code):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute(
            "UPDATE coupons SET used_count=used_count+1 WHERE code=?", (code.upper(),)
        )
        await db.commit()

async def delete_coupon(code):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("DELETE FROM coupons WHERE code=?", (code.upper(),))
        await db.commit()

async def get_all_coupons():
    async with aiosqlite.connect(DATABASE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM coupons ORDER BY code") as cur:
            return await cur.fetchall()


# ==================== SETTINGS + STATS ====================

async def get_setting(key, default=None):
    async with aiosqlite.connect(DATABASE) as db:
        async with db.execute("SELECT value FROM settings WHERE key=?", (key,)) as cur:
            row = await cur.fetchone()
            return row[0] if row else default

async def set_setting(key, value):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute(
            "INSERT OR REPLACE INTO settings (key,value) VALUES (?,?)", (key, str(value))
        )
        await db.commit()

async def get_dashboard_stats():
    return {
        "users": await get_user_count(),
        "products": await get_product_count(),
        "orders": await get_order_count(),
        "revenue": await get_total_revenue(),
    }
