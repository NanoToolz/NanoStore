"""NanoStore admin handlers — dashboard, categories, products, orders, users,
coupons, payments, proofs, settings, force join, bulk, broadcast."""

import json
import logging
from datetime import datetime
from html import escape as html_escape
from telegram import Update, InlineKeyboardButton as Btn, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import ADMIN_ID, PROOFS_CHANNEL_ID
from database import (
    get_dashboard_stats,
    get_all_categories,
    get_category,
    add_category,
    update_category,
    delete_category,
    get_products_by_category,
    get_product_count_in_category,
    get_product,
    add_product,
    update_product,
    delete_product,
    get_all_orders,
    get_order,
    update_order,
    get_all_users,
    get_user,
    get_user_count,
    ban_user,
    unban_user,
    get_user_order_count,
    get_user_balance,
    get_all_coupons,
    create_coupon,
    delete_coupon,
    toggle_coupon,
    get_all_payment_methods,
    add_payment_method,
    delete_payment_method,
    get_pending_proofs,
    get_pending_proof_count,
    get_payment_proof,
    update_proof,
    get_payment_method,
    get_all_settings,
    get_setting,
    set_setting,
    get_force_join_channels,
    add_force_join_channel,
    delete_force_join_channel,
    add_product_faq,
    delete_product_faq,
    get_product_faqs,
    add_product_media,
    delete_product_media,
    get_product_media,
    add_action_log,
    search_products,
    get_open_ticket_count,
)
from helpers import safe_edit, separator, log_action, format_stock, status_emoji
from keyboards import (
    admin_kb,
    admin_cats_kb,
    admin_cat_detail_kb,
    admin_prods_kb,
    admin_prod_detail_kb,
    admin_orders_kb,
    admin_order_detail_kb,
    admin_users_kb,
    admin_user_detail_kb,
    admin_coupons_kb,
    admin_payments_kb,
    admin_proofs_kb,
    admin_proof_detail_kb,
    admin_tickets_kb,
    admin_ticket_detail_kb,
    admin_fj_kb,
    admin_settings_kb,
    admin_broadcast_confirm_kb,
    back_kb,
)

logger = logging.getLogger(__name__)


def _is_admin(user_id: int) -> bool:
    """Check if user is the admin."""
    return user_id == ADMIN_ID


# ════════════════════════ ADMIN PANEL ════════════════════════

async def admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show admin panel."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        await query.answer("⛔ Access denied.", show_alert=True)
        return

    context.user_data.pop("state", None)
    context.user_data.pop("temp", None)

    stats = await get_dashboard_stats()
    currency = await get_setting("currency", "Rs")
    revenue = int(stats['revenue']) if stats['revenue'] == int(stats['revenue']) else f"{stats['revenue']:.2f}"

    text = (
        f"⚙️ <b>Admin Panel</b>\n"
        f"{separator()}\n"
        f"👥 Users: {stats['users']} | 📦 Orders: {stats['orders']}\n"
        f"💰 Revenue: {currency} {revenue} | ⏳ Proofs: {stats['pending_proofs']}\n"
        f"🎫 Tickets: {stats['open_tickets']}"
    )

    await safe_edit(
        query, text,
        reply_markup=admin_kb(stats['pending_proofs'], stats['open_tickets'])
    )


async def back_admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Back to admin panel."""
    await admin_handler(update, context)


# ════════════════════════ DASHBOARD ════════════════════════

async def admin_dashboard_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show detailed dashboard stats."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    stats = await get_dashboard_stats()
    currency = await get_setting("currency", "Rs")
    revenue = int(stats['revenue']) if stats['revenue'] == int(stats['revenue']) else f"{stats['revenue']:.2f}"

    text = (
        f"📊 <b>Dashboard</b>\n"
        f"{separator()}\n\n"
        f"👥 <b>Users:</b> {stats['users']}\n"
        f"📂 <b>Categories:</b> {stats['categories']}\n"
        f"📦 <b>Products:</b> {stats['products']}\n"
        f"🛒 <b>Orders:</b> {stats['orders']}\n"
        f"💰 <b>Revenue:</b> {currency} {revenue}\n"
        f"⏳ <b>Pending Proofs:</b> {stats['pending_proofs']}\n"
        f"🎫 <b>Open Tickets:</b> {stats['open_tickets']}"
    )

    await safe_edit(query, text, reply_markup=back_kb("admin"))


# ════════════════════════ CATEGORIES ════════════════════════

async def admin_cats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all categories for admin."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    cats = await get_all_categories()
    text = f"📂 <b>Manage Categories</b>\n{separator()}\n\n📦 Total: {len(cats)} categories"
    await safe_edit(query, text, reply_markup=admin_cats_kb(cats))


async def admin_cat_add_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompt admin to enter new category name."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    context.user_data["state"] = "adm_cat_name"
    text = (
        f"➕ <b>Add Category</b>\n"
        f"{separator()}\n\n"
        "📝 Send the category name:"
    )
    await safe_edit(query, text, reply_markup=back_kb("adm_cats"))


async def admin_cat_detail_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """View category details."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    cat_id = int(query.data.split(":")[1])
    cat = await get_category(cat_id)
    if not cat:
        await safe_edit(query, "❌ Category not found.", reply_markup=back_kb("adm_cats"))
        return

    count = await get_product_count_in_category(cat_id)
    text = (
        f"📂 <b>Category: {html_escape(cat['emoji'])} {html_escape(cat['name'])}</b>\n"
        f"{separator()}\n\n"
        f"🆔 ID: {cat_id}\n"
        f"📦 Products: {count}\n"
        f"📊 Sort Order: {cat['sort_order']}\n"
        f"✅ Active: {'Yes' if cat['active'] else 'No'}\n"
        f"🖼️ Image: {'Set' if cat.get('image_id') else 'Not set'}"
    )
    await safe_edit(query, text, reply_markup=admin_cat_detail_kb(cat_id))


async def admin_cat_edit_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompt admin to edit category name."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    cat_id = int(query.data.split(":")[1])
    context.user_data["state"] = f"adm_cat_emoji:{cat_id}"
    text = (
        f"✏️ <b>Edit Category</b>\n"
        f"{separator()}\n\n"
        "Send new name and emoji in format:\n"
        "<code>emoji | name</code>\n\n"
        "Example: <code>📚 | eBooks</code>"
    )
    await safe_edit(query, text, reply_markup=back_kb(f"adm_cat:{cat_id}"))


async def admin_cat_del_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Delete a category."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    cat_id = int(query.data.split(":")[1])
    cat = await get_category(cat_id)
    if cat:
        await delete_category(cat_id)
        await query.answer(f"✅ Category '{cat['name']}' deleted!", show_alert=True)
        await add_action_log("cat_deleted", ADMIN_ID, f"Category: {cat['name']}")

    cats = await get_all_categories()
    text = f"📂 <b>Manage Categories</b>\n{separator()}\n\n📦 Total: {len(cats)} categories"
    await safe_edit(query, text, reply_markup=admin_cats_kb(cats))


async def admin_cat_img_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompt admin to send category image."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    cat_id = int(query.data.split(":")[1])
    context.user_data["state"] = f"adm_cat_img:{cat_id}"
    text = (
        f"🖼️ <b>Set Category Image</b>\n"
        f"{separator()}\n\n"
        "📸 Send a photo for this category:"
    )
    await safe_edit(query, text, reply_markup=back_kb(f"adm_cat:{cat_id}"))


# ════════════════════════ PRODUCTS ════════════════════════

async def admin_prods_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List products in a category."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    cat_id = int(query.data.split(":")[1])
    cat = await get_category(cat_id)
    if not cat:
        await safe_edit(query, "❌ Category not found.", reply_markup=back_kb("adm_cats"))
        return

    products = await get_products_by_category(cat_id, limit=50)
    currency = await get_setting("currency", "Rs")

    text = (
        f"📦 <b>Products in {html_escape(cat['emoji'])} {html_escape(cat['name'])}</b>\n"
        f"{separator()}\n\n"
        f"📊 Total: {len(products)} products"
    )
    await safe_edit(query, text, reply_markup=admin_prods_kb(products, cat_id, currency))


async def admin_prod_add_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start product creation flow: prompt for name."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    cat_id = int(query.data.split(":")[1])
    context.user_data["state"] = f"adm_prod_name:{cat_id}"
    context.user_data["temp"] = {"cat_id": cat_id}

    text = (
        f"➕ <b>Add Product</b>\n"
        f"{separator()}\n\n"
        "Step 1/3: 📝 Send the product <b>name</b>:"
    )
    await safe_edit(query, text, reply_markup=back_kb(f"adm_prods:{cat_id}"))


async def admin_prod_detail_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """View product details for admin."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    prod_id = int(query.data.split(":")[1])
    prod = await get_product(prod_id)
    if not prod:
        await safe_edit(query, "❌ Product not found.", reply_markup=back_kb("adm_cats"))
        return

    currency = await get_setting("currency", "Rs")
    cat = await get_category(prod["category_id"])
    cat_name = f"{cat['emoji']} {cat['name']}" if cat else "Unknown"
    stock_text = format_stock(prod["stock"])
    price = int(prod['price']) if prod['price'] == int(prod['price']) else prod['price']
    desc = html_escape(prod['description']) if prod['description'] else 'No description'

    text = (
        f"📦 <b>Product: {html_escape(prod['name'])}</b>\n"
        f"{separator()}\n\n"
        f"🆔 ID: {prod_id}\n"
        f"💰 Price: {currency} {price}\n"
        f"📊 Stock: {stock_text}\n"
        f"📂 Category: {html_escape(cat_name)}\n"
        f"🖼️ Image: {'Set' if prod.get('image_id') else 'Not set'}\n\n"
        f"📝 <b>Description:</b>\n{desc}"
    )
    await safe_edit(query, text, reply_markup=admin_prod_detail_kb(prod_id))


async def admin_prod_edit_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompt admin to edit a product field."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    parts = query.data.split(":")
    prod_id = int(parts[1])
    field = parts[2]

    context.user_data["state"] = f"adm_prod_edit:{prod_id}:{field}"

    labels = {"name": "Name", "description": "Description", "price": "Price"}
    label = labels.get(field, field)

    text = (
        f"✏️ <b>Edit Product {label}</b>\n"
        f"{separator()}\n\n"
        f"📝 Send the new <b>{label.lower()}</b>:"
    )
    await safe_edit(query, text, reply_markup=back_kb(f"adm_prod:{prod_id}"))


async def admin_prod_del_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Delete a product."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    prod_id = int(query.data.split(":")[1])
    prod = await get_product(prod_id)

    if prod:
        cat_id = prod["category_id"]
        await delete_product(prod_id)
        await query.answer(f"✅ Product '{prod['name']}' deleted!", show_alert=True)
        await add_action_log("prod_deleted", ADMIN_ID, f"Product: {prod['name']}")

        products = await get_products_by_category(cat_id, limit=50)
        currency = await get_setting("currency", "Rs")
        text = f"📦 <b>Products</b>\n{separator()}\n\n📊 Total: {len(products)} products"
        await safe_edit(query, text, reply_markup=admin_prods_kb(products, cat_id, currency))
    else:
        await safe_edit(query, "❌ Product not found.", reply_markup=back_kb("adm_cats"))


async def admin_prod_img_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompt admin to send product image."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    prod_id = int(query.data.split(":")[1])
    context.user_data["state"] = f"adm_prod_img:{prod_id}"
    text = (
        f"🖼️ <b>Set Product Image</b>\n"
        f"{separator()}\n\n"
        "📸 Send a photo for this product:"
    )
    await safe_edit(query, text, reply_markup=back_kb(f"adm_prod:{prod_id}"))


async def admin_prod_stock_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompt admin to set product stock."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    prod_id = int(query.data.split(":")[1])
    context.user_data["state"] = f"adm_prod_stock:{prod_id}"
    text = (
        f"📊 <b>Set Stock</b>\n"
        f"{separator()}\n\n"
        "Send stock amount:\n"
        "• Number (e.g. <code>50</code>)\n"
        "• <code>-1</code> for unlimited\n"
        "• <code>0</code> for out of stock"
    )
    await safe_edit(query, text, reply_markup=back_kb(f"adm_prod:{prod_id}"))


# ════════════════════════ ORDERS ════════════════════════

async def admin_orders_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all orders for admin."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    orders = await get_all_orders(limit=20)
    currency = await get_setting("currency", "Rs")

    text = f"🛒 <b>All Orders</b>\n{separator()}\n\n📊 Total: {len(orders)} recent orders"
    await safe_edit(query, text, reply_markup=admin_orders_kb(orders, currency))


async def admin_order_detail_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """View order details for admin."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    order_id = int(query.data.split(":")[1])
    order = await get_order(order_id)
    if not order:
        await safe_edit(query, "❌ Order not found.", reply_markup=back_kb("adm_orders"))
        return

    currency = await get_setting("currency", "Rs")
    items = json.loads(order["items_json"]) if order["items_json"] else []
    user = await get_user(order["user_id"])
    user_name = user["full_name"] if user else str(order["user_id"])
    emoji = status_emoji(order["status"])
    pay_emoji = status_emoji(order["payment_status"])

    total = int(order['total']) if order['total'] == int(order['total']) else order['total']

    text = (
        f"📦 <b>Order #{order_id}</b>\n"
        f"{separator()}\n"
    )
    for item in items:
        text += f"\n• {html_escape(item['name'])} × {item['quantity']}\n"

    text += (
        f"{separator()}\n"
        f"👤 User: {html_escape(user_name)} ({order['user_id']})\n"
        f"💰 Total: <b>{currency} {total}</b>\n"
        f"{emoji} Status: <b>{order['status']}</b>\n"
        f"{pay_emoji} Payment: <b>{order['payment_status']}</b>\n"
    )
    if order.get("coupon_code"):
        text += f"🎫 Coupon: {html_escape(order['coupon_code'])}\n"
    if order.get("created_at"):
        text += f"📅 Date: {order['created_at'][:16]}\n"

    await safe_edit(query, text, reply_markup=admin_order_detail_kb(order_id))


async def admin_order_status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Change order status."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    parts = query.data.split(":")
    order_id = int(parts[1])
    new_status = parts[2]

    order = await get_order(order_id)
    if not order:
        await query.answer("❌ Order not found.", show_alert=True)
        return

    await update_order(order_id, status=new_status)
    await query.answer(f"✅ Order #{order_id} → {new_status}", show_alert=True)

    await add_action_log("order_status", ADMIN_ID, f"Order #{order_id} → {new_status}")

    # Notify user
    emoji = status_emoji(new_status)
    currency = await get_setting("currency", "Rs")
    try:
        await context.bot.send_message(
            chat_id=order["user_id"],
            text=(
                f"{emoji} <b>Order #{order_id} Update</b>\n"
                f"{separator()}\n\n"
                f"Status: <b>{new_status.title()}</b>\n"
                f"Check details in 📦 My Orders."
            ),
            parse_mode="HTML",
        )
    except Exception as e:
        logger.warning("Failed to notify user %s: %s", order["user_id"], e)

    # Refresh order detail
    order = await get_order(order_id)
    items = json.loads(order["items_json"]) if order["items_json"] else []
    user = await get_user(order["user_id"])
    user_name = user["full_name"] if user else str(order["user_id"])
    total = int(order['total']) if order['total'] == int(order['total']) else order['total']

    text = (
        f"📦 <b>Order #{order_id}</b>\n"
        f"{separator()}\n"
    )
    for item in items:
        text += f"\n• {html_escape(item['name'])} × {item['quantity']}\n"
    text += (
        f"{separator()}\n"
        f"👤 User: {html_escape(user_name)} ({order['user_id']})\n"
        f"💰 Total: <b>{currency} {total}</b>\n"
        f"{status_emoji(order['status'])} Status: <b>{order['status']}</b>\n"
        f"{status_emoji(order['payment_status'])} Payment: <b>{order['payment_status']}</b>\n"
    )

    await safe_edit(query, text, reply_markup=admin_order_detail_kb(order_id))


# ════════════════════════ USERS ════════════════════════

async def admin_users_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all users."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    users = await get_all_users(limit=20)
    total = await get_user_count()

    text = f"👥 <b>All Users</b>\n{separator()}\n\n📊 Total: {total} users"
    await safe_edit(query, text, reply_markup=admin_users_kb(users))


async def admin_user_detail_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """View user details."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    uid = int(query.data.split(":")[1])
    user = await get_user(uid)
    if not user:
        await safe_edit(query, "❌ User not found.", reply_markup=back_kb("adm_users"))
        return

    order_count = await get_user_order_count(uid)
    balance = await get_user_balance(uid)
    bal_display = int(balance) if balance == int(balance) else f"{balance:.2f}"
    currency = await get_setting("currency", "Rs")

    text = (
        f"👤 <b>User Details</b>\n"
        f"{separator()}\n\n"
        f"🆔 ID: <code>{uid}</code>\n"
        f"👤 Name: {html_escape(user['full_name'] or 'N/A')}\n"
        f"📎 Username: @{html_escape(user['username'] or 'N/A')}\n"
        f"💳 Balance: {currency} {bal_display}\n"
        f"🛒 Orders: {order_count}\n"
        f"🚫 Banned: {'Yes' if user['banned'] else 'No'}\n"
        f"📅 Joined: {user.get('joined_at', 'N/A')[:10]}"
    )

    await safe_edit(query, text, reply_markup=admin_user_detail_kb(uid, bool(user['banned'])))


async def admin_ban_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ban a user."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    uid = int(query.data.split(":")[1])
    await ban_user(uid)
    await query.answer(f"🚫 User {uid} banned!", show_alert=True)
    await add_action_log("user_banned", ADMIN_ID, f"User {uid}")

    # Refresh view
    user = await get_user(uid)
    if user:
        order_count = await get_user_order_count(uid)
        balance = await get_user_balance(uid)
        currency = await get_setting("currency", "Rs")
        bal_display = int(balance) if balance == int(balance) else f"{balance:.2f}"

        text = (
            f"👤 <b>User Details</b>\n{separator()}\n\n"
            f"🆔 ID: <code>{uid}</code>\n"
            f"👤 Name: {html_escape(user['full_name'] or 'N/A')}\n"
            f"📎 Username: @{html_escape(user['username'] or 'N/A')}\n"
            f"💳 Balance: {currency} {bal_display}\n"
            f"🛒 Orders: {order_count}\n"
            f"🚫 Banned: Yes\n"
            f"📅 Joined: {user.get('joined_at', 'N/A')[:10]}"
        )
        await safe_edit(query, text, reply_markup=admin_user_detail_kb(uid, True))


async def admin_unban_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Unban a user."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    uid = int(query.data.split(":")[1])
    await unban_user(uid)
    await query.answer(f"✅ User {uid} unbanned!", show_alert=True)
    await add_action_log("user_unbanned", ADMIN_ID, f"User {uid}")

    user = await get_user(uid)
    if user:
        order_count = await get_user_order_count(uid)
        balance = await get_user_balance(uid)
        currency = await get_setting("currency", "Rs")
        bal_display = int(balance) if balance == int(balance) else f"{balance:.2f}"

        text = (
            f"👤 <b>User Details</b>\n{separator()}\n\n"
            f"🆔 ID: <code>{uid}</code>\n"
            f"👤 Name: {html_escape(user['full_name'] or 'N/A')}\n"
            f"📎 Username: @{html_escape(user['username'] or 'N/A')}\n"
            f"💳 Balance: {currency} {bal_display}\n"
            f"🛒 Orders: {order_count}\n"
            f"🚫 Banned: No\n"
            f"📅 Joined: {user.get('joined_at', 'N/A')[:10]}"
        )
        await safe_edit(query, text, reply_markup=admin_user_detail_kb(uid, False))


# ════════════════════════ COUPONS ════════════════════════

async def admin_coupons_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all coupons."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    coupons = await get_all_coupons()
    text = f"🎫 <b>Manage Coupons</b>\n{separator()}\n\n📊 Total: {len(coupons)} coupons"
    await safe_edit(query, text, reply_markup=admin_coupons_kb(coupons))


async def admin_coupon_add_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompt admin to create coupon."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    context.user_data["state"] = "adm_coupon_data"
    text = (
        f"➕ <b>Add Coupon</b>\n"
        f"{separator()}\n\n"
        "Send coupon data in format:\n"
        "<code>CODE|discount_percent|max_uses</code>\n\n"
        "Example: <code>SAVE20|20|100</code>\n"
        "(0 max_uses = unlimited)"
    )
    await safe_edit(query, text, reply_markup=back_kb("adm_coupons"))


async def admin_coupon_toggle_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Toggle coupon active/inactive."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    code = query.data.split(":")[1]
    await toggle_coupon(code)
    await query.answer(f"✅ Coupon {code} toggled!", show_alert=True)

    coupons = await get_all_coupons()
    text = f"🎫 <b>Manage Coupons</b>\n{separator()}\n\n📊 Total: {len(coupons)} coupons"
    await safe_edit(query, text, reply_markup=admin_coupons_kb(coupons))


async def admin_coupon_del_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Delete a coupon."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    code = query.data.split(":")[1]
    await delete_coupon(code)
    await query.answer(f"✅ Coupon {code} deleted!", show_alert=True)

    coupons = await get_all_coupons()
    text = f"🎫 <b>Manage Coupons</b>\n{separator()}\n\n📊 Total: {len(coupons)} coupons"
    await safe_edit(query, text, reply_markup=admin_coupons_kb(coupons))


# ════════════════════════ PAYMENTS ════════════════════════

async def admin_payments_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List payment methods."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    methods = await get_all_payment_methods()
    text = f"💳 <b>Payment Methods</b>\n{separator()}\n\n📊 Total: {len(methods)} methods"
    await safe_edit(query, text, reply_markup=admin_payments_kb(methods))


async def admin_pay_add_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompt admin to add payment method."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    context.user_data["state"] = "adm_pay_data"
    text = (
        f"➕ <b>Add Payment Method</b>\n"
        f"{separator()}\n\n"
        "Send in format:\n"
        "<code>emoji|name|details</code>\n\n"
        "Example:\n"
        "<code>🏦|Bank Transfer|Bank: HBL\nAccount: 123456</code>"
    )
    await safe_edit(query, text, reply_markup=back_kb("adm_payments"))


async def admin_pay_del_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Delete a payment method."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    method_id = int(query.data.split(":")[1])
    await delete_payment_method(method_id)
    await query.answer("✅ Payment method deleted!", show_alert=True)

    methods = await get_all_payment_methods()
    text = f"💳 <b>Payment Methods</b>\n{separator()}\n\n📊 Total: {len(methods)} methods"
    await safe_edit(query, text, reply_markup=admin_payments_kb(methods))


# ════════════════════════ PROOFS ════════════════════════

async def admin_proofs_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List pending payment proofs."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    proofs = await get_pending_proofs()
    text = f"📸 <b>Pending Proofs</b>\n{separator()}\n\n⏳ {len(proofs)} awaiting review"
    await safe_edit(query, text, reply_markup=admin_proofs_kb(proofs))


async def admin_proof_detail_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """View proof details and send the screenshot."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    proof_id = int(query.data.split(":")[1])
    proof = await get_payment_proof(proof_id)
    if not proof:
        await safe_edit(query, "❌ Proof not found.", reply_markup=back_kb("adm_proofs"))
        return

    order = await get_order(proof["order_id"])
    method = await get_payment_method(proof["method_id"]) if proof.get("method_id") else None
    user = await get_user(proof["user_id"])
    currency = await get_setting("currency", "Rs")

    total = 0
    if order:
        total = int(order['total']) if order['total'] == int(order['total']) else order['total']

    text = (
        f"📸 <b>Proof #{proof_id}</b>\n"
        f"{separator()}\n\n"
        f"🆔 Order: #{proof['order_id']}\n"
        f"👤 User: {html_escape(user['full_name'] if user else 'N/A')} ({proof['user_id']})\n"
        f"💰 Amount: {currency} {total}\n"
        f"💳 Method: {html_escape(method['name'] if method else 'N/A')}\n"
        f"📊 Status: {proof['status']}\n"
        f"📅 Date: {proof.get('created_at', 'N/A')[:16]}"
    )

    # Send proof photo first
    if proof.get("file_id"):
        try:
            await query.message.chat.send_photo(
                photo=proof["file_id"],
                caption=text,
                parse_mode="HTML",
                reply_markup=admin_proof_detail_kb(proof_id),
            )
            try:
                await query.message.delete()
            except Exception:
                pass
            return
        except Exception as e:
            logger.warning("Failed to send proof photo: %s", e)

    await safe_edit(query, text, reply_markup=admin_proof_detail_kb(proof_id))


async def admin_proof_approve_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Approve a payment proof."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    proof_id = int(query.data.split(":")[1])
    proof = await get_payment_proof(proof_id)
    if not proof:
        await query.answer("❌ Proof not found.", show_alert=True)
        return

    await update_proof(proof_id, status="approved", reviewed_by=ADMIN_ID)
    await update_order(proof["order_id"], payment_status="paid")

    await query.answer("✅ Proof approved!", show_alert=True)
    await add_action_log("proof_approved", ADMIN_ID, f"Proof #{proof_id}, Order #{proof['order_id']}")

    # Notify user
    currency = await get_setting("currency", "Rs")
    try:
        await context.bot.send_message(
            chat_id=proof["user_id"],
            text=(
                f"✅ <b>Payment Approved!</b>\n"
                f"{separator()}\n\n"
                f"Your payment for Order #{proof['order_id']} has been approved!\n"
                "Thank you for your purchase! 🎉"
            ),
            parse_mode="HTML",
        )
    except Exception as e:
        logger.warning("Failed to notify user: %s", e)

    # Show remaining proofs
    proofs = await get_pending_proofs()
    text = f"📸 <b>Pending Proofs</b>\n{separator()}\n\n⏳ {len(proofs)} awaiting review"
    await safe_edit(query, text, reply_markup=admin_proofs_kb(proofs))


async def admin_proof_reject_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start proof rejection — prompt for reason."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    proof_id = int(query.data.split(":")[1])
    context.user_data["state"] = f"adm_proof_reject:{proof_id}"

    text = (
        f"❌ <b>Reject Proof #{proof_id}</b>\n"
        f"{separator()}\n\n"
        "📝 Send rejection reason:"
    )
    await safe_edit(query, text, reply_markup=back_kb("adm_proofs"))


async def admin_proof_post_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Post proof to the proofs channel."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    proof_id = int(query.data.split(":")[1])
    proof = await get_payment_proof(proof_id)
    if not proof or not proof.get("file_id"):
        await query.answer("❌ Proof not found.", show_alert=True)
        return

    if not PROOFS_CHANNEL_ID:
        await query.answer("⚠️ Proofs channel not configured.", show_alert=True)
        return

    try:
        await context.bot.send_photo(
            chat_id=PROOFS_CHANNEL_ID,
            photo=proof["file_id"],
            caption=f"✅ Payment Proof #{proof_id}\nOrder #{proof['order_id']}",
            parse_mode="HTML",
        )
        await query.answer("✅ Posted to channel!", show_alert=True)
    except Exception as e:
        logger.warning("Failed to post proof: %s", e)
        await query.answer(f"❌ Failed: {e}", show_alert=True)


# ════════════════════════ SETTINGS ════════════════════════

async def admin_settings_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show settings panel."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    settings = await get_all_settings()
    text = f"⚙️ <b>Settings</b>\n{separator()}\n\nTap a setting to edit:"
    await safe_edit(query, text, reply_markup=admin_settings_kb(settings))


async def admin_set_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompt admin to edit a setting."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    key = query.data.split(":")[1]
    current = await get_setting(key, "(not set)")
    context.user_data["state"] = f"adm_set:{key}"

    text = (
        f"⚙️ <b>Edit Setting: {html_escape(key)}</b>\n"
        f"{separator()}\n\n"
        f"Current value: <code>{html_escape(current)}</code>\n\n"
        "📝 Send the new value:"
    )
    await safe_edit(query, text, reply_markup=back_kb("adm_settings"))


# ════════════════════════ FORCE JOIN ════════════════════════

async def admin_fj_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show force join channels."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    channels = await get_force_join_channels()
    text = f"📢 <b>Force Join Channels</b>\n{separator()}\n\n📊 {len(channels)} channels configured"
    await safe_edit(query, text, reply_markup=admin_fj_kb(channels))


async def admin_fj_add_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompt admin to add force join channel."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    context.user_data["state"] = "adm_fj_channel"
    text = (
        f"➕ <b>Add Force Join Channel</b>\n"
        f"{separator()}\n\n"
        "Send channel info in format:\n"
        "<code>channel_id|name|invite_link</code>\n\n"
        "Example:\n"
        "<code>-1001234567890|NanoStore Updates|https://t.me/nanostore</code>"
    )
    await safe_edit(query, text, reply_markup=back_kb("adm_fj"))


async def admin_fj_del_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Delete a force join channel."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    fj_id = int(query.data.split(":")[1])
    await delete_force_join_channel(fj_id)
    await query.answer("✅ Channel removed!", show_alert=True)

    channels = await get_force_join_channels()
    text = f"📢 <b>Force Join Channels</b>\n{separator()}\n\n📊 {len(channels)} channels configured"
    await safe_edit(query, text, reply_markup=admin_fj_kb(channels))


# ════════════════════════ BULK IMPORT ════════════════════════

async def admin_bulk_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompt for bulk product import."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    context.user_data["state"] = "adm_bulk_data"
    text = (
        f"📥 <b>Bulk Product Import</b>\n"
        f"{separator()}\n\n"
        "Send products in format (one per line):\n"
        "<code>category_id|name|description|price|stock</code>\n\n"
        "Example:\n"
        "<code>1|Python eBook|Learn Python|500|-1</code>\n"
        "<code>2|Resume Template|Professional CV|200|50</code>"
    )
    await safe_edit(query, text, reply_markup=back_kb("admin"))


async def admin_bulk_stock_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompt for bulk stock update."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    context.user_data["state"] = "adm_bulk_stock_data"
    text = (
        f"📊 <b>Bulk Stock Update</b>\n"
        f"{separator()}\n\n"
        "Send stock updates (one per line):\n"
        "<code>product_id|stock</code>\n\n"
        "Example:\n"
        "<code>1|50</code>\n"
        "<code>2|-1</code>\n"
        "<code>3|0</code>"
    )
    await safe_edit(query, text, reply_markup=back_kb("admin"))


# ════════════════════════ BROADCAST ════════════════════════

async def admin_broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompt admin to type broadcast message."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    context.user_data["state"] = "adm_broadcast_text"
    text = (
        f"📣 <b>Broadcast Message</b>\n"
        f"{separator()}\n\n"
        "📝 Type the message to send to all users:\n\n"
        "<i>Supports HTML formatting.</i>"
    )
    await safe_edit(query, text, reply_markup=back_kb("admin"))


async def admin_broadcast_confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send broadcast to all users."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    broadcast_text = context.user_data.get("temp", {}).get("broadcast_text")
    if not broadcast_text:
        await query.answer("⚠️ No message to send.", show_alert=True)
        return

    context.user_data.pop("state", None)
    context.user_data.pop("temp", None)

    users = await get_all_users(limit=10000)
    sent = 0
    failed = 0

    for user in users:
        try:
            await context.bot.send_message(
                chat_id=user["user_id"],
                text=broadcast_text,
                parse_mode="HTML",
            )
            sent += 1
        except Exception:
            failed += 1

    text = (
        f"📣 <b>Broadcast Complete!</b>\n"
        f"{separator()}\n\n"
        f"✅ Sent: {sent}\n"
        f"❌ Failed: {failed}\n"
        f"📊 Total: {sent + failed}"
    )
    await safe_edit(query, text, reply_markup=back_kb("admin"))
    await add_action_log("broadcast", ADMIN_ID, f"Sent: {sent}, Failed: {failed}")


# ════════════════════════ ADMIN TEXT ROUTER ════════════════════════

async def admin_text_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Route admin text input based on state."""
    if not _is_admin(update.effective_user.id):
        return

    state = context.user_data.get("state", "")
    text = update.message.text.strip()

    # ---- Category: add name ----
    if state == "adm_cat_name":
        context.user_data.pop("state", None)
        cat_id = await add_category(text)
        await update.message.reply_text(
            f"✅ Category <b>{html_escape(text)}</b> created! (ID: {cat_id})",
            parse_mode="HTML",
        )
        await add_action_log("cat_added", ADMIN_ID, f"Category: {text}")
        return

    # ---- Category: edit (emoji | name) ----
    if state.startswith("adm_cat_emoji:"):
        cat_id = int(state.split(":")[1])
        context.user_data.pop("state", None)
        if "|" in text:
            emoji, name = text.split("|", 1)
            await update_category(cat_id, emoji=emoji.strip(), name=name.strip())
        else:
            await update_category(cat_id, name=text)
        await update.message.reply_text("✅ Category updated!", parse_mode="HTML")
        return

    # ---- Product: add name (step 1) ----
    if state.startswith("adm_prod_name:"):
        context.user_data["state"] = "adm_prod_desc"
        context.user_data.setdefault("temp", {})["name"] = text
        await update.message.reply_text(
            "Step 2/3: 📝 Send the product <b>description</b>:\n\n"
            "(or send <code>-</code> to skip)",
            parse_mode="HTML",
        )
        return

    # ---- Product: add description (step 2) ----
    if state == "adm_prod_desc":
        context.user_data["state"] = "adm_prod_price"
        desc = "" if text == "-" else text
        context.user_data.setdefault("temp", {})["desc"] = desc
        await update.message.reply_text(
            "Step 3/3: 💰 Send the <b>price</b> (number):",
            parse_mode="HTML",
        )
        return

    # ---- Product: add price (step 3 — create product) ----
    if state == "adm_prod_price":
        context.user_data.pop("state", None)
        temp = context.user_data.get("temp", {})
        try:
            price = float(text)
        except ValueError:
            await update.message.reply_text("❌ Invalid price. Send a number.", parse_mode="HTML")
            context.user_data["state"] = "adm_prod_price"
            return

        cat_id = temp.get("cat_id")
        name = temp.get("name", "Unnamed")
        desc = temp.get("desc", "")
        context.user_data.pop("temp", None)

        prod_id = await add_product(cat_id, name, desc, price)
        currency = await get_setting("currency", "Rs")
        price_display = int(price) if price == int(price) else price

        await update.message.reply_text(
            f"✅ Product created!\n\n"
            f"🏷️ <b>{html_escape(name)}</b>\n"
            f"💰 Price: {currency} {price_display}\n"
            f"🆔 ID: {prod_id}",
            parse_mode="HTML",
        )
        await add_action_log("prod_added", ADMIN_ID, f"Product: {name}, Price: {price}")
        return

    # ---- Product: edit field ----
    if state.startswith("adm_prod_edit:"):
        parts = state.split(":")
        prod_id = int(parts[1])
        field = parts[2]
        context.user_data.pop("state", None)

        if field == "price":
            try:
                value = float(text)
            except ValueError:
                await update.message.reply_text("❌ Invalid price.", parse_mode="HTML")
                return
            await update_product(prod_id, price=value)
        elif field == "name":
            await update_product(prod_id, name=text)
        elif field == "description":
            await update_product(prod_id, description=text)
        else:
            await update.message.reply_text("❌ Unknown field.", parse_mode="HTML")
            return

        await update.message.reply_text(f"✅ Product {field} updated!", parse_mode="HTML")
        return

    # ---- Product: stock ----
    if state.startswith("adm_prod_stock:"):
        prod_id = int(state.split(":")[1])
        context.user_data.pop("state", None)
        try:
            stock = int(text)
        except ValueError:
            await update.message.reply_text("❌ Invalid number.", parse_mode="HTML")
            return
        await update_product(prod_id, stock=stock)
        await update.message.reply_text(f"✅ Stock set to {format_stock(stock)}", parse_mode="HTML")
        return

    # ---- Coupon: add ----
    if state == "adm_coupon_data":
        context.user_data.pop("state", None)
        try:
            parts = text.split("|")
            code = parts[0].strip().upper()
            discount = int(parts[1].strip())
            max_uses = int(parts[2].strip()) if len(parts) > 2 else 0
            await create_coupon(code, discount, max_uses)
            await update.message.reply_text(
                f"✅ Coupon <b>{html_escape(code)}</b> created!\n"
                f"🎫 {discount}% off | Max uses: {max_uses or 'Unlimited'}",
                parse_mode="HTML",
            )
            await add_action_log("coupon_added", ADMIN_ID, f"Coupon: {code}")
        except (ValueError, IndexError):
            await update.message.reply_text(
                "❌ Invalid format. Use: <code>CODE|discount|max_uses</code>",
                parse_mode="HTML",
            )
        return

    # ---- Payment method: add ----
    if state == "adm_pay_data":
        context.user_data.pop("state", None)
        try:
            parts = text.split("|", 2)
            emoji = parts[0].strip()
            name = parts[1].strip()
            details = parts[2].strip()
            await add_payment_method(name, details, emoji)
            await update.message.reply_text(
                f"✅ Payment method <b>{html_escape(name)}</b> added!",
                parse_mode="HTML",
            )
        except (ValueError, IndexError):
            await update.message.reply_text(
                "❌ Invalid format. Use: <code>emoji|name|details</code>",
                parse_mode="HTML",
            )
        return

    # ---- Force join: add channel ----
    if state == "adm_fj_channel":
        context.user_data.pop("state", None)
        try:
            parts = text.split("|", 2)
            ch_id = parts[0].strip()
            ch_name = parts[1].strip()
            ch_link = parts[2].strip()
            await add_force_join_channel(ch_id, ch_name, ch_link)
            await update.message.reply_text(
                f"✅ Channel <b>{html_escape(ch_name)}</b> added!",
                parse_mode="HTML",
            )
        except (ValueError, IndexError):
            await update.message.reply_text(
                "❌ Invalid format. Use: <code>channel_id|name|invite_link</code>",
                parse_mode="HTML",
            )
        return

    # ---- Bulk import ----
    if state == "adm_bulk_data":
        context.user_data.pop("state", None)
        lines = text.strip().split("\n")
        added = 0
        errors = 0
        for line in lines:
            try:
                parts = line.split("|")
                cat_id = int(parts[0].strip())
                name = parts[1].strip()
                desc = parts[2].strip() if len(parts) > 2 else ""
                price = float(parts[3].strip()) if len(parts) > 3 else 0
                stock = int(parts[4].strip()) if len(parts) > 4 else -1
                await add_product(cat_id, name, desc, price, stock)
                added += 1
            except Exception:
                errors += 1

        await update.message.reply_text(
            f"📥 <b>Bulk Import Complete!</b>\n\n"
            f"✅ Added: {added}\n❌ Errors: {errors}",
            parse_mode="HTML",
        )
        await add_action_log("bulk_import", ADMIN_ID, f"Added: {added}, Errors: {errors}")
        return

    # ---- Bulk stock update ----
    if state == "adm_bulk_stock_data":
        context.user_data.pop("state", None)
        lines = text.strip().split("\n")
        updated = 0
        errors = 0
        for line in lines:
            try:
                parts = line.split("|")
                prod_id = int(parts[0].strip())
                stock = int(parts[1].strip())
                await update_product(prod_id, stock=stock)
                updated += 1
            except Exception:
                errors += 1

        await update.message.reply_text(
            f"📊 <b>Bulk Stock Update Complete!</b>\n\n"
            f"✅ Updated: {updated}\n❌ Errors: {errors}",
            parse_mode="HTML",
        )
        return

    # ---- Broadcast text ----
    if state == "adm_broadcast_text":
        context.user_data["state"] = None
        context.user_data.setdefault("temp", {})["broadcast_text"] = text
        user_count = await get_user_count()

        preview = (
            f"📣 <b>Broadcast Preview</b>\n"
            f"{separator()}\n\n"
            f"{text}\n\n"
            f"{separator()}\n"
            f"👥 Will be sent to <b>{user_count}</b> users."
        )
        await update.message.reply_text(
            preview,
            parse_mode="HTML",
            reply_markup=admin_broadcast_confirm_kb(),
        )
        return

    # ---- Settings: update value ----
    if state.startswith("adm_set:"):
        key = state.split(":")[1]
        context.user_data.pop("state", None)
        await set_setting(key, text)
        await update.message.reply_text(
            f"✅ Setting <b>{html_escape(key)}</b> updated to:\n<code>{html_escape(text)}</code>",
            parse_mode="HTML",
        )
        return

    # ---- Proof rejection reason ----
    if state.startswith("adm_proof_reject:"):
        proof_id = int(state.split(":")[1])
        context.user_data.pop("state", None)

        proof = await get_payment_proof(proof_id)
        if proof:
            await update_proof(proof_id, status="rejected", reviewed_by=ADMIN_ID, admin_note=text)
            await update_order(proof["order_id"], payment_status="rejected")

            # Notify user
            try:
                await context.bot.send_message(
                    chat_id=proof["user_id"],
                    text=(
                        f"❌ <b>Payment Rejected</b>\n"
                        f"{separator()}\n\n"
                        f"Order #{proof['order_id']}\n"
                        f"Reason: {html_escape(text)}\n\n"
                        "Please re-submit or contact support."
                    ),
                    parse_mode="HTML",
                )
            except Exception as e:
                logger.warning("Failed to notify user: %s", e)

            await add_action_log("proof_rejected", ADMIN_ID, f"Proof #{proof_id}: {text}")

        await update.message.reply_text("✅ Proof rejected.", parse_mode="HTML")
        return

    # ---- Product FAQ add ----
    if state.startswith("adm_prod_faq:"):
        prod_id = int(state.split(":")[1])
        context.user_data.pop("state", None)
        if "|" not in text:
            await update.message.reply_text(
                "❌ Invalid format. Use: <code>question | answer</code>",
                parse_mode="HTML",
            )
            return
        q, a = text.split("|", 1)
        await add_product_faq(prod_id, q.strip(), a.strip())
        await update.message.reply_text("✅ FAQ added!", parse_mode="HTML")
        return

    # ---- Product media add ----
    # (handled in photo/document router, not text)


# ════════════════════════ ADMIN PHOTO ROUTER ════════════════════════

async def admin_photo_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Route admin photo uploads based on state."""
    if not _is_admin(update.effective_user.id):
        return

    state = context.user_data.get("state", "")
    photo = update.message.photo[-1]
    file_id = photo.file_id

    # ---- Product image ----
    if state.startswith("adm_prod_img:"):
        prod_id = int(state.split(":")[1])
        context.user_data.pop("state", None)
        await update_product(prod_id, image_id=file_id)
        await update.message.reply_text("✅ Product image set!", parse_mode="HTML")
        return

    # ---- Category image ----
    if state.startswith("adm_cat_img:"):
        cat_id = int(state.split(":")[1])
        context.user_data.pop("state", None)
        await update_category(cat_id, image_id=file_id)
        await update.message.reply_text("✅ Category image set!", parse_mode="HTML")
        return

    # ---- Product media (photo as media) ----
    if state.startswith("adm_prod_media:"):
        parts = state.split(":")
        prod_id = int(parts[1])
        media_type = parts[2] if len(parts) > 2 else "file"
        context.user_data.pop("state", None)
        await add_product_media(prod_id, media_type, file_id)
        await update.message.reply_text(f"✅ Product {media_type} media added!", parse_mode="HTML")
        return


# ════════════════════════ FAQ & MEDIA ADMIN ════════════════════════

async def admin_prod_faq_add_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompt admin to add FAQ."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    prod_id = int(query.data.split(":")[1])
    context.user_data["state"] = f"adm_prod_faq:{prod_id}"
    text = (
        f"❓ <b>Add FAQ</b>\n"
        f"{separator()}\n\n"
        "Send in format:\n"
        "<code>question | answer</code>\n\n"
        "Example:\n"
        "<code>What format? | PDF and EPUB</code>"
    )
    await safe_edit(query, text, reply_markup=back_kb(f"adm_prod:{prod_id}"))


async def admin_prod_faq_del_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Delete a product FAQ."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    parts = query.data.split(":")
    faq_id = int(parts[2])
    await delete_product_faq(faq_id)
    await query.answer("✅ FAQ deleted!", show_alert=True)


async def admin_prod_media_add_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompt admin to send media file."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    parts = query.data.split(":")
    prod_id = int(parts[1])
    media_type = parts[2] if len(parts) > 2 else "video"
    context.user_data["state"] = f"adm_prod_media:{prod_id}:{media_type}"

    text = (
        f"🎬 <b>Add {media_type.title()} Media</b>\n"
        f"{separator()}\n\n"
        f"📸 Send the {media_type} file now:"
    )
    await safe_edit(query, text, reply_markup=back_kb(f"adm_prod:{prod_id}"))


async def admin_prod_media_del_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Delete a product media item."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        return

    parts = query.data.split(":")
    mid = int(parts[2])
    await delete_product_media(mid)
    await query.answer("✅ Media deleted!", show_alert=True)
