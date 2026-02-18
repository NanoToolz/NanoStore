"""NanoStore helpers — safe_edit, force join check, logging, formatting."""

import logging
from html import escape
from telegram import Bot
from telegram.error import BadRequest, Forbidden
from config import LOG_CHANNEL_ID
from database import get_force_join_channels, get_setting

logger = logging.getLogger(__name__)


# ════════════════════════ SAFE EDIT ════════════════════════

async def safe_edit(query, text: str, reply_markup=None, parse_mode: str = "HTML"):
    """Safely edit a callback query message.

    Handles all common Telegram edit errors:
    1. Try edit_message_text (normal text messages)
    2. Try edit_message_caption (photo/media messages)
    3. Delete old + send new (final fallback)
    Also catches parse errors and 'message not modified'.
    """
    # Attempt 1: edit_message_text
    try:
        return await query.edit_message_text(
            text=text, parse_mode=parse_mode, reply_markup=reply_markup
        )
    except BadRequest as e:
        err = str(e).lower()

        if "message is not modified" in err:
            return None

        if "can't parse entities" in err:
            try:
                return await query.edit_message_text(
                    text=text, reply_markup=reply_markup
                )
            except Exception:
                pass

        if "there is no text in the message" in err or "message can't be edited" in err:
            pass  # fall through to attempt 2
        else:
            logger.warning("safe_edit edit_text failed: %s", e)
    except Exception as e:
        logger.warning("safe_edit edit_text unexpected: %s", e)

    # Attempt 2: edit_message_caption (photo/media messages)
    try:
        return await query.edit_message_caption(
            caption=text, parse_mode=parse_mode, reply_markup=reply_markup
        )
    except BadRequest as e:
        err = str(e).lower()

        if "message is not modified" in err:
            return None

        if "can't parse entities" in err:
            try:
                return await query.edit_message_caption(
                    caption=text, reply_markup=reply_markup
                )
            except Exception:
                pass

        logger.warning("safe_edit edit_caption failed: %s", e)
    except Exception as e:
        logger.warning("safe_edit edit_caption unexpected: %s", e)

    # Attempt 3: delete old message + send new one
    try:
        chat = query.message.chat
        try:
            await query.message.delete()
        except Exception:
            pass

        try:
            return await chat.send_message(
                text=text, parse_mode=parse_mode, reply_markup=reply_markup
            )
        except BadRequest as e:
            if "can't parse entities" in str(e).lower():
                return await chat.send_message(
                    text=text, reply_markup=reply_markup
                )
            raise
    except Exception as e:
        logger.error("safe_edit all attempts failed: %s", e)
        return None


# ════════════════════════ FORCE JOIN ════════════════════════

async def check_force_join(bot: Bot, user_id: int) -> list[dict]:
    """Check if user has joined all required channels.

    Returns list of channels the user has NOT joined.
    Empty list means user has joined all (or no channels configured).
    """
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
        except Forbidden:
            logger.warning(
                "Bot not admin in channel %s (%s) — skipping force join check",
                ch["channel_name"], ch["channel_id"]
            )
        except Exception as e:
            logger.warning(
                "Force join check failed for channel %s: %s",
                ch["channel_id"], e
            )
            not_joined.append(ch)

    return not_joined


# ════════════════════════ ACTION LOGGING ════════════════════════

async def log_action(bot: Bot, text: str) -> None:
    """Send a log message to the LOG_CHANNEL_ID (if configured).

    Also logs to Python logger regardless.
    """
    logger.info("ACTION: %s", text)

    if not LOG_CHANNEL_ID:
        return

    try:
        await bot.send_message(
            chat_id=LOG_CHANNEL_ID,
            text=f"📝 <b>Log</b>\n\n{text}",
            parse_mode="HTML",
        )
    except Exception as e:
        logger.warning("Failed to send log to channel: %s", e)


# ════════════════════════ FORMATTING ════════════════════════

async def format_price(amount: float) -> str:
    """Format a price with the dynamic currency from settings.

    Example: 'Rs 1,500.00' or '$ 29.99'
    """
    currency = await get_setting("currency", "Rs")
    if amount == int(amount):
        formatted = f"{int(amount):,}"
    else:
        formatted = f"{amount:,.2f}"
    return f"{currency} {formatted}"


def format_stock(stock: int) -> str:
    """Format stock display text.

    -1 = unlimited, 0 = out of stock, >0 = X available.
    """
    if stock == -1:
        return "♾️ Unlimited"
    if stock == 0:
        return "🔴 Out of Stock"
    return f"✅ {stock} available"


def html_escape(text: str) -> str:
    """Escape HTML special characters in user input."""
    return escape(str(text))


def status_emoji(status: str) -> str:
    """Get emoji for order/ticket status."""
    mapping = {
        "pending": "🟡",
        "confirmed": "🟢",
        "processing": "🔵",
        "shipped": "📦",
        "delivered": "✅",
        "cancelled": "🔴",
        "paid": "🟢",
        "unpaid": "🟡",
        "rejected": "🔴",
        "approved": "🟢",
        "open": "🟢",
        "closed": "⚪",
    }
    return mapping.get(status, "⚪")


def separator() -> str:
    """Return a consistent visual separator line."""
    return "━━━━━━━━━━━━━━━━━━━"
