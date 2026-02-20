"""NanoStore Telegram Bot — main entry point."""

import asyncio
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
    stock_overview_handler,
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
from handlers.rewards import (
    daily_spin_handler,
)
from handlers.referral import (
    referral_handler,
    referral_history_handler,
)
from handlers.preferences import (
    user_preferences_handler,
    change_currency_handler,
    set_currency_handler,
)
from handlers.tickets import (
    support_handler,
    ticket_new_handler,
    ticket_subject_handler,
    ticket_message_handler,
    my_tickets_handler,
    ticket_detail_handler,
    ticket_reply_prompt_handler,
    ticket_reply_text_handler,
    admin_tickets_handler,
    admin_tickets_all_handler,
    admin_ticket_detail_handler,
    admin_ticket_close_handler,
    admin_ticket_reopen_handler,
)
from handlers.wallet import (
    wallet_handler,
    wallet_topup_handler,
    wallet_amt_preset_handler,
    wallet_amt_custom_handler,
    wallet_amount_text_handler,
    wallet_pay_method_handler,
    wallet_proof_photo_handler,
    wallet_history_handler,
)
from handlers.admin import (
    admin_handler,
    back_admin_handler,
    admin_dashboard_handler,
    admin_cats_handler,
    admin_cat_add_handler,
    admin_cat_detail_handler,
    admin_cat_edit_handler,
    admin_cat_del_handler,
    admin_cat_img_handler,
    admin_prods_handler,
    admin_prod_add_handler,
    admin_prod_detail_handler,
    admin_prod_edit_handler,
    admin_prod_del_handler,
    admin_prod_img_handler,
    admin_prod_stock_handler,
    admin_prod_faq_add_handler,
    admin_prod_faq_del_handler,
    admin_prod_media_add_handler,
    admin_prod_media_del_handler,
    admin_orders_handler,
    admin_order_detail_handler,
    admin_order_status_handler,
    admin_users_handler,
    admin_user_detail_handler,
    admin_ban_handler,
    admin_unban_handler,
    admin_coupons_handler,
    admin_coupon_add_handler,
    admin_coupon_toggle_handler,
    admin_coupon_del_handler,
    admin_payments_handler,
    admin_pay_add_handler,
    admin_pay_del_handler,
    admin_proofs_handler,
    admin_proof_detail_handler,
    admin_proof_approve_handler,
    admin_proof_reject_handler,
    admin_proof_post_handler,
    admin_topups_handler,
    admin_topup_detail_handler,
    admin_topup_approve_handler,
    admin_topup_reject_handler,
    admin_settings_handler,
    admin_set_handler,
    admin_welcome_image_handler,
    admin_img_panel_handler,
    admin_img_set_handler,
    admin_img_clear_handler,
    admin_img_toggle_handler,
    admin_global_img_toggle_handler,
    admin_txt_set_handler,
    admin_txt_clear_handler,
    admin_fj_handler,
    admin_fj_add_handler,
    admin_fj_del_handler,
    admin_bulk_handler,
    admin_bulk_stock_handler,
    admin_broadcast_handler,
    admin_broadcast_confirm_handler,
    admin_text_router,
    admin_photo_router,
)
from handlers.admin_content import (
    admin_content_handler,
    admin_content_screen_handler,
    admin_content_img_handler,
    admin_content_txt_handler,
    admin_content_img_clear_handler,
    admin_content_txt_clear_handler,
)
from database import set_setting
from utils import schedule_delete

logger = logging.getLogger(__name__)


async def post_init(application: Application) -> None:
    """Initialize database after application starts and send restart notification to admin."""
    import sys
    import subprocess
    from datetime import datetime
    from database import get_setting, set_setting
    from utils import send_restart_notification
    
    await init_db()
    logger.info("Bot initialized. ADMIN_ID=%s", ADMIN_ID)
    
    # Get bot name
    bot_name = await get_setting("bot_name", "NanoStore")
    
    # Get git info
    try:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()
    except Exception:
        branch = "unknown"
    
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()
    except Exception:
        commit = "unknown"
    
    # Get Python version
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    # Get current timestamp
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Store restart timestamp
    await set_setting("last_restart_at", now)
    
    # Send restart notification to admin with auto-delete after 60s
    admin_msg = (
        "✅ <b>Bot Restarted Successfully</b>\n\n"
        f"<b>Bot:</b> {bot_name}\n"
        f"<b>Branch:</b> {branch}\n"
        f"<b>Commit:</b> <code>{commit}</code>\n"
        f"<b>Time:</b> {now}\n"
        f"<b>Python:</b> {py_version}\n"
        f"<b>DB:</b> OK\n\n"
        "<i>This message will auto-delete in 60 seconds.</i>"
    )
    
    await send_restart_notification(
        bot=application.bot,
        admin_id=ADMIN_ID,
        message=admin_msg,
        auto_delete_seconds=60
    )


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
                    "\u26a0\ufe0f An error occurred. Please try again.", show_alert=True
                )
            except Exception:
                pass
        elif update.effective_message:
            try:
                await update.effective_message.reply_text(
                    "\u26a0\ufe0f An error occurred. Please try again."
                )
            except Exception:
                pass

    if LOG_CHANNEL_ID:
        error_text = (
            f"\U0001f6a8 <b>Error Report</b>\n\n"
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


# ======== TEXT / PHOTO ROUTERS ========

async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Route plain text messages based on user_data state."""
    state = context.user_data.get("state")
    if not state:
        return

    # Admin states
    if state.startswith("adm_"):
        # Check for Screen Content Manager text input
        if state.startswith("adm_txt_wait:"):
            # Handle text input for Screen Content Manager
            text_key = state.split(":", 1)[1]
            await set_setting(text_key, update.message.text.strip())
            
            # Delete the admin prompt message if stored
            prompt_msg_id = context.user_data.pop("adm_txt_prompt_msg_id", None)
            if prompt_msg_id:
                schedule_delete(context, update.message.chat_id, prompt_msg_id, 0, "admin_prompt")
            
            # Delete the admin's text message after 7s
            schedule_delete(context, update.message.chat_id, update.message.message_id, 7, "confirmation")
            
            context.user_data.pop("state", None)
            
            # Send confirmation
            conf_msg = await update.message.reply_text(
                "✅ Text updated successfully!",
                parse_mode="HTML"
            )
            # Delete confirmation after 7s
            schedule_delete(context, conf_msg.chat_id, conf_msg.message_id, 7, "confirmation")
            return
        
        await admin_text_router(update, context)
        return

    # User states
    if state == "search":
        await search_text_handler(update, context)
    elif state.startswith("apply_coupon:"):
        await coupon_text_handler(update, context)
    elif state == "ticket_subject":
        await ticket_subject_handler(update, context)
    elif state == "ticket_message":
        await ticket_message_handler(update, context)
    elif state.startswith("ticket_reply:"):
        await ticket_reply_text_handler(update, context)
    elif state == "wallet_topup_amount":
        await wallet_amount_text_handler(update, context)


async def photo_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Route photo messages based on user_data state."""
    state = context.user_data.get("state")
    if not state:
        return

    # Admin states
    if state.startswith("adm_"):
        # Check for Screen Content Manager image upload
        if state.startswith("adm_img_wait:"):
            # Handle image upload for Screen Content Manager
            image_key = state.split(":", 1)[1]
            photo = update.message.photo[-1]
            file_id = photo.file_id
            
            await set_setting(image_key, file_id)
            
            # Don't delete the prompt message - it has the back button!
            # Just clear the stored message_id
            context.user_data.pop("adm_img_prompt_msg_id", None)
            
            # Delete the admin's uploaded photo after 7s
            schedule_delete(context, update.message.chat_id, update.message.message_id, 7, "admin_uploaded_photo")
            
            context.user_data.pop("state", None)
            
            # Send confirmation
            conf_msg = await update.message.reply_text(
                "✅ Image uploaded successfully!",
                parse_mode="HTML"
            )
            # Delete confirmation after 7s
            schedule_delete(context, conf_msg.chat_id, conf_msg.message_id, 7, "confirmation")
            return
        
        await admin_photo_router(update, context)
        return

    # User states
    if state.startswith("proof_upload:"):
        await proof_upload_handler(update, context)
    elif state.startswith("wallet_proof:"):
        await wallet_proof_photo_handler(update, context)


def register_handlers(app: Application) -> None:
    """Register all handlers with correct priority ordering."""

    # ======== COMMANDS ========
    app.add_handler(CommandHandler("start", start_handler))

    # ======== CALLBACK QUERIES ========

    # ---- Start / Menu / Help / Noop ----
    app.add_handler(CallbackQueryHandler(main_menu_handler, pattern=r"^main_menu$"))
    app.add_handler(CallbackQueryHandler(help_handler, pattern=r"^help$"))
    app.add_handler(CallbackQueryHandler(noop_handler, pattern=r"^noop$"))
    app.add_handler(CallbackQueryHandler(verify_join_handler, pattern=r"^verify_join$"))

    # ---- Catalog ----
    app.add_handler(CallbackQueryHandler(shop_handler, pattern=r"^shop$"))
    app.add_handler(CallbackQueryHandler(stock_overview_handler, pattern=r"^stock_overview$"))
    app.add_handler(CallbackQueryHandler(category_page_handler, pattern=r"^cat:\d+:p:\d+$"))
    app.add_handler(CallbackQueryHandler(category_handler, pattern=r"^cat:\d+$"))
    app.add_handler(CallbackQueryHandler(product_faq_handler, pattern=r"^prod_faq:\d+$"))
    app.add_handler(CallbackQueryHandler(product_media_handler, pattern=r"^prod_media:\d+:\w+$"))
    app.add_handler(CallbackQueryHandler(product_detail_handler, pattern=r"^prod:\d+$"))
    app.add_handler(CallbackQueryHandler(add_to_cart_handler, pattern=r"^add:\d+$"))

    # ---- Cart ----
    app.add_handler(CallbackQueryHandler(cart_handler, pattern=r"^cart$"))
    app.add_handler(CallbackQueryHandler(cart_inc_handler, pattern=r"^cart_inc:\d+$"))
    app.add_handler(CallbackQueryHandler(cart_dec_handler, pattern=r"^cart_dec:\d+$"))
    app.add_handler(CallbackQueryHandler(cart_del_handler, pattern=r"^cart_del:\d+$"))
    app.add_handler(CallbackQueryHandler(cart_clear_handler, pattern=r"^cart_clear$"))

    # ---- Search ----
    app.add_handler(CallbackQueryHandler(search_handler, pattern=r"^search$"))

    # ---- Daily Spin ----
    app.add_handler(CallbackQueryHandler(daily_spin_handler, pattern=r"^daily_spin$"))

    # ---- Referral ----
    app.add_handler(CallbackQueryHandler(referral_handler, pattern=r"^referral$"))
    app.add_handler(CallbackQueryHandler(referral_history_handler, pattern=r"^referral_history$"))

    # ---- User Preferences ----
    app.add_handler(CallbackQueryHandler(user_preferences_handler, pattern=r"^user_preferences$"))
    app.add_handler(CallbackQueryHandler(change_currency_handler, pattern=r"^change_currency$"))
    app.add_handler(CallbackQueryHandler(set_currency_handler, pattern=r"^set_currency:\w+$"))

    # ---- Orders ----
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

    # ---- Support / Tickets (User) ----
    app.add_handler(CallbackQueryHandler(support_handler, pattern=r"^support$"))
    app.add_handler(CallbackQueryHandler(ticket_new_handler, pattern=r"^ticket_new$"))
    app.add_handler(CallbackQueryHandler(my_tickets_handler, pattern=r"^my_tickets$"))
    app.add_handler(CallbackQueryHandler(ticket_reply_prompt_handler, pattern=r"^ticket_reply:\d+$"))
    app.add_handler(CallbackQueryHandler(ticket_detail_handler, pattern=r"^ticket:\d+$"))

    # ---- Wallet ----
    app.add_handler(CallbackQueryHandler(wallet_handler, pattern=r"^wallet$"))
    app.add_handler(CallbackQueryHandler(wallet_topup_handler, pattern=r"^wallet_topup$"))
    app.add_handler(CallbackQueryHandler(wallet_amt_preset_handler, pattern=r"^wallet_amt:\d+"))
    app.add_handler(CallbackQueryHandler(wallet_amt_custom_handler, pattern=r"^wallet_amt_custom$"))
    app.add_handler(CallbackQueryHandler(wallet_pay_method_handler, pattern=r"^wallet_pay:\d+$"))
    app.add_handler(CallbackQueryHandler(wallet_history_handler, pattern=r"^wallet_history$"))

    # ---- Admin Panel ----
    app.add_handler(CallbackQueryHandler(admin_handler, pattern=r"^admin$"))
    app.add_handler(CallbackQueryHandler(back_admin_handler, pattern=r"^back_admin$"))
    app.add_handler(CallbackQueryHandler(admin_dashboard_handler, pattern=r"^adm_dash$"))

    # ---- Admin: Categories ----
    app.add_handler(CallbackQueryHandler(admin_cats_handler, pattern=r"^adm_cats$"))
    app.add_handler(CallbackQueryHandler(admin_cat_add_handler, pattern=r"^adm_cat_add$"))
    app.add_handler(CallbackQueryHandler(admin_cat_edit_handler, pattern=r"^adm_cat_edit:\d+$"))
    app.add_handler(CallbackQueryHandler(admin_cat_del_handler, pattern=r"^adm_cat_del:\d+$"))
    app.add_handler(CallbackQueryHandler(admin_cat_img_handler, pattern=r"^adm_cat_img:\d+$"))
    app.add_handler(CallbackQueryHandler(admin_cat_detail_handler, pattern=r"^adm_cat:\d+$"))

    # ---- Admin: Products ----
    app.add_handler(CallbackQueryHandler(admin_prod_add_handler, pattern=r"^adm_prod_add:\d+$"))
    app.add_handler(CallbackQueryHandler(admin_prod_edit_handler, pattern=r"^adm_prod_edit:\d+:\w+$"))
    app.add_handler(CallbackQueryHandler(admin_prod_del_handler, pattern=r"^adm_prod_del:\d+$"))
    app.add_handler(CallbackQueryHandler(admin_prod_img_handler, pattern=r"^adm_prod_img:\d+$"))
    app.add_handler(CallbackQueryHandler(admin_prod_stock_handler, pattern=r"^adm_prod_stock:\d+$"))
    app.add_handler(CallbackQueryHandler(admin_prod_faq_add_handler, pattern=r"^adm_prod_faq_add:\d+$"))
    app.add_handler(CallbackQueryHandler(admin_prod_faq_del_handler, pattern=r"^adm_prod_faq_del:\d+:\d+$"))
    app.add_handler(CallbackQueryHandler(admin_prod_media_add_handler, pattern=r"^adm_prod_media_add:\d+:\w+$"))
    app.add_handler(CallbackQueryHandler(admin_prod_media_add_handler, pattern=r"^adm_prod_media_add:\d+$"))
    app.add_handler(CallbackQueryHandler(admin_prod_media_del_handler, pattern=r"^adm_prod_media_del:\d+:\d+$"))
    app.add_handler(CallbackQueryHandler(admin_prods_handler, pattern=r"^adm_prods:\d+$"))
    app.add_handler(CallbackQueryHandler(admin_prod_detail_handler, pattern=r"^adm_prod:\d+$"))

    # ---- Admin: Orders ----
    app.add_handler(CallbackQueryHandler(admin_orders_handler, pattern=r"^adm_orders$"))
    app.add_handler(CallbackQueryHandler(admin_order_status_handler, pattern=r"^adm_ord_st:\d+:\w+$"))
    app.add_handler(CallbackQueryHandler(admin_order_detail_handler, pattern=r"^adm_ord:\d+$"))

    # ---- Admin: Users ----
    app.add_handler(CallbackQueryHandler(admin_users_handler, pattern=r"^adm_users$"))
    app.add_handler(CallbackQueryHandler(admin_ban_handler, pattern=r"^adm_ban:\d+$"))
    app.add_handler(CallbackQueryHandler(admin_unban_handler, pattern=r"^adm_unban:\d+$"))
    app.add_handler(CallbackQueryHandler(admin_user_detail_handler, pattern=r"^adm_user:\d+$"))

    # ---- Admin: Coupons ----
    app.add_handler(CallbackQueryHandler(admin_coupons_handler, pattern=r"^adm_coupons$"))
    app.add_handler(CallbackQueryHandler(admin_coupon_add_handler, pattern=r"^adm_coupon_add$"))
    app.add_handler(CallbackQueryHandler(admin_coupon_toggle_handler, pattern=r"^adm_coupon_toggle:.+$"))
    app.add_handler(CallbackQueryHandler(admin_coupon_del_handler, pattern=r"^adm_coupon_del:.+$"))

    # ---- Admin: Payment Methods ----
    app.add_handler(CallbackQueryHandler(admin_payments_handler, pattern=r"^adm_payments$"))
    app.add_handler(CallbackQueryHandler(admin_pay_add_handler, pattern=r"^adm_pay_add$"))
    app.add_handler(CallbackQueryHandler(admin_pay_del_handler, pattern=r"^adm_pay_del:\d+$"))

    # ---- Admin: Proofs ----
    app.add_handler(CallbackQueryHandler(admin_proofs_handler, pattern=r"^adm_proofs$"))
    app.add_handler(CallbackQueryHandler(admin_proof_approve_handler, pattern=r"^adm_proof_ok:\d+$"))
    app.add_handler(CallbackQueryHandler(admin_proof_reject_handler, pattern=r"^adm_proof_rej:\d+$"))
    app.add_handler(CallbackQueryHandler(admin_proof_post_handler, pattern=r"^adm_proof_post:\d+$"))
    app.add_handler(CallbackQueryHandler(admin_proof_detail_handler, pattern=r"^adm_proof:\d+$"))

    # ---- Admin: Top-Ups ----
    app.add_handler(CallbackQueryHandler(admin_topups_handler, pattern=r"^adm_topups$"))
    app.add_handler(CallbackQueryHandler(admin_topup_detail_handler, pattern=r"^adm_topup:\d+$"))
    app.add_handler(CallbackQueryHandler(admin_topup_approve_handler, pattern=r"^adm_topup_approve:\d+$"))
    app.add_handler(CallbackQueryHandler(admin_topup_reject_handler, pattern=r"^adm_topup_reject:\d+$"))

    # ---- Admin: Settings ----
    app.add_handler(CallbackQueryHandler(admin_settings_handler, pattern=r"^adm_settings$"))
    app.add_handler(CallbackQueryHandler(admin_set_handler, pattern=r"^adm_set:.+$"))
    app.add_handler(CallbackQueryHandler(admin_welcome_image_handler, pattern=r"^adm_welcome_image$"))
    app.add_handler(CallbackQueryHandler(admin_img_panel_handler, pattern=r"^adm_img_panel$"))
    app.add_handler(CallbackQueryHandler(admin_img_set_handler, pattern=r"^adm_img_set:.+$"))
    app.add_handler(CallbackQueryHandler(admin_img_clear_handler, pattern=r"^adm_img_clear:.+$"))
    app.add_handler(CallbackQueryHandler(admin_img_toggle_handler, pattern=r"^adm_img_toggle$"))
    app.add_handler(CallbackQueryHandler(admin_global_img_toggle_handler, pattern=r"^adm_global_img_toggle$"))
    app.add_handler(CallbackQueryHandler(admin_txt_set_handler, pattern=r"^adm_txt_set:.+$"))
    app.add_handler(CallbackQueryHandler(admin_txt_clear_handler, pattern=r"^adm_txt_clear:.+$"))

    # ---- Admin: Force Join ----
    app.add_handler(CallbackQueryHandler(admin_fj_handler, pattern=r"^adm_fj$"))
    app.add_handler(CallbackQueryHandler(admin_fj_add_handler, pattern=r"^adm_fj_add$"))
    app.add_handler(CallbackQueryHandler(admin_fj_del_handler, pattern=r"^adm_fj_del:\d+$"))

    # ---- Admin: Bulk ----
    app.add_handler(CallbackQueryHandler(admin_bulk_handler, pattern=r"^adm_bulk$"))
    app.add_handler(CallbackQueryHandler(admin_bulk_stock_handler, pattern=r"^adm_bulk_stock$"))

    # ---- Admin: Broadcast ----
    app.add_handler(CallbackQueryHandler(admin_broadcast_handler, pattern=r"^adm_broadcast$"))
    app.add_handler(CallbackQueryHandler(admin_broadcast_confirm_handler, pattern=r"^adm_broadcast_go"))

    # ---- Admin: Tickets ----
    app.add_handler(CallbackQueryHandler(admin_tickets_handler, pattern=r"^adm_tickets$"))
    app.add_handler(CallbackQueryHandler(admin_tickets_all_handler, pattern=r"^adm_tickets_all$"))
    app.add_handler(CallbackQueryHandler(admin_ticket_close_handler, pattern=r"^adm_ticket_close:\d+$"))
    app.add_handler(CallbackQueryHandler(admin_ticket_reopen_handler, pattern=r"^adm_ticket_reopen:\d+$"))
    app.add_handler(CallbackQueryHandler(admin_ticket_detail_handler, pattern=r"^adm_ticket:\d+$"))

    # ---- Admin: Screen Content Manager ----
    app.add_handler(CallbackQueryHandler(admin_content_handler, pattern=r"^adm_content$"))
    app.add_handler(CallbackQueryHandler(admin_content_screen_handler, pattern=r"^adm_content_screen:\w+$"))
    app.add_handler(CallbackQueryHandler(admin_content_img_handler, pattern=r"^adm_content_img:\w+$"))
    app.add_handler(CallbackQueryHandler(admin_content_txt_handler, pattern=r"^adm_content_txt:\w+$"))
    app.add_handler(CallbackQueryHandler(admin_content_img_clear_handler, pattern=r"^adm_content_img_clear:\w+$"))
    app.add_handler(CallbackQueryHandler(admin_content_txt_clear_handler, pattern=r"^adm_content_txt_clear:\w+$"))

    # ======== TEXT & PHOTO ROUTERS ========
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
    app.add_handler(MessageHandler(filters.PHOTO, photo_router))

    # ======== ERROR HANDLER ========
    app.add_error_handler(error_handler)

    logger.info("All handlers registered.")


def main() -> None:
    """Start the bot."""
    import asyncio
    
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)

    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not set! Check your .env file.")
        return

    logger.info("Starting NanoStore Bot...")

    # Fix for Python 3.14+ event loop issue
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

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
