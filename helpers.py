"""NanoStore helper utilities — safe_edit, formatting, logging, force join, etc."""

import logging
import asyncio
from html import escape
from telegram import InlineKeyboardMarkup
from config import LOG_CHANNEL_ID

logger = logging.getLogger(__name__)


# ════════════════════════ SAFE EDIT ════════════════════════

async def safe_edit(
    query,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
    parse_mode: str = "HTML",
) -> None:
    """Safely edit a callback query message.

    Works for both plain text messages and media messages with captions.
    Falls back to sending a new message if the original cannot be edited.
    """
    try:
        # First try editing as a normal text message
        await query.message.edit_text(
            text=text,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
            disable_web_page_preview=True,
        )
        return
    except Exception as e:
        error_msg = str(e).lower()

        # If there is no text (photo/document message), try editing caption instead
        if "there is no text in the message to edit" in error_msg:
            try:
                await query.message.edit_caption(
                    caption=text,
                    parse_mode=parse_mode,
                    reply_markup=reply_markup,
                )
                return
            except Exception as e2:
                error_msg2 = str(e2).lower()
                if "message is not modified" in error_msg2:
                    return
                if "message to edit not found" in error_msg2 or "message can't be edited" in error_msg2:
                    try:
                        await query.message.chat.send_message(
                            text=text,
                            parse_mode=parse_mode,
                            reply_markup=reply_markup,
                            disable_web_page_preview=True,
                        )
                    except Exception as send_err:
                        logger.warning("Failed to send replacement message after caption edit failure: %s", send_err)
                    return
                logger.warning("safe_edit caption failed: %s", e2)
                return

        # Original text edit cases
        if "message is not modified" in error_msg:
            return
        if "message to edit not found" in error_msg or "message can't be edited" in error_msg:
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
        return ""}
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


def delivery_icon(delivery_type: str) -> str:
    """Emoji icon for delivery type (auto/manual)."""
    mapping = {
        "auto": "⚡",    # instant / auto delivery
        "manual": "🕐",  # manual delivery
    }
    return mapping.get(delivery_type, "📦")


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


async def notify_log_channel(bot, text: str) -> None:
    """Backward-compatible wrapper for logging helper.

    Used by newer handlers; internally calls log_action.
    """
    await log_action(bot, text)


# ════════════════════════ AUTO-DELETE & TYPING ════════════════════════

async def send_typing(chat_id: int, bot) -> None:
    """Send 'typing' action to give instant feedback to the user."""
    try:
        await bot.send_chat_action(chat_id=chat_id, action="typing")
    except Exception as e:
        logger.warning("send_typing failed: %s", e)


async def auto_delete(message, delay: int | None = None) -> None:
    """Schedule auto-deletion of a message.

    If delay is None, reads the `auto_delete` setting from DB (seconds).
    0 or invalid values disable auto-delete.
    """
    if message is None:
        return

    from database import get_setting

    try:
        if delay is None:
            raw = await get_setting("auto_delete", "0")
            delay = int(raw or 0)
        else:
            delay = int(delay)
    except Exception:
        delay = 0

    if delay <= 0:
        return

    async def _delete_later() -> None:
        try:
            await asyncio.sleep(delay)
            await message.delete()
        except Exception as e:
            logger.warning("auto_delete failed: %s", e)

    # Fire-and-forget, does not block handler
    try:
        asyncio.create_task(_delete_later())
    except RuntimeError:
        # If no running loop (edge cases), just skip silently
        logger.warning("auto_delete could not create task (no running loop)")


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
