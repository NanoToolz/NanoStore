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

    # Notify user if possible
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

    # Send error to log channel if configured
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

    # Catalog: specific patterns BEFORE general
    app.add_handler(CallbackQueryHandler(shop_handler, pattern=r"^shop$"))
    app.add_handler(CallbackQueryHandler(category_page_handler, pattern=r"^cat:\d+:p:\d+$"))
    app.add_handler(CallbackQueryHandler(category_handler, pattern=r"^cat:\d+$"))
    app.add_handler(CallbackQueryHandler(product_faq_handler, pattern=r"^prod_faq:\d+$"))
    app.add_handler(CallbackQueryHandler(product_media_handler, pattern=r"^prod_media:\d+:\w+$"))
    app.add_handler(CallbackQueryHandler(product_detail_handler, pattern=r"^prod:\d+$"))
    app.add_handler(CallbackQueryHandler(add_to_cart_handler, pattern=r"^add:\d+$"))

    # ---- ERROR HANDLER ----
    app.add_error_handler(error_handler)

    logger.info("All handlers registered.")


def main() -> None:
    """Start the bot."""
    # Configure logging
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
