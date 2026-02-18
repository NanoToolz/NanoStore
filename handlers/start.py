import os
from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_ID
from database import add_user, is_banned
from keyboards import main_menu_kb


WELCOME_IMAGE = "assets/welcome.jpg"


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await add_user(user.id, user.username, user.first_name)

    if await is_banned(user.id):
        await update.message.reply_text("\u26d4 You have been banned from this store.")
        return

    is_admin = user.id == ADMIN_ID
    text = (
        f"\ud83d\udecd\ufe0f *Welcome to NanoStore, {user.first_name}!*\n\n"
        "Your premium digital product marketplace.\n"
        "eBooks, Templates, Courses, Software & more!\n\n"
        "Choose an option below:"
    )

    kb = main_menu_kb(is_admin)

    if os.path.exists(WELCOME_IMAGE):
        with open(WELCOME_IMAGE, "rb") as photo:
            await update.message.reply_photo(
                photo=photo, caption=text, parse_mode="Markdown", reply_markup=kb
            )
    else:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)


async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    is_admin = user.id == ADMIN_ID
    text = (
        f"\ud83d\udecd\ufe0f *NanoStore Main Menu*\n\n"
        f"Welcome back, {user.first_name}!"
    )
    try:
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=main_menu_kb(is_admin))
    except Exception:
        await query.edit_message_caption(caption=text, parse_mode="Markdown", reply_markup=main_menu_kb(is_admin))


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "\u2753 *NanoStore Help*\n\n"
        "\ud83d\udecd\ufe0f *Shop* \u2014 Browse products by category\n"
        "\ud83d\udd0d *Search* \u2014 Find products by keyword\n"
        "\ud83d\uded2 *Cart* \u2014 View & manage your cart\n"
        "\ud83d\udce6 *Orders* \u2014 Track your order history\n\n"
        "Need help? Contact admin directly."
    )
    from keyboards import back_kb
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=back_kb("main_menu"))


async def noop_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
