"""NanoStore helper functions — safe_edit, render_screen, formatting, logging."""

import asyncio
import logging
from typing import Optional, Union
from telegram import Update, InlineKeyboardMarkup, Message
from telegram.ext import ContextTypes
from telegram.error import BadRequest, TelegramError

logger = logging.getLogger(__name__)


def sep() -> str:
    """Return a visual separator line."""
    return "━━━━━━━━━━━━━━━━━━━━"


def separator() -> str:
    """Alias for sep()."""
    return sep()


def html_escape(text: str) -> str:
    """Escape HTML special characters."""
    if not text:
        return ""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def format_stock(stock: int) -> str:
    """Format stock display."""
    if stock == -1:
        return "♾️ Unlimited"
    elif stock == 0:
        return "🔴 Out of Stock"
    elif stock < 10:
        return f"🟡 {stock} left"
    else:
        return f"🟢 {stock} available"


def format_price(amount: float, currency: str = "Rs") -> str:
    """Format price display with currency."""
    if amount == int(amount):
        return f"{currency} {int(amount)}"
    return f"{currency} {amount:.2f}"


def delivery_icon(delivery_type: str) -> str:
    """Return emoji for delivery type."""
    if delivery_type == "auto":
        return "⚡"
    return "🕐"


def status_emoji(status: str) -> str:
    """Return emoji for order/payment status."""
    status_map = {
        "pending": "⏳",
        "confirmed": "✅",
        "processing": "⚙️",
        "shipped": "📦",
        "delivered": "✅",
        "cancelled": "❌",
        "unpaid": "⏳",
        "paid": "✅",
        "pending_review": "⏳",
        "approved": "✅",
        "rejected": "❌",
        "open": "🟢",
        "closed": "🔴",
    }
    return status_map.get(status.lower(), "❓")


async def send_typing(chat_id: int, bot) -> None:
    """Send typing action to chat."""
    try:
        await bot.send_chat_action(chat_id=chat_id, action="typing")
    except Exception as e:
        logger.warning(f"Failed to send typing action: {e}")


async def notify_log_channel(bot, message: str, log_channel_id: Optional[int] = None) -> None:
    """Send notification to log channel (alias for log_action)."""
    await log_action(bot, message, log_channel_id)


async def auto_delete(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int, delay: int = 7) -> None:
    """Auto-delete a message after delay (alias for schedule_delete)."""
    schedule_delete(context, chat_id, message_id, delay)


async def safe_edit(
    obj: Union[Update, object],
    text: str,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
    parse_mode: str = "HTML",
) -> Optional[Message]:
    """
    Safely edit a message. Handles both CallbackQuery and Message objects.
    Automatically detects if message is photo (uses edit_caption) or text (uses edit_text).
    
    Args:
        obj: Either a CallbackQuery (from update.callback_query) or a Message object
        text: New message text or caption
        reply_markup: Optional keyboard markup
        parse_mode: Parse mode (default: HTML)
    
    Returns:
        The edited Message object, or None if failed
    """
    try:
        # Handle CallbackQuery
        if hasattr(obj, 'message') and hasattr(obj, 'answer'):
            message = obj.message
        # Handle Message directly
        elif hasattr(obj, 'edit_text'):
            message = obj
        else:
            logger.warning(f"safe_edit: Unknown object type {type(obj)}")
            return None
        
        # Check if message has photo (use edit_caption)
        if message.photo:
            return await message.edit_caption(
                caption=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode,
            )
        # Otherwise use edit_text
        else:
            return await message.edit_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode,
            )
    except BadRequest as e:
        if "message is not modified" in str(e).lower():
            logger.debug("Message content unchanged, skipping edit")
            return None
        logger.warning(f"BadRequest in safe_edit: {e}")
        return None
    except TelegramError as e:
        logger.error(f"TelegramError in safe_edit: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in safe_edit: {e}")
        return None


async def resolve_image_id(
    image_setting_key: str,
    from_database_module
) -> Optional[str]:
    """
    Resolve image ID using 3-tier priority system:
    1. Screen-specific image (e.g., shop_image_id)
    2. Global banner image (global_banner_image_id)
    3. Global UI image (global_ui_image_id) if use_global_image is "on"
    
    Args:
        image_setting_key: The specific screen image key (e.g., "shop_image_id")
        from_database_module: The database module to call get_setting from
    
    Returns:
        file_id string or None
    """
    # Tier 1: Screen-specific image
    screen_image = await from_database_module.get_setting(image_setting_key, "")
    if screen_image:
        return screen_image
    
    # Tier 2: Global banner image
    banner_image = await from_database_module.get_setting("global_banner_image_id", "")
    if banner_image:
        return banner_image
    
    # Tier 3: Global UI image (if enabled)
    use_global = await from_database_module.get_setting("use_global_image", "on")
    if use_global.lower() == "on":
        global_image = await from_database_module.get_setting("global_ui_image_id", "")
        if global_image:
            return global_image
    
    return None


async def render_screen(
    query,
    bot,
    chat_id: int,
    text: str,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
    image_setting_key: Optional[str] = None,
    admin_id: int = 0,
    parse_mode: str = "HTML",
) -> Optional[Message]:
    """
    Render a screen with optional image using 3-tier priority system.
    EDIT IN PLACE - never deletes the current message.
    
    Args:
        query: CallbackQuery object
        bot: Bot instance
        chat_id: Chat ID
        text: Message text/caption
        reply_markup: Optional keyboard
        image_setting_key: Key for screen-specific image (e.g., "shop_image_id")
        admin_id: Admin user ID for notifications
        parse_mode: Parse mode (default: HTML)
    
    Returns:
        Edited/sent Message object or None
    """
    import database
    
    file_id = None
    if image_setting_key:
        file_id = await resolve_image_id(image_setting_key, database)
    
    # If we have a query (callback), always edit in place
    if query:
        # Check if current message has photo
        current_has_photo = query.message.photo is not None and len(query.message.photo) > 0
        
        # If we want to show image AND current message has photo
        if file_id and current_has_photo:
            try:
                # Edit caption of existing photo message
                return await query.message.edit_caption(
                    caption=text,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode,
                )
            except BadRequest as e:
                error_msg = str(e).lower()
                if "wrong file identifier" in error_msg or "file_id" in error_msg:
                    logger.warning(f"Invalid file_id for {image_setting_key}: {file_id}. Clearing setting.")
                    if image_setting_key:
                        await database.set_setting(image_setting_key, "")
                    # Fall through to text edit
                elif "message is not modified" not in error_msg:
                    logger.error(f"BadRequest editing caption for {image_setting_key}: {e}")
            except Exception as e:
                logger.error(f"Error editing caption for {image_setting_key}: {e}")
        
        # Otherwise, edit as text message (works for both text and photo messages)
        return await safe_edit(query, text, reply_markup=reply_markup, parse_mode=parse_mode)
    
    else:
        # No query - this is a new message (e.g., from /start command)
        if file_id:
            try:
                return await bot.send_photo(
                    chat_id=chat_id,
                    photo=file_id,
                    caption=text,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode,
                )
            except Exception as e:
                logger.error(f"Error sending photo for {image_setting_key}: {e}")
        
        # Fallback to text message
        return await bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
        )


def schedule_delete(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    message_id: int,
    delay_seconds: int,
    label: str = "message"
) -> None:
    """
    Schedule a message for deletion after a delay using context.application.create_task.
    
    Args:
        context: Context object
        chat_id: Chat ID
        message_id: Message ID to delete
        delay_seconds: Delay in seconds before deletion
        label: Label for logging (e.g., "admin_prompt", "confirmation")
    """
    async def _delete_task():
        try:
            await asyncio.sleep(delay_seconds)
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            logger.info(f"Auto-deleted {label} (msg={message_id}) after {delay_seconds}s")
        except Exception as e:
            logger.warning(f"Failed to auto-delete {label} (msg={message_id}): {e}")
    
    context.application.create_task(_delete_task())


async def send_restart_notification(
    bot,
    admin_id: int,
    message: str,
    auto_delete_seconds: int = 60,
    parse_mode: str = "HTML"
) -> Optional[Message]:
    """
    Send a restart notification to admin with auto-delete.
    
    Args:
        bot: Bot instance
        admin_id: Admin user ID
        message: Notification message
        auto_delete_seconds: Seconds before auto-delete (default: 60)
        parse_mode: Parse mode (default: HTML)
    
    Returns:
        Sent Message object or None
    """
    try:
        msg = await bot.send_message(
            chat_id=admin_id,
            text=message,
            parse_mode=parse_mode
        )
        logger.info(f"Sent restart notification to admin {admin_id}")
        
        # Schedule deletion
        async def _delete_notification():
            try:
                await asyncio.sleep(auto_delete_seconds)
                await bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)
                logger.info(f"Auto-deleted restart notification (msg={msg.message_id})")
            except Exception as e:
                logger.warning(f"Failed to auto-delete restart notification: {e}")
        
        # Use asyncio.create_task for the deletion
        asyncio.create_task(_delete_notification())
        
        return msg
    except Exception as e:
        logger.warning(f"Failed to send restart notification: {e}")
        return None


async def log_action(bot, message: str, log_channel_id: Optional[int] = None) -> None:
    """Send action log to log channel."""
    from config import LOG_CHANNEL_ID
    
    channel = log_channel_id or LOG_CHANNEL_ID
    if not channel:
        return
    
    try:
        await bot.send_message(
            chat_id=channel,
            text=message,
            parse_mode="HTML",
        )
    except Exception as e:
        logger.warning(f"Failed to log action: {e}")



# ======================== MULTI-CURRENCY SYSTEM ========================

# In-memory cache for currency rates (refreshed every 5 minutes)
_currency_cache = {}
_cache_timestamp = None

SUPPORTED_CURRENCIES = {
    "PKR": {"symbol": "Rs", "flag": "🇵🇰", "name": "Pakistani Rupee"},
    "USD": {"symbol": "$", "flag": "💵", "name": "US Dollar"},
    "AED": {"symbol": "د.إ", "flag": "🇦🇪", "name": "UAE Dirham"},
    "SAR": {"symbol": "﷼", "flag": "🇸🇦", "name": "Saudi Riyal"},
    "GBP": {"symbol": "£", "flag": "🇬🇧", "name": "British Pound"},
}


async def fetch_live_rates() -> dict:
    """
    Fetch live currency rates from CoinGecko API.
    Returns dict of {currency: rate_vs_pkr}.
    Falls back to cached rates if API fails.
    """
    global _currency_cache, _cache_timestamp
    from datetime import datetime, timedelta
    import aiohttp
    
    # Check if cache is still valid (5 minutes)
    if _cache_timestamp and (datetime.utcnow() - _cache_timestamp) < timedelta(minutes=5):
        if _currency_cache:
            return _currency_cache
    
    try:
        # Fetch rates from CoinGecko (free API, no key needed)
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={
                    "ids": "tether",  # Use USDT as stable reference
                    "vs_currencies": "pkr,usd,aed,sar,gbp"
                },
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    tether = data.get("tether", {})
                    
                    # Calculate rates vs PKR
                    pkr_rate = tether.get("pkr", 280)  # Fallback to 280
                    rates = {
                        "PKR": 1.0,  # Base currency
                        "USD": pkr_rate / tether.get("usd", 1.0),
                        "AED": pkr_rate / tether.get("aed", 3.67),
                        "SAR": pkr_rate / tether.get("sar", 3.75),
                        "GBP": pkr_rate / tether.get("gbp", 0.79),
                    }
                    
                    _currency_cache = rates
                    _cache_timestamp = datetime.utcnow()
                    
                    # Store in database for persistence
                    import database
                    for curr, rate in rates.items():
                        if curr != "PKR":
                            await database.update_currency_rate(curr, rate)
                    
                    logger.info(f"Updated currency rates: {rates}")
                    return rates
    except Exception as e:
        logger.warning(f"Failed to fetch live rates: {e}")
    
    # Fallback to database cache
    if not _currency_cache:
        import database
        _currency_cache = {
            "PKR": 1.0,
            "USD": await database.get_currency_rate("USD") or 280.0,
            "AED": await database.get_currency_rate("AED") or 76.0,
            "SAR": await database.get_currency_rate("SAR") or 75.0,
            "GBP": await database.get_currency_rate("GBP") or 355.0,
        }
        _cache_timestamp = datetime.utcnow()
    
    return _currency_cache


async def convert_amount(amount_pkr: float, target_currency: str) -> float:
    """
    Convert amount from PKR to target currency.
    
    Args:
        amount_pkr: Amount in PKR (base currency)
        target_currency: Target currency code (USD, AED, SAR, GBP, PKR)
    
    Returns:
        Converted amount
    """
    if target_currency == "PKR":
        return amount_pkr
    
    rates = await fetch_live_rates()
    rate = rates.get(target_currency, 1.0)
    
    return amount_pkr / rate


async def format_currency(amount: float, currency_code: str) -> str:
    """
    Format amount with currency symbol.
    
    Args:
        amount: Amount to format
        currency_code: Currency code (PKR, USD, AED, SAR, GBP)
    
    Returns:
        Formatted string like "Rs 1,000" or "$10.50"
    """
    curr_info = SUPPORTED_CURRENCIES.get(currency_code, SUPPORTED_CURRENCIES["PKR"])
    symbol = curr_info["symbol"]
    
    # Format with 2 decimals for non-PKR, no decimals for PKR if whole number
    if currency_code == "PKR":
        if amount == int(amount):
            return f"{symbol} {int(amount):,}"
        return f"{symbol} {amount:,.2f}"
    else:
        return f"{symbol} {amount:,.2f}"


def get_currency_display(currency_code: str) -> str:
    """Get display string for currency (e.g., 'PKR 🇵🇰')."""
    curr_info = SUPPORTED_CURRENCIES.get(currency_code, SUPPORTED_CURRENCIES["PKR"])
    return f"{currency_code} {curr_info['flag']}"
