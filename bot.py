import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from config import BOT_TOKEN
from database import init_db

from handlers.start import start_handler, main_menu_handler, help_handler, noop_handler
from handlers.catalog import shop_handler, category_handler, product_detail_handler
from handlers.cart import (
    addcart_handler, cart_handler, cart_inc_handler,
    cart_dec_handler, cart_del_handler, clear_cart_handler
)
from handlers.orders import (
    checkout_handler, confirm_order_handler, my_orders_handler,
    view_order_handler, apply_coupon_handler, coupon_text_handler
)
from handlers.search import search_handler, search_text_handler
from handlers.admin import (
    admin_handler, admin_dash_handler, admin_cats_handler,
    admin_cat_detail_handler, admin_addcat_handler, admin_editcat_handler,
    admin_delcat_handler, admin_confirmdelcat_handler,
    admin_prods_handler, admin_prod_detail_handler,
    admin_addprod_handler, admin_editprod_handler, admin_delprod_handler,
    admin_confirmdelprod_handler,
    admin_orders_handler, admin_order_detail_handler, admin_setstatus_handler,
    admin_users_handler, admin_user_detail_handler, admin_ban_handler,
    admin_unban_handler, admin_broadcast_handler, admin_coupons_handler,
    admin_coupon_detail_handler, admin_addcoupon_handler, admin_delcoupon_handler,
    admin_settings_handler, admin_set_welcome_img_handler,
    admin_text_handler, admin_photo_handler
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def post_init(application):
    await init_db()
    logger.info("Database initialized.")


async def text_router(update, context):
    """Routes text messages to the correct handler based on user state."""
    # Admin text inputs (category, product, coupon, broadcast)
    if await admin_text_handler(update, context):
        return
    # Coupon code input
    if await coupon_text_handler(update, context):
        return
    # Search input
    if await search_text_handler(update, context):
        return


async def photo_router(update, context):
    """Routes photo messages to the correct handler."""
    if await admin_photo_handler(update, context):
        return


def main():
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN not set! Create a .env file with your BOT_TOKEN.")
        return

    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    # === Command Handlers ===
    app.add_handler(CommandHandler("start", start_handler))

    # === Callback Query Handlers ===

    # Navigation
    app.add_handler(CallbackQueryHandler(main_menu_handler, pattern=r"^main_menu$"))
    app.add_handler(CallbackQueryHandler(help_handler, pattern=r"^help$"))
    app.add_handler(CallbackQueryHandler(noop_handler, pattern=r"^noop$"))

    # Shop & Catalog
    app.add_handler(CallbackQueryHandler(shop_handler, pattern=r"^shop$"))
    app.add_handler(CallbackQueryHandler(category_handler, pattern=r"^cat_\d+$"))
    app.add_handler(CallbackQueryHandler(product_detail_handler, pattern=r"^prod_\d+$"))

    # Cart
    app.add_handler(CallbackQueryHandler(addcart_handler, pattern=r"^addcart_\d+$"))
    app.add_handler(CallbackQueryHandler(cart_handler, pattern=r"^cart$"))
    app.add_handler(CallbackQueryHandler(cart_inc_handler, pattern=r"^cartinc_\d+$"))
    app.add_handler(CallbackQueryHandler(cart_dec_handler, pattern=r"^cartdec_\d+$"))
    app.add_handler(CallbackQueryHandler(cart_del_handler, pattern=r"^cartdel_\d+$"))
    app.add_handler(CallbackQueryHandler(clear_cart_handler, pattern=r"^clear_cart$"))

    # Orders & Checkout
    app.add_handler(CallbackQueryHandler(checkout_handler, pattern=r"^checkout$"))
    app.add_handler(CallbackQueryHandler(confirm_order_handler, pattern=r"^confirm_order$"))
    app.add_handler(CallbackQueryHandler(my_orders_handler, pattern=r"^my_orders$"))
    app.add_handler(CallbackQueryHandler(view_order_handler, pattern=r"^vieworder_\d+$"))
    app.add_handler(CallbackQueryHandler(apply_coupon_handler, pattern=r"^apply_coupon$"))

    # Search
    app.add_handler(CallbackQueryHandler(search_handler, pattern=r"^search$"))

    # === Admin Handlers ===
    app.add_handler(CallbackQueryHandler(admin_handler, pattern=r"^admin$"))
    app.add_handler(CallbackQueryHandler(admin_dash_handler, pattern=r"^adm_dash$"))

    # Admin Categories
    app.add_handler(CallbackQueryHandler(admin_cats_handler, pattern=r"^adm_cats$"))
    app.add_handler(CallbackQueryHandler(admin_cat_detail_handler, pattern=r"^adm_cat_\d+$"))
    app.add_handler(CallbackQueryHandler(admin_addcat_handler, pattern=r"^adm_addcat$"))
    app.add_handler(CallbackQueryHandler(admin_editcat_handler, pattern=r"^adm_editcat_\d+$"))
    app.add_handler(CallbackQueryHandler(admin_delcat_handler, pattern=r"^adm_delcat_\d+$"))
    app.add_handler(CallbackQueryHandler(admin_confirmdelcat_handler, pattern=r"^adm_confirmdelcat_\d+$"))

    # Admin Products
    app.add_handler(CallbackQueryHandler(admin_prods_handler, pattern=r"^adm_prods$"))
    app.add_handler(CallbackQueryHandler(admin_prod_detail_handler, pattern=r"^adm_prod_\d+$"))
    app.add_handler(CallbackQueryHandler(admin_addprod_handler, pattern=r"^adm_addprod$"))
    app.add_handler(CallbackQueryHandler(admin_editprod_handler, pattern=r"^adm_editprod_"))
    app.add_handler(CallbackQueryHandler(admin_delprod_handler, pattern=r"^adm_delprod_\d+$"))
    app.add_handler(CallbackQueryHandler(admin_confirmdelprod_handler, pattern=r"^adm_confirmdelprod_\d+$"))

    # Admin Orders
    app.add_handler(CallbackQueryHandler(admin_orders_handler, pattern=r"^adm_orders$"))
    app.add_handler(CallbackQueryHandler(admin_order_detail_handler, pattern=r"^adm_order_\d+$"))
    app.add_handler(CallbackQueryHandler(admin_setstatus_handler, pattern=r"^adm_setstatus_"))

    # Admin Users
    app.add_handler(CallbackQueryHandler(admin_users_handler, pattern=r"^adm_users$"))
    app.add_handler(CallbackQueryHandler(admin_user_detail_handler, pattern=r"^adm_user_\d+$"))
    app.add_handler(CallbackQueryHandler(admin_ban_handler, pattern=r"^adm_ban_\d+$"))
    app.add_handler(CallbackQueryHandler(admin_unban_handler, pattern=r"^adm_unban_\d+$"))

    # Admin Broadcast
    app.add_handler(CallbackQueryHandler(admin_broadcast_handler, pattern=r"^adm_broadcast$"))

    # Admin Coupons
    app.add_handler(CallbackQueryHandler(admin_coupons_handler, pattern=r"^adm_coupons$"))
    app.add_handler(CallbackQueryHandler(admin_coupon_detail_handler, pattern=r"^adm_coupon_"))
    app.add_handler(CallbackQueryHandler(admin_addcoupon_handler, pattern=r"^adm_addcoupon$"))
    app.add_handler(CallbackQueryHandler(admin_delcoupon_handler, pattern=r"^adm_delcoupon_"))

    # Admin Settings
    app.add_handler(CallbackQueryHandler(admin_settings_handler, pattern=r"^adm_settings$"))
    app.add_handler(CallbackQueryHandler(admin_set_welcome_img_handler, pattern=r"^adm_set_welcome_img$"))

    # === Message Handlers (Text & Photo Router) ===
    app.add_handler(MessageHandler(filters.PHOTO, photo_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))

    print("[BOT] NanoStore Bot is running...")
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
