"""NanoStore Telegram Bot — main entry point."""

import logging
import traceback
from html import escape

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from config import BOT_TOKEN, ADMIN_ID, LOG_CHANNEL_ID
from database import init_db
from handlers.start import (
    start_handler,
    main_menu_handler,
    help_handler,
    noop_handler,
    verify_join_handler,
)
from handlers.catalog import (
    shop_handler,
    category_page_handler,
    category_handler,
    product_detail_handler,
    product_faq_handler,
    product_media_handler,
    add_to_cart_handler,
)
from handlers.cart import (
    cart_handler,
    cart_inc_handler,
    cart_dec_handler,
    cart_del_handler,
    cart_clear_handler,
)
from handlers.search import (
    search_handler,
    search_text_handler,
)
from handlers.orders import (
    checkout_handler,
    apply_coupon_handler,
    coupon_text_handler,
    apply_balance_handler,
    confirm_order_handler,
    cancel_order_handler,
    pay_handler,
    pay_method_handler,
    proof_upload_handler,
    my_orders_handler,
    orders_page_handler,
    order_detail_handler,
)

logger = logging.getLogger(__name__)


async def post_init(application: Application) -> None:
    """Initialize database after application starts."""
    await init_db()
    logger.info("Bot initialized. ADMIN_ID=%s", ADMIN_ID)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Global error handler — log and notify admin."""
    logger.error("Exception while handling an update:", exc_info=context.error)

    tb_string = traceback.format_exception(
        type(context.error), context.error, context.error.__traceback__
    )
    tb_text = "".join(tb_string)

    if isinstance(update, Update):
        if update.callback_query:
            try:
                await update.callback_query.answer(
                    "⚠️ An error occurred. Please try again.", show_alert=True
                )
            except Exception:
                pass
        elif update.effective_message:
            try:
                await update.effective_message.reply_text(
                    "⚠️ An error occurred. Please try again."
                )
            except Exception:
                pass

    if LOG_CHANNEL_ID:
        error_text = (
            f"🚨 <b>Error Report</b>\n\n"
            f"<pre>{escape(tb_text[-3000:])}</pre>"
        )
        try:
            await context.bot.send_message(
                chat_id=LOG_CHANNEL_ID,
                text=error_text,
                parse_mode="HTML",
            )
        except Exception as e:
            logger.error("Failed to send error to log channel: %s", e)


# ---- TEXT / PHOTO ROUTERS ----

async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Route plain text messages based on user_data state."""
    state = context.user_data.get("state")
    if not state:
        return

    if state == "search":
        await search_text_handler(update, context)
    elif state.startswith("apply_coupon:"):
        await coupon_text_handler(update, context)
    # Future states:
    # elif state == "ticket_subject": ...
    # elif state.startswith("ticket_reply:"): ...
    # elif state.startswith("adm_"): ...


async def photo_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Route photo messages based on user_data state."""
    state = context.user_data.get("state")
    if not state:
        return

    if state.startswith("proof_upload:"):
        await proof_upload_handler(update, context)
    # Future states:
    # elif state.startswith("adm_prod_img:"): ...
    # elif state.startswith("adm_cat_img:"): ...
    # elif state.startswith("adm_prod_media:"): ...


def register_handlers(app: Application) -> None:
    """Register all handlers with correct priority ordering."""

    # ---- COMMANDS ----
    app.add_handler(CommandHandler("start", start_handler))

    # ---- CALLBACK QUERIES (most specific patterns first) ----

    # Start / Menu / Help / Noop
    app.add_handler(CallbackQueryHandler(main_menu_handler, pattern=r"^main_menu$"))
    app.add_handler(CallbackQueryHandler(help_handler, pattern=r"^help$"))
    app.add_handler(CallbackQueryHandler(noop_handler, pattern=r"^noop$"))
    app.add_handler(CallbackQueryHandler(verify_join_handler, pattern=r"^verify_join$"))

    # Catalog
    app.add_handler(CallbackQueryHandler(shop_handler, pattern=r"^shop$"))
    app.add_handler(CallbackQueryHandler(category_page_handler, pattern=r"^cat:\d+:p:\d+$"))
    app.add_handler(CallbackQueryHandler(category_handler, pattern=r"^cat:\d+$"))
    app.add_handler(CallbackQueryHandler(product_faq_handler, pattern=r"^prod_faq:\d+$"))
    app.add_handler(CallbackQueryHandler(product_media_handler, pattern=r"^prod_media:\d+:\w+$"))
    app.add_handler(CallbackQueryHandler(product_detail_handler, pattern=r"^prod:\d+$"))
    app.add_handler(CallbackQueryHandler(add_to_cart_handler, pattern=r"^add:\d+$"))

    # Cart
    app.add_handler(CallbackQueryHandler(cart_handler, pattern=r"^cart$"))
    app.add_handler(CallbackQueryHandler(cart_inc_handler, pattern=r"^cart_inc:\d+$"))
    app.add_handler(CallbackQueryHandler(cart_dec_handler, pattern=r"^cart_dec:\d+$"))
    app.add_handler(CallbackQueryHandler(cart_del_handler, pattern=r"^cart_del:\d+$"))
    app.add_handler(CallbackQueryHandler(cart_clear_handler, pattern=r"^cart_clear$"))

    # Search
    app.add_handler(CallbackQueryHandler(search_handler, pattern=r"^search$"))

    # Orders
    app.add_handler(CallbackQueryHandler(checkout_handler, pattern=r"^checkout$"))
    app.add_handler(CallbackQueryHandler(apply_coupon_handler, pattern=r"^apply_coupon:\d+$"))
    app.add_handler(CallbackQueryHandler(apply_balance_handler, pattern=r"^apply_balance:\d+$"))
    app.add_handler(CallbackQueryHandler(confirm_order_handler, pattern=r"^confirm_order:\d+$"))
    app.add_handler(CallbackQueryHandler(cancel_order_handler, pattern=r"^cancel_order:\d+$"))
    app.add_handler(CallbackQueryHandler(pay_method_handler, pattern=r"^pay_method:\d+:\d+$"))
    app.add_handler(CallbackQueryHandler(pay_handler, pattern=r"^pay:\d+$"))
    app.add_handler(CallbackQueryHandler(my_orders_handler, pattern=r"^my_orders$"))
    app.add_handler(CallbackQueryHandler(orders_page_handler, pattern=r"^orders_p:\d+$"))
    app.add_handler(CallbackQueryHandler(order_detail_handler, pattern=r"^order:\d+$"))

    # ---- TEXT & PHOTO ROUTERS ----
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
    app.add_handler(MessageHandler(filters.PHOTO, photo_router))

    # ---- ERROR HANDLER ----
    app.add_error_handler(error_handler)

    logger.info("All handlers registered.")


def main() -> None:
    """Start the bot."""
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)

    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not set! Check your .env file.")
        return

    logger.info("Starting NanoStore Bot...")

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    register_handlers(app)

    logger.info("Bot is running. Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
