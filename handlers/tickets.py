"""NanoStore ticket handlers — user create/view/reply + admin list/view/reply/close."""

import logging
from telegram import Update, InlineKeyboardButton as Btn, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import ADMIN_ID
from database import (
    create_ticket,
    get_ticket,
    get_user_tickets,
    get_open_tickets,
    get_all_tickets,
    add_ticket_reply,
    get_ticket_replies,
    close_ticket,
    reopen_ticket,
    get_user,
    add_action_log,
)
from helpers import safe_edit, html_escape, separator, log_action
from keyboards import back_kb

logger = logging.getLogger(__name__)

TICKETS_PER_PAGE: int = 10


# ══════════════════ USER: CREATE TICKET ══════════════════

async def support_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show support menu."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    tickets = await get_user_tickets(user_id, limit=5)

    text = (
        f"🎫 <b>Support Center</b>\n"
        f"{separator()}\n\n"
        "Need help? Create a ticket or view existing ones."
    )

    rows = []
    if tickets:
        for t in tickets:
            emoji = "🟢" if t["status"] == "open" else "🔴"
            rows.append([Btn(
                f"{emoji} #{t['id']} — {t['subject'][:30]}",
                callback_data=f"ticket:{t['id']}",
            )])

    rows.append([Btn("➕ New Ticket", callback_data="ticket_new")])
    rows.append([Btn("📦 My Tickets", callback_data="my_tickets")])
    rows.append([Btn("◀️ Main Menu", callback_data="main_menu")])

    await safe_edit(query, text, reply_markup=InlineKeyboardMarkup(rows))


async def ticket_new_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompt user to enter ticket subject."""
    query = update.callback_query
    await query.answer()

    context.user_data["state"] = "ticket_subject"
    text = (
        f"➕ <b>New Ticket</b>\n"
        f"{separator()}\n\n"
        "📝 Enter the subject of your issue:"
    )
    await safe_edit(query, text, reply_markup=back_kb("support"))


async def ticket_subject_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process ticket subject from text."""
    context.user_data.pop("state", None)
    subject = update.message.text.strip()

    if len(subject) < 3:
        await update.message.reply_text(
            "⚠️ Subject too short. Please enter at least 3 characters.",
            parse_mode="HTML",
        )
        context.user_data["state"] = "ticket_subject"
        return

    context.user_data["state"] = "ticket_message"
    context.user_data.setdefault("temp", {})["ticket_subject"] = subject

    await update.message.reply_text(
        f"📝 Subject: <b>{html_escape(subject)}</b>\n\n"
        "Now describe your issue in detail:",
        parse_mode="HTML",
    )


async def ticket_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process ticket message and create ticket."""
    context.user_data.pop("state", None)
    message = update.message.text.strip()
    temp = context.user_data.get("temp", {})
    subject = temp.get("ticket_subject", "No Subject")
    context.user_data.pop("temp", None)

    user_id = update.effective_user.id
    ticket_id = await create_ticket(user_id, subject, message)

    text = (
        f"✅ <b>Ticket Created!</b>\n"
        f"{separator()}\n\n"
        f"🎫 Ticket: <b>#{ticket_id}</b>\n"
        f"📌 Subject: {html_escape(subject)}\n\n"
        "Our team will respond shortly.\n"
        "You'll be notified when there's a reply."
    )

    kb = InlineKeyboardMarkup([
        [Btn(f"👁️ View Ticket #{ticket_id}", callback_data=f"ticket:{ticket_id}")],
        [Btn("◀️ Main Menu", callback_data="main_menu")],
    ])

    await update.message.reply_text(text, parse_mode="HTML", reply_markup=kb)

    # Notify admin
    user = await get_user(user_id)
    user_name = user["full_name"] if user else str(user_id)
    await log_action(
        context.bot,
        f"🎫 <b>New Ticket #{ticket_id}</b>\n"
        f"👤 User: {html_escape(user_name)} ({user_id})\n"
        f"📌 Subject: {html_escape(subject)}\n"
        f"📝 {html_escape(message[:200])}"
    )
    await add_action_log("ticket_created", user_id, f"Ticket #{ticket_id}: {subject}")


# ══════════════════ USER: VIEW TICKETS ══════════════════

async def my_tickets_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show user's tickets list."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    tickets = await get_user_tickets(user_id, limit=20)

    text = f"🎫 <b>My Tickets</b>\n{separator()}\n"

    if not tickets:
        text += "\nYou have no tickets yet."
        await safe_edit(query, text, reply_markup=back_kb("support"))
        return

    rows = []
    for t in tickets:
        emoji = "🟢" if t["status"] == "open" else "🔴"
        rows.append([Btn(
            f"{emoji} #{t['id']} — {t['subject'][:30]}",
            callback_data=f"ticket:{t['id']}",
        )])

    rows.append([Btn("◀️ Support", callback_data="support")])

    text += f"\n📊 Total: {len(tickets)} tickets"
    await safe_edit(query, text, reply_markup=InlineKeyboardMarkup(rows))


async def ticket_detail_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show ticket details with conversation."""
    query = update.callback_query
    await query.answer()

    ticket_id = int(query.data.split(":")[1])
    ticket = await get_ticket(ticket_id)

    if not ticket:
        await safe_edit(query, "❌ Ticket not found.", reply_markup=back_kb("support"))
        return

    emoji = "🟢" if ticket["status"] == "open" else "🔴"
    text = (
        f"🎫 <b>Ticket #{ticket_id}</b>\n"
        f"{separator()}\n"
        f"📌 Subject: {html_escape(ticket['subject'])}\n"
        f"{emoji} Status: <b>{ticket['status'].title()}</b>\n"
        f"📅 Created: {ticket.get('created_at', 'N/A')[:16]}\n"
        f"{separator()}\n"
    )

    # Original message
    text += f"\n👤 <b>You:</b>\n{html_escape(ticket['message'])}\n"

    # Replies
    replies = await get_ticket_replies(ticket_id)
    for r in replies:
        sender = "👤 You" if r["sender"] == "user" else "👨‍💻 Admin"
        text += f"\n{sender}:\n{html_escape(r['message'])}\n"

    rows = []
    if ticket["status"] == "open":
        rows.append([Btn("📝 Reply", callback_data=f"ticket_reply:{ticket_id}")])

    # Back button depends on who is viewing
    user_id = update.effective_user.id
    if user_id == ADMIN_ID:
        rows.append([Btn("◀️ Back", callback_data="adm_tickets")])
    else:
        rows.append([Btn("◀️ My Tickets", callback_data="my_tickets")])

    await safe_edit(query, text, reply_markup=InlineKeyboardMarkup(rows))


async def ticket_reply_prompt_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompt user to type reply."""
    query = update.callback_query
    await query.answer()

    ticket_id = int(query.data.split(":")[1])
    context.user_data["state"] = f"ticket_reply:{ticket_id}"

    text = (
        f"📝 <b>Reply to Ticket #{ticket_id}</b>\n"
        f"{separator()}\n\n"
        "Type your reply message:"
    )
    await safe_edit(query, text, reply_markup=back_kb(f"ticket:{ticket_id}"))


async def ticket_reply_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process ticket reply from text."""
    state = context.user_data.get("state", "")
    ticket_id = int(state.split(":")[1])
    context.user_data.pop("state", None)

    message = update.message.text.strip()
    user_id = update.effective_user.id
    sender = "admin" if user_id == ADMIN_ID else "user"

    await add_ticket_reply(ticket_id, sender, message)

    ticket = await get_ticket(ticket_id)

    text = (
        f"✅ <b>Reply Sent!</b>\n"
        f"{separator()}\n\n"
        f"🎫 Ticket: #{ticket_id}"
    )

    kb = InlineKeyboardMarkup([
        [Btn(f"👁️ View Ticket #{ticket_id}", callback_data=f"ticket:{ticket_id}")],
    ])

    await update.message.reply_text(text, parse_mode="HTML", reply_markup=kb)

    # Notify other party
    if sender == "user" and ticket:
        await log_action(
            context.bot,
            f"💬 <b>Ticket #{ticket_id} Reply</b>\n"
            f"👤 User: {user_id}\n"
            f"📝 {html_escape(message[:200])}"
        )
    elif sender == "admin" and ticket:
        try:
            await context.bot.send_message(
                chat_id=ticket["user_id"],
                text=(
                    f"💬 <b>New Reply on Ticket #{ticket_id}</b>\n"
                    f"{separator()}\n\n"
                    f"👨‍💻 Admin:\n{html_escape(message[:500])}\n\n"
                    "Tap below to view full conversation."
                ),
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [Btn(f"👁️ View Ticket", callback_data=f"ticket:{ticket_id}")],
                ]),
            )
        except Exception as e:
            logger.warning("Failed to notify user about ticket reply: %s", e)


# ══════════════════ ADMIN: TICKETS ══════════════════

async def admin_tickets_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all open tickets for admin."""
    query = update.callback_query
    await query.answer()

    if update.effective_user.id != ADMIN_ID:
        return

    tickets = await get_open_tickets(limit=20)

    text = f"🎫 <b>Support Tickets</b>\n{separator()}\n\n🟢 {len(tickets)} open tickets"

    rows = []
    for t in tickets:
        user = await get_user(t["user_id"])
        uname = user["full_name"][:15] if user else str(t["user_id"])
        rows.append([Btn(
            f"🟢 #{t['id']} — {uname}: {t['subject'][:20]}",
            callback_data=f"adm_ticket:{t['id']}",
        )])

    rows.append([Btn("📜 All Tickets", callback_data="adm_tickets_all")])
    rows.append([Btn("◀️ Admin Panel", callback_data="admin")])

    await safe_edit(query, text, reply_markup=InlineKeyboardMarkup(rows))


async def admin_tickets_all_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all tickets (open + closed)."""
    query = update.callback_query
    await query.answer()

    if update.effective_user.id != ADMIN_ID:
        return

    tickets = await get_all_tickets(limit=30)

    text = f"🎫 <b>All Tickets</b>\n{separator()}\n\n📊 Total: {len(tickets)} tickets"

    rows = []
    for t in tickets:
        emoji = "🟢" if t["status"] == "open" else "🔴"
        rows.append([Btn(
            f"{emoji} #{t['id']} — {t['subject'][:25]}",
            callback_data=f"adm_ticket:{t['id']}",
        )])

    rows.append([Btn("◀️ Tickets", callback_data="adm_tickets")])

    await safe_edit(query, text, reply_markup=InlineKeyboardMarkup(rows))


async def admin_ticket_detail_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """View ticket details for admin."""
    query = update.callback_query
    await query.answer()

    if update.effective_user.id != ADMIN_ID:
        return

    ticket_id = int(query.data.split(":")[1])
    ticket = await get_ticket(ticket_id)

    if not ticket:
        await safe_edit(query, "❌ Ticket not found.", reply_markup=back_kb("adm_tickets"))
        return

    user = await get_user(ticket["user_id"])
    user_name = user["full_name"] if user else str(ticket["user_id"])
    emoji = "🟢" if ticket["status"] == "open" else "🔴"

    text = (
        f"🎫 <b>Ticket #{ticket_id}</b>\n"
        f"{separator()}\n"
        f"👤 User: {html_escape(user_name)} ({ticket['user_id']})\n"
        f"📌 Subject: {html_escape(ticket['subject'])}\n"
        f"{emoji} Status: <b>{ticket['status'].title()}</b>\n"
        f"📅 Created: {ticket.get('created_at', 'N/A')[:16]}\n"
        f"{separator()}\n"
    )

    # Original message
    text += f"\n👤 <b>{html_escape(user_name)}:</b>\n{html_escape(ticket['message'])}\n"

    # Replies
    replies = await get_ticket_replies(ticket_id)
    for r in replies:
        sender_label = "👨‍💻 Admin" if r["sender"] == "admin" else f"👤 {html_escape(user_name)}"
        text += f"\n{sender_label}:\n{html_escape(r['message'])}\n"

    rows = []
    if ticket["status"] == "open":
        rows.append([
            Btn("📝 Reply", callback_data=f"ticket_reply:{ticket_id}"),
            Btn("🔒 Close", callback_data=f"adm_ticket_close:{ticket_id}"),
        ])
    else:
        rows.append([Btn("🔓 Reopen", callback_data=f"adm_ticket_reopen:{ticket_id}")])

    rows.append([Btn("◀️ Tickets", callback_data="adm_tickets")])

    await safe_edit(query, text, reply_markup=InlineKeyboardMarkup(rows))


async def admin_ticket_close_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Close a ticket."""
    query = update.callback_query
    await query.answer()

    if update.effective_user.id != ADMIN_ID:
        return

    ticket_id = int(query.data.split(":")[1])
    await close_ticket(ticket_id)
    await query.answer(f"🔒 Ticket #{ticket_id} closed!", show_alert=True)

    ticket = await get_ticket(ticket_id)
    if ticket:
        try:
            await context.bot.send_message(
                chat_id=ticket["user_id"],
                text=(
                    f"🔒 <b>Ticket #{ticket_id} Closed</b>\n"
                    f"{separator()}\n\n"
                    f"Subject: {html_escape(ticket['subject'])}\n\n"
                    "If you need more help, create a new ticket."
                ),
                parse_mode="HTML",
            )
        except Exception:
            pass

    await add_action_log("ticket_closed", ADMIN_ID, f"Ticket #{ticket_id}")

    # Refresh ticket list
    tickets = await get_open_tickets(limit=20)
    text = f"🎫 <b>Support Tickets</b>\n{separator()}\n\n🟢 {len(tickets)} open tickets"
    rows = []
    for t in tickets:
        u = await get_user(t["user_id"])
        uname = u["full_name"][:15] if u else str(t["user_id"])
        rows.append([Btn(
            f"🟢 #{t['id']} — {uname}: {t['subject'][:20]}",
            callback_data=f"adm_ticket:{t['id']}",
        )])
    rows.append([Btn("◀️ Admin Panel", callback_data="admin")])
    await safe_edit(query, text, reply_markup=InlineKeyboardMarkup(rows))


async def admin_ticket_reopen_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reopen a closed ticket."""
    query = update.callback_query
    await query.answer()

    if update.effective_user.id != ADMIN_ID:
        return

    ticket_id = int(query.data.split(":")[1])
    await reopen_ticket(ticket_id)
    await query.answer(f"🔓 Ticket #{ticket_id} reopened!", show_alert=True)
    await add_action_log("ticket_reopened", ADMIN_ID, f"Ticket #{ticket_id}")

    # Refresh detail
    ticket = await get_ticket(ticket_id)
    if ticket:
        # Re-trigger detail view
        query.data = f"adm_ticket:{ticket_id}"
        await admin_ticket_detail_handler(update, context)
