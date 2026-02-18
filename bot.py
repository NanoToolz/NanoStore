import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from products import products, get_categories, get_products_by_category, get_product_by_id, search_products

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


def main_menu_keyboard():
    return ReplyKeyboardMarkup(
        [["📚 Browse Products", "🔍 Search"], ["🛒 My Cart", "ℹ️ Help"]],
        resize_keyboard=True,
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.setdefault("cart", [])
    await update.message.reply_text(
        "🛍️ *Welcome to NanoStore!*\n\n"
        "Your one-stop shop for premium digital products.\n"
        "eBooks, Templates, Courses, Software & more!\n\n"
        "Choose an option below to get started:",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(),
    )


async def browse_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    categories = get_categories()
    emoji_map = {"ebooks": "📚", "templates": "🎨", "courses": "🎓", "software": "💻"}
    keyboard = []
    for cat in categories:
        emoji = emoji_map.get(cat, "📦")
        keyboard.append([InlineKeyboardButton(f"{emoji} {cat.title()}", callback_data=f"cat_{cat}")])
    keyboard.append([InlineKeyboardButton("🛍️ View All", callback_data="cat_all")])
    await update.message.reply_text(
        "📂 *Choose a category:*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def category_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category = query.data.replace("cat_", "")
    prods = products if category == "all" else get_products_by_category(category)
    title = "All Products" if category == "all" else category.title()
    if not prods:
        await query.edit_message_text("No products found in this category.")
        return
    keyboard = []
    for p in prods:
        keyboard.append(
            [InlineKeyboardButton(f"{p['emoji']} {p['name']} — ${p['price']:.2f}", callback_data=f"prod_{p['id']}")]
        )
    keyboard.append([InlineKeyboardButton("⬅️ Back to Categories", callback_data="back_categories")])
    await query.edit_message_text(
        f"📂 *{title}*\n\nSelect a product for details:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def product_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    product_id = int(query.data.replace("prod_", ""))
    product = get_product_by_id(product_id)
    if not product:
        await query.edit_message_text("Product not found.")
        return
    text = (
        f"{product['emoji']} *{product['name']}*\n\n"
        f"📂 Category: {product['category'].title()}\n"
        f"💰 Price: *${product['price']:.2f}*\n\n"
        f"📝 {product['description']}"
    )
    keyboard = [
        [InlineKeyboardButton("🛒 Add to Cart", callback_data=f"add_{product['id']}")],
        [InlineKeyboardButton(f"⬅️ Back to {product['category'].title()}", callback_data=f"cat_{product['category']}")],
    ]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))


async def add_to_cart_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    product_id = int(query.data.replace("add_", ""))
    product = get_product_by_id(product_id)
    if not product:
        await query.answer("Product not found!", show_alert=True)
        return
    cart = context.user_data.setdefault("cart", [])
    existing = next((item for item in cart if item["id"] == product_id), None)
    if existing:
        existing["qty"] += 1
    else:
        cart.append({**product, "qty": 1})
    total_items = sum(item["qty"] for item in cart)
    await query.answer(f"✅ {product['name']} added! Cart: {total_items} item(s)", show_alert=True)


async def view_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cart = context.user_data.get("cart", [])
    if not cart:
        await update.message.reply_text(
            "🛒 Your cart is empty!\n\nBrowse products to add items.", reply_markup=main_menu_keyboard()
        )
        return
    text = "🛒 *Your Cart:*\n\n"
    total = 0
    keyboard = []
    for item in cart:
        subtotal = item["price"] * item["qty"]
        total += subtotal
        text += f"{item['emoji']} *{item['name']}*\n"
        text += f"   ${item['price']:.2f} x {item['qty']} = ${subtotal:.2f}\n\n"
        keyboard.append([InlineKeyboardButton(f"❌ Remove {item['name']}", callback_data=f"remove_{item['id']}")])
    text += f"━━━━━━━━━━━━━━━\n💰 *Total: ${total:.2f}*"
    keyboard.append([InlineKeyboardButton("🗑️ Clear Cart", callback_data="clear_cart")])
    keyboard.append([InlineKeyboardButton("💳 Checkout", callback_data="checkout")])
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))


async def remove_from_cart_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    product_id = int(query.data.replace("remove_", ""))
    cart = context.user_data.get("cart", [])
    context.user_data["cart"] = [item for item in cart if item["id"] != product_id]
    cart = context.user_data["cart"]
    if not cart:
        await query.edit_message_text("🛒 Your cart is now empty!")
        await query.answer("Item removed!")
        return
    text = "🛒 *Your Cart:*\n\n"
    total = 0
    keyboard = []
    for item in cart:
        subtotal = item["price"] * item["qty"]
        total += subtotal
        text += f"{item['emoji']} *{item['name']}*\n"
        text += f"   ${item['price']:.2f} x {item['qty']} = ${subtotal:.2f}\n\n"
        keyboard.append([InlineKeyboardButton(f"❌ Remove {item['name']}", callback_data=f"remove_{item['id']}")])
    text += f"━━━━━━━━━━━━━━━\n💰 *Total: ${total:.2f}*"
    keyboard.append([InlineKeyboardButton("🗑️ Clear Cart", callback_data="clear_cart")])
    keyboard.append([InlineKeyboardButton("💳 Checkout", callback_data="checkout")])
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    await query.answer("Item removed!")


async def clear_cart_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    context.user_data["cart"] = []
    await query.edit_message_text("🗑️ Cart cleared!")
    await query.answer("Cart cleared!")


async def checkout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    cart = context.user_data.get("cart", [])
    if not cart:
        await query.answer("Cart is empty!", show_alert=True)
        return
    total = sum(item["price"] * item["qty"] for item in cart)
    text = (
        "💳 *Checkout*\n\n"
        f"Total: *${total:.2f}*\n\n"
        "To complete your purchase, contact the store owner.\n\n"
        "📩 Payment methods:\n"
        "• PayPal\n"
        "• Crypto (BTC/ETH)\n"
        "• Bank Transfer\n\n"
        "_Thank you for shopping at NanoStore!_ 🛍️"
    )
    context.user_data["cart"] = []
    await query.edit_message_text(text, parse_mode="Markdown")
    await query.answer("Order placed! ✅", show_alert=True)


async def search_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 *Search Products*\n\nType the product name or keyword:", parse_mode="Markdown")
    context.user_data["awaiting_search"] = True


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_search"):
        context.user_data["awaiting_search"] = False
        query_text = update.message.text
        results = search_products(query_text)
        if not results:
            await update.message.reply_text(f"No products found for '{query_text}'.\nTry a different keyword!")
            return
        keyboard = []
        for p in results:
            keyboard.append(
                [InlineKeyboardButton(f"{p['emoji']} {p['name']} — ${p['price']:.2f}", callback_data=f"prod_{p['id']}")]
            )
        await update.message.reply_text(
            f"🔍 *Results for '{query_text}':*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ *NanoStore Bot Help*\n\n"
        "📚 *Browse Products* — View by category\n"
        "🔍 *Search* — Find products by keyword\n"
        "🛒 *My Cart* — View your shopping cart\n\n"
        "*Commands:*\n"
        "/start — Restart the bot\n"
        "/help — Show this help\n"
        "/products — Browse products\n"
        "/cart — View cart",
        parse_mode="Markdown",
    )


async def back_categories_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    categories = get_categories()
    emoji_map = {"ebooks": "📚", "templates": "🎨", "courses": "🎓", "software": "💻"}
    keyboard = []
    for cat in categories:
        emoji = emoji_map.get(cat, "📦")
        keyboard.append([InlineKeyboardButton(f"{emoji} {cat.title()}", callback_data=f"cat_{cat}")])
    keyboard.append([InlineKeyboardButton("🛍️ View All", callback_data="cat_all")])
    await query.edit_message_text(
        "📂 *Choose a category:*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard)
    )


def main():
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not set! Create a .env file with your BOT_TOKEN.")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("products", browse_products))
    app.add_handler(CommandHandler("cart", view_cart))

    # Callback query handlers
    app.add_handler(CallbackQueryHandler(category_callback, pattern=r"^cat_"))
    app.add_handler(CallbackQueryHandler(product_callback, pattern=r"^prod_"))
    app.add_handler(CallbackQueryHandler(add_to_cart_callback, pattern=r"^add_"))
    app.add_handler(CallbackQueryHandler(remove_from_cart_callback, pattern=r"^remove_"))
    app.add_handler(CallbackQueryHandler(clear_cart_callback, pattern=r"^clear_cart$"))
    app.add_handler(CallbackQueryHandler(checkout_callback, pattern=r"^checkout$"))
    app.add_handler(CallbackQueryHandler(back_categories_callback, pattern=r"^back_categories$"))

    # Reply keyboard & text handlers
    app.add_handler(MessageHandler(filters.Regex("^📚 Browse Products$"), browse_products))
    app.add_handler(MessageHandler(filters.Regex("^🔍 Search$"), search_handler))
    app.add_handler(MessageHandler(filters.Regex("^🛒 My Cart$"), view_cart))
    app.add_handler(MessageHandler(filters.Regex("^ℹ️ Help$"), help_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("🤖 NanoStore Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
