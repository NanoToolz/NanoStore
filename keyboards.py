"""NanoStore inline keyboards — every keyboard used across all handlers."""

import math
from telegram import InlineKeyboardButton as Btn, InlineKeyboardMarkup


# ════════════════════════ COMMON ════════════════════════

def back_kb(target: str) -> InlineKeyboardMarkup:
    """Single back button."""
    label_map = {
        "main_menu": "◀️ Main Menu",
        "shop": "◀️ Shop",
        "cart": "◀️ Cart",
        "admin": "◀️ Admin Panel",
        "adm_cats": "◀️ Categories",
        "adm_orders": "◀️ Orders",
        "adm_users": "◀️ Users",
        "adm_coupons": "◀️ Coupons",
        "adm_payments": "◀️ Payments",
        "adm_proofs": "◀️ Proofs",
        "adm_settings": "◀️ Settings",
        "adm_fj": "◀️ Force Join",
        "adm_tickets": "◀️ Tickets",
        "support": "◀️ Support",
        "my_orders": "◀️ My Orders",
        "my_tickets": "◀️ My Tickets",
        "checkout": "◀️ Checkout",
    }
    # Dynamic labels for patterns like adm_cat:5, adm_prod:12
    label = label_map.get(target, "◀️ Back")
    return InlineKeyboardMarkup([[Btn(label, callback_data=target)]])


# ════════════════════════ MAIN MENU ════════════════════════

def main_menu_kb(is_admin: bool = False) -> InlineKeyboardMarkup:
    """Main menu keyboard.

    Layout (user request):
    Row 1: 🛍️ Shop
    Row 2: 🛒 Cart | 📦 My Orders
    Row 3: 🎫 Support | ❓ Help
    Row 4: 🔍 Search | 💳 My Wallet
    Last (admin only): ⚙️ Admin Panel
    """
    rows = [
        [Btn("🛍️ Shop", callback_data="shop")],
        [Btn("🛒 Cart", callback_data="cart"), Btn("📦 My Orders", callback_data="my_orders")],
        [Btn("🎫 Support", callback_data="support"), Btn("❓ Help", callback_data="help")],
        [Btn("🔍 Search", callback_data="search"), Btn("💳 My Wallet", callback_data="wallet")],
    ]
    if is_admin:
        rows.append([Btn("⚙️ Admin Panel", callback_data="admin")])
    return InlineKeyboardMarkup(rows)


def force_join_kb(channels: list) -> InlineKeyboardMarkup:
    """Force join channels keyboard."""
    rows = []
    for ch in channels:
        rows.append([Btn(f"📢 {ch['name']}", url=ch["invite_link"])])
    rows.append([Btn("✅ I've Joined", callback_data="verify_join")])
    return InlineKeyboardMarkup(rows)


# ════════════════════════ CATALOG ════════════════════════

def categories_kb(categories: list) -> InlineKeyboardMarkup:
    """Categories grid (2 per row) + stock overview button."""
    rows = []
    for i in range(0, len(categories), 2):
        row = []
        for cat in categories[i:i + 2]:
            emoji = cat.get("emoji", "📁")
            row.append(Btn(f"{emoji} {cat['name']}", callback_data=f"cat:{cat['id']}"))
        rows.append(row)
    # Stock overview button
    rows.append([Btn("📊 Stock Overview", callback_data="stock_overview")])
    rows.append([Btn("◀️ Main Menu", callback_data="main_menu")])
    return InlineKeyboardMarkup(rows)


def products_kb(
    products: list, cat_id: int, currency: str,
    page: int = 1, per_page: int = 20,
) -> InlineKeyboardMarkup:
    """Products list with pagination."""
    total_pages = max(1, math.ceil(len(products) / per_page)) if products else 1
    start = (page - 1) * per_page
    display = products[start:start + per_page]

    rows = []
    for p in display:
        price = int(p["price"]) if p["price"] == int(p["price"]) else p["price"]
        stock_dot = "🟢" if p.get("stock", -1) != 0 else "🔴"
        rows.append([Btn(
            f"{stock_dot} {p['name']} — {currency} {price}",
            callback_data=f"prod:{p['id']}",
        )])

    # Pagination
    if total_pages > 1:
        nav = []
        if page > 1:
            nav.append(Btn("◀️ Prev", callback_data=f"cat:{cat_id}:p:{page - 1}"))
        nav.append(Btn(f"📄 {page}/{total_pages}", callback_data="noop"))
        if page < total_pages:
            nav.append(Btn("Next ▶️", callback_data=f"cat:{cat_id}:p:{page + 1}"))
        rows.append(nav)

    rows.append([Btn("◀️ Shop", callback_data="shop")])
    return InlineKeyboardMarkup(rows)


def product_detail_kb(
    product: dict,
    has_faq: bool = False,
    has_media: list = None,
) -> InlineKeyboardMarkup:
    """Product detail actions."""
    pid = product["id"]
    cat_id = product["category_id"]
    rows = []

    # Add to cart (only if in stock)
    if product.get("stock", -1) != 0:
        rows.append([Btn("🛒 Add to Cart", callback_data=f"add:{pid}")])

    # Media buttons
    if has_media:
        media_row = []
        for m in has_media:
            mtype = m["media_type"]
            labels = {"video": "🎬 Video", "voice": "🎙️ Voice", "file": "📎 File"}
            label = labels.get(mtype, f"📎 {mtype}")
            media_row.append(Btn(label, callback_data=f"prod_media:{pid}:{mtype}"))
        rows.append(media_row)

    # FAQ
    if has_faq:
        rows.append([Btn("❓ FAQs", callback_data=f"prod_faq:{pid}")])

    rows.append([Btn("◀️ Back", callback_data=f"cat:{cat_id}")])
    return InlineKeyboardMarkup(rows)


def faq_kb(faqs: list, prod_id: int) -> InlineKeyboardMarkup:
    """FAQ back button."""
    return InlineKeyboardMarkup([
        [Btn("◀️ Back to Product", callback_data=f"prod:{prod_id}")],
    ])


# ════════════════════════ CART ════════════════════════

def cart_kb(items: list) -> InlineKeyboardMarkup:
    """Cart with per-item controls."""
    rows = []
    for item in items:
        cid = item["cart_id"]
        rows.append([
            Btn("➖", callback_data=f"cart_dec:{cid}"),
            Btn(f"{item['quantity']}", callback_data="noop"),
            Btn("➕", callback_data=f"cart_inc:{cid}"),
            Btn("🗑️", callback_data=f"cart_del:{cid}"),
        ])

    rows.append([
        Btn("🗑️ Clear Cart", callback_data="cart_clear"),
        Btn("✅ Checkout", callback_data="checkout"),
    ])
    rows.append([Btn("◀️ Main Menu", callback_data="main_menu")])
    return InlineKeyboardMarkup(rows)


def empty_cart_kb() -> InlineKeyboardMarkup:
    """Empty cart options."""
    return InlineKeyboardMarkup([
        [Btn("🛍️ Shop", callback_data="shop")],
        [Btn("◀️ Main Menu", callback_data="main_menu")],
    ])


# ════════════════════════ ORDERS ════════════════════════

def checkout_kb(order_id: int, has_balance: bool = False) -> InlineKeyboardMarkup:
    """Checkout summary actions."""
    rows = [
        [Btn("🎫 Apply Coupon", callback_data=f"apply_coupon:{order_id}")],
    ]
    if has_balance:
        rows.append([Btn("💳 Use Balance", callback_data=f"apply_balance:{order_id}")])
    rows.append([
        Btn("✅ Confirm", callback_data=f"confirm_order:{order_id}"),
        Btn("❌ Cancel", callback_data=f"cancel_order:{order_id}"),
    ])
    return InlineKeyboardMarkup(rows)


def payment_methods_kb(methods: list, order_id: int) -> InlineKeyboardMarkup:
    """Payment methods selection."""
    rows = []
    for m in methods:
        emoji = m.get("emoji", "💳")
        rows.append([Btn(
            f"{emoji} {m['name']}",
            callback_data=f"pay_method:{order_id}:{m['id']}",
        )])
    rows.append([Btn("◀️ My Orders", callback_data="my_orders")])
    return InlineKeyboardMarkup(rows)


def orders_kb(
    orders: list, currency: str = "Rs",
    page: int = 1, per_page: int = 10,
) -> InlineKeyboardMarkup:
    """User orders list."""
    rows = []
    for o in orders:
        oid = o["id"]
        total = int(o["total"]) if o["total"] == int(o["total"]) else o["total"]
        emoji = _order_status_icon(o["status"])
        rows.append([Btn(
            f"{emoji} #{oid} — {currency} {total} — {o['status']}",
            callback_data=f"order:{oid}",
        )])

    # Pagination
    nav = []
    if page > 1:
        nav.append(Btn("◀️ Prev", callback_data=f"orders_p:{page - 1}"))
    if len(orders) >= per_page:
        nav.append(Btn("Next ▶️", callback_data=f"orders_p:{page + 1}"))
    if nav:
        rows.append(nav)

    rows.append([Btn("◀️ Main Menu", callback_data="main_menu")])
    return InlineKeyboardMarkup(rows)


def order_detail_kb(order_id: int, status: str) -> InlineKeyboardMarkup:
    """Order detail actions."""
    rows = []
    if status in ("confirmed", "pending"):
        rows.append([Btn("💳 Pay Now", callback_data=f"pay:{order_id}")])
    rows.append([Btn("◀️ My Orders", callback_data="my_orders")])
    return InlineKeyboardMarkup(rows)


def _order_status_icon(status: str) -> str:
    icons = {
        "pending": "⏳",
        "confirmed": "✅",
        "processing": "⚙️",
        "shipped": "🚚",
        "completed": "✅",
        "delivered": "📦",
        "cancelled": "❌",
    }
    return icons.get(status, "📦")


# ════════════════════════ ADMIN ════════════════════════

def admin_kb(pending_proofs: int = 0, open_tickets: int = 0, pending_topups: int = 0) -> InlineKeyboardMarkup:
    """Admin main panel."""
    proof_badge = f" ({pending_proofs})" if pending_proofs else ""
    ticket_badge = f" ({open_tickets})" if open_tickets else ""
    topup_badge = f" ({pending_topups})" if pending_topups else ""

    rows = [
        [Btn("📊 Dashboard", callback_data="adm_dash")],
        [Btn("📂 Categories", callback_data="adm_cats"), Btn("🛒 Orders", callback_data="adm_orders")],
        [Btn("👥 Users", callback_data="adm_users"), Btn("🎫 Coupons", callback_data="adm_coupons")],
        [Btn("💳 Payments", callback_data="adm_payments"), Btn(f"📸 Proofs{proof_badge}", callback_data="adm_proofs")],
        [Btn(f"💳 Top-Ups{topup_badge}", callback_data="adm_topups"), Btn(f"🎫 Tickets{ticket_badge}", callback_data="adm_tickets")],
        [Btn("⚙️ Settings", callback_data="adm_settings"), Btn("📢 Force Join", callback_data="adm_fj")],
        [Btn("📣 Broadcast", callback_data="adm_broadcast"), Btn("📥 Bulk Import", callback_data="adm_bulk")],
        [Btn("📊 Bulk Stock", callback_data="adm_bulk_stock")],
        [Btn("◀️ Main Menu", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(rows)


# ---- Admin: Categories ----

def admin_cats_kb(cats: list) -> InlineKeyboardMarkup:
    """Admin category list."""
    rows = []
    for c in cats:
        emoji = c.get("emoji", "📁")
        active = "✅" if c.get("active", True) else "⛔"
        rows.append([Btn(
            f"{active} {emoji} {c['name']}",
            callback_data=f"adm_cat:{c['id']}",
        )])
    rows.append([Btn("➕ Add Category", callback_data="adm_cat_add")])
    rows.append([Btn("◀️ Admin Panel", callback_data="admin")])
    return InlineKeyboardMarkup(rows)


def admin_cat_detail_kb(cat_id: int) -> InlineKeyboardMarkup:
    """Category detail admin actions."""
    return InlineKeyboardMarkup([
        [Btn("📦 Products", callback_data=f"adm_prods:{cat_id}")],
        [Btn("✏️ Edit", callback_data=f"adm_cat_edit:{cat_id}"),
         Btn("🖼️ Image", callback_data=f"adm_cat_img:{cat_id}")],
        [Btn("🗑️ Delete", callback_data=f"adm_cat_del:{cat_id}")],
        [Btn("◀️ Categories", callback_data="adm_cats")],
    ])


# ---- Admin: Products ----

def admin_prods_kb(products: list, cat_id: int, currency: str) -> InlineKeyboardMarkup:
    """Admin product list in category."""
    rows = []
    for p in products:
        price = int(p["price"]) if p["price"] == int(p["price"]) else p["price"]
        rows.append([Btn(
            f"🏷️ {p['name']} — {currency} {price}",
            callback_data=f"adm_prod:{p['id']}",
        )])
    rows.append([Btn("➕ Add Product", callback_data=f"adm_prod_add:{cat_id}")])
    rows.append([Btn("◀️ Category", callback_data=f"adm_cat:{cat_id}")])
    return InlineKeyboardMarkup(rows)


def admin_prod_detail_kb(prod_id: int) -> InlineKeyboardMarkup:
    """Product detail admin actions."""
    return InlineKeyboardMarkup([
        [
            Btn("✏️ Name", callback_data=f"adm_prod_edit:{prod_id}:name"),
            Btn("✏️ Desc", callback_data=f"adm_prod_edit:{prod_id}:description"),
            Btn("✏️ Price", callback_data=f"adm_prod_edit:{prod_id}:price"),
        ],
        [
            Btn("🖼️ Image", callback_data=f"adm_prod_img:{prod_id}"),
            Btn("📊 Stock", callback_data=f"adm_prod_stock:{prod_id}"),
        ],
        [
            Btn("❓ Add FAQ", callback_data=f"adm_prod_faq_add:{prod_id}"),
            Btn("🎬 Add Media", callback_data=f"adm_prod_media_add:{prod_id}"),
        ],
        [Btn("🗑️ Delete Product", callback_data=f"adm_prod_del:{prod_id}")],
        [Btn("◀️ Back", callback_data="adm_cats")],
    ])


# ---- Admin: Orders ----

def admin_orders_kb(orders: list, currency: str) -> InlineKeyboardMarkup:
    """Admin orders list."""
    rows = []
    for o in orders:
        oid = o["id"]
        total = int(o["total"]) if o["total"] == int(o["total"]) else o["total"]
        emoji = _order_status_icon(o["status"])
        rows.append([Btn(
            f"{emoji} #{oid} — {currency} {total} — {o['status']}",
            callback_data=f"adm_ord:{oid}",
        )])
    rows.append([Btn("◀️ Admin Panel", callback_data="admin")])
    return InlineKeyboardMarkup(rows)


def admin_order_detail_kb(order_id: int) -> InlineKeyboardMarkup:
    """Order admin actions."""
    statuses = [
        ("confirmed", "✅"), ("processing", "⚙️"), ("shipped", "🚚"),
        ("delivered", "📦"), ("completed", "✅"), ("cancelled", "❌"),
    ]

    rows = []
    row = []
    for st, em in statuses:
        row.append(Btn(f"{em} {st.title()}", callback_data=f"adm_ord_st:{order_id}:{st}"))
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)

    rows.append([Btn("◀️ Orders", callback_data="adm_orders")])
    return InlineKeyboardMarkup(rows)


# ---- Admin: Users ----

def admin_users_kb(users: list) -> InlineKeyboardMarkup:
    """Admin user list."""
    rows = []
    for u in users:
        uid = u["user_id"]
        name = u.get("full_name", str(uid)) or str(uid)
        ban_dot = "🔴" if u.get("banned") else "🟢"
        rows.append([Btn(
            f"{ban_dot} {name[:25]} ({uid})",
            callback_data=f"adm_user:{uid}",
        )])
    rows.append([Btn("◀️ Admin Panel", callback_data="admin")])
    return InlineKeyboardMarkup(rows)


def admin_user_detail_kb(uid: int, is_banned: bool) -> InlineKeyboardMarkup:
    """User admin actions."""
    rows = []
    if is_banned:
        rows.append([Btn("✅ Unban", callback_data=f"adm_unban:{uid}")])
    else:
        rows.append([Btn("🚫 Ban", callback_data=f"adm_ban:{uid}")])
    rows.append([Btn("◀️ Users", callback_data="adm_users")])
    return InlineKeyboardMarkup(rows)


# ---- Admin: Coupons ----

def admin_coupons_kb(coupons: list) -> InlineKeyboardMarkup:
    """Admin coupons list."""
    rows = []
    for c in coupons:
        code = c["code"]
        active = "✅" if c.get("active", True) else "⛔"
        disc = c.get("discount_percent", 0)
        used = c.get("used_count", 0)
        max_u = c.get("max_uses", 0)
        max_label = f"/{max_u}" if max_u else "/∞"
        rows.append([
            Btn(f"{active} {code} ({disc}%) [{used}{max_label}]", callback_data=f"adm_coupon_toggle:{code}"),
            Btn("🗑️", callback_data=f"adm_coupon_del:{code}"),
        ])
    rows.append([Btn("➕ Add Coupon", callback_data="adm_coupon_add")])
    rows.append([Btn("◀️ Admin Panel", callback_data="admin")])
    return InlineKeyboardMarkup(rows)


# ---- Admin: Payments ----

def admin_payments_kb(methods: list) -> InlineKeyboardMarkup:
    """Admin payment methods list."""
    rows = []
    for m in methods:
        emoji = m.get("emoji", "💳")
        rows.append([
            Btn(f"{emoji} {m['name']}", callback_data="noop"),
            Btn("🗑️", callback_data=f"adm_pay_del:{m['id']}"),
        ])
    rows.append([Btn("➕ Add Method", callback_data="adm_pay_add")])
    rows.append([Btn("◀️ Admin Panel", callback_data="admin")])
    return InlineKeyboardMarkup(rows)


# ---- Admin: Proofs ----

def admin_proofs_kb(proofs: list) -> InlineKeyboardMarkup:
    """Admin pending proofs list."""
    rows = []
    for p in proofs:
        pid = p["id"]
        oid = p.get("order_id", "?")
        rows.append([Btn(
            f"⏳ Proof #{pid} — Order #{oid}",
            callback_data=f"adm_proof:{pid}",
        )])
    if not proofs:
        rows.append([Btn("✅ No pending proofs", callback_data="noop")])
    rows.append([Btn("◀️ Admin Panel", callback_data="admin")])
    return InlineKeyboardMarkup(rows)


def admin_proof_detail_kb(proof_id: int) -> InlineKeyboardMarkup:
    """Proof detail admin actions."""
    return InlineKeyboardMarkup([
        [
            Btn("✅ Approve", callback_data=f"adm_proof_ok:{proof_id}"),
            Btn("❌ Reject", callback_data=f"adm_proof_rej:{proof_id}"),
        ],
        [Btn("📢 Post to Channel", callback_data=f"adm_proof_post:{proof_id}")],
        [Btn("◀️ Proofs", callback_data="adm_proofs")],
    ])


# ---- Admin: Tickets ----

def admin_tickets_kb(tickets: list) -> InlineKeyboardMarkup:
    """Admin tickets list."""
    rows = []
    for t in tickets:
        emoji = "🟢" if t["status"] == "open" else "🔴"
        rows.append([Btn(
            f"{emoji} #{t['id']} — {t['subject'][:25]}",
            callback_data=f"adm_ticket:{t['id']}",
        )])
    rows.append([Btn("◀️ Admin Panel", callback_data="admin")])
    return InlineKeyboardMarkup(rows)


def admin_ticket_detail_kb(ticket_id: int, is_open: bool = True) -> InlineKeyboardMarkup:
    """Ticket admin actions."""
    rows = []
    if is_open:
        rows.append([
            Btn("📝 Reply", callback_data=f"ticket_reply:{ticket_id}"),
            Btn("🔒 Close", callback_data=f"adm_ticket_close:{ticket_id}"),
        ])
    else:
        rows.append([Btn("🔓 Reopen", callback_data=f"adm_ticket_reopen:{ticket_id}")])
    rows.append([Btn("◀️ Tickets", callback_data="adm_tickets")])
    return InlineKeyboardMarkup(rows)


# ---- Admin: Force Join ----

def admin_fj_kb(channels: list) -> InlineKeyboardMarkup:
    """Admin force join channels list."""
    rows = []
    for ch in channels:
        rows.append([
            Btn(f"📢 {ch['name']}", callback_data="noop"),
            Btn("🗑️", callback_data=f"adm_fj_del:{ch['id']}"),
        ])
    rows.append([Btn("➕ Add Channel", callback_data="adm_fj_add")])
    rows.append([Btn("◀️ Admin Panel", callback_data="admin")])
    return InlineKeyboardMarkup(rows)


# ---- Admin: Settings ----

def admin_settings_kb() -> InlineKeyboardMarkup:
    """Admin settings keyboard with compact 2x style."""
    rows = [
        [
            Btn("🏪 Name", callback_data="adm_set:bot_name"),
            Btn("💰 Curr", callback_data="adm_set:currency"),
        ],
        [
            Btn("👋 Welcome", callback_data="adm_set:welcome_text"),
            Btn("🖼️ Images", callback_data="adm_img_panel"),
        ],
        [
            Btn("🛒 Min Order", callback_data="adm_set:min_order"),
            Btn("🎁 Reward", callback_data="adm_set:daily_reward"),
        ],
        [
            Btn("💳 Top-Up On/Off", callback_data="adm_set:topup_enabled"),
            Btn("💵 Min Top-Up", callback_data="adm_set:topup_min_amount"),
        ],
        [
            Btn("💸 Max Top-Up", callback_data="adm_set:topup_max_amount"),
            Btn("🎁 Bonus %", callback_data="adm_set:topup_bonus_percent"),
        ],
        [
            Btn("⏱️ Auto-Del", callback_data="adm_set:auto_delete"),
            Btn("🔧 Maint", callback_data="adm_set:maintenance"),
        ],
        [
            Btn("📝 Maint Txt", callback_data="adm_set:maintenance_text"),
            Btn("💳 Pay Info", callback_data="adm_set:payment_instructions"),
        ],
        [Btn("◀️ Admin Panel", callback_data="admin")],
    ]
    return InlineKeyboardMarkup(rows)


def admin_images_kb(statuses: dict) -> InlineKeyboardMarkup:
    """Admin images panel keyboard showing status for each screen.
    
    Args:
        statuses: Dict mapping setting keys to bool (True = set, False = not set)
    """
    def status_icon(key: str) -> str:
        return "✅" if statuses.get(key, False) else "❌"
    
    rows = [
        [Btn(f"📱 Welcome: {status_icon('welcome_image_id')}", callback_data="noop")],
        [
            Btn("Set Image", callback_data="adm_img_set:welcome_image_id"),
            Btn("Clear", callback_data="adm_img_clear:welcome_image_id"),
        ],
        [Btn(f"🛍️ Shop: {status_icon('shop_image_id')}", callback_data="noop")],
        [
            Btn("Set Image", callback_data="adm_img_set:shop_image_id"),
            Btn("Clear", callback_data="adm_img_clear:shop_image_id"),
        ],
        [Btn(f"🛒 Cart: {status_icon('cart_image_id')}", callback_data="noop")],
        [
            Btn("Set Image", callback_data="adm_img_set:cart_image_id"),
            Btn("Clear", callback_data="adm_img_clear:cart_image_id"),
        ],
        [Btn(f"📦 Orders: {status_icon('orders_image_id')}", callback_data="noop")],
        [
            Btn("Set Image", callback_data="adm_img_set:orders_image_id"),
            Btn("Clear", callback_data="adm_img_clear:orders_image_id"),
        ],
        [Btn(f"💳 Wallet: {status_icon('wallet_image_id')}", callback_data="noop")],
        [
            Btn("Set Image", callback_data="adm_img_set:wallet_image_id"),
            Btn("Clear", callback_data="adm_img_clear:wallet_image_id"),
        ],
        [Btn(f"🎫 Support: {status_icon('support_image_id')}", callback_data="noop")],
        [
            Btn("Set Image", callback_data="adm_img_set:support_image_id"),
            Btn("Clear", callback_data="adm_img_clear:support_image_id"),
        ],
        [Btn(f"⚙️ Admin Panel: {status_icon('admin_panel_image_id')}", callback_data="noop")],
        [
            Btn("Set Image", callback_data="adm_img_set:admin_panel_image_id"),
            Btn("Clear", callback_data="adm_img_clear:admin_panel_image_id"),
        ],
        [Btn("━━━━━━━━━━━━━━━━━━━", callback_data="noop")],
        [Btn("🔧 Toggle Images On/Off", callback_data="adm_img_toggle")],
        [Btn("◀️ Settings", callback_data="adm_settings")],
    ]
    return InlineKeyboardMarkup(rows)


# ---- Admin: Broadcast ----

def admin_broadcast_confirm_kb() -> InlineKeyboardMarkup:
    """Broadcast confirm/cancel."""
    return InlineKeyboardMarkup([
        [
            Btn("✅ Send Broadcast", callback_data="adm_broadcast_go"),
            Btn("❌ Cancel", callback_data="admin"),
        ],
    ])


# ════════════════════════ WALLET ════════════════════════

def wallet_kb() -> InlineKeyboardMarkup:
    """Wallet main menu."""
    return InlineKeyboardMarkup([
        [Btn("💰 Top-Up Wallet", callback_data="wallet_topup")],
        [Btn("📜 Top-Up History", callback_data="wallet_history")],
        [Btn("◀️ Main Menu", callback_data="main_menu")],
    ])


def wallet_topup_amounts_kb(min_amt: float, max_amt: float, currency: str) -> InlineKeyboardMarkup:
    """Wallet top-up amount selection."""
    presets = [500, 1000, 2000, 5000]
    rows = []
    row = []
    for amt in presets:
        if min_amt <= amt <= max_amt:
            row.append(Btn(f"{currency} {int(amt)}", callback_data=f"wallet_amt:{amt}"))
            if len(row) == 2:
                rows.append(row)
                row = []
    if row:
        rows.append(row)
    rows.append([Btn("✏️ Custom Amount", callback_data="wallet_amt_custom")])
    rows.append([Btn("◀️ Back", callback_data="wallet")])
    return InlineKeyboardMarkup(rows)


def wallet_pay_methods_kb(methods: list) -> InlineKeyboardMarkup:
    """Wallet payment methods selection."""
    rows = []
    for m in methods:
        emoji = m.get("emoji", "💳")
        rows.append([Btn(f"{emoji} {m['name']}", callback_data=f"wallet_pay:{m['id']}")])
    rows.append([Btn("◀️ Back", callback_data="wallet")])
    return InlineKeyboardMarkup(rows)


def admin_topups_kb(topups: list, currency: str) -> InlineKeyboardMarkup:
    """Admin topups list."""
    rows = []
    for t in topups:
        tid = t["id"]
        amt = int(t["amount"]) if t["amount"] == int(t["amount"]) else t["amount"]
        rows.append([Btn(f"⏳ #{tid} — {currency} {amt} — User {t['user_id']}", callback_data=f"adm_topup:{tid}")])
    if not topups:
        rows.append([Btn("✅ No pending top-ups", callback_data="noop")])
    rows.append([Btn("◀️ Admin Panel", callback_data="admin")])
    return InlineKeyboardMarkup(rows)


def admin_topup_detail_kb(topup_id: int) -> InlineKeyboardMarkup:
    """Admin topup detail actions."""
    return InlineKeyboardMarkup([
        [
            Btn("✅ Approve", callback_data=f"adm_topup_approve:{topup_id}"),
            Btn("❌ Reject", callback_data=f"adm_topup_reject:{topup_id}"),
        ],
        [Btn("◀️ Top-Ups", callback_data="adm_topups")],
    ])
