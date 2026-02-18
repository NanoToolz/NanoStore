"""NanoStore cart handlers — view, increment, decrement, remove, clear."""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from database import (
    get_cart,
    get_cart_count,
    get_cart_item,
    update_cart_qty,
    remove_from_cart_by_id,
    clear_cart,
    get_setting,
)
from helpers import safe_edit, html_escape, separator
from keyboards import cart_kb, empty_cart_kb

logger = logging.getLogger(__name__)


async def cart_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show user's cart contents."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    await _show_cart(query, user_id)


async def _show_cart(query, user_id: int) -> None:
    """Internal: render the cart view."""
    items = await get_cart(user_id)
    currency = await get_setting("currency", "Rs")

    if not items:
        text = (
            f"🛒 <b>Your Cart</b>\n"
            f"{separator()}\n"
            "Your cart is empty! Browse our shop."
        )
        await safe_edit(query, text, reply_markup=empty_cart_kb())
        return

    text = f"🛒 <b>Your Cart</b>\n{separator()}\n"
    total = 0.0

    for i, item in enumerate(items, 1):
        price = item["price"]
        qty = item["quantity"]
        subtotal = price * qty
        total += subtotal

        price_display = int(price) if price == int(price) else price
        sub_display = int(subtotal) if subtotal == int(subtotal) else f"{subtotal:.2f}"

        text += (
            f"\n{i}. {html_escape(item['name'])}\n"
            f"   💰 {currency} {price_display} × {qty} = {currency} {sub_display}\n"
        )

    total_display = int(total) if total == int(total) else f"{total:.2f}"
    text += f"{separator()}\n💰 <b>Total: {currency} {total_display}</b>"

    await safe_edit(query, text, reply_markup=cart_kb(items))


async def cart_inc_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Increase cart item quantity by 1."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    cart_id = int(query.data.split(":")[1])

    item = await get_cart_item(cart_id)
    if not item:
        await query.answer("❌ Item not found.", show_alert=True)
        return

    # Check stock limit
    new_qty = item["quantity"] + 1
    if item["stock"] != -1 and new_qty > item["stock"]:
        await query.answer(
            f"⚠️ Only {item['stock']} available in stock.",
            show_alert=True,
        )
        return

    await update_cart_qty(cart_id, new_qty)
    await _show_cart(query, user_id)


async def cart_dec_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Decrease cart item quantity by 1 (removes if qty reaches 0)."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    cart_id = int(query.data.split(":")[1])

    item = await get_cart_item(cart_id)
    if not item:
        await query.answer("❌ Item not found.", show_alert=True)
        return

    new_qty = item["quantity"] - 1
    await update_cart_qty(cart_id, new_qty)  # removes if <= 0
    await _show_cart(query, user_id)


async def cart_del_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove a specific item from cart entirely."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    cart_id = int(query.data.split(":")[1])

    await remove_from_cart_by_id(cart_id)
    await _show_cart(query, user_id)


async def cart_clear_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear all items from user's cart."""
    query = update.callback_query
    await query.answer("🗑️ Cart cleared!")

    user_id = update.effective_user.id
    await clear_cart(user_id)
    await _show_cart(query, user_id)
