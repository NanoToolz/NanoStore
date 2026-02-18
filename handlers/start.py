"""NanoStore start handlers — /start, main menu, help, noop, force join verify."""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_ID
from database import ensure_user, is_user_banned, get_setting, get_cart_count, add_action_log
from helpers import safe_edit, check_force_join, log_action, html_escape, separator
from keyboards import main_menu_kb, back_kb, force_join_kb

logger = logging.getLogger(__name__)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command — register user, check force join, show welcome."""
    user = update.effective_user
    await ensure_user(user.id, user.first_name or "User", user.username or "")

    if await is_user_banned(user.id):
        await update.message.reply_text(
            "⛔ <b>Access Denied</b>\n\n"
            "You have been banned from this store.\n"
            "Contact admin if you think this is a mistake.",
            parse_mode="HTML",
        )
        return

    # Force join check
    not_joined = await check_force_join(context.bot, user.id)
    if not_joined:
        text = (
            f"🔒 <b>Access Required</b>\n"
            f"{separator()}\n"
            "Join these channels to use the bot:"
        )
        await update.message.reply_text(
            text, parse_mode="HTML", reply_markup=force_join_kb(not_joined)
        )
        return

    await _show_welcome(update, context)

    # Log new user
    await add_action_log("new_user", user.id, f"@{user.username} ({user.first_name})")
    await log_action(context.bot, f"👤 New user: <b>{html_escape(user.first_name)}</b> (@{user.username or 'N/A'})")


async def _show_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send welcome message with optional image."""
    user = update.effective_user
    is_admin = user.id == ADMIN_ID
    store_name = await get_setting("bot_name", "NanoStore")

    custom_msg = await get_setting("welcome_text", "")
    if custom_msg:
        text = custom_msg
    else:
        text = (
            f"🏠 <b>Welcome to {html_escape(store_name)}!</b>\n\n"
            "Your premium digital product marketplace.\n"
            "📦 Templates, Courses, Software & more!\n\n"
            "👇 Choose an option below:"
        )

    kb = main_menu_kb(is_admin=is_admin)

    # Prefer new setting key 'welcome_image_id' if present; fall back to legacy 'welcome_image'
    welcome_image_id = await get_setting("welcome_image_id", "") or await get_setting("welcome_image", "")
    if welcome_image_id:
        try:
            await update.message.reply_photo(
                photo=welcome_image_id,
                caption=text,
                parse_mode="HTML",
                reply_markup=kb,
            )
            return
        except Exception as e:
            logger.warning("Welcome image failed: %s", e)

    await update.message.reply_text(text, parse_mode="HTML", reply_markup=kb)


async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Return to main menu via callback."""
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    is_admin = user.id == ADMIN_ID
    store_name = await get_setting("bot_name", "NanoStore")

    context.user_data.pop("state", None)
    context.user_data.pop("temp", None)

    text = (
        f"🏠 <b>{html_escape(store_name)} — Main Menu</b>\n\n"
        f"Welcome back, {html_escape(user.first_name)}!"
    )

    await safe_edit(query, text, reply_markup=main_menu_kb(is_admin=is_admin))


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show help/info page."""
    query = update.callback_query
    await query.answer()

    store_name = await get_setting("bot_name", "NanoStore")

    text = (
        f"ℹ️ <b>{html_escape(store_name)} — Help</b>\n"
        f"{separator()}\n\n"
        "🛍️ <b>Shop</b> — Browse products by category\n"
        "🔍 <b>Search</b> — Find products by keyword\n"
        "🛒 <b>Cart</b> — View & manage your cart\n"
        "📦 <b>Orders</b> — Track your order history\n"
        "🎫 <b>Support</b> — Create support tickets\n"
    )

    await safe_edit(query, text, reply_markup=back_kb("main_menu"))


async def noop_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle disabled/placeholder buttons."""
    await update.callback_query.answer()


async def verify_join_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Verify that user has joined all required channels."""
    query = update.callback_query
    await query.answer()

    user = update.effective_user

    not_joined = await check_force_join(context.bot, user.id)
    if not_joined:
        text = (
            "❌ <b>Not Verified</b>\n\n"
            "You haven't joined all required channels yet.\n"
            "Please join and try again:"
        )
        await safe_edit(query, text, reply_markup=force_join_kb(not_joined))
        return

    is_admin = user.id == ADMIN_ID
    store_name = await get_setting("bot_name", "NanoStore")

    text = (
        f"✅ <b>Verified!</b>\n\n"
        f"Welcome to {html_escape(store_name)}!\n"
        "👇 Choose an option below:"
    )

    await safe_edit(query, text, reply_markup=main_menu_kb(is_admin=is_admin))
