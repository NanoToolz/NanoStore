from telegram import Update
from telegram.ext import ContextTypes
from database import (
    add_to_cart, decrease_cart_qty, remove_from_cart,
    get_cart, clear_cart, get_cart_total, get_product,
    is_banned
)
from keyboards import cart_kb, empty_cart_kb, back_kb


async def addcart_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    prod_id = int(query.data.replace("addcart_", ""))

    if await is_banned(user_id):
        await query.answer("\u26d4 You are banned.", show_alert=True)
        return

    p = await get_product(prod_id)
    if not p:
        await query.answer("Product not found!", show_alert=True)
        return

    await add_to_cart(user_id, prod_id)
    await query.answer(f"\u2705 {p['name']} added to cart!", show_alert=True)


async def cart_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    items = await get_cart(user_id)
    if not items:
        await query.edit_message_text(
            "\ud83d\uded2 Your cart is empty!",
            reply_markup=empty_cart_kb()
        )
        return

    total = await get_cart_total(user_id)
    text = "\ud83d\uded2 *Your Cart:*\n\n"
    for item in items:
        sub = item["price"] * item["quantity"]
        text += f"\u2022 *{item['name']}*\n  ${item['price']:.2f} x {item['quantity']} = ${sub:.2f}\n\n"
    text += f"\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n\ud83d\udcb0 *Total: ${total:.2f}*"

    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=cart_kb(items, total))


async def cart_inc_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    prod_id = int(query.data.replace("cartinc_", ""))
    await add_to_cart(user_id, prod_id)
    await _refresh_cart(query, user_id)


async def cart_dec_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    prod_id = int(query.data.replace("cartdec_", ""))
    await decrease_cart_qty(user_id, prod_id)
    await _refresh_cart(query, user_id)


async def cart_del_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    prod_id = int(query.data.replace("cartdel_", ""))
    await remove_from_cart(user_id, prod_id)
    await _refresh_cart(query, user_id)


async def clear_cart_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    await clear_cart(user_id)
    await query.answer("\ud83d\uddd1\ufe0f Cart cleared!")
    await query.edit_message_text(
        "\ud83d\uded2 Your cart is empty!",
        reply_markup=empty_cart_kb()
    )


async def _refresh_cart(query, user_id):
    await query.answer()
    items = await get_cart(user_id)
    if not items:
        await query.edit_message_text(
            "\ud83d\uded2 Your cart is empty!",
            reply_markup=empty_cart_kb()
        )
        return
    total = await get_cart_total(user_id)
    text = "\ud83d\uded2 *Your Cart:*\n\n"
    for item in items:
        sub = item["price"] * item["quantity"]
        text += f"\u2022 *{item['name']}*\n  ${item['price']:.2f} x {item['quantity']} = ${sub:.2f}\n\n"
    text += f"\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n\ud83d\udcb0 *Total: ${total:.2f}*"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=cart_kb(items, total))
