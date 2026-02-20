"""NanoStore referral system handler — referral links, stats, history."""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from database import (
    get_setting,
    get_referral_stats,
    get_referral_history,
)
from utils import safe_edit, html_escape, separator
from utils import referral_kb, referral_history_kb

logger = logging.getLogger(__name__)


async def referral_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show referral program main screen."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    
    # Get bot username for referral link
    bot_info = await context.bot.get_me()
    bot_username = bot_info.username
    
    # Get referral stats
    stats = await get_referral_stats(user_id)
    total_referred = stats["total_referrals"]
    points_earned = stats["points_earned"]
    active_referrals = stats["active_referrals"]
    
    # Generate referral link
    referral_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    
    text = (
        f"👥 <b>Your Referral Program</b>\n"
        f"{separator()}\n\n"
        f"🔗 <b>Your Link:</b>\n"
        f"<code>{referral_link}</code>\n\n"
        f"📊 <b>Stats</b>\n"
        f"👥 Total Referred: <b>{total_referred} friends</b>\n"
        f"💎 Points Earned: <b>{points_earned:,} pts</b>\n"
        f"✅ Active Referrals: <b>{active_referrals}</b>\n\n"
        f"💡 <b>How it works:</b>\n"
        f"• Share your link with friends\n"
        f"• They get <b>500 pts</b> welcome bonus\n"
        f"• You get <b>1,000 pts</b> per referral!\n\n"
        f"<i>Start earning points by inviting friends!</i>"
    )
    
    await safe_edit(query, text, reply_markup=referral_kb(bot_username, user_id))


async def referral_history_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show referral history — list of referred users."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    
    # Get referral history
    referrals = await get_referral_history(user_id, limit=20)
    
    if not referrals:
        text = (
            f"📊 <b>Referral History</b>\n"
            f"{separator()}\n\n"
            f"You haven't referred anyone yet.\n\n"
            f"Share your referral link to start earning points!"
        )
    else:
        text = (
            f"📊 <b>Referral History</b>\n"
            f"{separator()}\n\n"
        )
        
        for i, ref in enumerate(referrals, 1):
            name = ref.get("full_name", "User")
            username = ref.get("username", "")
            username_display = f"@{username}" if username else "No username"
            
            # Format join date
            from datetime import datetime
            try:
                joined = datetime.fromisoformat(ref["joined_at"])
                join_date = joined.strftime("%b %d, %Y")
            except Exception:
                join_date = "Unknown"
            
            text += f"{i}. <b>{html_escape(name)}</b> ({username_display})\n"
            text += f"   Joined: {join_date}\n\n"
        
        text += f"<i>Total: {len(referrals)} referrals</i>"
    
    await safe_edit(query, text, reply_markup=referral_history_kb())
