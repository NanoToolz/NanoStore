"""NanoStore catalog handlers — shop, categories, products, FAQ, media."""

import logging
import math
from telegram import Update
from telegram.ext import ContextTypes
from database import (
    get_active_categories,
    get_category,
    get_products_by_category,
    get_product_count_in_category,
    get_product,
    get_setting,
    get_product_faqs,
    get_product_media,
    add_to_cart,
)
from helpers import safe_edit, format_stock, html_escape, separator
from keyboards import (
    categories_kb,
    products_kb,
    product_detail_kb,
    faq_kb,
    back_kb,
)

logger = logging.getLogger(__name__)

PER_PAGE: int = 20


async def shop_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show all active categories."""
    query = update.callback_query
    await query.answer()

    cats = await get_active_categories()
    text = (
        f"🏠 <b>Shop Categories</b>\n"
        f"{separator()}\n"
        f"📂 Browse our collection:"
    )

    if not cats:
        text += "\n\n🙅 No categories available yet."
        await safe_edit(query, text, reply_markup=back_kb("main_menu"))
        return

    await safe_edit(query, text, reply_markup=categories_kb(cats))


async def stock_overview_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show stock overview for all products across categories."""
    query = update.callback_query
    await query.answer()

    cats = await get_active_categories()
    if not cats:
        await safe_edit(query, "❌ No categories available.", reply_markup=back_kb("shop"))
        return

    currency = await get_setting("currency", "Rs")

    lines = ["📊 <b>Stock Overview</b>", separator(), ""]
    for cat in cats:
        cat_name = f"{cat.get('emoji', '📂')} {cat['name']}"
        products = await get_products_by_category(cat["id"], limit=200)
        if not products:
            continue
        lines.append(f"📂 <b>{html_escape(cat_name)}</b>")
        for p in products:
            stock_text = format_stock(p.get("stock", -1))
            price = p["price"]
            price_display = int(price) if price == int(price) else price
            lines.append(
                f"• {html_escape(p['name'])} — {currency} {price_display} | {stock_text}"
            )
        lines.append("")

    text = "\n".join(lines) if lines else "❌ No products found."
    await safe_edit(query, text, reply_markup=back_kb("shop"))


async def category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show products in a category (page 1)."""
    query = update.callback_query
    await query.answer()

    cat_id = int(query.data.split(":")[1])
    await _show_category_page(query, cat_id, page=1)


async def category_page_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show products in a category with pagination."""
    query = update.callback_query
    await query.answer()

    parts = query.data.split(":")
    cat_id = int(parts[1])
    page = int(parts[3])
    await _show_category_page(query, cat_id, page=page)


async def _show_category_page(query, cat_id: int, page: int = 1) -> None:
    """Internal: render category page with products."""
    cat = await get_category(cat_id)
    if not cat:
        await safe_edit(query, "❌ Category not found.", reply_markup=back_kb("shop"))
        return

    currency = await get_setting("currency", "Rs")
    total_count = await get_product_count_in_category(cat_id)
    products = await get_products_by_category(cat_id, limit=200)

    text = (
        f"📂 <b>{html_escape(cat['emoji'])} {html_escape(cat['name'])}</b>\n"
        f"📦 {total_count} products:"
    )

    if not products:
        text += "\n\n🙅 No products in this category yet."
        await safe_edit(query, text, reply_markup=back_kb("shop"))
        return

    kb = products_kb(
        products=products,
        cat_id=cat_id,
        currency=currency,
        page=page,
        per_page=PER_PAGE,
    )
    await safe_edit(query, text, reply_markup=kb)


async def product_detail_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show full product details."""
    query = update.callback_query
    await query.answer()

    product_id = int(query.data.split(":")[1])
    product = await get_product(product_id)

    if not product:
        await safe_edit(query, "❌ Product not found.", reply_markup=back_kb("shop"))
        return

    currency = await get_setting("currency", "Rs")
    cat = await get_category(product["category_id"])
    cat_name = f"{cat['emoji']} {cat['name']}" if cat else "Unknown"
    stock_text = format_stock(product["stock"])

    price = product["price"]
    price_display = int(price) if price == int(price) else price

    desc = html_escape(product["description"]) if product["description"] else "No description."

    text = (
        f"🏷️ <b>{html_escape(product['name'])}</b>\n"
        f"{separator()}\n"
        f"📝 {desc}\n\n"
        f"💰 Price: <b>{currency} {price_display}</b>\n"
        f"📊 Stock: {stock_text}\n"
        f"📂 Category: {html_escape(cat_name)}"
    )

    faqs = await get_product_faqs(product_id)
    media = await get_product_media(product_id)

    kb = product_detail_kb(
        product=product,
        has_faq=bool(faqs),
        has_media=media if media else None,
    )

    # Try sending product image if available
    if product.get("image_id"):
        try:
            try:
                await query.message.delete()
            except Exception:
                pass
            await query.message.chat.send_photo(
                photo=product["image_id"],
                caption=text,
                parse_mode="HTML",
                reply_markup=kb,
            )
            return
        except Exception as e:
            logger.warning("Product image failed for product %s: %s", product_id, e)

    await safe_edit(query, text, reply_markup=kb)


async def product_faq_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show product FAQs."""
    query = update.callback_query
    await query.answer()

    product_id = int(query.data.split(":")[1])
    product = await get_product(product_id)

    if not product:
        await safe_edit(query, "❌ Product not found.", reply_markup=back_kb("shop"))
        return

    faqs = await get_product_faqs(product_id)

    text = (
        f"❓ <b>FAQ — {html_escape(product['name'])}</b>\n"
        f"{separator()}\n"
    )

    if not faqs:
        text += "\nNo FAQs available for this product."
    else:
        for i, f in enumerate(faqs, 1):
            text += (
                f"\n<b>Q{i}: {html_escape(f['question'])}</b>\n"
                f"A: {html_escape(f['answer'])}\n"
            )

    await safe_edit(query, text, reply_markup=faq_kb(faqs, product_id))


async def product_media_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send product media files to user."""
    query = update.callback_query
    await query.answer()

    parts = query.data.split(":")
    product_id = int(parts[1])
    media_type = parts[2]

    product = await get_product(product_id)
    if not product:
        await safe_edit(query, "❌ Product not found.", reply_markup=back_kb("shop"))
        return

    media_items = await get_product_media(product_id)
    # Filter by type
    media_items = [m for m in media_items if m["media_type"] == media_type]

    if not media_items:
        await query.answer("❌ No media found.", show_alert=True)
        return

    chat = query.message.chat
    for item in media_items:
        try:
            if item["media_type"] == "video":
                await chat.send_video(video=item["file_id"])
            elif item["media_type"] == "voice":
                await chat.send_voice(voice=item["file_id"])
            elif item["media_type"] == "file":
                await chat.send_document(document=item["file_id"])
        except Exception as e:
            logger.warning("Failed to send media %s: %s", item["id"], e)


async def add_to_cart_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add product to user's cart."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    product_id = int(query.data.split(":")[1])
    product = await get_product(product_id)

    if not product:
        await query.answer("❌ Product not found.", show_alert=True)
        return

    if product["stock"] == 0:
        await query.answer("🔴 This product is out of stock.", show_alert=True)
        return

    await add_to_cart(user_id, product_id)
    await query.answer(f"✅ {product['name']} added to cart!", show_alert=True)
