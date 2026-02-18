from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import search_products, is_banned
from keyboards import back_kb, back_btn


async def search_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if await is_banned(update.effective_user.id):
        await query.edit_message_text("\u26d4 You are banned.")
        return

    context.user_data["awaiting_search"] = True
    await query.edit_message_text(
        "\ud83d\udd0d *Search Products*\n\nType the product name or keyword:",
        parse_mode="Markdown",
        reply_markup=back_kb("main_menu")
    )


async def search_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_search"):
        return False

    context.user_data["awaiting_search"] = False
    query_text = update.message.text.strip()

    if len(query_text) < 2:
        await update.message.reply_text(
            "\u26a0\ufe0f Search query too short. Try at least 2 characters.",
            reply_markup=back_kb("search")
        )
        return True

    results = await search_products(query_text)

    if not results:
        await update.message.reply_text(
            f"\ud83d\udd0d No results for '*{query_text}*'.\nTry a different keyword!",
            parse_mode="Markdown",
            reply_markup=back_kb("main_menu")
        )
        return True

    buttons = []
    for p in results[:15]:
        buttons.append([InlineKeyboardButton(
            f"{p['name']} \u2014 ${p['price']:.2f}",
            callback_data=f"prod_{p['id']}"
        )])
    buttons.append([back_btn("main_menu")])

    await update.message.reply_text(
        f"\ud83d\udd0d *Results for '{query_text}':*\n\nFound {len(results)} product(s):",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return True
