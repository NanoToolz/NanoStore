from telegram import Update
from telegram.ext import ContextTypes
from database import get_categories, get_products_by_category, get_product, is_banned
from keyboards import categories_kb, products_kb, product_detail_kb, back_kb


async def shop_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if await is_banned(update.effective_user.id):
        await query.edit_message_text("\u26d4 You have been banned.")
        return

    cats = await get_categories()
    if not cats:
        await query.edit_message_text(
            "\ud83d\udcc2 No categories available yet.\nCheck back later!",
            reply_markup=back_kb("main_menu")
        )
        return

    await query.edit_message_text(
        "\ud83d\udcc2 *Choose a category:*",
        parse_mode="Markdown",
        reply_markup=categories_kb(cats)
    )


async def category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    cat_id = int(query.data.replace("cat_", ""))
    prods = await get_products_by_category(cat_id)

    if not prods:
        await query.edit_message_text(
            "\ud83d\udce6 No products in this category yet.",
            reply_markup=back_kb("shop")
        )
        return

    await query.edit_message_text(
        "\ud83d\udce6 *Select a product:*",
        parse_mode="Markdown",
        reply_markup=products_kb(prods, cat_id)
    )


async def product_detail_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    prod_id = int(query.data.replace("prod_", ""))
    p = await get_product(prod_id)

    if not p:
        await query.edit_message_text("Product not found.", reply_markup=back_kb("shop"))
        return

    text = (
        f"*{p['name']}*\n\n"
        f"\ud83d\udcdd {p['description']}\n\n"
        f"\ud83d\udcb0 Price: *${p['price']:.2f}*"
    )

    if p["image_id"]:
        try:
            await query.message.delete()
            await query.message.chat.send_photo(
                photo=p["image_id"],
                caption=text,
                parse_mode="Markdown",
                reply_markup=product_detail_kb(prod_id, p["category_id"])
            )
            return
        except Exception:
            pass

    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=product_detail_kb(prod_id, p["category_id"])
    )
