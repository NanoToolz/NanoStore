import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import ADMIN_ID
from database import (
    get_dashboard_stats, get_categories, get_category, add_category,
    update_category, delete_category, get_all_products, get_product,
    add_product, update_product_field, delete_product, get_all_orders,
    get_order, update_order_status, get_all_users, get_user, ban_user,
    unban_user, get_all_coupons, create_coupon, delete_coupon,
    get_setting, set_setting
)
from keyboards import (
    admin_kb, admin_cats_kb, admin_cat_detail_kb, admin_prods_kb,
    admin_prod_detail_kb, admin_orders_kb, admin_order_detail_kb,
    admin_users_kb, admin_user_detail_kb, admin_coupons_kb,
    admin_coupon_detail_kb, back_kb, back_btn
)


def admin_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != ADMIN_ID:
            if update.callback_query:
                await update.callback_query.answer("\u26d4 Admin only!", show_alert=True)
            return
        return await func(update, context)
    return wrapper


# ==================== ADMIN PANEL ====================

@admin_only
async def admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "\ud83d\udc64 *Admin Panel*\n\nChoose an option:",
        parse_mode="Markdown", reply_markup=admin_kb()
    )


# ==================== DASHBOARD ====================

@admin_only
async def admin_dash_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    stats = await get_dashboard_stats()
    text = (
        "\ud83d\udcca *Dashboard*\n\n"
        f"\ud83d\udc65 Users: *{stats['users']}*\n"
        f"\ud83d\udce6 Products: *{stats['products']}*\n"
        f"\ud83d\uded2 Orders: *{stats['orders']}*\n"
        f"\ud83d\udcb0 Revenue: *${stats['revenue']:.2f}*"
    )
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=back_kb("admin"))


# ==================== CATEGORIES ====================

@admin_only
async def admin_cats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cats = await get_categories()
    await query.edit_message_text(
        "\ud83d\udcc2 *Manage Categories:*", parse_mode="Markdown",
        reply_markup=admin_cats_kb(cats)
    )

@admin_only
async def admin_cat_detail_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cat_id = int(query.data.replace("adm_cat_", ""))
    cat = await get_category(cat_id)
    if not cat:
        await query.edit_message_text("Category not found.", reply_markup=back_kb("adm_cats"))
        return
    text = f"{cat['emoji']} *{cat['name']}*\n\nID: {cat['id']}"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=admin_cat_detail_kb(cat_id))

@admin_only
async def admin_addcat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["admin_action"] = "addcat"
    await query.edit_message_text(
        "\u2795 *Add Category*\n\nSend category name and emoji:\n`emoji CategoryName`\n\nExample: `\ud83d\udcda eBooks`",
        parse_mode="Markdown", reply_markup=back_kb("adm_cats")
    )

@admin_only
async def admin_editcat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cat_id = int(query.data.replace("adm_editcat_", ""))
    context.user_data["admin_action"] = "editcat"
    context.user_data["edit_cat_id"] = cat_id
    await query.edit_message_text(
        "\u270f\ufe0f *Edit Category*\n\nSend new name and emoji:\n`emoji NewName`\n\nExample: `\ud83c\udfa8 Templates`",
        parse_mode="Markdown", reply_markup=back_kb("adm_cats")
    )

@admin_only
async def admin_delcat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cat_id = int(query.data.replace("adm_delcat_", ""))
    await delete_category(cat_id)
    await query.answer("\ud83d\uddd1\ufe0f Category deleted!", show_alert=True)
    cats = await get_categories()
    await query.edit_message_text(
        "\ud83d\udcc2 *Manage Categories:*", parse_mode="Markdown",
        reply_markup=admin_cats_kb(cats)
    )


# ==================== PRODUCTS ====================

@admin_only
async def admin_prods_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    prods = await get_all_products()
    await query.edit_message_text(
        "\ud83d\udce6 *Manage Products:*", parse_mode="Markdown",
        reply_markup=admin_prods_kb(prods)
    )

@admin_only
async def admin_prod_detail_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    prod_id = int(query.data.replace("adm_prod_", ""))
    p = await get_product(prod_id)
    if not p:
        await query.edit_message_text("Product not found.", reply_markup=back_kb("adm_prods"))
        return
    cat = await get_category(p["category_id"])
    cat_name = cat["name"] if cat else "Unknown"
    text = (
        f"*{p['name']}*\n\n"
        f"\ud83d\udcdd {p['description']}\n"
        f"\ud83d\udcb0 Price: ${p['price']:.2f}\n"
        f"\ud83d\udcc2 Category: {cat_name}\n"
        f"\ud83d\uddbc\ufe0f Image: {'Yes' if p['image_id'] else 'No'}\n"
        f"ID: {p['id']}"
    )
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=admin_prod_detail_kb(prod_id))

@admin_only
async def admin_addprod_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cats = await get_categories()
    if not cats:
        await query.edit_message_text(
            "\u26a0\ufe0f Create a category first!", reply_markup=back_kb("adm_cats")
        )
        return
    cat_list = "\n".join([f"{c['id']}. {c['emoji']} {c['name']}" for c in cats])
    context.user_data["admin_action"] = "addprod"
    await query.edit_message_text(
        f"\u2795 *Add Product*\n\nSend product details in this format:\n"
        f"`name | description | price | category_id`\n\n"
        f"*Categories:*\n{cat_list}\n\n"
        f"Example:\n`Pro eBook | Advanced guide | 19.99 | 1`",
        parse_mode="Markdown", reply_markup=back_kb("adm_prods")
    )

@admin_only
async def admin_editprod_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    parts = query.data.replace("adm_editprod_", "").split("_")
    field = parts[0]
    prod_id = int(parts[1])
    context.user_data["admin_action"] = f"editprod_{field}"
    context.user_data["edit_prod_id"] = prod_id
    prompts = {
        "name": "Send new product name:",
        "price": "Send new price (number only):",
        "desc": "Send new description:",
        "img": "Send a photo for this product:"
    }
    if field == "img":
        context.user_data["admin_action"] = "editprod_image"
    await query.edit_message_text(
        f"\u270f\ufe0f *Edit Product*\n\n{prompts.get(field, 'Send new value:')}",
        parse_mode="Markdown", reply_markup=back_kb("adm_prods")
    )

@admin_only
async def admin_delprod_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    prod_id = int(query.data.replace("adm_delprod_", ""))
    await delete_product(prod_id)
    await query.answer("\ud83d\uddd1\ufe0f Product deleted!", show_alert=True)
    prods = await get_all_products()
    await query.edit_message_text(
        "\ud83d\udce6 *Manage Products:*", parse_mode="Markdown",
        reply_markup=admin_prods_kb(prods)
    )


# ==================== ORDERS ====================

@admin_only
async def admin_orders_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    orders = await get_all_orders(30)
    if not orders:
        await query.edit_message_text("No orders yet.", reply_markup=back_kb("admin"))
        return
    await query.edit_message_text(
        "\ud83d\uded2 *All Orders:*", parse_mode="Markdown",
        reply_markup=admin_orders_kb(orders)
    )

@admin_only
async def admin_order_detail_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    order_id = int(query.data.replace("adm_order_", ""))
    order = await get_order(order_id)
    if not order:
        await query.edit_message_text("Order not found.", reply_markup=back_kb("adm_orders"))
        return
    items = json.loads(order["items"])
    text = f"\ud83d\udce6 *Order #{order['id']}*\n\n"
    for item in items:
        text += f"\u2022 {item['name']} x{item['qty']} = ${item['price'] * item['qty']:.2f}\n"
    text += (
        f"\n\ud83d\udcb0 Total: ${order['total']:.2f}\n"
        f"Status: *{order['status'].title()}*\n"
        f"User: {order['user_id']}\n"
        f"Date: {order['created_at']}\n\n"
        "\u2b07\ufe0f *Update Status:*"
    )
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=admin_order_detail_kb(order_id))

@admin_only
async def admin_setstatus_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    parts = query.data.replace("adm_setstatus_", "").split("_")
    order_id = int(parts[0])
    status = parts[1]
    await update_order_status(order_id, status)
    await query.answer(f"\u2705 Status updated to {status}!", show_alert=True)
    order = await get_order(order_id)
    items = json.loads(order["items"])
    text = f"\ud83d\udce6 *Order #{order['id']}*\n\n"
    for item in items:
        text += f"\u2022 {item['name']} x{item['qty']} = ${item['price'] * item['qty']:.2f}\n"
    text += (
        f"\n\ud83d\udcb0 Total: ${order['total']:.2f}\n"
        f"Status: *{order['status'].title()}*\n"
        f"User: {order['user_id']}\n"
        f"Date: {order['created_at']}\n\n"
        "\u2b07\ufe0f *Update Status:*"
    )
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=admin_order_detail_kb(order_id))


# ==================== USERS ====================

@admin_only
async def admin_users_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    users = await get_all_users()
    if not users:
        await query.edit_message_text("No users yet.", reply_markup=back_kb("admin"))
        return
    await query.edit_message_text(
        f"\ud83d\udc65 *Users ({len(users)}):*", parse_mode="Markdown",
        reply_markup=admin_users_kb(users)
    )

@admin_only
async def admin_user_detail_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = int(query.data.replace("adm_user_", ""))
    user = await get_user(uid)
    if not user:
        await query.edit_message_text("User not found.", reply_markup=back_kb("adm_users"))
        return
    banned_status = "\ud83d\udd34 Banned" if user["banned"] else "\ud83d\udfe2 Active"
    text = (
        f"\ud83d\udc64 *User Details*\n\n"
        f"ID: `{user['user_id']}`\n"
        f"Name: {user['full_name'] or 'N/A'}\n"
        f"Username: @{user['username'] or 'N/A'}\n"
        f"Joined: {user['joined']}\n"
        f"Status: {banned_status}"
    )
    await query.edit_message_text(
        text, parse_mode="Markdown",
        reply_markup=admin_user_detail_kb(uid, user["banned"])
    )

@admin_only
async def admin_ban_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = int(query.data.replace("adm_ban_", ""))
    await ban_user(uid)
    await query.answer("\ud83d\udeab User banned!", show_alert=True)
    user = await get_user(uid)
    text = (
        f"\ud83d\udc64 *User Details*\n\n"
        f"ID: `{user['user_id']}`\n"
        f"Name: {user['full_name'] or 'N/A'}\n"
        f"Status: \ud83d\udd34 Banned"
    )
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=admin_user_detail_kb(uid, True))

@admin_only
async def admin_unban_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = int(query.data.replace("adm_unban_", ""))
    await unban_user(uid)
    await query.answer("\u2705 User unbanned!", show_alert=True)
    user = await get_user(uid)
    text = (
        f"\ud83d\udc64 *User Details*\n\n"
        f"ID: `{user['user_id']}`\n"
        f"Name: {user['full_name'] or 'N/A'}\n"
        f"Status: \ud83d\udfe2 Active"
    )
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=admin_user_detail_kb(uid, False))


# ==================== BROADCAST ====================

@admin_only
async def admin_broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["admin_action"] = "broadcast"
    await query.edit_message_text(
        "\ud83d\udce3 *Broadcast Message*\n\n"
        "Send a message (text or photo with caption) to broadcast to ALL users:",
        parse_mode="Markdown", reply_markup=back_kb("admin")
    )


# ==================== COUPONS ====================

@admin_only
async def admin_coupons_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    coupons = await get_all_coupons()
    await query.edit_message_text(
        "\ud83c\udff7\ufe0f *Manage Coupons:*", parse_mode="Markdown",
        reply_markup=admin_coupons_kb(coupons)
    )

@admin_only
async def admin_coupon_detail_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    code = query.data.replace("adm_coupon_", "")
    from database import get_coupon
    coupon = await get_coupon(code)
    if not coupon:
        await query.edit_message_text("Coupon not found.", reply_markup=back_kb("adm_coupons"))
        return
    uses = f"{coupon['used_count']}/{coupon['max_uses']}" if coupon["max_uses"] != -1 else f"{coupon['used_count']}/Unlimited"
    text = (
        f"\ud83c\udff7\ufe0f *Coupon: {coupon['code']}*\n\n"
        f"Discount: {coupon['discount_percent']}%\n"
        f"Uses: {uses}\n"
        f"Active: {'Yes' if coupon['active'] else 'No'}"
    )
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=admin_coupon_detail_kb(code))

@admin_only
async def admin_addcoupon_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["admin_action"] = "addcoupon"
    await query.edit_message_text(
        "\u2795 *Add Coupon*\n\nSend coupon details:\n`CODE | discount% | max_uses`\n\n"
        "Example: `SAVE20 | 20 | 100`\n"
        "Use -1 for unlimited uses.",
        parse_mode="Markdown", reply_markup=back_kb("adm_coupons")
    )

@admin_only
async def admin_delcoupon_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    code = query.data.replace("adm_delcoupon_", "")
    await delete_coupon(code)
    await query.answer("\ud83d\uddd1\ufe0f Coupon deleted!", show_alert=True)
    coupons = await get_all_coupons()
    await query.edit_message_text(
        "\ud83c\udff7\ufe0f *Manage Coupons:*", parse_mode="Markdown",
        reply_markup=admin_coupons_kb(coupons)
    )


# ==================== SETTINGS ====================

@admin_only
async def admin_settings_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    welcome_img = await get_setting("welcome_image", "Not set")
    buttons = [
        [InlineKeyboardButton("\ud83d\uddbc\ufe0f Set Welcome Image", callback_data="adm_set_welcome_img")],
        [back_btn("admin")],
    ]
    await query.edit_message_text(
        f"\u2699\ufe0f *Bot Settings*\n\nWelcome Image: {welcome_img}",
        parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons)
    )

@admin_only
async def admin_set_welcome_img_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["admin_action"] = "set_welcome_img"
    await query.edit_message_text(
        "\ud83d\uddbc\ufe0f *Set Welcome Image*\n\nSend a photo to use as welcome banner:",
        parse_mode="Markdown", reply_markup=back_kb("adm_settings")
    )


# ==================== TEXT INPUT HANDLER ====================

async def admin_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    action = context.user_data.get("admin_action")
    if not action:
        return False
    if update.effective_user.id != ADMIN_ID:
        return False

    text = update.message.text.strip() if update.message.text else ""
    context.user_data["admin_action"] = None

    if action == "addcat":
        parts = text.split(" ", 1)
        if len(parts) < 2:
            await update.message.reply_text("\u274c Format: emoji CategoryName", reply_markup=back_kb("adm_cats"))
            return True
        emoji, name = parts[0], parts[1]
        await add_category(name, emoji)
        await update.message.reply_text(f"\u2705 Category '{emoji} {name}' added!", reply_markup=back_kb("adm_cats"))
        return True

    elif action == "editcat":
        cat_id = context.user_data.get("edit_cat_id")
        parts = text.split(" ", 1)
        if len(parts) < 2:
            await update.message.reply_text("\u274c Format: emoji CategoryName", reply_markup=back_kb("adm_cats"))
            return True
        emoji, name = parts[0], parts[1]
        await update_category(cat_id, name, emoji)
        await update.message.reply_text(f"\u2705 Category updated!", reply_markup=back_kb("adm_cats"))
        return True

    elif action == "addprod":
        parts = [p.strip() for p in text.split("|")]
        if len(parts) < 4:
            await update.message.reply_text("\u274c Format: name | desc | price | category_id", reply_markup=back_kb("adm_prods"))
            return True
        try:
            name, desc, price, cat_id = parts[0], parts[1], float(parts[2]), int(parts[3])
        except ValueError:
            await update.message.reply_text("\u274c Invalid price or category ID.", reply_markup=back_kb("adm_prods"))
            return True
        await add_product(name, desc, price, None, cat_id)
        await update.message.reply_text(f"\u2705 Product '{name}' added!", reply_markup=back_kb("adm_prods"))
        return True

    elif action == "editprod_name":
        prod_id = context.user_data.get("edit_prod_id")
        await update_product_field(prod_id, "name", text)
        await update.message.reply_text("\u2705 Name updated!", reply_markup=back_kb("adm_prods"))
        return True

    elif action == "editprod_price":
        prod_id = context.user_data.get("edit_prod_id")
        try:
            price = float(text)
        except ValueError:
            await update.message.reply_text("\u274c Invalid price.", reply_markup=back_kb("adm_prods"))
            return True
        await update_product_field(prod_id, "price", price)
        await update.message.reply_text("\u2705 Price updated!", reply_markup=back_kb("adm_prods"))
        return True

    elif action == "editprod_desc":
        prod_id = context.user_data.get("edit_prod_id")
        await update_product_field(prod_id, "description", text)
        await update.message.reply_text("\u2705 Description updated!", reply_markup=back_kb("adm_prods"))
        return True

    elif action == "addcoupon":
        parts = [p.strip() for p in text.split("|")]
        if len(parts) < 3:
            await update.message.reply_text("\u274c Format: CODE | discount% | max_uses", reply_markup=back_kb("adm_coupons"))
            return True
        try:
            code, discount, max_uses = parts[0], int(parts[1]), int(parts[2])
        except ValueError:
            await update.message.reply_text("\u274c Invalid values.", reply_markup=back_kb("adm_coupons"))
            return True
        await create_coupon(code, discount, max_uses)
        await update.message.reply_text(f"\u2705 Coupon '{code.upper()}' created!", reply_markup=back_kb("adm_coupons"))
        return True

    elif action == "broadcast":
        users = await get_all_users()
        success = 0
        for u in users:
            try:
                await context.bot.send_message(chat_id=u["user_id"], text=text)
                success += 1
            except Exception:
                pass
        await update.message.reply_text(
            f"\ud83d\udce3 Broadcast sent to {success}/{len(users)} users.",
            reply_markup=back_kb("admin")
        )
        return True

    return False


async def admin_photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    action = context.user_data.get("admin_action")
    if not action or update.effective_user.id != ADMIN_ID:
        return False

    photo = update.message.photo[-1]
    file_id = photo.file_id
    context.user_data["admin_action"] = None

    if action == "editprod_image":
        prod_id = context.user_data.get("edit_prod_id")
        await update_product_field(prod_id, "image_id", file_id)
        await update.message.reply_text("\u2705 Product image updated!", reply_markup=back_kb("adm_prods"))
        return True

    elif action == "set_welcome_img":
        await set_setting("welcome_image", file_id)
        await update.message.reply_text("\u2705 Welcome image updated!", reply_markup=back_kb("adm_settings"))
        return True

    elif action == "broadcast":
        caption = update.message.caption or ""
        users = await get_all_users()
        success = 0
        for u in users:
            try:
                await context.bot.send_photo(chat_id=u["user_id"], photo=file_id, caption=caption)
                success += 1
            except Exception:
                pass
        await update.message.reply_text(
            f"\ud83d\udce3 Photo broadcast sent to {success}/{len(users)} users.",
            reply_markup=back_kb("admin")
        )
        return True

    return False
