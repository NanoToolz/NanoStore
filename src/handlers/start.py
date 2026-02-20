"""NanoStore start handlers — /start, main menu, help, noop, force join verify."""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_ID
from database import (
    ensure_user, is_user_banned, get_setting, add_action_log,
    get_user_balance, get_user_total_spent, get_user_total_deposited,
    get_user_join_date, get_user_pending_orders, get_user_completed_orders,
    get_user_referral_count, get_spin_status, get_user_order_count,
    create_referral, add_points
)
from utils import safe_edit, html_escape, separator, send_typing
from utils import main_menu_kb, back_kb

logger = logging.getLogger(__name__)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start — entry point. Sends ONE message with welcome text + inline buttons."""
    user = update.effective_user
    args = context.args
    
    # Log command
    from utils.activity_logger import log_command
    log_command("start", user.id, user.username, args)

    # Check for referral link (format: ref_123456789)
    referrer_id = None
    if args and len(args) > 0 and args[0].startswith("ref_"):
        try:
            referrer_id = int(args[0].split("_")[1])
            if referrer_id == user.id:
                referrer_id = None  # Can't refer yourself
        except (ValueError, IndexError):
            referrer_id = None

    # 1. Ensure user exists
    await ensure_user(user.id, user.first_name or "User", user.username or "")

    # 2. Ban check
    if await is_user_banned(user.id):
        await update.message.reply_text(
            "⛔ <b>Access Denied</b>\n\n"
            "You have been banned from this store.\n"
            "Contact support if you believe this is a mistake.",
            parse_mode="HTML",
        )
        return

    # 3. Maintenance check (admin bypasses)
    maintenance = await get_setting("maintenance", "off")
    if maintenance == "on" and user.id != ADMIN_ID:
        maintenance_text = await get_setting("maintenance_text", "Bot is under maintenance. Please try again later.")
        await update.message.reply_text(
            f"🔧 <b>Maintenance Mode</b>\n\n{html_escape(maintenance_text)}",
            parse_mode="HTML",
        )
        return

    # Handle referral if this is a new user
    if referrer_id:
        from database import get_user
        existing = await get_user(user.id)
        
        # Only process referral if user just joined (within last 10 seconds)
        from datetime import datetime, timedelta
        try:
            joined = datetime.fromisoformat(existing["joined_at"])
            if datetime.utcnow() - joined < timedelta(seconds=10):
                # Create referral relationship
                if await create_referral(referrer_id, user.id):
                    # Award points: 500 to new user, 1000 to referrer
                    await add_points(user.id, 500, "Referral welcome bonus")
                    await add_points(referrer_id, 1000, f"Referred user {user.id}")
                    
                    # Notify referrer
                    try:
                        await context.bot.send_message(
                            chat_id=referrer_id,
                            text=f"🎉 <b>New Referral!</b>\n\n"
                                 f"<b>{html_escape(user.first_name)}</b> joined using your link!\n"
                                 f"💎 You earned: <b>1,000 points</b>",
                            parse_mode="HTML"
                        )
                    except Exception:
                        pass
        except Exception:
            pass

    # Delete user's /start command
    try:
        await update.message.delete()
    except Exception:
        pass

    # Build welcome text with all stats
    welcome_text = await _build_welcome_text(user, context)
    is_admin = user.id == ADMIN_ID
    
    # Check if welcome image is configured
    welcome_image_id = await get_setting("shop_image_id", "")
    
    # Send ONE message with text + inline buttons
    if welcome_image_id:
        # Send photo with caption + inline keyboard
        try:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=welcome_image_id,
                caption=welcome_text,
                reply_markup=main_menu_kb(is_admin=is_admin),
                parse_mode="HTML"
            )
        except Exception as e:
            logger.warning(f"Failed to send welcome image: {e}, falling back to text")
            # Fallback to text if image fails
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=welcome_text,
                reply_markup=main_menu_kb(is_admin=is_admin),
                parse_mode="HTML"
            )
    else:
        # Send text message with inline keyboard
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=welcome_text,
            reply_markup=main_menu_kb(is_admin=is_admin),
            parse_mode="HTML"
        )

    # Log
    await add_action_log("user_start", user.id, f"@{user.username} ({user.first_name})")


async def _build_welcome_text(user, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Build detailed welcome message text with all user stats."""
    store_name = await get_setting("bot_name", "NanoStore")
    currency = await get_setting("currency", "Rs")
    
    # Get all user stats
    balance = await get_user_balance(user.id)
    total_spent = await get_user_total_spent(user.id)
    total_deposited = await get_user_total_deposited(user.id)
    join_date = await get_user_join_date(user.id)
    total_orders = await get_user_order_count(user.id)
    completed_orders = await get_user_completed_orders(user.id)
    pending_orders = await get_user_pending_orders(user.id)
    referral_count = await get_user_referral_count(user.id)
    spin_status = await get_spin_status(user.id)
    
    # Format values
    full_name = user.first_name or "User"
    username = user.username if user.username else "no username"
    user_id = user.id
    
    # User status (VIP if spent > 50000)
    status = "⭐ VIP Member" if total_spent > 50000 else "Regular Member"
    
    # Format amounts
    bal_display = int(balance) if balance == int(balance) else f"{balance:.2f}"
    spent_display = int(total_spent) if total_spent == int(total_spent) else f"{total_spent:.2f}"
    deposited_display = int(total_deposited) if total_deposited == int(total_deposited) else f"{total_deposited:.2f}"
    
    # Spin status text
    if spin_status["available"]:
        spin_text = "Ready to Spin! ✅"
    else:
        h = spin_status["hours_left"]
        m = spin_status["mins_left"]
        spin_text = f"Come back in {h}h {m}m ⏳"
    
    # Build orders line (hide pending if 0)
    if pending_orders > 0:
        orders_line = f"📦 Orders: {total_orders}   ✅ Done: {completed_orders}   ⏳ Pending: {pending_orders}"
    else:
        orders_line = f"📦 Orders: {total_orders}   ✅ Done: {completed_orders}"
    
    text = (
        f"🛍️ <b>{html_escape(store_name)}</b>\n"
        f"Hey {html_escape(full_name)}, Welcome Back! 👋\n\n"
        f"👤 {html_escape(full_name)}  •  @{html_escape(username)}  •  ID: {user_id}\n"
        f"📅 Member since {join_date}  •  {status}\n\n"
        f"💳 Balance: {currency} {bal_display}\n"
        f"💸 Total Spent: {currency} {spent_display}\n"
        f"💰 Total Deposited: {currency} {deposited_display}\n\n"
        f"{orders_line}\n\n"
        f"🎰 Daily Spin — {spin_text}\n"
        f"👥 Referrals — {referral_count} friends joined 🎉\n\n"
        f"⚡ Instant Auto-Delivery on all products!"
    )
    
    return text


async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show Main Menu (callback from button) - edits existing message, does NOT resend welcome."""
    query = update.callback_query
    await query.answer()
    
    # Log callback click
    from utils.activity_logger import log_callback_click
    user = update.effective_user
    log_callback_click("main_menu", user.id, user.username)

    is_admin = user.id == ADMIN_ID
    
    # Clear any state
    context.user_data.pop("state", None)
    context.user_data.pop("temp", None)

    # Build simple main menu text (NOT the full welcome)
    store_name = await get_setting("bot_name", "NanoStore")
    first_name = user.first_name or "User"
    
    text = (
        f"🏠 <b>{html_escape(store_name)} — Main Menu</b>\n\n"
        f"Welcome back, {html_escape(first_name)}! Choose an option below:"
    )
    
    # Log the action
    logger.info(f"Main menu accessed | Editing message in place | user_id={user.id}")
    
    # Edit the existing message - NEVER delete, NEVER send new
    await safe_edit(query, text, reply_markup=main_menu_kb(is_admin=is_admin))
    
    logger.info(f"Main menu rendered successfully | action=edited_message")


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show static help guide."""
    query = update.callback_query
    await query.answer()

    store_name = await get_setting("bot_name", "NanoStore")
    text = (
        f"ℹ️ <b>{html_escape(store_name)} — Help Guide</b>\n"
        f"{separator()}\n\n"
        "🛍️ <b>Shop</b> — Browse all product categories\n"
        "🛒 <b>Cart</b> — Add items, adjust quantities\n"
        "📦 <b>My Orders</b> — Track order status\n"
        "🎫 <b>Support</b> — Create tickets for help\n"
        "💳 <b>Wallet</b> — Top-up balance, view history\n"
        "🎰 <b>Daily Spin</b> — Earn points daily\n"
        "👥 <b>Referral</b> — Invite friends, earn rewards\n\n"
        "<i>Create a support ticket for any issue.</i>"
    )
    await safe_edit(query, text, reply_markup=back_kb("main_menu"))


async def noop_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Placeholder handler for disabled/label buttons."""
    await update.callback_query.answer()


async def verify_join_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Verify user has joined required channels."""
    query = update.callback_query
    await query.answer()
    
    # Import membership check
    from middleware import check_membership
    
    # Check if user is now a member
    if await check_membership(update, context):
        await query.answer("✅ Verified! Welcome!", show_alert=True)
        
        # Redirect to main menu
        await main_menu_handler(update, context)
    else:
        await query.answer("⚠️ Please join all channels first!", show_alert=True)
