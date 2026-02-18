import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import (
    get_cart, get_cart_total, clear_cart, create_order,
    get_user_orders, get_order, validate_coupon, use_coupon,
    is_banned
)
from keyboards import checkout_kb, order_detail_kb, back_kb, back_btn, empty_cart_kb


async def checkout_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    if await is_banned(user_id):
        await query.edit_message_text("\u26d4 You are banned.")
        return

    items = await get_cart(user_id)
    if not items:
        await query.edit_message_text("\ud83d\uded2 Cart is empty!", reply_markup=empty_cart_kb())
        return

    total = await get_cart_total(user_id)

    coupon_code = context.user_data.get("coupon_code")
    discount = context.user_data.get("coupon_discount", 0)
    if coupon_code and discount > 0:
        discount_amount = total * (discount / 100)
        final_total = total - discount_amount
        text = "\ud83d\udcb3 *Order Summary*\n\n"
        for item in items:
            sub = item["price"] * item["quantity"]
            text += f"\u2022 {item['name']} x{item['quantity']} = ${sub:.2f}\n"
        text += (
            f"\n\ud83d\udcb0 Subtotal: ${total:.2f}\n"
            f"\ud83c\udff7\ufe0f Coupon: {coupon_code} (-{discount}%)\n"
            f"\ud83d\udcb5 Discount: -${discount_amount:.2f}\n"
            f"\n\u2705 *Total: ${final_total:.2f}*"
        )
    else:
        final_total = total
        text = "\ud83d\udcb3 *Order Summary*\n\n"
        for item in items:
            sub = item["price"] * item["quantity"]
            text += f"\u2022 {item['name']} x{item['quantity']} = ${sub:.2f}\n"
        text += f"\n\u2705 *Total: ${final_total:.2f}*"

    context.user_data["final_total"] = final_total
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=checkout_kb())


async def confirm_order_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    items = await get_cart(user_id)
    if not items:
        await query.edit_message_text("\ud83d\uded2 Cart is empty!", reply_markup=empty_cart_kb())
        return

    final_total = context.user_data.get("final_total", await get_cart_total(user_id))
    coupon_code = context.user_data.get("coupon_code")

    items_data = [{"name": i["name"], "price": i["price"], "qty": i["quantity"]} for i in items]
    order_id = await create_order(user_id, items_data, final_total, coupon_code)

    if coupon_code:
        await use_coupon(coupon_code)
        context.user_data.pop("coupon_code", None)
        context.user_data.pop("coupon_discount", None)

    await clear_cart(user_id)
    context.user_data.pop("final_total", None)

    text = (
        f"\u2705 *Order Placed Successfully!*\n\n"
        f"\ud83d\udce6 Order ID: *#{order_id}*\n"
        f"\ud83d\udcb0 Total: *${final_total:.2f}*\n"
        f"\ud83d\udccc Status: Pending\n\n"
        "\ud83d\udce9 *Payment Methods:*\n"
        "\u2022 PayPal\n"
        "\u2022 Crypto (BTC/ETH)\n"
        "\u2022 Bank Transfer\n\n"
        "Contact admin to complete payment.\n"
        "_Thank you for shopping at NanoStore!_ \ud83d\udecd\ufe0f"
    )
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=back_kb("main_menu"))


async def my_orders_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    orders = await get_user_orders(user_id)
    if not orders:
        await query.edit_message_text(
            "\ud83d\udce6 You have no orders yet.",
            reply_markup=back_kb("main_menu")
        )
        return

    text = "\ud83d\udce6 *Your Orders:*\n\n"
    buttons = []
    status_emoji = {
        "pending": "\ud83d\udfe1", "confirmed": "\ud83d\udfe2", "processing": "\ud83d\udd35",
        "shipped": "\ud83d\udce6", "delivered": "\u2705", "cancelled": "\ud83d\udd34"
    }
    for o in orders[:10]:
        emoji = status_emoji.get(o["status"], "\u26aa")
        buttons.append([InlineKeyboardButton(
            f"{emoji} #{o['id']} \u2014 ${o['total']:.2f} ({o['status']})",
            callback_data=f"vieworder_{o['id']}"
        )])
    buttons.append([back_btn("main_menu")])
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))


async def view_order_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    order_id = int(query.data.replace("vieworder_", ""))
    order = await get_order(order_id)
    if not order:
        await query.edit_message_text("Order not found.", reply_markup=back_kb("my_orders"))
        return

    items = json.loads(order["items"])
    status_emoji = {
        "pending": "\ud83d\udfe1", "confirmed": "\ud83d\udfe2", "processing": "\ud83d\udd35",
        "shipped": "\ud83d\udce6", "delivered": "\u2705", "cancelled": "\ud83d\udd34"
    }
    emoji = status_emoji.get(order["status"], "\u26aa")

    text = f"\ud83d\udce6 *Order #{order['id']}*\n\n"
    for item in items:
        text += f"\u2022 {item['name']} x{item['qty']} = ${item['price'] * item['qty']:.2f}\n"
    text += (
        f"\n\ud83d\udcb0 Total: *${order['total']:.2f}*\n"
        f"{emoji} Status: *{order['status'].title()}*\n"
        f"\ud83d\udcc5 Date: {order['created_at']}"
    )
    if order["coupon_code"]:
        text += f"\n\ud83c\udff7\ufe0f Coupon: {order['coupon_code']}"

    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=order_detail_kb("my_orders"))


async def apply_coupon_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["awaiting_coupon"] = True
    await query.edit_message_text(
        "\ud83c\udff7\ufe0f *Enter Coupon Code:*\n\nType your coupon code below:",
        parse_mode="Markdown",
        reply_markup=back_kb("cart")
    )


async def coupon_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_coupon"):
        return False

    context.user_data["awaiting_coupon"] = False
    code = update.message.text.strip()
    coupon = await validate_coupon(code)

    if not coupon:
        await update.message.reply_text(
            "\u274c Invalid or expired coupon code.\nTry again or go back to cart.",
            reply_markup=back_kb("cart")
        )
        return True

    context.user_data["coupon_code"] = coupon["code"]
    context.user_data["coupon_discount"] = coupon["discount_percent"]
    await update.message.reply_text(
        f"\u2705 Coupon *{coupon['code']}* applied!\n"
        f"\ud83c\udff7\ufe0f Discount: *{coupon['discount_percent']}% off*\n\n"
        "Go to cart to checkout.",
        parse_mode="Markdown",
        reply_markup=back_kb("cart")
    )
    return True
