"""NanoStore wallet handlers — wallet balance, top-up, history."""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_ID
from database import (
    get_user_balance,
    get_setting,
    create_topup,
    get_user_topups,
    update_topup,
    get_payment_methods,
    get_payment_method,
    add_action_log,
)
from utils import safe_edit, html_escape, separator, status_emoji
from utils import (
    wallet_kb,
    wallet_topup_amounts_kb,
    wallet_pay_methods_kb,
    back_kb,
)

logger = logging.getLogger(__name__)


# ════════════════════════ WALLET MAIN ════════════════════════

async def wallet_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show wallet balance and options.
    
    Uses render_screen with wallet_image_id.
    """
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    balance = await get_user_balance(user_id)
    currency = await get_setting("currency", "Rs")
    bal_display = int(balance) if balance == int(balance) else f"{balance:.2f}"

    text = (
        f"💳 <b>My Wallet</b>\n"
        f"{separator()}\n\n"
        f"💰 Balance: <b>{currency} {bal_display}</b>\n\n"
        "Use your wallet to pay for orders or top-up anytime."
    )
    
    # Use render_screen with wallet_image_id
    from utils import render_screen
    await render_screen(
        query=query,
        bot=context.bot,
        chat_id=query.message.chat_id,
        text=text,
        reply_markup=wallet_kb(),
        image_setting_key="wallet_image_id"
    )


# ════════════════════════ TOP-UP ════════════════════════

async def wallet_topup_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show top-up amount selection."""
    query = update.callback_query
    await query.answer()

    enabled = await get_setting("topup_enabled", "on")
    if enabled.lower() != "on":
        await query.answer("⚠️ Top-up is currently disabled.", show_alert=True)
        return

    currency = await get_setting("currency", "Rs")
    min_amt = float(await get_setting("topup_min_amount", "100"))
    max_amt = float(await get_setting("topup_max_amount", "10000"))

    text = (
        f"💰 <b>Top-Up Wallet</b>\n"
        f"{separator()}\n\n"
        f"Select amount to top-up:\n"
        f"Min: {currency} {int(min_amt)} | Max: {currency} {int(max_amt)}"
    )
    await safe_edit(query, text, reply_markup=wallet_topup_amounts_kb(min_amt, max_amt, currency))


async def wallet_amt_preset_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle preset amount selection."""
    query = update.callback_query
    await query.answer()

    amount = float(query.data.split(":")[1])
    context.user_data["wallet_topup_amount"] = amount

    methods = await get_payment_methods()
    if not methods:
        await query.answer("⚠️ No payment methods available.", show_alert=True)
        return

    currency = await get_setting("currency", "Rs")
    amt_display = int(amount) if amount == int(amount) else amount

    text = (
        f"💳 <b>Top-Up: {currency} {amt_display}</b>\n"
        f"{separator()}\n\n"
        "Select payment method:"
    )
    await safe_edit(query, text, reply_markup=wallet_pay_methods_kb(methods))


async def wallet_amt_custom_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompt for custom amount."""
    query = update.callback_query
    await query.answer()

    context.user_data["state"] = "wallet_topup_amount"
    currency = await get_setting("currency", "Rs")
    min_amt = float(await get_setting("topup_min_amount", "100"))
    max_amt = float(await get_setting("topup_max_amount", "10000"))

    text = (
        f"✏️ <b>Custom Amount</b>\n"
        f"{separator()}\n\n"
        f"Enter amount ({currency} {int(min_amt)} - {int(max_amt)}):"
    )
    await safe_edit(query, text, reply_markup=back_kb("wallet_topup"))


async def wallet_amount_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process custom amount from text."""
    context.user_data.pop("state", None)

    try:
        amount = float(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("❌ Invalid amount. Please enter a number.", parse_mode="HTML")
        return

    min_amt = float(await get_setting("topup_min_amount", "100"))
    max_amt = float(await get_setting("topup_max_amount", "10000"))
    currency = await get_setting("currency", "Rs")

    if amount < min_amt or amount > max_amt:
        await update.message.reply_text(
            f"⚠️ Amount must be between {currency} {int(min_amt)} and {int(max_amt)}.",
            parse_mode="HTML"
        )
        return

    context.user_data["wallet_topup_amount"] = amount
    methods = await get_payment_methods()

    if not methods:
        await update.message.reply_text("⚠️ No payment methods available.", parse_mode="HTML")
        return

    amt_display = int(amount) if amount == int(amount) else amount
    text = (
        f"💳 <b>Top-Up: {currency} {amt_display}</b>\n"
        f"{separator()}\n\n"
        "Select payment method:"
    )
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=wallet_pay_methods_kb(methods))


# ════════════════════════ PAYMENT METHOD ════════════════════════

async def wallet_pay_method_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show payment details and prompt for proof."""
    query = update.callback_query
    await query.answer()

    method_id = int(query.data.split(":")[1])
    amount = context.user_data.get("wallet_topup_amount")

    if not amount:
        await query.answer("⚠️ Amount not set.", show_alert=True)
        return

    method = await get_payment_method(method_id)
    if not method:
        await query.answer("❌ Payment method not found.", show_alert=True)
        return

    user_id = update.effective_user.id
    topup_id = await create_topup(user_id, amount, method_id)
    context.user_data["wallet_topup_id"] = topup_id

    currency = await get_setting("currency", "Rs")
    amt_display = int(amount) if amount == int(amount) else amount

    text = (
        f"💳 <b>{html_escape(method['emoji'])} {html_escape(method['name'])}</b>\n"
        f"{separator()}\n"
        f"📋 <b>Payment Details:</b>\n"
        f"{html_escape(method['details'])}\n\n"
        f"💰 Amount: <b>{currency} {amt_display}</b>\n"
        f"🆔 Reference: <b>#TOPUP{topup_id}</b>\n"
        f"{separator()}\n"
        f"📸 <b>Send your payment screenshot now.</b>"
    )

    context.user_data["state"] = f"wallet_proof:{topup_id}"
    await safe_edit(query, text, reply_markup=back_kb("wallet"))


# ════════════════════════ PROOF UPLOAD ════════════════════════

async def wallet_proof_photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process wallet top-up proof photo."""
    state = context.user_data.get("state", "")
    if not state.startswith("wallet_proof:"):
        return

    topup_id = int(state.split(":")[1])
    context.user_data.pop("state", None)
    context.user_data.pop("wallet_topup_amount", None)
    context.user_data.pop("wallet_topup_id", None)

    photo = update.message.photo[-1]
    file_id = photo.file_id
    user_id = update.effective_user.id

    await update_topup(topup_id, proof_file_id=file_id)

    currency = await get_setting("currency", "Rs")
    from database import get_topup
    topup = await get_topup(topup_id)
    amt_display = int(topup["amount"]) if topup["amount"] == int(topup["amount"]) else topup["amount"]

    text = (
        f"✅ <b>Top-Up Proof Submitted!</b>\n"
        f"{separator()}\n\n"
        f"🆔 Top-Up ID: <b>#{topup_id}</b>\n"
        f"💰 Amount: <b>{currency} {amt_display}</b>\n\n"
        "⏳ Your top-up is under review.\n"
        "You'll be notified once approved.\n\n"
        "Check status in 💳 My Wallet → History."
    )

    from telegram import InlineKeyboardButton as Btn, InlineKeyboardMarkup
    kb = InlineKeyboardMarkup([
        [Btn("💳 My Wallet", callback_data="wallet")],
        [Btn("◀️ Main Menu", callback_data="main_menu")],
    ])

    await update.message.reply_text(text, parse_mode="HTML", reply_markup=kb)

    # Notify admin
    admin_text = (
        f"💳 <b>New Wallet Top-Up!</b>\n"
        f"{separator()}\n\n"
        f"🆔 Top-Up: #{topup_id}\n"
        f"👤 User: {user_id}\n"
        f"💰 Amount: {currency} {amt_display}\n\n"
        "Review in Admin → Top-Ups"
    )
    try:
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=file_id,
            caption=admin_text,
            parse_mode="HTML",
        )
    except Exception as e:
        logger.warning("Failed to notify admin about topup: %s", e)

    await add_action_log("topup_submitted", user_id, f"Top-Up #{topup_id}, Amount: {amt_display}")


# ════════════════════════ HISTORY ════════════════════════

async def wallet_history_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show wallet top-up history."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    topups = await get_user_topups(user_id, limit=10)
    currency = await get_setting("currency", "Rs")

    text = f"📜 <b>Top-Up History</b>\n{separator()}\n"

    if not topups:
        text += "\nNo top-up records yet."
    else:
        for t in topups:
            amt = int(t["amount"]) if t["amount"] == int(t["amount"]) else t["amount"]
            emoji = status_emoji(t["status"])
            date = t["created_at"][:10] if t.get("created_at") else "N/A"
            text += f"\n{emoji} #{t['id']} — {currency} {amt} — {t['status'].title()} ({date})"
            if t.get("admin_note"):
                text += f"\n   Note: {html_escape(t['admin_note'])}"

    await safe_edit(query, text, reply_markup=back_kb("wallet"))
