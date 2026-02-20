"""Maintenance mode middleware - Block users when bot is under maintenance."""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from database import get_setting
from config import ADMIN_ID

logger = logging.getLogger(__name__)


async def check_maintenance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Check if bot is in maintenance mode.
    
    Returns:
        True if bot is available (can proceed)
        False if bot is in maintenance (action blocked)
    """
    user = update.effective_user
    if not user:
        return True
    
    # Admin bypasses maintenance
    if user.id == ADMIN_ID:
        return True
    
    # Check maintenance mode
    maintenance = await get_setting("maintenance", "off")
    if maintenance != "on":
        return True
    
    # Bot is in maintenance mode
    maintenance_text = await get_setting(
        "maintenance_text",
        "Bot is under maintenance. We are working on updates. Please wait and try again later."
    )
    
    # Send maintenance message
    if update.message:
        await update.message.reply_text(
            f"🔧 <b>Maintenance Mode</b>\n\n{maintenance_text}",
            parse_mode="HTML"
        )
    elif update.callback_query:
        await update.callback_query.answer(
            "🔧 Bot is under maintenance. Please try again later.",
            show_alert=True
        )
    
    logger.info(f"Blocked user {user.id} due to maintenance mode")
    return False
