"""NanoStore order handlers — checkout, coupon, balance, payment, proof upload."""

import json
import logging
from telegram import Update, InlineKeyboardButton as Btn, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import ADMIN_ID, PROOFS_CHANNEL_ID
from database import (
    get_cart,
    get_cart_count,
    get_cart_total,
    clear_cart,
    get_setting,
    create_order,
    get_order,
    get_user_orders,
    get_user_order_count,
    update_order,
    get_user_balance,
    update_user_balance,
    validate_coupon,
    use_coupon,
    get_payment_methods,
    get_payment_method,
    create_payment_proof,
    decrement_stock,
    add_action_log,
)
from utils import (
    safe_edit,
    html_escape,
    separator,
    status_emoji,
    log_action,
)
from utils import (
    checkout_kb,
    payment_methods_kb,
    order_detail_kb,
    orders_kb,
    back_kb,
    empty_cart_kb,
)

logger = logging.getLogger(__name__)

ORDERS_PER_PAGE: int = 10


# ════════════════════════ CHECKOUT ════════════════════════

async def checkout_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start checkout — create order from cart and show summary."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    cart_items = await get_cart(user_id)

    if not cart_items:
        text = (
            f"🛒 <b>Your Cart</b>\n"
            f"{separator()}\n"
            "Your cart is empty! Browse our shop."
        )
        await safe_edit(query, text, reply_markup=empty_cart_kb())
        return

    currency = await get_setting("currency", "Rs")

    # Build items list for order
    items_data = []
    total = 0.0
    for item in cart_items:
        subtotal = item["price"] * item["quantity"]
        total += subtotal
        items_data.append({
            "product_id": item["product_id"],
            "name": item["name"],
            "price": item["price"],
            "quantity": item["quantity"],
            "subtotal": subtotal,
        })

    # Check minimum order
    min_order = float(await get_setting("min_order", "0"))
    if total < min_order:
        min_display = int(min_order) if min_order == int(min_order) else min_order
        await query.answer(
            f"⚠️ Minimum order is {currency} {min_display}",
            show_alert=True,
        )
        return

    # Create order
    order_id = await create_order(user_id, items_data, total)

    # Store temp data for coupon/balance
    context.user_data["temp"] = {
        "order_id": order_id,
        "original_total": total,
        "discount": 0.0,
        "balance_used": 0.0,
    }

    await _show_checkout(query, order_id, items_data, total, 0.0, 0.0, currency, user_id)


async def _show_checkout(
    query, order_id: int, items: list, subtotal: float,
    discount: float, balance_used: float, currency: str, user_id: int
) -> None:
    """Render checkout summary."""
    final = max(0, subtotal - discount - balance_used)
    user_balance = await get_user_balance(user_id)
    has_balance = user_balance > 0

    text = f"📋 <b>Order Summary</b>\n{separator()}\n"

    for item in items:
        price = int(item["price"]) if item["price"] == int(item["price"]) else item["price"]
        sub = int(item["subtotal"]) if item["subtotal"] == int(item["subtotal"]) else f"{item['subtotal']:.2f}"
        text += f"\n• {html_escape(item['name'])}\n  {currency} {price} × {item['quantity']} = {currency} {sub}\n"

    sub_display = int(subtotal) if subtotal == int(subtotal) else f"{subtotal:.2f}"
    text += f"{separator()}\n"
    text += f"💰 Subtotal: {currency} {sub_display}\n"

    if discount > 0:
        disc_display = int(discount) if discount == int(discount) else f"{discount:.2f}"
        text += f"🎫 Coupon: -{currency} {disc_display}\n"

    if balance_used > 0:
        bal_display = int(balance_used) if balance_used == int(balance_used) else f"{balance_used:.2f}"
        text += f"💳 Balance: -{currency} {bal_display}\n"

    final_display = int(final) if final == int(final) else f"{final:.2f}"
    text += f"{separator()}\n"
    text += f"💰 <b>Total: {currency} {final_display}</b>"

    await safe_edit(query, text, reply_markup=checkout_kb(order_id, has_balance=has_balance))


# ════════════════════════ COUPON ════════════════════════

async def apply_coupon_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompt user to enter coupon code."""
    query = update.callback_query
    await query.answer()

    order_id = int(query.data.split(":")[1])
    context.user_data["state"] = f"apply_coupon:{order_id}"

    text = (
        f"🎫 <b>Apply Coupon</b>\n"
        f"{separator()}\n\n"
        "📝 Enter your coupon code:"
    )
    await safe_edit(query, text, reply_markup=back_kb("checkout"))


async def coupon_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process coupon code from text message."""
    state = context.user_data.get("state", "")
    order_id = int(state.split(":")[1])
    context.user_data.pop("state", None)

    code = update.message.text.strip().upper()
    coupon = await validate_coupon(code)

    if not coupon:
        await update.message.reply_text(
            "❌ Invalid or expired coupon code.",
            parse_mode="HTML",
        )
        return

    order = await get_order(order_id)
    if not order:
        await update.message.reply_text("❌ Order not found.", parse_mode="HTML")
        return

    temp = context.user_data.get("temp", {})
    original_total = temp.get("original_total", order["total"])
    discount = original_total * coupon["discount_percent"] / 100
    temp["discount"] = discount
    temp["coupon_code"] = code
    context.user_data["temp"] = temp

    await update_order(order_id, coupon_code=code)

    currency = await get_setting("currency", "Rs")
    disc_display = int(discount) if discount == int(discount) else f"{discount:.2f}"

    await update.message.reply_text(
        f"✅ Coupon <b>{html_escape(code)}</b> applied!\n"
        f"🎫 Discount: {coupon['discount_percent']}% (-{currency} {disc_display})\n\n"
        "Tap ✅ Confirm below to proceed.",
        parse_mode="HTML",
    )


# ════════════════════════ BALANCE ════════════════════════

async def apply_balance_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Apply user wallet balance to order."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    order_id = int(query.data.split(":")[1])
    order = await get_order(order_id)

    if not order:
        await query.answer("❌ Order not found.", show_alert=True)
        return

    temp = context.user_data.get("temp", {})
    original_total = temp.get("original_total", order["total"])
    discount = temp.get("discount", 0.0)
    remaining = original_total - discount

    balance = await get_user_balance(user_id)
    if balance <= 0:
        await query.answer("⚠️ No balance available.", show_alert=True)
        return

    balance_used = min(balance, remaining)
    temp["balance_used"] = balance_used
    context.user_data["temp"] = temp

    currency = await get_setting("currency", "Rs")
    bal_display = int(balance_used) if balance_used == int(balance_used) else f"{balance_used:.2f}"
    await query.answer(f"💳 Balance {currency} {bal_display} applied!", show_alert=True)

    items = json.loads(order["items_json"])
    await _show_checkout(query, order_id, items, original_total, discount, balance_used, currency, user_id)


# ════════════════════════ CONFIRM / CANCEL ════════════════════════

async def confirm_order_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Confirm order — deduct balance, use coupon, decrement stock, show payment."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    order_id = int(query.data.split(":")[1])
    order = await get_order(order_id)

    if not order:
        await query.answer("❌ Order not found.", show_alert=True)
        return

    if order["status"] != "pending":
        await query.answer("⚠️ Order already processed.", show_alert=True)
        return

    temp = context.user_data.get("temp", {})
    discount = temp.get("discount", 0.0)
    balance_used = temp.get("balance_used", 0.0)
    coupon_code = temp.get("coupon_code")

    # Deduct balance if used
    if balance_used > 0:
        await update_user_balance(user_id, -balance_used)

    # Use coupon
    if coupon_code:
        await use_coupon(coupon_code)

    # Decrement stock
    items = json.loads(order["items_json"])
    for item in items:
        await decrement_stock(item["product_id"], item["quantity"])

    # Update order total
    final_total = max(0, order["total"] - discount - balance_used)
    await update_order(order_id, status="confirmed")

    # Clear cart
    await clear_cart(user_id)

    # Clear temp
    context.user_data.pop("temp", None)
    context.user_data.pop("state", None)

    currency = await get_setting("currency", "Rs")

    if final_total <= 0:
        # Fully paid with balance
        await update_order(order_id, payment_status="paid")
        text = (
            f"✅ <b>Order #{order_id} Confirmed!</b>\n"
            f"{separator()}\n\n"
            f"💳 Paid with wallet balance.\n"
            "Thank you for your purchase!\n\n"
            "Check your order in 📦 My Orders."
        )
        await safe_edit(query, text, reply_markup=back_kb("my_orders"))
    else:
        # Show payment methods
        methods = await get_payment_methods()
        if not methods:
            text = (
                f"✅ <b>Order #{order_id} Confirmed!</b>\n"
                f"{separator()}\n\n"
                "⚠️ No payment methods configured.\n"
                "Please contact support."
            )
            await safe_edit(query, text, reply_markup=back_kb("my_orders"))
            return

        total_display = int(final_total) if final_total == int(final_total) else f"{final_total:.2f}"
        text = (
            f"✅ <b>Order #{order_id} Confirmed!</b>\n"
            f"{separator()}\n\n"
            f"💰 Amount Due: <b>{currency} {total_display}</b>\n\n"
            "💳 Select a payment method:"
        )
        await safe_edit(query, text, reply_markup=payment_methods_kb(methods, order_id))

    # Log action
    await add_action_log("order_confirmed", user_id, f"Order #{order_id}")
    await log_action(
        context.bot,
        f"🛒 <b>New Order #{order_id}</b>\n"
        f"👤 User: {user_id}\n"
        f"💰 Total: {currency} {final_total}"
    )


async def cancel_order_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Cancel an order."""
    query = update.callback_query
    await query.answer()

    order_id = int(query.data.split(":")[1])
    order = await get_order(order_id)

    if not order:
        await query.answer("❌ Order not found.", show_alert=True)
        return

    await update_order(order_id, status="cancelled")

    context.user_data.pop("temp", None)
    context.user_data.pop("state", None)

    text = (
        f"❌ <b>Order #{order_id} Cancelled</b>\n"
        f"{separator()}\n\n"
        "Your order has been cancelled."
    )
    await safe_edit(query, text, reply_markup=back_kb("main_menu"))


# ════════════════════════ PAYMENT ════════════════════════

async def pay_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show payment methods for an existing order."""
    query = update.callback_query
    await query.answer()

    order_id = int(query.data.split(":")[1])
    order = await get_order(order_id)

    if not order:
        await query.answer("❌ Order not found.", show_alert=True)
        return

    methods = await get_payment_methods()
    currency = await get_setting("currency", "Rs")
    total_display = int(order["total"]) if order["total"] == int(order["total"]) else order["total"]

    text = (
        f"💳 <b>Pay for Order #{order_id}</b>\n"
        f"{separator()}\n\n"
        f"💰 Amount: <b>{currency} {total_display}</b>\n\n"
        "Select a payment method:"
    )
    await safe_edit(query, text, reply_markup=payment_methods_kb(methods, order_id))


async def pay_method_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show payment details for selected method and prompt for screenshot."""
    query = update.callback_query
    await query.answer()

    parts = query.data.split(":")
    order_id = int(parts[1])
    method_id = int(parts[2])

    order = await get_order(order_id)
    method = await get_payment_method(method_id)

    if not order or not method:
        await query.answer("❌ Not found.", show_alert=True)
        return

    await update_order(order_id, payment_method_id=method_id)

    currency = await get_setting("currency", "Rs")
    total_display = int(order["total"]) if order["total"] == int(order["total"]) else order["total"]

    text = (
        f"💳 <b>{html_escape(method['emoji'])} {html_escape(method['name'])}</b>\n"
        f"{separator()}\n"
        f"📋 <b>Payment Details:</b>\n"
        f"{html_escape(method['details'])}\n\n"
        f"💰 Amount: <b>{currency} {total_display}</b>\n"
        f"🆔 Reference: <b>#{order_id}</b>\n"
        f"{separator()}\n"
        f"📸 <b>Send your payment screenshot now.</b>"
    )

    context.user_data["state"] = f"proof_upload:{order_id}"
    context.user_data.setdefault("temp", {})["method_id"] = method_id

    await safe_edit(query, text, reply_markup=back_kb("main_menu"))


async def proof_upload_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process payment screenshot upload."""
    state = context.user_data.get("state", "")
    order_id = int(state.split(":")[1])

    context.user_data.pop("state", None)

    photo = update.message.photo[-1]  # highest resolution
    file_id = photo.file_id
    user_id = update.effective_user.id

    temp = context.user_data.get("temp", {})
    method_id = temp.get("method_id", 0)

    # Save proof
    proof_id = await create_payment_proof(user_id, order_id, method_id, file_id)
    await update_order(order_id, payment_proof_id=proof_id, payment_status="pending_review")

    context.user_data.pop("temp", None)

    text = (
        f"✅ <b>Payment Proof Submitted!</b>\n"
        f"{separator()}\n\n"
        f"🆔 Order: <b>#{order_id}</b>\n"
        f"📸 Proof ID: <b>#{proof_id}</b>\n\n"
        "⏳ Your payment is under review.\n"
        "You'll be notified once approved.\n\n"
        "Check status in 📦 My Orders."
    )

    kb = InlineKeyboardMarkup([
        [Btn("📦 My Orders", callback_data="my_orders")],
        [Btn("◀️ Main Menu", callback_data="main_menu")],
    ])

    await update.message.reply_text(text, parse_mode="HTML", reply_markup=kb)

    # Notify admin
    admin_text = (
        f"📸 <b>New Payment Proof!</b>\n"
        f"{separator()}\n\n"
        f"🆔 Order: #{order_id}\n"
        f"👤 User: {user_id}\n"
        f"📸 Proof: #{proof_id}\n\n"
        "Review in Admin → Proofs"
    )
    try:
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=file_id,
            caption=admin_text,
            parse_mode="HTML",
        )
    except Exception as e:
        logger.warning("Failed to notify admin about proof: %s", e)

    # Post to proofs channel if configured
    if PROOFS_CHANNEL_ID:
        try:
            await context.bot.send_photo(
                chat_id=PROOFS_CHANNEL_ID,
                photo=file_id,
                caption=admin_text,
                parse_mode="HTML",
            )
        except Exception as e:
            logger.warning("Failed to post proof to channel: %s", e)

    await add_action_log("proof_submitted", user_id, f"Order #{order_id}, Proof #{proof_id}")


# ════════════════════════ MY ORDERS ════════════════════════

async def my_orders_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show user's orders (page 1)."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    await _show_orders_page(query, user_id, page=1)


async def orders_page_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show user's orders with pagination."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    page = int(query.data.split(":")[1])
    await _show_orders_page(query, user_id, page=page)


async def _show_orders_page(query, user_id: int, page: int = 1) -> None:
    """Internal: render orders list page.
    
    Uses render_screen with orders_image_id.
    """
    offset = (page - 1) * ORDERS_PER_PAGE
    user_orders = await get_user_orders(user_id, limit=ORDERS_PER_PAGE, offset=offset)
    currency = await get_setting("currency", "Rs")

    text = f"📦 <b>My Orders</b>\n{separator()}\n"

    if not user_orders:
        text += "\nYou have no orders yet."
        await safe_edit(query, text, reply_markup=back_kb("main_menu"))
        return

    total_orders = await get_user_order_count(user_id)
    text += f"\n📊 Total: {total_orders} orders"

    # Use render_screen with orders_image_id
    from utils import render_screen
    await render_screen(
        query=query,
        bot=query.message.get_bot(),
        chat_id=query.message.chat_id,
        text=text,
        reply_markup=orders_kb(user_orders, currency=currency, page=page, per_page=ORDERS_PER_PAGE),
        image_setting_key="orders_image_id"
    )


async def order_detail_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show details of a specific order."""
    query = update.callback_query
    await query.answer()

    order_id = int(query.data.split(":")[1])
    order = await get_order(order_id)

    if not order:
        await safe_edit(query, "❌ Order not found.", reply_markup=back_kb("my_orders"))
        return

    currency = await get_setting("currency", "Rs")
    items = json.loads(order["items_json"]) if order["items_json"] else []
    emoji = status_emoji(order["status"])
    pay_emoji = status_emoji(order["payment_status"])

    text = (
        f"📦 <b>Order #{order_id}</b>\n"
        f"{separator()}\n"
    )

    for item in items:
        price = int(item["price"]) if item["price"] == int(item["price"]) else item["price"]
        text += f"\n• {html_escape(item['name'])} × {item['quantity']} = {currency} {price}\n"

    total_display = int(order["total"]) if order["total"] == int(order["total"]) else order["total"]
    text += (
        f"{separator()}\n"
        f"💰 Total: <b>{currency} {total_display}</b>\n"
        f"{emoji} Status: <b>{order['status'].title()}</b>\n"
        f"{pay_emoji} Payment: <b>{order['payment_status']}</b>\n"
    )

    if order.get("coupon_code"):
        text += f"🎫 Coupon: <b>{html_escape(order['coupon_code'])}</b>\n"

    if order.get("created_at"):
        text += f"📅 Date: {order['created_at'][:10]}\n"

    await safe_edit(query, text, reply_markup=order_detail_kb(order_id, order["status"]))
