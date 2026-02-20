"""NanoStore daily reward handler — claim free balance once per day."""

import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from database import (
    get_setting,
    get_user_balance,
    update_user_balance,
    add_action_log,
    get_user,
)
from utils import safe_edit, html_escape, separator, format_price, log_action
from utils import back_kb

logger = logging.getLogger(__name__)


async def _get_last_reward_time(db, user_id: int):
    """Check action_logs for user's last daily_reward claim."""
    import aiosqlite
    from database import get_db
    conn = await get_db()
    cur = await conn.execute(
        """SELECT created_at FROM action_logs
           WHERE action = 'daily_reward' AND user_id = ?
           ORDER BY created_at DESC LIMIT 1""",
        (user_id,),
    )
    row = await cur.fetchone()
    if row:
        try:
            return datetime.fromisoformat(row["created_at"])
        except Exception:
            return None
    return None


async def reward_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show daily reward page — claim or show cooldown."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    reward_amount_str = await get_setting("daily_reward", "10")
    currency = await get_setting("currency", "Rs")

    try:
        reward_amount = float(reward_amount_str)
    except ValueError:
        reward_amount = 10.0

    last_claim = await _get_last_reward_time(None, user_id)
    now = datetime.utcnow()

    if last_claim and (now - last_claim) < timedelta(hours=24):
        # Already claimed today
        next_claim = last_claim + timedelta(hours=24)
        diff = next_claim - now
        hours = int(diff.total_seconds() // 3600)
        minutes = int((diff.total_seconds() % 3600) // 60)

        balance = await get_user_balance(user_id)
        bal_display = format_price(balance, currency)

        text = (
            f"\U0001f381 <b>Daily Reward</b>\n"
            f"{separator()}\n\n"
            f"\u23f3 You already claimed your reward today!\n\n"
            f"\u23f0 Next claim in: <b>{hours}h {minutes}m</b>\n\n"
            f"\U0001f4b0 Your balance: <b>{bal_display}</b>"
        )
        await safe_edit(query, text, reply_markup=back_kb("main_menu"))
        return

    # Claim reward
    await update_user_balance(user_id, reward_amount)
    await add_action_log("daily_reward", user_id, f"Claimed {currency} {reward_amount}")

    new_balance = await get_user_balance(user_id)
    reward_display = format_price(reward_amount, currency)
    bal_display = format_price(new_balance, currency)

    text = (
        f"\U0001f381 <b>Daily Reward</b>\n"
        f"{separator()}\n\n"
        f"\u2705 <b>Reward Claimed!</b>\n\n"
        f"\U0001f4b0 You received: <b>{reward_display}</b>\n"
        f"\U0001f4b3 New balance: <b>{bal_display}</b>\n\n"
        f"Come back in 24 hours for more!"
    )
    await safe_edit(query, text, reply_markup=back_kb("main_menu"))

    # Log
    user = update.effective_user
    await log_action(
        context.bot,
        f"\U0001f381 Daily reward: <b>{html_escape(user.first_name)}</b> claimed {reward_display}",
    )
