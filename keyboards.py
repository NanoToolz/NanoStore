"""NanoStore keyboards — all inline keyboard builders."""

import math
from telegram import InlineKeyboardButton as Btn, InlineKeyboardMarkup


# ════════════════════════ HELPERS ════════════════════════

def back_btn(target: str = "main_menu") -> Btn:
    """Reusable back button."""
    return Btn("◀️ Back", callback_data=target)


def back_kb(target: str = "main_menu") -> InlineKeyboardMarkup:
    """Single back-button keyboard."""
    return InlineKeyboardMarkup([[back_btn(target)]])


# ════════════════════════ USER KEYBOARDS ════════════════════════

def main_menu_kb(is_admin: bool = False, cart_count: int = 0) -> InlineKeyboardMarkup:
    """Main menu keyboard with dynamic cart count."""
    cart_label = f"🛒 Cart ({cart_count})" if cart_count > 0 else "🛒 Cart"
    rows = [
        [Btn("🛍️ Shop", callback_data="shop"),
         Btn("🔍 Search", callback_data="search")],
        [Btn(cart_label, callback_data="cart"),
         Btn("📦 My Orders", callback_data="my_orders")],
        [Btn("🎁 Daily Reward", callback_data="daily_reward"),
         Btn("🎫 Support", callback_data="support")],
        [Btn("ℹ️ Help", callback_data="help")],
    ]
    if is_admin:
        rows.append([Btn("⚙️ Admin Panel", callback_data="admin")])
    return InlineKeyboardMarkup(rows)


def categories_kb(categories: list[dict]) -> InlineKeyboardMarkup:
    """Category list — 2 per row."""
    rows = []
    row = []
    for c in categories:
        row.append(Btn(f"{c['emoji']} {c['name']}", callback_data=f"cat:{c['id']}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([Btn("◀️ Main Menu", callback_data="main_menu")])
    return InlineKeyboardMarkup(rows)


def products_kb(
    products: list[dict], cat_id: int, currency: str = "Rs",
    page: int = 1, total_count: int = 0, per_page: int = 20
) -> InlineKeyboardMarkup:
    """Product list with pagination."""
    rows = []
    for p in products:
        price = int(p['price']) if p['price'] == int(p['price']) else p['price']
        rows.append([Btn(
            f"🏷️ {p['name']} — {currency} {price}",
            callback_data=f"prod:{p['id']}"
        )])

    total_pages = max(1, math.ceil(total_count / per_page)) if total_count else 1
    if total_pages > 1:
        nav = []
        if page > 1:
            nav.append(Btn("◀️ Prev", callback_data=f"cat:{cat_id}:p:{page - 1}"))
        nav.append(Btn(f"Page {page}/{total_pages}", callback_data="noop"))
        if page < total_pages:
            nav.append(Btn("Next ▶️", callback_data=f"cat:{cat_id}:p:{page + 1}"))
        rows.append(nav)

    rows.append([Btn("◀️ Back to Categories", callback_data="shop")])
    return InlineKeyboardMarkup(rows)


def product_detail_kb(
    product_id: int, cat_id: int, stock: int = -1,
    faq_count: int = 0, media_counts: dict | None = None
) -> InlineKeyboardMarkup:
    """Product detail buttons: cart, FAQ, media, back."""
    rows = []

    if stock == 0:
        rows.append([Btn("🔴 Out of Stock", callback_data="noop")])
    else:
        rows.append([Btn("🛒 Add to Cart", callback_data=f"add:{product_id}")])

    if faq_count > 0:
        rows.append([Btn(f"❓ FAQ ({faq_count})", callback_data=f"prod_faq:{product_id}")])

    if media_counts:
        media_row = []
        if media_counts.get("video"):
            media_row.append(Btn("🎬 Video", callback_data=f"prod_media:{product_id}:video"))
        if media_counts.get("voice"):
            media_row.append(Btn("🎙️ Voice", callback_data=f"prod_media:{product_id}:voice"))
        if media_counts.get("file"):
            media_row.append(Btn("📎 Files", callback_data=f"prod_media:{product_id}:file"))
        if media_row:
            rows.append(media_row)

    rows.append([back_btn(f"cat:{cat_id}")])
    return InlineKeyboardMarkup(rows)


def product_faq_kb(product_id: int) -> InlineKeyboardMarkup:
    """Back button from FAQ view."""
    return InlineKeyboardMarkup([[back_btn(f"prod:{product_id}")]])


# ════════════════════════ CART ════════════════════════

def cart_kb(cart_items: list[dict]) -> InlineKeyboardMarkup:
    """Cart view with per-item controls."""
    rows = []
    for item in cart_items:
        rows.append([
            Btn("➖", callback_data=f"cart_dec:{item['id']}"),
            Btn(f"{item['quantity']}", callback_data="noop"),
            Btn("➕", callback_data=f"cart_inc:{item['id']}"),
            Btn("🗑️", callback_data=f"cart_del:{item['id']}"),
        ])
    rows.append([
        Btn("🗑️ Clear", callback_data="cart_clear"),
        Btn("✅ Checkout", callback_data="checkout"),
    ])
    rows.append([Btn("◀️ Main Menu", callback_data="main_menu")])
    return InlineKeyboardMarkup(rows)


def empty_cart_kb() -> InlineKeyboardMarkup:
    """Empty cart actions."""
    return InlineKeyboardMarkup([
        [Btn("🛍️ Shop", callback_data="shop")],
        [Btn("◀️ Main Menu", callback_data="main_menu")],
    ])


# ════════════════════════ CHECKOUT / ORDERS ════════════════════════

def checkout_kb(order_id: int, has_balance: bool = False) -> InlineKeyboardMarkup:
    """Checkout actions: coupon, balance, confirm, cancel."""
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


def payment_methods_kb(methods: list[dict], order_id: int) -> InlineKeyboardMarkup:
    """Payment method selection."""
    rows = []
    for m in methods:
        rows.append([Btn(
            f"{m['emoji']} {m['name']}",
            callback_data=f"pay_method:{order_id}:{m['id']}"
        )])
    rows.append([Btn("❌ Cancel", callback_data="main_menu")])
    return InlineKeyboardMarkup(rows)


def order_detail_kb(order_id: int, status: str = "pending") -> InlineKeyboardMarkup:
    """User order detail view."""
    rows = []
    if status == "pending":
        rows.append([Btn("💳 Pay Now", callback_data=f"pay:{order_id}")])
        rows.append([Btn("❌ Cancel Order", callback_data=f"cancel_order:{order_id}")])
    rows.append([back_btn("my_orders")])
    return InlineKeyboardMarkup(rows)


def orders_kb(orders: list[dict], currency: str = "Rs", page: int = 1, per_page: int = 10) -> InlineKeyboardMarkup:
    """User orders list with pagination."""
    from helpers import status_emoji
    rows = []
    for o in orders:
        emoji = status_emoji(o["status"])
        total = int(o['total']) if o['total'] == int(o['total']) else o['total']
        rows.append([Btn(
            f"{emoji} #{o['id']} — {currency} {total} ({o['status']})",
            callback_data=f"order:{o['id']}"
        )])

    nav = []
    if page > 1:
        nav.append(Btn("◀️ Prev", callback_data=f"orders_p:{page - 1}"))
    if len(orders) >= per_page:
        nav.append(Btn("Next ▶️", callback_data=f"orders_p:{page + 1}"))
    if nav:
        rows.append(nav)

    rows.append([Btn("◀️ Main Menu", callback_data="main_menu")])
    return InlineKeyboardMarkup(rows)


# ════════════════════════ TICKETS ════════════════════════

def support_kb(tickets: list[dict]) -> InlineKeyboardMarkup:
    """Support menu: new ticket + existing tickets."""
    rows = [[Btn("➕ New Ticket", callback_data="new_ticket")]]
    for t in tickets[:10]:
        status = "🟢" if t["status"] == "open" else "⚪"
        rows.append([Btn(
            f"{status} #{t['id']} — {t['subject'][:30]}",
            callback_data=f"ticket:{t['id']}"
        )])
    rows.append([Btn("◀️ Main Menu", callback_data="main_menu")])
    return InlineKeyboardMarkup(rows)


def ticket_detail_kb(ticket_id: int, status: str = "open") -> InlineKeyboardMarkup:
    """Ticket detail actions."""
    rows = []
    if status == "open":
        rows.append([
            Btn("✉️ Reply", callback_data=f"ticket_reply:{ticket_id}"),
            Btn("🔒 Close", callback_data=f"ticket_close:{ticket_id}"),
        ])
    else:
        rows.append([Btn("🔓 Reopen", callback_data=f"ticket_reopen:{ticket_id}")])
    rows.append([back_btn("support")])
    return InlineKeyboardMarkup(rows)


# ════════════════════════ DAILY REWARD ════════════════════════

def reward_kb(claimed: bool = False) -> InlineKeyboardMarkup:
    """Daily reward screen buttons."""
    rows = []
    if not claimed:
        rows.append([Btn("🎁 Claim Reward!", callback_data="claim_reward")])
    rows.append([Btn("◀️ Main Menu", callback_data="main_menu")])
    return InlineKeyboardMarkup(rows)


# ════════════════════════ FORCE JOIN ════════════════════════

def force_join_kb(channels: list[dict]) -> InlineKeyboardMarkup:
    """Force join screen with channel URL buttons + verify."""
    rows = []
    for ch in channels:
        rows.append([Btn(f"📢 Join {ch['channel_name']}", url=ch["channel_link"])])
    rows.append([Btn("✅ I've Joined — Verify", callback_data="verify_join")])
    return InlineKeyboardMarkup(rows)


# ════════════════════════ ADMIN KEYBOARDS ════════════════════════

def admin_kb(pending_proofs: int = 0, open_tickets: int = 0) -> InlineKeyboardMarkup:
    """Admin panel main keyboard."""
    proofs_label = f"📸 Proofs ({pending_proofs})" if pending_proofs else "📸 Proofs"
    tickets_label = f"🎫 Tickets ({open_tickets})" if open_tickets else "🎫 Tickets"
    return InlineKeyboardMarkup([
        [Btn("📂 Categories", callback_data="adm_cats"),
         Btn("📦 Products", callback_data="adm_cats")],
        [Btn("🛒 Orders", callback_data="adm_orders"),
         Btn("👥 Users", callback_data="adm_users")],
        [Btn("🎫 Coupons", callback_data="adm_coupons"),
         Btn("💳 Payments", callback_data="adm_payments")],
        [Btn(proofs_label, callback_data="adm_proofs"),
         Btn(tickets_label, callback_data="adm_tickets")],
        [Btn("📢 Force Join", callback_data="adm_fj"),
         Btn("📥 Bulk Import", callback_data="adm_bulk")],
        [Btn("📊 Dashboard", callback_data="adm_dash"),
         Btn("⚙️ Settings", callback_data="adm_settings")],
        [Btn("📣 Broadcast", callback_data="adm_broadcast")],
        [Btn("◀️ Main Menu", callback_data="main_menu")],
    ])


def admin_cats_kb(categories: list[dict]) -> InlineKeyboardMarkup:
    """Admin categories list."""
    rows = []
    for c in categories:
        rows.append([Btn(
            f"{c['emoji']} {c['name']}",
            callback_data=f"adm_cat:{c['id']}"
        )])
    rows.append([Btn("➕ Add Category", callback_data="adm_cat_add")])
    rows.append([back_btn("admin")])
    return InlineKeyboardMarkup(rows)


def admin_cat_detail_kb(cat_id: int) -> InlineKeyboardMarkup:
    """Admin category detail actions."""
    return InlineKeyboardMarkup([
        [Btn("✏️ Edit", callback_data=f"adm_cat_edit:{cat_id}"),
         Btn("🖼️ Image", callback_data=f"adm_cat_img:{cat_id}")],
        [Btn("📦 Products", callback_data=f"adm_prods:{cat_id}"),
         Btn("🗑️ Delete", callback_data=f"adm_cat_del:{cat_id}")],
        [back_btn("adm_cats")],
    ])


def admin_prods_kb(products: list[dict], cat_id: int, currency: str = "Rs") -> InlineKeyboardMarkup:
    """Admin products list in a category."""
    rows = []
    for p in products:
        price = int(p['price']) if p['price'] == int(p['price']) else p['price']
        rows.append([Btn(
            f"{p['name']} — {currency} {price}",
            callback_data=f"adm_prod:{p['id']}"
        )])
    rows.append([Btn("➕ Add Product", callback_data=f"adm_prod_add:{cat_id}")])
    rows.append([back_btn(f"adm_cat:{cat_id}")])
    return InlineKeyboardMarkup(rows)


def admin_prod_detail_kb(prod_id: int) -> InlineKeyboardMarkup:
    """Admin product detail actions."""
    return InlineKeyboardMarkup([
        [Btn("✏️ Name", callback_data=f"adm_prod_edit:{prod_id}:name"),
         Btn("💰 Price", callback_data=f"adm_prod_edit:{prod_id}:price")],
        [Btn("📝 Desc", callback_data=f"adm_prod_edit:{prod_id}:description"),
         Btn("📊 Stock", callback_data=f"adm_prod_stock:{prod_id}")],
        [Btn("🖼️ Image", callback_data=f"adm_prod_img:{prod_id}"),
         Btn("❓ FAQ", callback_data=f"adm_prod_faq_add:{prod_id}")],
        [Btn("🎬 Media", callback_data=f"adm_prod_media_add:{prod_id}:video"),
         Btn("🗑️ Delete", callback_data=f"adm_prod_del:{prod_id}")],
        [back_btn("adm_cats")],
    ])


def admin_orders_kb(orders: list[dict], currency: str = "Rs") -> InlineKeyboardMarkup:
    """Admin orders list."""
    from helpers import status_emoji
    rows = []
    for o in orders[:20]:
        emoji = status_emoji(o["status"])
        total = int(o['total']) if o['total'] == int(o['total']) else o['total']
        rows.append([Btn(
            f"{emoji} #{o['id']} — {currency} {total}",
            callback_data=f"adm_order:{o['id']}"
        )])
    rows.append([back_btn("admin")])
    return InlineKeyboardMarkup(rows)


def admin_order_detail_kb(order_id: int) -> InlineKeyboardMarkup:
    """Admin order status change buttons."""
    statuses = [
        ("confirmed", "✅"), ("processing", "🔵"), ("shipped", "📦"),
        ("delivered", "🌟"), ("cancelled", "❌"),
    ]
    rows = []
    row = []
    for s, emoji in statuses:
        row.append(Btn(f"{emoji} {s.title()}", callback_data=f"adm_order_status:{order_id}:{s}"))
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([back_btn("adm_orders")])
    return InlineKeyboardMarkup(rows)


def admin_users_kb(users: list[dict]) -> InlineKeyboardMarkup:
    """Admin users list."""
    rows = []
    for u in users[:20]:
        banned = "🔴" if u["banned"] else "🟢"
        name = u["full_name"] or u["username"] or str(u["user_id"])
        rows.append([Btn(
            f"{banned} {name}",
            callback_data=f"adm_user:{u['user_id']}"
        )])
    rows.append([back_btn("admin")])
    return InlineKeyboardMarkup(rows)


def admin_user_detail_kb(user_id: int, is_banned: bool) -> InlineKeyboardMarkup:
    """Admin user detail: ban/unban."""
    if is_banned:
        action_btn = Btn("✅ Unban", callback_data=f"adm_unban:{user_id}")
    else:
        action_btn = Btn("🚫 Ban", callback_data=f"adm_ban:{user_id}")
    return InlineKeyboardMarkup([
        [action_btn],
        [back_btn("adm_users")],
    ])


def admin_coupons_kb(coupons: list[dict]) -> InlineKeyboardMarkup:
    """Admin coupons list."""
    rows = []
    for c in coupons:
        active = "🟢" if c["active"] else "🔴"
        rows.append([Btn(
            f"{active} {c['code']} — {c['discount_percent']}% off",
            callback_data=f"adm_coupon_toggle:{c['code']}"
        )])
    rows.append([Btn("➕ Add Coupon", callback_data="adm_coupon_add")])
    rows.append([back_btn("admin")])
    return InlineKeyboardMarkup(rows)


def admin_payments_kb(methods: list[dict]) -> InlineKeyboardMarkup:
    """Admin payment methods list."""
    rows = []
    for m in methods:
        rows.append([Btn(
            f"{m['emoji']} {m['name']}",
            callback_data=f"adm_pay_del:{m['id']}"
        )])
    rows.append([Btn("➕ Add Payment Method", callback_data="adm_pay_add")])
    rows.append([back_btn("admin")])
    return InlineKeyboardMarkup(rows)


def admin_proofs_kb(proofs: list[dict]) -> InlineKeyboardMarkup:
    """Admin pending proofs list."""
    rows = []
    for p in proofs[:20]:
        rows.append([Btn(
            f"📸 Proof #{p['id']} — Order #{p['order_id']}",
            callback_data=f"adm_proof:{p['id']}"
        )])
    if not proofs:
        rows.append([Btn("✅ No pending proofs", callback_data="noop")])
    rows.append([back_btn("admin")])
    return InlineKeyboardMarkup(rows)


def admin_proof_detail_kb(proof_id: int) -> InlineKeyboardMarkup:
    """Admin proof review: approve/reject/post."""
    return InlineKeyboardMarkup([
        [Btn("✅ Approve", callback_data=f"adm_proof_approve:{proof_id}"),
         Btn("❌ Reject", callback_data=f"adm_proof_reject:{proof_id}")],
        [Btn("📢 Post to Channel", callback_data=f"adm_proof_post:{proof_id}")],
        [back_btn("adm_proofs")],
    ])


def admin_tickets_kb(tickets: list[dict]) -> InlineKeyboardMarkup:
    """Admin tickets list."""
    rows = []
    for t in tickets[:20]:
        status = "🟢" if t["status"] == "open" else "⚪"
        rows.append([Btn(
            f"{status} #{t['id']} — {t['subject'][:30]}",
            callback_data=f"adm_ticket:{t['id']}"
        )])
    if not tickets:
        rows.append([Btn("✅ No open tickets", callback_data="noop")])
    rows.append([back_btn("admin")])
    return InlineKeyboardMarkup(rows)


def admin_ticket_detail_kb(ticket_id: int, status: str = "open") -> InlineKeyboardMarkup:
    """Admin ticket actions."""
    rows = []
    if status == "open":
        rows.append([
            Btn("✉️ Reply", callback_data=f"adm_ticket_reply:{ticket_id}"),
            Btn("🔒 Close", callback_data=f"adm_ticket_close:{ticket_id}"),
        ])
    else:
        rows.append([Btn("🔓 Reopen", callback_data=f"adm_ticket:{ticket_id}")])
    rows.append([back_btn("adm_tickets")])
    return InlineKeyboardMarkup(rows)


def admin_fj_kb(channels: list[dict]) -> InlineKeyboardMarkup:
    """Admin force join channels list."""
    rows = []
    for ch in channels:
        rows.append([Btn(
            f"📢 {ch['channel_name']}",
            callback_data=f"adm_fj_del:{ch['id']}"
        )])
    rows.append([Btn("➕ Add Channel", callback_data="adm_fj_add")])
    rows.append([back_btn("admin")])
    return InlineKeyboardMarkup(rows)


def admin_bulk_kb() -> InlineKeyboardMarkup:
    """Admin bulk import options."""
    return InlineKeyboardMarkup([
        [Btn("📥 Bulk Products", callback_data="adm_bulk")],
        [Btn("📊 Bulk Stock Update", callback_data="adm_bulk_stock")],
        [back_btn("admin")],
    ])


def admin_settings_kb(settings: dict) -> InlineKeyboardMarkup:
    """Admin settings list."""
    setting_labels = {
        "store_name": "🏠 Store Name",
        "currency": "💱 Currency",
        "min_order": "💰 Min Order",
        "contact": "📞 Contact",
        "welcome_message": "📝 Welcome Message",
        "welcome_image": "🖼️ Welcome Image",
    }
    rows = []
    for key, label in setting_labels.items():
        val = settings.get(key, "")
        display = val[:20] if val else "(not set)"
        rows.append([Btn(f"{label}: {display}", callback_data=f"adm_set:{key}")])
    rows.append([back_btn("admin")])
    return InlineKeyboardMarkup(rows)


def admin_broadcast_confirm_kb() -> InlineKeyboardMarkup:
    """Confirm broadcast."""
    return InlineKeyboardMarkup([
        [Btn("✅ Send to All Users", callback_data="adm_broadcast_confirm"),
         Btn("❌ Cancel", callback_data="admin")],
    ])
