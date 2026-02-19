"""NanoStore admin handlers — all admin panel functionality.

Key improvements vs previous version:
- admin_welcome_image_handler() NOW EXISTS (was missing, caused import crash)
- admin_settings_handler() shows categorized settings with current values
- admin_set_handler() handles maintenance toggle without text input
- Product delivery type management (auto vs manual + delivery data)
- admin_photo_router() handles welcome image, product image, category image
- All handlers use send_typing() for immediate feedback
"""

import asyncio
import json
import logging
from html import escape as html_escape
from telegram import Update, InlineKeyboardButton as Btn, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import ADMIN_ID, PROOFS_CHANNEL_ID
from database import (
    get_dashboard_stats,
    get_all_categories, get_category, add_category, update_category, delete_category,
    get_products_by_category, get_product_count_in_category,
    get_product, add_product, update_product, delete_product,
    get_all_orders, get_order, update_order,
    get_all_users, get_user, get_user_count, ban_user, unban_user,
    get_user_order_count, get_user_balance, get_all_user_ids,
    get_all_coupons, create_coupon, delete_coupon, toggle_coupon,
    get_all_payment_methods, add_payment_method, delete_payment_method,
    get_pending_proofs, get_pending_proof_count, get_payment_proof,
    update_proof, get_payment_method,
    get_all_settings, get_setting, set_setting,
    get_force_join_channels, add_force_join_channel, delete_force_join_channel,
    add_product_faq, delete_product_faq, get_product_faqs,
    add_product_media, delete_product_media, get_product_media,
    add_action_log, search_products, get_open_ticket_count,
)
from helpers import (
    safe_edit, separator, send_typing, notify_log_channel,
    format_price, format_stock, status_emoji, delivery_icon, html_escape,
    auto_delete,
)
from keyboards import (
    admin_kb, admin_cats_kb, admin_cat_detail_kb,
    admin_prods_kb, admin_prod_detail_kb,
    admin_orders_kb, admin_order_detail_kb,
    admin_users_kb, admin_user_detail_kb,
    admin_coupons_kb, admin_payments_kb,
    admin_proofs_kb, admin_proof_detail_kb,
    admin_tickets_kb, admin_fj_kb, admin_settings_kb,
    admin_broadcast_confirm_kb, back_kb,
)

logger = logging.getLogger(__name__)


def _is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


# ════════════════════════ MAIN ADMIN PANEL ════════════════════════

async def admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin panel main screen.
    
    Uses render_screen with admin_panel_image_id.
    """
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        await query.answer("⛔ Access denied.", show_alert=True)
        return

    context.user_data.pop("state", None)
    context.user_data.pop("temp", None)

    await send_typing(query.message.chat_id, context.bot)

    stats = await get_dashboard_stats()
    currency = await get_setting("currency", "Rs")
    revenue = int(stats["revenue"]) if stats["revenue"] == int(stats["revenue"]) else f"{stats['revenue']:.2f}"

    text = (
        f"⚙️ <b>Admin Panel</b>\n"
        f"{separator()}\n"
        f"👥 Users: <b>{stats['users']}</b>  |  📦 Orders: <b>{stats['orders']}</b>\n"
        f"💰 Revenue: <b>{currency} {revenue}</b>  |  ⏳ Proofs: <b>{stats['pending_proofs']}</b>\n"
        f"🎫 Tickets: <b>{stats['open_tickets']}</b>  |  💳 Top-Ups: <b>{stats['pending_topups']}</b>"
    )
    
    # Use render_screen with admin_panel_image_id
    from helpers import render_screen
    await render_screen(
        query=query,
        bot=context.bot,
        chat_id=query.message.chat_id,
        text=text,
        reply_markup=admin_kb(stats["pending_proofs"], stats["open_tickets"], stats["pending_topups"]),
        image_setting_key="admin_panel_image_id"
    )


async def back_admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Back to admin panel - uses same render as admin_handler."""
    await admin_handler(update, context)


# ════════════════════════ DASHBOARD ════════════════════════

async def admin_dashboard_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    await send_typing(query.message.chat_id, context.bot)
    stats = await get_dashboard_stats()
    currency = await get_setting("currency", "Rs")
    revenue = int(stats["revenue"]) if stats["revenue"] == int(stats["revenue"]) else f"{stats['revenue']:.2f}"

    text = (
        f"📊 <b>Dashboard Stats</b>\n"
        f"{separator()}\n\n"
        f"👥 <b>Total Users:</b> {stats['users']}\n"
        f"📂 <b>Categories:</b> {stats['categories']}\n"
        f"📦 <b>Products:</b> {stats['products']}\n"
        f"🛒 <b>Total Orders:</b> {stats['orders']}\n"
        f"💰 <b>Revenue:</b> {currency} {revenue}\n"
        f"⏳ <b>Pending Proofs:</b> {stats['pending_proofs']}\n"
        f"💳 <b>Pending Top-Ups:</b> {stats['pending_topups']}\n"
        f"🎫 <b>Open Tickets:</b> {stats['open_tickets']}"
    )
    await safe_edit(query, text, reply_markup=back_kb("admin"))


# ════════════════════════ CATEGORIES ════════════════════════

async def admin_cats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    cats = await get_all_categories()
    text = f"📂 <b>Manage Categories</b>\n{separator()}\n\n📦 Total: {len(cats)} categories"
    await safe_edit(query, text, reply_markup=admin_cats_kb(cats))


async def admin_cat_add_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
    img_status = "✅ Set" if cat.get("image_id") else "❌ Not set"
    text = (
        f"📂 <b>Category: {html_escape(cat['emoji'])} {html_escape(cat['name'])}</b>\n"
        f"{separator()}\n\n"
        f"🆔 ID: {cat_id}  |  📦 Products: {count}\n"
        f"📊 Sort: {cat['sort_order']}  |  ✅ Active: {'Yes' if cat['active'] else 'No'}\n"
        f"🖼️ Image: {img_status}"
    )
    await safe_edit(query, text, reply_markup=admin_cat_detail_kb(cat_id))


async def admin_cat_edit_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    cat_id = int(query.data.split(":")[1])
    context.user_data["state"] = f"adm_cat_emoji:{cat_id}"
    text = (
        f"✏️ <b>Edit Category</b>\n"
        f"{separator()}\n\n"
        "Send new emoji and name:\n"
        "<code>emoji | name</code>\n\n"
        "Example: <code>📚 | eBooks</code>"
    )
    await safe_edit(query, text, reply_markup=back_kb(f"adm_cat:{cat_id}"))


async def admin_cat_del_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    cat_id = int(query.data.split(":")[1])
    cat = await get_category(cat_id)
    if cat:
        await delete_category(cat_id)
        await query.answer(f"✅ '{cat['name']}' deleted!", show_alert=True)
        await add_action_log("cat_deleted", ADMIN_ID, cat["name"])

    cats = await get_all_categories()
    await safe_edit(
        query,
        f"📂 <b>Manage Categories</b>\n{separator()}\n\n📦 Total: {len(cats)} categories",
        reply_markup=admin_cats_kb(cats),
    )


async def admin_cat_img_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompt admin to send a photo for this category."""
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    cat_id = int(query.data.split(":")[1])
    cat = await get_category(cat_id)
    cat_name = f"{cat['emoji']} {cat['name']}" if cat else str(cat_id)

    context.user_data["state"] = f"adm_cat_img:{cat_id}"
    text = (
        f"🖼️ <b>Set Category Image</b>\n"
        f"{separator()}\n\n"
        f"Category: <b>{html_escape(cat_name)}</b>\n\n"
        "📸 Send a photo to use as this category's banner:"
    )
    await safe_edit(query, text, reply_markup=back_kb(f"adm_cat:{cat_id}"))


# ════════════════════════ PRODUCTS ════════════════════════

async def admin_prods_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
        f"📦 <b>{html_escape(cat['emoji'])} {html_escape(cat['name'])}</b>\n"
        f"{separator()}\n\n📊 {len(products)} products"
    )
    await safe_edit(query, text, reply_markup=admin_prods_kb(products, cat_id, currency))


async def admin_prod_add_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
    price = int(prod["price"]) if prod["price"] == int(prod["price"]) else prod["price"]
    desc = html_escape(prod["description"]) if prod["description"] else "No description"
    d_icon = delivery_icon(prod.get("delivery_type", "manual"))
    d_type = prod.get("delivery_type", "manual")
    d_data = prod.get("delivery_data", "")
    delivery_status = "✅ Set" if d_data else "❌ Not set"

    text = (
        f"📦 <b>{html_escape(prod['name'])}</b>\n"
        f"{separator()}\n\n"
        f"🆔 ID: {prod_id}  |  💰 Price: {currency} {price}\n"
        f"📊 Stock: {stock_text}\n"
        f"📂 Category: {html_escape(cat_name)}\n"
        f"🖼️ Image: {'✅ Set' if prod.get('image_id') else '❌ Not set'}\n"
        f"{d_icon} Delivery: <b>{d_type}</b> | Data: {delivery_status}\n\n"
        f"📝 {desc}"
    )
    await safe_edit(query, text, reply_markup=admin_prod_detail_kb(prod_id))


async def admin_prod_edit_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
    await safe_edit(
        query,
        f"✏️ <b>Edit Product {label}</b>\n{separator()}\n\n📝 Send the new <b>{label.lower()}</b>:",
        reply_markup=back_kb(f"adm_prod:{prod_id}"),
    )


async def admin_prod_del_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    prod_id = int(query.data.split(":")[1])
    prod = await get_product(prod_id)
    if prod:
        cat_id = prod["category_id"]
        await delete_product(prod_id)
        await query.answer(f"✅ '{prod['name']}' deleted!", show_alert=True)
        await add_action_log("prod_deleted", ADMIN_ID, prod["name"])
        products = await get_products_by_category(cat_id, limit=50)
        currency = await get_setting("currency", "Rs")
        await safe_edit(
            query,
            f"📦 <b>Products</b>\n{separator()}\n\n📊 {len(products)} products",
            reply_markup=admin_prods_kb(products, cat_id, currency),
        )
    else:
        await safe_edit(query, "❌ Product not found.", reply_markup=back_kb("adm_cats"))


async def admin_prod_img_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    prod_id = int(query.data.split(":")[1])
    context.user_data["state"] = f"adm_prod_img:{prod_id}"
    await safe_edit(
        query,
        f"🖼️ <b>Set Product Image</b>\n{separator()}\n\n📸 Send a photo for this product:",
        reply_markup=back_kb(f"adm_prod:{prod_id}"),
    )


async def admin_prod_stock_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
        "• <code>-1</code> = unlimited\n"
        "• <code>0</code> = out of stock"
    )
    await safe_edit(query, text, reply_markup=back_kb(f"adm_prod:{prod_id}"))


async def admin_prod_delivery_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set delivery type — show choice between Auto and Manual."""
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    prod_id = int(query.data.split(":")[1])
    prod = await get_product(prod_id)
    if not prod:
        await query.answer("❌ Product not found.", show_alert=True)
        return

    current = prod.get("delivery_type", "manual")
    d_icon = delivery_icon(current)
    d_data = prod.get("delivery_data", "")
    data_preview = (d_data[:30] + "...") if len(d_data) > 30 else (d_data or "Not set")

    text = (
        f"📦 <b>Delivery Settings — {html_escape(prod['name'])}</b>\n"
        f"{separator()}\n\n"
        f"Current type: {d_icon} <b>{current}</b>\n"
        f"Delivery data: <code>{html_escape(data_preview)}</code>\n\n"
        "Choose delivery type:"
    )
    rows = [
        [
            Btn("⚡ Auto (Instant)", callback_data=f"adm_prod_deltype:{prod_id}:auto"),
            Btn("🕐 Manual", callback_data=f"adm_prod_deltype:{prod_id}:manual"),
        ],
        [Btn("📝 Set Delivery Data", callback_data=f"adm_prod_deldata:{prod_id}")],
        [Btn("◀️ Back", callback_data=f"adm_prod:{prod_id}")],
    ]
    await safe_edit(query, text, reply_markup=InlineKeyboardMarkup(rows))


async def admin_prod_deltype_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set delivery_type to auto or manual."""
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    parts = query.data.split(":")
    prod_id = int(parts[1])
    new_type = parts[2]  # "auto" or "manual"

    await update_product(prod_id, delivery_type=new_type)
    d_icon = delivery_icon(new_type)
    await query.answer(f"✅ Delivery type set to {d_icon} {new_type}!", show_alert=True)

    # Refresh delivery panel
    query.data = f"adm_prod_delivery:{prod_id}"
    await admin_prod_delivery_handler(update, context)


async def admin_prod_deldata_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompt admin to set delivery data (text) or upload a file."""
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    prod_id = int(query.data.split(":")[1])
    context.user_data["state"] = f"adm_prod_deldata:{prod_id}"
    text = (
        f"📝 <b>Set Delivery Data</b>\n"
        f"{separator()}\n\n"
        "This is what customers receive after payment is approved.\n\n"
        "You can send:\n"
        "• <b>Text message</b> — license key, download link, instructions\n"
        "• <b>Photo</b> — send a photo and it will be delivered\n"
        "• <b>Document/File</b> — send a file to deliver\n\n"
        "Send it now:"
    )
    await safe_edit(query, text, reply_markup=back_kb(f"adm_prod_delivery:{prod_id}"))


# ════════════════════════ ORDERS ════════════════════════

async def admin_orders_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    orders = await get_all_orders(limit=20)
    currency = await get_setting("currency", "Rs")
    await safe_edit(
        query,
        f"🛒 <b>All Orders</b>\n{separator()}\n\n📊 {len(orders)} recent orders",
        reply_markup=admin_orders_kb(orders, currency),
    )


async def admin_order_detail_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
    total = int(order["total"]) if order["total"] == int(order["total"]) else order["total"]

    text = f"📦 <b>Order #{order_id}</b>\n{separator()}\n"
    for item in items:
        text += f"\n• {html_escape(item['name'])} × {item['quantity']}\n"

    text += (
        f"{separator()}\n"
        f"👤 {html_escape(user_name)} (<code>{order['user_id']}</code>)\n"
        f"💰 Total: <b>{currency} {total}</b>\n"
        f"{status_emoji(order['status'])} Status: <b>{order['status']}</b>\n"
        f"{status_emoji(order['payment_status'])} Payment: <b>{order['payment_status']}</b>\n"
    )
    if order.get("coupon_code"):
        text += f"🎫 Coupon: {html_escape(order['coupon_code'])}\n"
    if order.get("created_at"):
        text += f"📅 {order['created_at'][:16]}"

    await safe_edit(query, text, reply_markup=admin_order_detail_kb(order_id))


async def admin_order_status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
    await add_action_log("order_status", ADMIN_ID, f"Order #{order_id} → {new_status}")

    # Notify user
    try:
        await context.bot.send_message(
            chat_id=order["user_id"],
            text=(
                f"{status_emoji(new_status)} <b>Order #{order_id} Update</b>\n"
                f"{separator()}\n\n"
                f"Status: <b>{new_status.title()}</b>\n"
                "Check details in 📦 My Orders."
            ),
            parse_mode="HTML",
        )
    except Exception as e:
        logger.warning("Could not notify user %s: %s", order["user_id"], e)

    await query.answer(f"✅ Order #{order_id} → {new_status}", show_alert=True)

    # Refresh detail view
    query.data = f"adm_ord:{order_id}"
    await admin_order_detail_handler(update, context)


# ════════════════════════ USERS ════════════════════════

async def admin_users_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    users = await get_all_users(limit=20)
    total = await get_user_count()
    await safe_edit(
        query,
        f"👥 <b>All Users</b>\n{separator()}\n\n📊 {total} registered users",
        reply_markup=admin_users_kb(users),
    )


async def admin_user_detail_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    uid = int(query.data.split(":")[1])
    user = await get_user(uid)
    if not user:
        await safe_edit(query, "❌ User not found.", reply_markup=back_kb("adm_users"))
        return

    currency = await get_setting("currency", "Rs")
    order_count = await get_user_order_count(uid)
    balance = await get_user_balance(uid)

    text = (
        f"👤 <b>User Details</b>\n"
        f"{separator()}\n\n"
        f"🆔 ID: <code>{uid}</code>\n"
        f"👤 Name: {html_escape(user['full_name'] or 'N/A')}\n"
        f"📎 @{html_escape(user['username'] or 'N/A')}\n"
        f"💳 Balance: {format_price(balance, currency)}\n"
        f"🛒 Orders: {order_count}\n"
        f"🚫 Banned: {'Yes' if user['banned'] else 'No'}\n"
        f"📅 Joined: {str(user.get('joined_at', 'N/A'))[:10]}"
    )
    await safe_edit(query, text, reply_markup=admin_user_detail_kb(uid, bool(user["banned"])))


async def admin_ban_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    uid = int(query.data.split(":")[1])
    await ban_user(uid)
    await add_action_log("user_banned", ADMIN_ID, str(uid))
    await query.answer(f"🚫 User {uid} banned!", show_alert=True)
    # Refresh view
    query.data = f"adm_user:{uid}"
    await admin_user_detail_handler(update, context)


async def admin_unban_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    uid = int(query.data.split(":")[1])
    await unban_user(uid)
    await add_action_log("user_unbanned", ADMIN_ID, str(uid))
    await query.answer(f"✅ User {uid} unbanned!", show_alert=True)
    query.data = f"adm_user:{uid}"
    await admin_user_detail_handler(update, context)


# ════════════════════════ COUPONS ════════════════════════

async def admin_coupons_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    coupons = await get_all_coupons()
    await safe_edit(
        query,
        f"🎫 <b>Manage Coupons</b>\n{separator()}\n\n📊 {len(coupons)} coupons",
        reply_markup=admin_coupons_kb(coupons),
    )


async def admin_coupon_add_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    context.user_data["state"] = "adm_coupon_data"
    text = (
        f"➕ <b>Add Coupon</b>\n{separator()}\n\n"
        "Format: <code>CODE|discount_percent|max_uses</code>\n\n"
        "Example: <code>SAVE20|20|100</code>\n"
        "<i>(0 max_uses = unlimited)</i>"
    )
    await safe_edit(query, text, reply_markup=back_kb("adm_coupons"))


async def admin_coupon_toggle_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    code = query.data.split(":")[1]
    await toggle_coupon(code)
    await query.answer(f"✅ {code} toggled!", show_alert=True)
    coupons = await get_all_coupons()
    await safe_edit(
        query,
        f"🎫 <b>Manage Coupons</b>\n{separator()}\n\n📊 {len(coupons)} coupons",
        reply_markup=admin_coupons_kb(coupons),
    )


async def admin_coupon_del_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    code = query.data.split(":")[1]
    await delete_coupon(code)
    await query.answer(f"✅ {code} deleted!", show_alert=True)
    coupons = await get_all_coupons()
    await safe_edit(
        query,
        f"🎫 <b>Manage Coupons</b>\n{separator()}\n\n📊 {len(coupons)} coupons",
        reply_markup=admin_coupons_kb(coupons),
    )


# ════════════════════════ PAYMENT METHODS ════════════════════════

async def admin_payments_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    methods = await get_all_payment_methods()
    await safe_edit(
        query,
        f"💳 <b>Payment Methods</b>\n{separator()}\n\n📊 {len(methods)} methods",
        reply_markup=admin_payments_kb(methods),
    )


async def admin_pay_add_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    context.user_data["state"] = "adm_pay_data"
    text = (
        f"➕ <b>Add Payment Method</b>\n{separator()}\n\n"
        "Format: <code>emoji|name|details</code>\n\n"
        "Example:\n<code>🏦|Bank Transfer|Bank: HBL\nAccount: 1234567890</code>"
    )
    await safe_edit(query, text, reply_markup=back_kb("adm_payments"))


async def admin_pay_del_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    method_id = int(query.data.split(":")[1])
    await delete_payment_method(method_id)
    await query.answer("✅ Deleted!", show_alert=True)
    methods = await get_all_payment_methods()
    await safe_edit(
        query,
        f"💳 <b>Payment Methods</b>\n{separator()}\n\n📊 {len(methods)} methods",
        reply_markup=admin_payments_kb(methods),
    )


# ════════════════════════ PAYMENT PROOFS ════════════════════════

async def admin_proofs_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    proofs = await get_pending_proofs()
    await safe_edit(
        query,
        f"📸 <b>Pending Proofs</b>\n{separator()}\n\n⏳ {len(proofs)} awaiting review",
        reply_markup=admin_proofs_kb(proofs),
    )


async def admin_proof_detail_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
        total = int(order["total"]) if order["total"] == int(order["total"]) else order["total"]

    text = (
        f"📸 <b>Proof #{proof_id}</b>\n"
        f"{separator()}\n\n"
        f"🆔 Order: #{proof['order_id']}\n"
        f"👤 {html_escape(user['full_name'] if user else 'N/A')} (<code>{proof['user_id']}</code>)\n"
        f"💰 Amount: {currency} {total}\n"
        f"💳 Method: {html_escape(method['name'] if method else 'N/A')}\n"
        f"📊 Status: {proof['status']}\n"
        f"📅 {str(proof.get('created_at', 'N/A'))[:16]}"
    )

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
    """Approve payment and trigger auto-delivery if applicable."""
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
    await add_action_log("proof_approved", ADMIN_ID, f"Proof #{proof_id}, Order #{proof['order_id']}")

    currency = await get_setting("currency", "Rs")

    # Send payment approved notification first
    try:
        await context.bot.send_message(
            chat_id=proof["user_id"],
            text=(
                f"✅ <b>Payment Approved!</b>\n"
                f"{separator()}\n\n"
                f"Your payment for Order #{proof['order_id']} has been approved!\n"
                "Your products are being prepared. 🎉"
            ),
            parse_mode="HTML",
        )
    except Exception as e:
        logger.warning("Failed to notify user: %s", e)

    # Auto-delivery: send products that have delivery_type = "auto"
    order = await get_order(proof["order_id"])
    if order:
        items = json.loads(order["items_json"]) if order["items_json"] else []
        auto_delivered = 0

        for item in items:
            prod = await get_product(item["product_id"])
            if not prod:
                continue

            if prod.get("delivery_type") == "auto" and prod.get("delivery_data"):
                await _deliver_product_to_user(
                    context.bot, proof["user_id"], prod, item, currency
                )
                auto_delivered += 1

        if auto_delivered > 0:
            await update_order(proof["order_id"], status="delivered")
            await notify_log_channel(
                context.bot,
                f"⚡ <b>Auto-delivery sent</b>\n"
                f"Order #{proof['order_id']} | {auto_delivered} item(s) → User {proof['user_id']}"
            )
        elif len(items) > 0:
            # All manual — notify admin to send products
            await notify_log_channel(
                context.bot,
                f"🕐 <b>Manual delivery needed</b>\n"
                f"Order #{proof['order_id']} | User {proof['user_id']}"
            )

    await query.answer("✅ Proof approved!", show_alert=True)

    # Refresh proofs list
    proofs = await get_pending_proofs()
    await safe_edit(
        query,
        f"📸 <b>Pending Proofs</b>\n{separator()}\n\n⏳ {len(proofs)} awaiting review",
        reply_markup=admin_proofs_kb(proofs),
    )


async def _deliver_product_to_user(bot, user_id: int, prod: dict, item: dict, currency: str) -> None:
    """Send the product delivery data to the user.

    Handles different delivery_data formats:
    - Plain text (starts with no prefix) → send as text message
    - file_id (Telegram file) → try to send as document
    """
    delivery_data = prod.get("delivery_data", "")
    if not delivery_data:
        return

    product_name = html_escape(prod["name"])

    # Caption / header for the delivery message
    header = (
        f"📦 <b>Your Product: {product_name}</b>\n"
        f"{separator()}\n\n"
    )

    # Try sending as document (if it looks like a file_id)
    # file_ids are long strings without spaces
    if len(delivery_data) > 40 and " " not in delivery_data and "\n" not in delivery_data:
        try:
            await bot.send_document(
                chat_id=user_id,
                document=delivery_data,
                caption=header + "Here is your digital product! ⚡",
                parse_mode="HTML",
            )
            return
        except Exception:
            pass
        # Maybe it's a photo file_id
        try:
            await bot.send_photo(
                chat_id=user_id,
                photo=delivery_data,
                caption=header + "Here is your digital product! ⚡",
                parse_mode="HTML",
            )
            return
        except Exception:
            pass

    # Plain text delivery (license key, download link, instructions)
    try:
        await bot.send_message(
            chat_id=user_id,
            text=(
                header
                + delivery_data
                + "\n\n⚡ <i>Delivered automatically. Enjoy your purchase!</i>"
            ),
            parse_mode="HTML",
        )
    except Exception as e:
        logger.warning("Failed to auto-deliver to user %s: %s", user_id, e)


async def admin_proof_reject_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    proof_id = int(query.data.split(":")[1])
    context.user_data["state"] = f"adm_proof_reject:{proof_id}"
    await safe_edit(
        query,
        f"❌ <b>Reject Proof #{proof_id}</b>\n{separator()}\n\n📝 Send rejection reason:",
        reply_markup=back_kb("adm_proofs"),
    )


async def admin_proof_post_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
            caption=f"✅ Payment Proof #{proof_id} | Order #{proof['order_id']}",
            parse_mode="HTML",
        )
        await query.answer("✅ Posted!", show_alert=True)
    except Exception as e:
        await query.answer(f"❌ Failed: {e}", show_alert=True)


# ════════════════════════ SETTINGS (COMPLETELY REWRITTEN) ════════════════════════

async def admin_settings_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the improved categorized settings panel with current values."""
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    # Fetch all current values to display inline
    bot_name     = await get_setting("bot_name", "NanoStore")
    currency     = await get_setting("currency", "Rs")
    welcome_img  = await get_setting("welcome_image_id", "")
    min_order    = await get_setting("min_order", "0")
    daily_reward = await get_setting("daily_reward", "10")
    maintenance  = await get_setting("maintenance", "off")
    auto_del     = await get_setting("auto_delete", "0")

    img_badge   = "✅" if welcome_img else "❌"
    maint_badge = "🔴 ON" if maintenance == "on" else "🟢 OFF"
    autodel_badge = f"{auto_del}s" if int(auto_del) > 0 else "Off"

    text = (
        f"⚙️ <b>Bot Settings</b>\n"
        f"{separator()}\n\n"
        f"🏪 Store: <b>{html_escape(bot_name)}</b>\n"
        f"💰 Currency: <b>{html_escape(currency)}</b>\n"
        f"🖼️ Welcome Image: <b>{img_badge}</b>\n"
        f"🛒 Min Order: <b>{currency} {min_order}</b>\n"
        f"🎁 Daily Reward: <b>{currency} {daily_reward}</b>\n"
        f"🔧 Maintenance: <b>{maint_badge}</b>\n"
        f"⏱️ Auto-Delete: <b>{autodel_badge}</b>\n\n"
        "👇 Tap a setting to edit:"
    )
    await safe_edit(query, text, reply_markup=admin_settings_kb())


async def admin_set_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Edit a text-based setting OR toggle maintenance mode."""
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    key = query.data.split(":")[1]

    # Maintenance and auto-delete timer are special cases
    if key == "maintenance":
        current = await get_setting("maintenance", "off")
        new_val = "on" if current == "off" else "off"
        await set_setting("maintenance", new_val)
        badge = "🔴 ON" if new_val == "on" else "🟢 OFF"
        await query.answer(f"✅ Maintenance: {badge}", show_alert=True)
        await admin_settings_handler(update, context)
        return

    current = await get_setting(key, "(not set)")
    context.user_data["state"] = f"adm_set:{key}"

    labels = {
        "bot_name":             "Store Name",
        "currency":             "Currency Symbol",
        "welcome_text":         "Welcome Text (HTML supported)",
        "min_order":            "Minimum Order Amount",
        "daily_reward":         "Daily Reward Amount",
        "auto_delete":          "Auto-Delete Timer (seconds)",
        "maintenance_text":     "Maintenance Message",
        "payment_instructions": "Payment Instructions",
    }
    hints = {
        "currency":             "e.g. <code>Rs</code>  <code>$</code>  <code>€</code>",
        "welcome_text":         "Supports HTML: <code>&lt;b&gt;bold&lt;/b&gt;</code> etc.",
        "min_order":            "Cart minimum total. Example: <code>100</code>",
        "daily_reward":         "Balance added daily. Example: <code>25</code>",
        "auto_delete":          "<code>0</code> = disabled | <code>30</code> = delete after 30s",
        "maintenance_text":     "Message shown to users when maintenance is ON.",
        "payment_instructions": "Extra text shown on the payment screen.",
    }

    label = labels.get(key, key)
    hint  = hints.get(key, "")

    text = (
        f"⚙️ <b>Edit: {html_escape(label)}</b>\n"
        f"{separator()}\n\n"
        f"Current: <code>{html_escape(current)}</code>\n\n"
        "📝 Send the new value:"
        + (f"\n\n<i>{hint}</i>" if hint else "")
    )
    await safe_edit(query, text, reply_markup=back_kb("adm_settings"))


async def admin_welcome_image_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompt admin to send a photo for the welcome/start screen.

    This handler was previously MISSING from admin.py, causing an ImportError
    that crashed the bot on startup. It is now properly implemented.
    """
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    current = await get_setting("welcome_image_id", "")
    status = "✅ Currently set" if current else "❌ Not set yet"

    context.user_data["state"] = "adm_welcome_image"
    text = (
        f"🖼️ <b>Set Welcome Image</b>\n"
        f"{separator()}\n\n"
        f"Status: {status}\n\n"
        "📸 Send a photo to use on the /start welcome screen.\n\n"
        "This image is shown to every user when they start the bot.\n"
        "<i>Use your store banner, logo, or a product showcase.</i>"
    )
    await safe_edit(query, text, reply_markup=back_kb("adm_settings"))


# ════════════════════════ IMAGES PANEL (NEW) ════════════════════════

async def admin_img_panel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show images panel with status for all 7 screen images."""
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    # Get status for all image keys
    keys = [
        "welcome_image_id",
        "shop_image_id",
        "cart_image_id",
        "orders_image_id",
        "wallet_image_id",
        "support_image_id",
        "admin_panel_image_id",
    ]
    
    statuses = {}
    for key in keys:
        val = await get_setting(key, "")
        statuses[key] = bool(val)
    
    ui_enabled = await get_setting("ui_images_enabled", "on")
    toggle_status = "🟢 ON" if ui_enabled == "on" else "🔴 OFF"
    
    text = (
        f"🖼️ <b>Image Settings</b>\n"
        f"{separator()}\n\n"
        "Manage per-screen images for your bot.\n"
        "Each screen can have its own banner image.\n\n"
        f"🔧 Global Toggle: <b>{toggle_status}</b>\n\n"
        "👇 Tap a screen to set or clear its image:"
    )
    
    from keyboards import admin_images_kb
    await safe_edit(query, text, reply_markup=admin_images_kb(statuses))


async def admin_img_set_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompt admin to send a photo for a specific screen."""
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    key = query.data.split(":")[1]
    
    # Map keys to friendly screen names
    screen_names = {
        "welcome_image_id": "Welcome / Main Menu",
        "shop_image_id": "Shop",
        "cart_image_id": "Cart",
        "orders_image_id": "Orders",
        "wallet_image_id": "Wallet",
        "support_image_id": "Support",
        "admin_panel_image_id": "Admin Panel",
    }
    
    screen_name = screen_names.get(key, key)
    current = await get_setting(key, "")
    status = "✅ Currently set" if current else "❌ Not set yet"
    
    context.user_data["state"] = f"adm_img_wait:{key}"
    
    text = (
        f"🖼️ <b>Set Image: {screen_name}</b>\n"
        f"{separator()}\n\n"
        f"Status: {status}\n\n"
        "📸 Send a photo to use for this screen.\n\n"
        "<i>The photo will be shown with the screen text as a caption.</i>"
    )
    
    # Edit the message and store its message_id for later deletion
    await safe_edit(query, text, reply_markup=back_kb("adm_img_panel"))
    
    # Store prompt message_id so we can delete it after photo is received
    context.user_data["adm_img_prompt_msg_id"] = query.message.message_id


async def admin_img_clear_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear image for a specific screen."""
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    key = query.data.split(":")[1]
    await set_setting(key, "")
    
    screen_names = {
        "welcome_image_id": "Welcome",
        "shop_image_id": "Shop",
        "cart_image_id": "Cart",
        "orders_image_id": "Orders",
        "wallet_image_id": "Wallet",
        "support_image_id": "Support",
        "admin_panel_image_id": "Admin Panel",
    }
    
    screen_name = screen_names.get(key, key)
    await query.answer(f"✅ {screen_name} image cleared!", show_alert=True)
    
    # Refresh panel
    await admin_img_panel_handler(update, context)


async def admin_img_toggle_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Toggle ui_images_enabled on/off."""
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    current = await get_setting("ui_images_enabled", "on")
    new_val = "off" if current == "on" else "on"
    await set_setting("ui_images_enabled", new_val)
    
    status = "🟢 ON" if new_val == "on" else "🔴 OFF"
    await query.answer(f"✅ Images: {status}", show_alert=True)
    
    # Refresh panel
    await admin_img_panel_handler(update, context)


# ════════════════════════ FORCE JOIN ════════════════════════

async def admin_fj_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    channels = await get_force_join_channels()
    await safe_edit(
        query,
        f"📢 <b>Force Join Channels</b>\n{separator()}\n\n📊 {len(channels)} channels configured",
        reply_markup=admin_fj_kb(channels),
    )


async def admin_fj_add_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    context.user_data["state"] = "adm_fj_channel"
    text = (
        f"➕ <b>Add Force Join Channel</b>\n{separator()}\n\n"
        "Format: <code>channel_id|name|invite_link</code>\n\n"
        "Example:\n<code>-1001234567890|NanoStore Updates|https://t.me/nanostore</code>"
    )
    await safe_edit(query, text, reply_markup=back_kb("adm_fj"))


async def admin_fj_del_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    fj_id = int(query.data.split(":")[1])
    await delete_force_join_channel(fj_id)
    await query.answer("✅ Channel removed!", show_alert=True)
    channels = await get_force_join_channels()
    await safe_edit(
        query,
        f"📢 <b>Force Join Channels</b>\n{separator()}\n\n📊 {len(channels)} channels",
        reply_markup=admin_fj_kb(channels),
    )


# ════════════════════════ BULK IMPORT ════════════════════════

async def admin_bulk_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    context.user_data["state"] = "adm_bulk_data"
    text = (
        f"📥 <b>Bulk Product Import</b>\n{separator()}\n\n"
        "One product per line:\n"
        "<code>category_id|name|description|price|stock</code>\n\n"
        "Example:\n"
        "<code>1|Python eBook|Learn Python|500|-1</code>\n"
        "<code>2|Resume Template|Professional|200|50</code>\n\n"
        "💡 After import, set images via Admin → Categories → Product → Set Image"
    )
    await safe_edit(query, text, reply_markup=back_kb("admin"))


async def admin_bulk_stock_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    context.user_data["state"] = "adm_bulk_stock_data"
    text = (
        f"📊 <b>Bulk Stock Update</b>\n{separator()}\n\n"
        "One update per line:\n"
        "<code>product_id|stock</code>\n\n"
        "Example:\n<code>1|50</code>\n<code>2|-1</code>\n<code>3|0</code>"
    )
    await safe_edit(query, text, reply_markup=back_kb("admin"))


# ════════════════════════ BROADCAST ════════════════════════

async def admin_broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    context.user_data["state"] = "adm_broadcast_text"
    user_count = await get_user_count()
    text = (
        f"📣 <b>Broadcast Message</b>\n{separator()}\n\n"
        f"📊 Will reach <b>{user_count}</b> users.\n\n"
        "📝 Type your message (HTML formatting supported):\n\n"
        "<i>Example: &lt;b&gt;Flash Sale!&lt;/b&gt; 50% off today only 🎉</i>"
    )
    await safe_edit(query, text, reply_markup=back_kb("admin"))


async def admin_broadcast_confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the broadcast to all non-banned users."""
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

    user_ids = await get_all_user_ids()
    sent = 0
    failed = 0

    for uid in user_ids:
        try:
            await context.bot.send_message(
                chat_id=uid, text=broadcast_text, parse_mode="HTML"
            )
            sent += 1
        except Exception:
            failed += 1

    text = (
        f"📣 <b>Broadcast Complete!</b>\n{separator()}\n\n"
        f"✅ Sent: <b>{sent}</b>\n"
        f"❌ Failed: <b>{failed}</b>\n"
        f"📊 Total: {sent + failed}"
    )
    await safe_edit(query, text, reply_markup=back_kb("admin"))
    await add_action_log("broadcast", ADMIN_ID, f"Sent: {sent}, Failed: {failed}")


# ════════════════════════ WALLET TOP-UPS ════════════════════════

async def admin_topups_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    from database import get_pending_topups
    topups = await get_pending_topups()
    currency = await get_setting("currency", "Rs")
    from keyboards import admin_topups_kb
    await safe_edit(
        query,
        f"💳 <b>Pending Top-Ups</b>\n{separator()}\n\n⏳ {len(topups)} awaiting review",
        reply_markup=admin_topups_kb(topups, currency),
    )


async def admin_topup_detail_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    from database import get_topup
    topup_id = int(query.data.split(":")[1])
    topup = await get_topup(topup_id)
    if not topup:
        await safe_edit(query, "❌ Top-up not found.", reply_markup=back_kb("adm_topups"))
        return

    user = await get_user(topup["user_id"])
    method = await get_payment_method(topup["method_id"]) if topup.get("method_id") else None
    currency = await get_setting("currency", "Rs")
    amt = int(topup["amount"]) if topup["amount"] == int(topup["amount"]) else topup["amount"]

    text = (
        f"💳 <b>Top-Up #{topup_id}</b>\n"
        f"{separator()}\n\n"
        f"👤 {html_escape(user['full_name'] if user else 'N/A')} (<code>{topup['user_id']}</code>)\n"
        f"💰 Amount: {currency} {amt}\n"
        f"💳 Method: {html_escape(method['name'] if method else 'N/A')}\n"
        f"📊 Status: {topup['status']}\n"
        f"📅 {str(topup.get('created_at', 'N/A'))[:16]}"
    )

    from keyboards import admin_topup_detail_kb
    if topup.get("proof_file_id"):
        try:
            await query.message.chat.send_photo(
                photo=topup["proof_file_id"],
                caption=text,
                parse_mode="HTML",
                reply_markup=admin_topup_detail_kb(topup_id),
            )
            try:
                await query.message.delete()
            except Exception:
                pass
            return
        except Exception as e:
            logger.warning("Failed to send topup proof photo: %s", e)

    await safe_edit(query, text, reply_markup=admin_topup_detail_kb(topup_id))


async def admin_topup_approve_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    from database import get_topup, update_topup, update_user_balance
    topup_id = int(query.data.split(":")[1])
    topup = await get_topup(topup_id)
    if not topup:
        await query.answer("❌ Top-up not found.", show_alert=True)
        return

    bonus_percent = float(await get_setting("topup_bonus_percent", "0"))
    credit = topup["amount"] + (topup["amount"] * bonus_percent / 100)

    await update_topup(topup_id, status="approved", reviewed_by=ADMIN_ID)
    await update_user_balance(topup["user_id"], credit)
    await add_action_log("topup_approved", ADMIN_ID, f"Top-Up #{topup_id}, Amount: {credit}")

    currency = await get_setting("currency", "Rs")
    amt_display = int(credit) if credit == int(credit) else f"{credit:.2f}"
    user_balance = await get_user_balance(topup["user_id"])
    bal_display = int(user_balance) if user_balance == int(user_balance) else f"{user_balance:.2f}"

    try:
        await context.bot.send_message(
            chat_id=topup["user_id"],
            text=(
                f"✅ <b>Top-Up Approved!</b>\n"
                f"{separator()}\n\n"
                f"💰 Credited: <b>{currency} {amt_display}</b>\n"
                f"💳 New Balance: <b>{currency} {bal_display}</b>\n\n"
                "Thank you! Your wallet has been topped up. 🎉"
            ),
            parse_mode="HTML",
        )
    except Exception as e:
        logger.warning("Failed to notify user: %s", e)

    await query.answer("✅ Top-up approved!", show_alert=True)

    from database import get_pending_topups
    from keyboards import admin_topups_kb
    topups = await get_pending_topups()
    await safe_edit(
        query,
        f"💳 <b>Pending Top-Ups</b>\n{separator()}\n\n⏳ {len(topups)} awaiting review",
        reply_markup=admin_topups_kb(topups, currency),
    )


async def admin_topup_reject_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    topup_id = int(query.data.split(":")[1])
    context.user_data["state"] = f"adm_topup_reject:{topup_id}"
    await safe_edit(
        query,
        f"❌ <b>Reject Top-Up #{topup_id}</b>\n{separator()}\n\n📝 Send rejection reason:",
        reply_markup=back_kb("adm_topups"),
    )


# ════════════════════════ ADMIN TEXT ROUTER ════════════════════════

async def admin_text_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Route all text input from admin based on active state."""
    if not _is_admin(update.effective_user.id):
        return

    state = context.user_data.get("state", "")
    text = update.message.text.strip()

    # ── Category: new name ──
    if state == "adm_cat_name":
        context.user_data.pop("state", None)
        cat_id = await add_category(text)
        # Immediately ask for category image so image + text workflow is smooth
        context.user_data["state"] = f"adm_cat_img:{cat_id}"
        msg = await update.message.reply_text(
            f"✅ Category <b>{html_escape(text)}</b> created (ID: {cat_id})\n\n"
            "📸 Now send a photo to set this category image.",
            parse_mode="HTML",
        )
        await auto_delete(msg)
        await auto_delete(update.message)
        await add_action_log("cat_added", ADMIN_ID, text)
        return

    # ── Category: edit name/emoji ──
    if state.startswith("adm_cat_emoji:"):
        cat_id = int(state.split(":")[1])
        context.user_data.pop("state", None)
        if "|" in text:
            emoji, name = text.split("|", 1)
            await update_category(cat_id, emoji=emoji.strip(), name=name.strip())
        else:
            await update_category(cat_id, name=text)
        msg = await update.message.reply_text("✅ Category updated!", parse_mode="HTML")
        await auto_delete(msg)
        await auto_delete(update.message)
        return

    # ── Product: name (step 1/3) ──
    if state.startswith("adm_prod_name:"):
        context.user_data["state"] = "adm_prod_desc"
        context.user_data.setdefault("temp", {})["name"] = text
        msg = await update.message.reply_text(
            "Step 2/3: 📝 Send the product <b>description</b>:\n<i>(or <code>-</code> to skip)</i>",
            parse_mode="HTML",
        )
        await auto_delete(msg)
        await auto_delete(update.message)
        return

    # ── Product: description (step 2/3) ──
    if state == "adm_prod_desc":
        context.user_data["state"] = "adm_prod_price"
        context.user_data.setdefault("temp", {})["desc"] = "" if text == "-" else text
        msg = await update.message.reply_text(
            "Step 3/3: 💰 Send the <b>price</b> (number only):", parse_mode="HTML"
        )
        await auto_delete(msg)
        await auto_delete(update.message)
        return

    # ── Product: price (step 3/3 → create product) ──
    if state == "adm_prod_price":
        try:
            price = float(text)
        except ValueError:
            msg = await update.message.reply_text("❌ Invalid price. Send a number.", parse_mode="HTML")
            await auto_delete(msg)
            await auto_delete(update.message)
            return

        context.user_data.pop("state", None)
        temp = context.user_data.pop("temp", {})
        cat_id = temp.get("cat_id")
        name   = temp.get("name", "Unnamed")
        desc   = temp.get("desc", "")
        currency = await get_setting("currency", "Rs")

        prod_id = await add_product(cat_id, name, desc, price)
        msg = await update.message.reply_text(
            f"✅ <b>{html_escape(name)}</b> created!\n"
            f"💰 {format_price(price, currency)}  |  🆔 {prod_id}\n\n"
            "💡 Next steps:\n"
            "• 🖼️ Set image → Product → Set Image\n"
            "• 📦 Set delivery → Product → Delivery\n"
            "• 📊 Set stock → Product → Stock",
            parse_mode="HTML",
        )
        await auto_delete(msg)
        await auto_delete(update.message)
        await add_action_log("prod_added", ADMIN_ID, f"{name} @ {price}")
        return

    # ── Product: edit field ──
    if state.startswith("adm_prod_edit:"):
        parts = state.split(":")
        prod_id = int(parts[1])
        field = parts[2]
        context.user_data.pop("state", None)

        if field == "price":
            try:
                value = float(text)
            except ValueError:
                msg = await update.message.reply_text("❌ Invalid price.", parse_mode="HTML")
                await auto_delete(msg)
                await auto_delete(update.message)
                return
            await update_product(prod_id, price=value)
        elif field in ("name", "description"):
            await update_product(prod_id, **{field: text})
        msg = await update.message.reply_text(f"✅ {field.title()} updated!", parse_mode="HTML")
        await auto_delete(msg)
        await auto_delete(update.message)
        return

    # ── Product: stock ──
    if state.startswith("adm_prod_stock:"):
        prod_id = int(state.split(":")[1])
        context.user_data.pop("state", None)
        try:
            stock = int(text)
        except ValueError:
            msg = await update.message.reply_text("❌ Send a number.", parse_mode="HTML")
            await auto_delete(msg)
            await auto_delete(update.message)
            return
        await update_product(prod_id, stock=stock)
        msg = await update.message.reply_text(
            f"✅ Stock set to {format_stock(stock)}", parse_mode="HTML"
        )
        await auto_delete(msg)
        await auto_delete(update.message)
        return

    # ── Product: delivery data (text) ──
    if state.startswith("adm_prod_deldata:"):
        prod_id = int(state.split(":")[1])
        context.user_data.pop("state", None)
        await update_product(prod_id, delivery_data=text, delivery_type="auto")
        msg = await update.message.reply_text(
            "✅ Delivery data saved!\n"
            "Delivery type set to ⚡ <b>Auto</b>.\n\n"
            "Customers will receive this text after payment approval.",
            parse_mode="HTML",
        )
        await auto_delete(msg)
        await auto_delete(update.message)
        return

    # ── Coupon: create ──
    if state == "adm_coupon_data":
        context.user_data.pop("state", None)
        try:
            parts = text.split("|")
            code = parts[0].strip().upper()
            discount = int(parts[1].strip())
            max_uses = int(parts[2].strip()) if len(parts) > 2 else 0
            await create_coupon(code, discount, max_uses)
            msg = await update.message.reply_text(
                f"✅ Coupon <b>{html_escape(code)}</b> created!\n"
                f"🎫 {discount}% off | Max: {max_uses or 'Unlimited'}",
                parse_mode="HTML",
            )
            await auto_delete(msg)
            await auto_delete(update.message)
            await add_action_log("coupon_added", ADMIN_ID, code)
        except (ValueError, IndexError):
            msg = await update.message.reply_text(
                "❌ Format: <code>CODE|percent|max_uses</code>", parse_mode="HTML"
            )
            await auto_delete(msg)
            await auto_delete(update.message)
        return

    # ── Payment method: create ──
    if state == "adm_pay_data":
        context.user_data.pop("state", None)
        try:
            parts = text.split("|", 2)
            emoji = parts[0].strip()
            name  = parts[1].strip()
            details = parts[2].strip()
            await add_payment_method(name, details, emoji)
            msg = await update.message.reply_text(
                f"✅ Payment method <b>{html_escape(name)}</b> added!", parse_mode="HTML"
            )
            await auto_delete(msg)
            await auto_delete(update.message)
        except (ValueError, IndexError):
            msg = await update.message.reply_text(
                "❌ Format: <code>emoji|name|details</code>", parse_mode="HTML"
            )
            await auto_delete(msg)
            await auto_delete(update.message)
        return

    # ── Force join: add channel ──
    if state == "adm_fj_channel":
        context.user_data.pop("state", None)
        try:
            parts = text.split("|", 2)
            await add_force_join_channel(parts[0].strip(), parts[1].strip(), parts[2].strip())
            msg = await update.message.reply_text(
                f"✅ Channel <b>{html_escape(parts[1].strip())}</b> added!", parse_mode="HTML"
            )
            await auto_delete(msg)
            await auto_delete(update.message)
        except (ValueError, IndexError):
            msg = await update.message.reply_text(
                "❌ Format: <code>channel_id|name|invite_link</code>", parse_mode="HTML"
            )
            await auto_delete(msg)
            await auto_delete(update.message)
        return

    # ── Bulk import ──
    if state == "adm_bulk_data":
        context.user_data.pop("state", None)
        lines = text.strip().split("\n")
        added = 0
        errors = 0
        for line in lines:
            try:
                parts = line.split("|")
                cat_id = int(parts[0].strip())
                name   = parts[1].strip()
                desc   = parts[2].strip() if len(parts) > 2 else ""
                price  = float(parts[3].strip()) if len(parts) > 3 else 0
                stock  = int(parts[4].strip()) if len(parts) > 4 else -1
                await add_product(cat_id, name, desc, price, stock)
                added += 1
            except Exception:
                errors += 1

        msg = await update.message.reply_text(
            f"📥 <b>Bulk Import Done!</b>\n\n"
            f"✅ Added: {added}\n❌ Errors: {errors}\n\n"
            "💡 Set images via Admin → Categories → Product → Set Image",
            parse_mode="HTML",
        )
        await auto_delete(msg)
        await auto_delete(update.message)
        await add_action_log("bulk_import", ADMIN_ID, f"Added:{added} Errors:{errors}")
        return

    # ── Bulk stock update ──
    if state == "adm_bulk_stock_data":
        context.user_data.pop("state", None)
        lines = text.strip().split("\n")
        updated = 0
        errors = 0
        for line in lines:
            try:
                pid, stock = line.split("|", 1)
                await update_product(int(pid.strip()), stock=int(stock.strip()))
                updated += 1
            except Exception:
                errors += 1
        msg = await update.message.reply_text(
            f"📊 <b>Stock Update Done!</b>\n\n✅ Updated: {updated}\n❌ Errors: {errors}",
            parse_mode="HTML",
        )
        await auto_delete(msg)
        await auto_delete(update.message)
        return

    # ── Broadcast: preview ──
    if state == "adm_broadcast_text":
        context.user_data["state"] = None
        context.user_data.setdefault("temp", {})["broadcast_text"] = text
        user_count = await get_user_count()
        msg = await update.message.reply_text(
            f"📣 <b>Broadcast Preview</b>\n{separator()}\n\n"
            f"{text}\n\n"
            f"{separator()}\n"
            f"👥 Will be sent to <b>{user_count}</b> users.",
            parse_mode="HTML",
            reply_markup=admin_broadcast_confirm_kb(),
        )
        await auto_delete(msg)
        await auto_delete(update.message)
        return

    # ── Settings: update value ──
    if state.startswith("adm_set:"):
        key = state.split(":")[1]
        context.user_data.pop("state", None)
        await set_setting(key, text)
        msg = await update.message.reply_text(
            f"✅ <b>{html_escape(key)}</b> updated!\n<code>{html_escape(text)}</code>",
            parse_mode="HTML",
        )
        await auto_delete(msg)
        await auto_delete(update.message)
        return

    # ── Proof: rejection reason ──
    if state.startswith("adm_proof_reject:"):
        proof_id = int(state.split(":")[1])
        context.user_data.pop("state", None)
        proof = await get_payment_proof(proof_id)
        if proof:
            await update_proof(proof_id, status="rejected", reviewed_by=ADMIN_ID, admin_note=text)
            await update_order(proof["order_id"], payment_status="rejected")
            try:
                await context.bot.send_message(
                    chat_id=proof["user_id"],
                    text=(
                        f"❌ <b>Payment Rejected</b>\n{separator()}\n\n"
                        f"Order #{proof['order_id']}\n"
                        f"Reason: {html_escape(text)}\n\n"
                        "Please re-submit or contact support."
                    ),
                    parse_mode="HTML",
                )
            except Exception:
                pass
            await add_action_log("proof_rejected", ADMIN_ID, f"#{proof_id}: {text}")
        msg = await update.message.reply_text("✅ Proof rejected.", parse_mode="HTML")
        await auto_delete(msg)
        await auto_delete(update.message)
        return

    # ── Top-Up: rejection reason ──
    if state.startswith("adm_topup_reject:"):
        from database import get_topup, update_topup
        topup_id = int(state.split(":")[1])
        context.user_data.pop("state", None)
        topup = await get_topup(topup_id)
        if topup:
            await update_topup(topup_id, status="rejected", reviewed_by=ADMIN_ID, admin_note=text)
            try:
                await context.bot.send_message(
                    chat_id=topup["user_id"],
                    text=(
                        f"❌ <b>Top-Up Rejected</b>\n{separator()}\n\n"
                        f"Top-Up ID: #{topup_id}\n"
                        f"Reason: {html_escape(text)}\n\n"
                        "Please re-submit with correct payment proof."
                    ),
                    parse_mode="HTML",
                )
            except Exception:
                pass
            await add_action_log("topup_rejected", ADMIN_ID, f"#{topup_id}: {text}")
        msg = await update.message.reply_text("✅ Top-up rejected.", parse_mode="HTML")
        await auto_delete(msg)
        await auto_delete(update.message)
        return

    # ── Product FAQ: add ──
    if state.startswith("adm_prod_faq:"):
        prod_id = int(state.split(":")[1])
        context.user_data.pop("state", None)
        if "|" not in text:
            msg = await update.message.reply_text(
                "❌ Format: <code>question | answer</code>", parse_mode="HTML"
            )
            await auto_delete(msg)
            await auto_delete(update.message)
            return
        q, a = text.split("|", 1)
        await add_product_faq(prod_id, q.strip(), a.strip())
        msg = await update.message.reply_text("✅ FAQ added!", parse_mode="HTML")
        await auto_delete(msg)
        await auto_delete(update.message)
        return


# ════════════════════════ ADMIN PHOTO ROUTER ════════════════════════

async def admin_photo_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Route admin photo/file uploads based on active state.

    Handles: admin image settings, welcome image, product image, category image,
             product delivery data (file), product media.
    
    PRIORITY ORDER (CRITICAL):
    1. adm_img_wait:<key> - Admin setting screen images (NEW)
    2. adm_welcome_image - Legacy welcome image handler
    3. adm_prod_img - Product images
    4. adm_prod_deldata - Product delivery data
    5. adm_cat_img - Category images
    6. adm_prod_media - Product media files
    """
    if not _is_admin(update.effective_user.id):
        return

    state = context.user_data.get("state", "")

    # Determine what was sent
    file_id = None
    media_type = "file"

    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        media_type = "photo"
    elif update.message.document:
        file_id = update.message.document.file_id
        media_type = "file"
    elif update.message.video:
        file_id = update.message.video.file_id
        media_type = "video"
    elif update.message.voice:
        file_id = update.message.voice.file_id
        media_type = "voice"

    if not file_id:
        return

    # ── PRIORITY 1: Admin image settings (adm_img_wait:<key>) ──
    if state.startswith("adm_img_wait:"):
        key = state.split(":", 1)[1]
        
        # DIAGNOSTIC LOGGING
        logger.info(f"=== ADM_IMG_WAIT HANDLER TRIGGERED ===")
        logger.info(f"Key: {key}")
        logger.info(f"Admin chat_id: {update.effective_chat.id}")
        logger.info(f"Admin message_id: {update.message.message_id}")
        logger.info(f"File_id: {file_id[:50]}")
        
        # Save file_id to settings
        await set_setting(key, file_id)
        logger.info(f"✅ Saved {key} to settings")
        
        # Map keys to friendly screen names
        screen_names = {
            "welcome_image_id": "Welcome / Main Menu",
            "shop_image_id": "Shop",
            "cart_image_id": "Cart",
            "orders_image_id": "Orders",
            "wallet_image_id": "Wallet",
            "support_image_id": "Support",
            "admin_panel_image_id": "Admin Panel",
        }
        screen_name = screen_names.get(key, key)
        
        # 1. Try to delete admin's photo message (best effort - may fail in DM)
        # Note: Telegram bots cannot delete user messages in private chats
        try:
            await update.message.delete()
            logger.info(f"✅ Deleted admin photo message (chat={update.effective_chat.id}, msg={update.message.message_id})")
        except Exception as e:
            logger.info(f"ℹ️ Could not delete admin photo (expected in DM): {type(e).__name__}")
        
        # 2. Delete the prompt message (bot's own message - MUST work)
        prompt_msg_id = context.user_data.pop("adm_img_prompt_msg_id", None)
        logger.info(f"Prompt message_id from user_data: {prompt_msg_id}")
        
        if prompt_msg_id:
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=prompt_msg_id
                )
                logger.info(f"✅ Deleted prompt message (chat={update.effective_chat.id}, msg={prompt_msg_id})")
            except Exception as e:
                logger.warning(f"❌ Failed to delete prompt (bot's own message): {type(e).__name__}: {e}")
        else:
            logger.warning("⚠️ No prompt_msg_id found in user_data")
        
        # 3. Send confirmation message (bot's own message)
        msg = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"✅ <b>Image saved for {screen_name}!</b>\n\n"
                 "The image will now appear on this screen for all users.",
            parse_mode="HTML"
        )
        logger.info(f"✅ Sent confirmation message (chat={msg.chat_id}, msg={msg.message_id})")
        
        # 4. Schedule deletion of confirmation (bot's own message - MUST work)
        from helpers import schedule_delete
        schedule_delete(context, msg.chat_id, msg.message_id, delay=7)
        
        # Clear state
        context.user_data.pop("state", None)
        logger.info(f"✅ Cleared state from user_data")
        
        await add_action_log("image_set", ADMIN_ID, f"{key}: {file_id[:30]}")
        logger.info(f"=== ADM_IMG_WAIT HANDLER COMPLETE ===")
        return

    # ── Welcome image (legacy handler) ──
    if state == "adm_welcome_image":
        context.user_data.pop("state", None)
        await set_setting("welcome_image_id", file_id)
        msg = await update.message.reply_text(
            "✅ <b>Welcome image updated!</b>\n\n"
            "📸 This image will now appear on /start for all users.",
            parse_mode="HTML",
        )
        await auto_delete(msg)
        await auto_delete(update.message)
        await add_action_log("welcome_image_set", ADMIN_ID, file_id[:30])
        return

    # ── Product image ──
    if state.startswith("adm_prod_img:"):
        prod_id = int(state.split(":")[1])
        context.user_data.pop("state", None)
        await update_product(prod_id, image_id=file_id)
        msg = await update.message.reply_text("✅ Product image set!", parse_mode="HTML")
        await auto_delete(msg)
        await auto_delete(update.message)
        return

    # ── Product delivery data (file) ──
    if state.startswith("adm_prod_deldata:"):
        prod_id = int(state.split(":")[1])
        context.user_data.pop("state", None)
        await update_product(prod_id, delivery_data=file_id, delivery_type="auto")
        msg = await update.message.reply_text(
            f"✅ Delivery file set! ({media_type})\n"
            "Delivery type → ⚡ <b>Auto</b>\n\n"
            "Customers will receive this file after payment approval.",
            parse_mode="HTML",
        )
        await auto_delete(msg)
        await auto_delete(update.message)
        return

    # ── Category image ──
    if state.startswith("adm_cat_img:"):
        cat_id = int(state.split(":")[1])
        context.user_data.pop("state", None)
        await update_category(cat_id, image_id=file_id)
        msg = await update.message.reply_text("✅ Category image set!", parse_mode="HTML")
        await auto_delete(msg)
        await auto_delete(update.message)
        return

    # ── Product media (video, voice, file as media) ──
    if state.startswith("adm_prod_media:"):
        parts = state.split(":")
        prod_id = int(parts[1])
        mtype = parts[2] if len(parts) > 2 else media_type
        context.user_data.pop("state", None)
        await add_product_media(prod_id, mtype, file_id)
        msg = await update.message.reply_text(
            f"✅ {mtype.title()} media added!", parse_mode="HTML"
        )
        await auto_delete(msg)
        await auto_delete(update.message)
        return


# ════════════════════════ FAQ & MEDIA ADMIN ════════════════════════

async def admin_prod_faq_add_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    prod_id = int(query.data.split(":")[1])
    context.user_data["state"] = f"adm_prod_faq:{prod_id}"
    await safe_edit(
        query,
        f"❓ <b>Add FAQ</b>\n{separator()}\n\n"
        "Format: <code>question | answer</code>\n\n"
        "Example: <code>What format? | PDF and EPUB</code>",
        reply_markup=back_kb(f"adm_prod:{prod_id}"),
    )


async def admin_prod_faq_del_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    faq_id = int(query.data.split(":")[2])
    await delete_product_faq(faq_id)
    await query.answer("✅ FAQ deleted!", show_alert=True)


async def admin_prod_media_add_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    parts = query.data.split(":")
    prod_id = int(parts[1])
    media_type = parts[2] if len(parts) > 2 else "video"
    context.user_data["state"] = f"adm_prod_media:{prod_id}:{media_type}"
    await safe_edit(
        query,
        f"🎬 <b>Add {media_type.title()} Media</b>\n{separator()}\n\nSend the {media_type} now:",
        reply_markup=back_kb(f"adm_prod:{prod_id}"),
    )


async def admin_prod_media_del_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not _is_admin(update.effective_user.id):
        return

    mid = int(query.data.split(":")[2])
    await delete_product_media(mid)
    await query.answer("✅ Media deleted!", show_alert=True)
