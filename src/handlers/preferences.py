"""NanoStore user preferences handler — currency selection, settings."""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from database import (
    get_user_currency,
    set_user_currency,
)
from utils import safe_edit, separator, get_currency_display
from utils import user_preferences_kb, currency_selection_kb

logger = logging.getLogger(__name__)


async def user_preferences_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show user preferences screen."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    
    # Get current currency
    current_currency = await get_user_currency(user_id)
    currency_display = get_currency_display(current_currency)
    
    text = (
        f"⚙️ <b>My Preferences</b>\n"
        f"{separator()}\n\n"
        f"💱 Currency:  <b>{currency_display}</b>\n\n"
        f"<i>All prices will be shown in your selected currency.</i>"
    )
    
    await safe_edit(query, text, reply_markup=user_preferences_kb(currency_display))


async def change_currency_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show currency selection screen."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    
    # Get current currency
    current_currency = await get_user_currency(user_id)
    
    text = (
        f"💱 <b>Select Currency</b>\n"
        f"{separator()}\n\n"
        f"Choose your preferred currency:\n\n"
        f"<i>All prices will be converted to your selected currency using live exchange rates.</i>"
    )
    
    await safe_edit(query, text, reply_markup=currency_selection_kb(current_currency))


async def set_currency_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set user's preferred currency."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    
    # Extract currency code from callback data (format: set_currency:USD)
    currency_code = query.data.split(":", 1)[1]
    
    # Update user currency
    await set_user_currency(user_id, currency_code)
    
    # Show confirmation
    await query.answer(f"✅ Currency changed to {currency_code}", show_alert=True)
    
    # Return to preferences
    await user_preferences_handler(update, context)
