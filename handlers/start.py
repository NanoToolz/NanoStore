"""NanoStore start handlers — /start, main menu, help, noop, force join verify.

Key improvements:
- Maintenance mode check (admin bypasses it)
- auto_delete() on /start command to keep chats clean
- send_typing() for immediate feedback
- welcome_image properly loaded from settings
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_ID
from database import ensure_user, is_user_banned, get_setting, add_action_log, get_user_order_count, get_user_balance
from helpers import (
    safe_edit, check_force_join, notify_log_channel,
    html_escape, separator, auto_delete, send_typing,
)
from keyboards import main_menu_kb, back_kb, force_join_kb

logger = logging.getLogger(__name__)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start — entry point. Checks ban, maintenance, force join, then shows welcome."""
    user = update.effective_user

    # Register or update user
    await ensure_user(user.id, user.first_name or "User", user.username or "")

    # Ban check
    if await is_user_banned(user.id):
        await update.message.reply_text(
            "⛔ <b>Access Denied</b>\n\n"
            "You have been banned from this store.\n"
            "Contact support if you believe this is a mistake.",
            parse_mode="HTML",
        )
        return

    # Maintenance mode — only admin bypasses this
    if user.id != ADMIN_ID:
        maintenance = await get_setting("maintenance", "off")
        if maintenance == "on":
            mtext = await get_setting(
                "maintenance_text",
                "🔧 <b>Under Maintenance</b>\n\nBot is temporarily unavailable. Please check back soon!"
            )
            await update.message.reply_text(mtext, parse_mode="HTML")
            return

    # Typing indicator — immediate feedback
    await send_typing(update.message.chat_id, context.bot)

    # Force join check
    not_joined = await check_force_join(context.bot, user.id)
    if not_joined:
        text = (
            f"🔒 <b>Channel Join Required</b>\n"
            f"{separator()}\n\n"
            "Join these channels to use the store:"
        )
        await update.message.reply_text(
            text, parse_mode="HTML", reply_markup=force_join_kb(not_joined)
        )
        return

    # Show welcome screen
    await _show_welcome(update, context)

    # Auto-delete the /start command (keeps chat clean)
    await auto_delete(update.message)

    # Log
    await add_action_log("user_start", user.id, f"@{user.username} ({user.first_name})")
    await notify_log_channel(
        context.bot,
        f"👤 <b>User Started Bot</b>\n"
        f"Name: {html_escape(user.first_name)}\n"
        f"@{html_escape(user.username or 'none')} | <code>{user.id}</code>"
    )


async def _show_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send welcome message — with image if configured, else plain text.

    Now includes user profile summary (ID, username, orders, balance).
    Uses render_screen helper for consistent image handling.
    """
    user = update.effective_user
    is_admin = user.id == ADMIN_ID
    store_name = await get_setting("bot_name", "NanoStore")

    # Base welcome text (custom or default)
    custom_msg = await get_setting("welcome_text", "")

    currency = await get_setting("currency", "Rs")
    orders_count = await get_user_order_count(user.id)
    balance = await get_user_balance(user.id)

    profile_block = (
        f"👤 <b>Profile</b>\n"
        f"🆔 <code>{user.id}</code>\n"
        f"📎 @{html_escape(user.username or 'N/A')}\n"
        f"🛒 Orders: <b>{orders_count}</b>\n"
        f"💳 Balance: <b>{currency} {balance}</b>\n\n"
    )

    if custom_msg:
        text = custom_msg + "\n\n" + profile_block + "👇 Choose an option:"
    else:
        text = (
            f"🛍️ <b>Welcome to {html_escape(store_name)}!</b>\n\n"
            + profile_block +
            "Your premium digital product marketplace.\n"
            "📦 eBooks, Templates, Courses, Software & more!\n\n"
            "👇 Choose an option:"
        )

    kb = main_menu_kb(is_admin=is_admin)

    # Use render_screen helper for consistent image handling
    from helpers import render_screen
    await render_screen(
        message=update.message,
        bot=context.bot,
        chat_id=update.message.chat_id,
        text=text,
        reply_markup=kb,
        image_setting_key="welcome_image_id"
    )


async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Return to main menu — clears any active conversation state.
    
    Uses render_screen with welcome_image_id for consistent main menu experience.
    """
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    is_admin = user.id == ADMIN_ID
    store_name = await get_setting("bot_name", "NanoStore")

    context.user_data.pop("state", None)
    context.user_data.pop("temp", None)

    text = (
        f"🏠 <b>{html_escape(store_name)}</b>\n\n"
        f"Welcome back, {html_escape(user.first_name)}! 👋"
    )
    
    # Use render_screen for consistent main menu experience
    from helpers import render_screen
    await render_screen(
        query=query,
        bot=context.bot,
        chat_id=query.message.chat_id,
        text=text,
        reply_markup=main_menu_kb(is_admin=is_admin),
        image_setting_key="welcome_image_id"
    )


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show help/feature guide."""
    query = update.callback_query
    await query.answer()

    store_name = await get_setting("bot_name", "NanoStore")
    text = (
        f"ℹ️ <b>{html_escape(store_name)} — Help Guide</b>\n"
        f"{separator()}\n\n"
        "🛍️ <b>Shop</b> — Browse all product categories\n"
        "🔍 <b>Search</b> — Find products by keyword\n"
        "🛒 <b>Cart</b> — Add items, adjust quantities\n"
        "📦 <b>My Orders</b> — Track order status\n"
        "🎁 <b>Daily Reward</b> — Free balance once per day\n"
        "🎫 <b>Support</b> — Create tickets for help\n\n"
        "⚡ = Instant auto-delivery after payment\n"
        "🕐 = Manual delivery by our team\n\n"
        "<i>Create a support ticket for any issue.</i>"
    )
    await safe_edit(query, text, reply_markup=back_kb("main_menu"))


async def noop_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Placeholder handler for disabled/label buttons."""
    await update.callback_query.answer()


async def verify_join_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Verify channel membership after user taps 'I've Joined'."""
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    not_joined = await check_force_join(context.bot, user.id)

    if not_joined:
        text = (
            "❌ <b>Not Verified Yet</b>\n\n"
            "You haven't joined all required channels.\n"
            "Please join and tap the button again:"
        )
        await safe_edit(query, text, reply_markup=force_join_kb(not_joined))
        return

    is_admin = user.id == ADMIN_ID
    store_name = await get_setting("bot_name", "NanoStore")
    text = (
        f"✅ <b>Verified!</b>\n\n"
        f"Welcome to {html_escape(store_name)}! 🎉\n"
        "👇 Choose an option:"
    )
    await safe_edit(query, text, reply_markup=main_menu_kb(is_admin=is_admin))
