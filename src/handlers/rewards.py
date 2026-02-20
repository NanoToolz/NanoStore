"""NanoStore daily spin handler — spin wheel for points once per day."""

import logging
import random
from telegram import Update
from telegram.ext import ContextTypes
from database import (
    get_setting,
    can_spin,
    get_next_spin_time,
    record_spin,
    get_user_points,
    add_action_log,
)
from utils import safe_edit, html_escape, separator
from utils import back_kb
from telegram import InlineKeyboardButton as Btn, InlineKeyboardMarkup

logger = logging.getLogger(__name__)


def _get_spin_reward() -> tuple[int, str]:
    """
    Generate random spin reward with rarity tiers.
    
    Returns:
        (points, rarity_name)
    
    Tiers:
    - Common (60%): 50-200 pts
    - Rare (25%): 201-500 pts
    - Epic (12%): 501-1000 pts
    - Legendary (3%): 1001-2000 pts
    """
    roll = random.random()
    
    if roll < 0.60:  # 60% - Common
        points = random.randint(50, 200)
        rarity = "Common"
    elif roll < 0.85:  # 25% - Rare
        points = random.randint(201, 500)
        rarity = "Rare"
    elif roll < 0.97:  # 12% - Epic
        points = random.randint(501, 1000)
        rarity = "Epic"
    else:  # 3% - Legendary
        points = random.randint(1001, 2000)
        rarity = "Legendary"
    
    return points, rarity


async def daily_spin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show daily spin page — spin or show cooldown."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    
    # Check if user can spin
    if not await can_spin(user_id):
        # Show cooldown
        time_left = await get_next_spin_time(user_id)
        current_points = await get_user_points(user_id)
        
        text = (
            f"🎰 <b>Daily Spin</b>\n"
            f"{separator()}\n\n"
            f"⏳ You already spun today!\n\n"
            f"⏰ Next spin in: <b>{time_left}</b>\n\n"
            f"💎 Your Points: <b>{current_points:,} pts</b>\n\n"
            f"<i>Come back tomorrow for another spin!</i>"
        )
        
        kb = InlineKeyboardMarkup([
            [Btn("👥 Refer & Earn More Points", callback_data="referral")],
            [Btn("◀️ Main Menu", callback_data="main_menu")],
        ])
        
        await safe_edit(query, text, reply_markup=kb)
        return
    
    # User can spin - perform spin
    points_won, rarity = _get_spin_reward()
    
    # Record spin and award points
    await record_spin(user_id, points_won)
    
    # Get new points total
    new_points = await get_user_points(user_id)
    
    # Rarity emoji
    rarity_emoji = {
        "Common": "⚪",
        "Rare": "🔵",
        "Epic": "🟣",
        "Legendary": "🟡",
    }.get(rarity, "⚪")
    
    text = (
        f"🎰 <b>Daily Spin Result!</b>\n"
        f"{separator()}\n\n"
        f"🎯 You won: <b>{points_won:,} Points!</b> 🎉\n"
        f"⭐ Rarity: <b>{rarity_emoji} {rarity}!</b>\n\n"
        f"💎 Your Points: <b>{new_points:,} pts</b>\n\n"
        f"⏳ Next Spin: <b>24 hours</b>\n\n"
        f"<i>Use points to get up to 20% off on orders!</i>"
    )
    
    kb = InlineKeyboardMarkup([
        [Btn("👥 Refer & Earn More Points", callback_data="referral")],
        [Btn("◀️ Main Menu", callback_data="main_menu")],
    ])
    
    await safe_edit(query, text, reply_markup=kb)
    
    # Log
    user = update.effective_user
    await add_action_log(
        "daily_spin",
        user_id,
        f"{html_escape(user.first_name)} won {points_won} pts ({rarity})"
    )
