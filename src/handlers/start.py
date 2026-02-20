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
    """/start — entry point. Shows Welcome Splash only."""
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

    # Show welcome screen
    await _show_welcome(update, context)

    # Log
    await add_action_log("user_start", user.id, f"@{user.username} ({user.first_name})")


async def _show_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send welcome splash with profile info and single 'Go to Main Menu' button.
    
    Uses render_screen with welcome_image_id.
    """
    user = update.effective_user
    store_name = await get_setting("bot_name", "NanoStore")
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
        text = custom_msg + "\n\n" + profile_block + "👇 Tap below to continue:"
    else:
        text = (
            f"🛍️ <b>Welcome to {html_escape(store_name)}!</b>\n\n"
            + profile_block +
            "Your premium digital product marketplace.\n"
            "📦 eBooks, Templates, Courses, Software & more!\n\n"
            "👇 Tap below to continue:"
        )

    from utils import welcome_kb
    from utils import render_screen
    
    await render_screen(
        query=None,  # No query for /start command
        bot=context.bot,
        chat_id=update.message.chat_id,
        text=text,
        reply_markup=welcome_kb(),
        image_setting_key="welcome_image_id",
        admin_id=ADMIN_ID
    )


async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show Main Menu Hub (no welcome content, only balance + navigation).
    
    Uses render_screen with NO image (hub is text-only by design).
    """
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    is_admin = user.id == ADMIN_ID
    store_name = await get_setting("bot_name", "NanoStore")

    context.user_data.pop("state", None)
    context.user_data.pop("temp", None)

    # Get user balance and cart count
    currency = await get_setting("currency", "Rs")
    balance = await get_user_balance(user.id)
    bal_display = int(balance) if balance == int(balance) else f"{balance:.2f}"
    
    from database import get_cart_count
    cart_count = await get_cart_count(user.id)

    text = (
        f"🏠 <b>{html_escape(store_name)} — Main Menu</b>\n"
        f"{separator()}\n\n"
        f"💳 Balance: <b>{currency} {bal_display}</b>\n\n"
        "Choose an option below:"
    )
    
    from keyboards import main_menu_kb
    await safe_edit(query, text, reply_markup=main_menu_kb(is_admin=is_admin, cart_count=cart_count))


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
