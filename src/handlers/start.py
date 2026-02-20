"""NanoStore start handlers — /start, main menu, help, noop, force join verify."""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_ID
from database import ensure_user, is_user_banned, get_setting, add_action_log, get_user_order_count, get_user_balance
from utils import safe_edit, html_escape, separator
from utils import main_menu_kb, back_kb, force_join_kb

logger = logging.getLogger(__name__)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start — entry point. Shows Main Menu directly with image."""
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

    # Show main menu directly
    await _show_main_menu(update, context, is_command=True)

    # Log
    await add_action_log("user_start", user.id, f"@{user.username} ({user.first_name})")


async def _show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, is_command: bool = False) -> None:
    """Show Main Menu with image from settings.
    
    Args:
        update: Telegram update
        context: Bot context
        is_command: True if called from /start command, False if from callback
    """
    user = update.effective_user
    store_name = await get_setting("bot_name", "NanoStore")
    currency = await get_setting("currency", "Rs")
    
    # Get user data
    from database import get_cart_count
    balance = await get_user_balance(user.id)
    cart_count = await get_cart_count(user.id)
    bal_display = int(balance) if balance == int(balance) else f"{balance:.2f}"
    
    # Check if user is admin
    is_admin = user.id == ADMIN_ID
    
    # Clear any state
    context.user_data.pop("state", None)
    context.user_data.pop("temp", None)

    text = (
        f"🏠 <b>{html_escape(store_name)} — Main Menu</b>\n"
        f"{separator()}\n\n"
        f"💳 Balance: <b>{currency} {bal_display}</b>\n\n"
        "Choose an option below:"
    )
    
    from utils import main_menu_kb, render_screen
    
    if is_command:
        # Called from /start command - send new message with image
        await render_screen(
            query=None,
            bot=context.bot,
            chat_id=update.message.chat_id,
            text=text,
            reply_markup=main_menu_kb(is_admin=is_admin, cart_count=cart_count),
            image_setting_key="shop_image_id",  # Use shop image for main menu
            admin_id=ADMIN_ID
        )
    else:
        # Called from callback - edit existing message
        query = update.callback_query
        await render_screen(
            query=query,
            bot=context.bot,
            chat_id=query.message.chat_id,
            text=text,
            reply_markup=main_menu_kb(is_admin=is_admin, cart_count=cart_count),
            image_setting_key="shop_image_id",
            admin_id=ADMIN_ID
        )


async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show Main Menu Hub (callback from button).
    
    Uses render_screen with shop_image_id.
    """
    query = update.callback_query
    await query.answer()

    # Use the shared function
    await _show_main_menu(update, context, is_command=False)


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show static help guide."""
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
        "🎫 <b>Support</b> — Create tickets for help\n"
        "💳 <b>Wallet</b> — Top-up balance, view history\n\n"
        "<i>Create a support ticket for any issue.</i>"
    )
    await safe_edit(query, text, reply_markup=back_kb("main_menu"))


async def noop_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Placeholder handler for disabled/label buttons."""
    await update.callback_query.answer()


async def verify_join_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Placeholder for force join verification (simplified version)."""
    query = update.callback_query
    await query.answer("✅ Verified!", show_alert=True)
    
    # Redirect to main menu
    await main_menu_handler(update, context)
