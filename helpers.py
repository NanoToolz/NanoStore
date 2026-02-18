"""NanoStore helper utilities — safe_edit, formatting, logging, force join, etc."""

import logging
from html import escape
from telegram import InlineKeyboardMarkup
from config import LOG_CHANNEL_ID

logger = logging.getLogger(__name__)


# ════════════════════════ SAFE EDIT ════════════════════════

async def safe_edit(
    query,
    text: str,
    reply_markup: InlineKeyboardMarkup = None,
    parse_mode: str = "HTML",
) -> None:
    """Safely edit a callback query message.

    Handles common errors:
    - Message is not modified (same content)
    - Message to edit not found (deleted)
    - Message can't be edited (too old / not inline)
    """
    try:
        await query.message.edit_text(
            text=text,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
            disable_web_page_preview=True,
        )
    except Exception as e:
        error_msg = str(e).lower()
        if "message is not modified" in error_msg:
            return
        if "message to edit not found" in error_msg:
            try:
                await query.message.chat.send_message(
                    text=text,
                    parse_mode=parse_mode,
                    reply_markup=reply_markup,
                    disable_web_page_preview=True,
                )
            except Exception as send_err:
                logger.warning("Failed to send replacement message: %s", send_err)
            return
        if "message can't be edited" in error_msg:
            try:
                await query.message.chat.send_message(
                    text=text,
                    parse_mode=parse_mode,
                    reply_markup=reply_markup,
                    disable_web_page_preview=True,
                )
            except Exception as send_err:
                logger.warning("Failed to send replacement message: %s", send_err)
            return
        logger.warning("safe_edit failed: %s", e)


# ════════════════════════ FORCE JOIN ════════════════════════

async def check_force_join(bot, user_id: int) -> list:
    """Check if user has joined all required channels.

    Returns list of channels NOT joined (empty = all good).
    """
    from database import get_force_join_channels

    channels = await get_force_join_channels()
    if not channels:
        return []

    not_joined = []
    for ch in channels:
        try:
            member = await bot.get_chat_member(
                chat_id=ch["channel_id"], user_id=user_id
            )
            if member.status in ("left", "kicked"):
                not_joined.append(ch)
        except Exception:
            # Can't check = assume not joined
            not_joined.append(ch)

    return not_joined


# ════════════════════════ FORMATTING ════════════════════════

def html_escape(text: str) -> str:
    """Escape HTML special characters for Telegram."""
    if not text:
        return ""
    return escape(str(text))


def separator(char: str = "━", length: int = 19) -> str:
    """Return a visual separator line."""
    return char * length


def format_price(price: float, currency: str = "Rs") -> str:
    """Format price with currency, removing .0 for whole numbers."""
    if price == int(price):
        return f"{currency} {int(price)}"
    return f"{currency} {price:.2f}"


def format_stock(stock: int) -> str:
    """Format stock display."""
    if stock == -1:
        return "♾️ Unlimited"
    if stock == 0:
        return "🔴 Out of Stock"
    return f"🟢 {stock} available"


def status_emoji(status: str) -> str:
    """Get emoji for order/payment status."""
    emojis = {
        "pending": "⏳",
        "confirmed": "✅",
        "processing": "⚙️",
        "shipped": "🚚",
        "delivered": "📦",
        "completed": "✅",
        "cancelled": "❌",
        "unpaid": "💰",
        "paid": "✅",
        "pending_review": "⏳",
        "rejected": "❌",
        "refunded": "🔄",
        "open": "🟢",
        "closed": "🔴",
        "approved": "✅",
    }
    return emojis.get(status, "📌")


def truncate(text: str, max_len: int = 100) -> str:
    """Truncate text with ellipsis."""
    if not text:
        return ""
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."


# ════════════════════════ LOGGING ════════════════════════

async def log_action(bot, text: str) -> None:
    """Send action log to the log channel."""
    if not LOG_CHANNEL_ID:
        return
    try:
        await bot.send_message(
            chat_id=LOG_CHANNEL_ID,
            text=text,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    except Exception as e:
        logger.warning("Failed to log to channel: %s", e)


# ════════════════════════ VALIDATION ════════════════════════

def is_valid_price(text: str) -> bool:
    """Check if text is a valid price."""
    try:
        val = float(text)
        return val >= 0
    except (ValueError, TypeError):
        return False


def is_valid_stock(text: str) -> bool:
    """Check if text is a valid stock value."""
    try:
        val = int(text)
        return val >= -1
    except (ValueError, TypeError):
        return False


def parse_int(text: str, default: int = 0) -> int:
    """Safe integer parsing."""
    try:
        return int(text)
    except (ValueError, TypeError):
        return default


def parse_float(text: str, default: float = 0.0) -> float:
    """Safe float parsing."""
    try:
        return float(text)
    except (ValueError, TypeError):
        return default
