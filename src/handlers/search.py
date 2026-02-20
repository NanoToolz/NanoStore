"""NanoStore search handlers — search prompt + text query + results."""

import logging
from telegram import Update, InlineKeyboardButton as Btn, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import search_products, get_setting
from utils import safe_edit, html_escape, separator
from utils import back_kb

logger = logging.getLogger(__name__)

MAX_RESULTS: int = 20


async def search_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show search prompt and set state."""
    query = update.callback_query
    await query.answer()

    context.user_data["state"] = "search"

    text = (
        f"🔍 <b>Search Products</b>\n"
        f"{separator()}\n\n"
        "📝 Type a product name or keyword to search:\n\n"
        "<i>Example: template, course, eBook</i>"
    )
    await safe_edit(query, text, reply_markup=back_kb("main_menu"))


async def search_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process search text query and show results."""
    context.user_data.pop("state", None)

    query_text = update.message.text.strip()
    if not query_text:
        await update.message.reply_text(
            "⚠️ Please enter a search term.",
            parse_mode="HTML",
        )
        return

    if len(query_text) < 2:
        await update.message.reply_text(
            "⚠️ Search query too short. Please enter at least 2 characters.",
            parse_mode="HTML",
        )
        return

    results = await search_products(query_text)
    currency = await get_setting("currency", "Rs")

    if not results:
        text = (
            f"🔍 <b>Search Results</b>\n"
            f"{separator()}\n\n"
            f"🙅 No products found for \"<b>{html_escape(query_text)}</b>\"\n\n"
            "Try a different keyword."
        )
        kb = InlineKeyboardMarkup([
            [Btn("🔍 Search Again", callback_data="search")],
            [Btn("🛍️ Shop", callback_data="shop")],
            [Btn("◀️ Main Menu", callback_data="main_menu")],
        ])
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=kb)
        return

    display = results[:MAX_RESULTS]
    text = (
        f"🔍 <b>Search Results</b>\n"
        f"{separator()}\n"
        f"📦 Found <b>{len(results)}</b> result(s) for \"<b>{html_escape(query_text)}</b>\":"
    )

    rows = []
    for p in display:
        price = int(p["price"]) if p["price"] == int(p["price"]) else p["price"]
        rows.append([Btn(
            f"🏷️ {p['name']} — {currency} {price}",
            callback_data=f"prod:{p['id']}",
        )])

    if len(results) > MAX_RESULTS:
        text += f"\n\n<i>Showing first {MAX_RESULTS} of {len(results)} results.</i>"

    rows.append([Btn("🔍 Search Again", callback_data="search")])
    rows.append([Btn("◀️ Main Menu", callback_data="main_menu")])

    await update.message.reply_text(
        text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(rows)
    )
