"""Admin panel section — all admin handlers."""

from .dashboard import admin_dashboard_handler
from .products import (
    admin_cats_handler, admin_cat_add_handler, admin_cat_detail_handler,
    admin_cat_edit_handler, admin_cat_del_handler, admin_cat_img_handler,
    admin_prods_handler, admin_prod_add_handler, admin_prod_detail_handler,
    admin_prod_edit_handler, admin_prod_del_handler, admin_prod_img_handler,
    admin_prod_stock_handler, admin_prod_delivery_handler,
    admin_bulk_handler, admin_bulk_stock_handler,
)
from .orders import admin_orders_handler, admin_order_detail_handler, admin_order_status_handler
from .users import admin_users_handler, admin_user_detail_handler, admin_ban_handler, admin_unban_handler
from .proofs import admin_proofs_handler, admin_proof_detail_handler, admin_proof_approve_handler, admin_proof_reject_handler
from .topups import admin_topups_handler, admin_topup_detail_handler, admin_topup_approve_handler, admin_topup_reject_handler
from .coupons import admin_coupons_handler, admin_coupon_add_handler, admin_coupon_toggle_handler, admin_coupon_del_handler
from .broadcast import admin_broadcast_handler, admin_broadcast_confirm_handler
from .content import (
    admin_img_panel_handler, admin_img_set_handler, admin_img_clear_handler,
    admin_img_toggle_handler, admin_global_img_toggle_handler,
    admin_txt_set_handler, admin_txt_clear_handler,
)

__all__ = [
    "admin_dashboard_handler",
    "admin_cats_handler", "admin_cat_add_handler", "admin_cat_detail_handler",
    "admin_cat_edit_handler", "admin_cat_del_handler", "admin_cat_img_handler",
    "admin_prods_handler", "admin_prod_add_handler", "admin_prod_detail_handler",
    "admin_prod_edit_handler", "admin_prod_del_handler", "admin_prod_img_handler",
    "admin_prod_stock_handler", "admin_prod_delivery_handler",
    "admin_bulk_handler", "admin_bulk_stock_handler",
    "admin_orders_handler", "admin_order_detail_handler", "admin_order_status_handler",
    "admin_users_handler", "admin_user_detail_handler", "admin_ban_handler", "admin_unban_handler",
    "admin_proofs_handler", "admin_proof_detail_handler", "admin_proof_approve_handler", "admin_proof_reject_handler",
    "admin_topups_handler", "admin_topup_detail_handler", "admin_topup_approve_handler", "admin_topup_reject_handler",
    "admin_coupons_handler", "admin_coupon_add_handler", "admin_coupon_toggle_handler", "admin_coupon_del_handler",
    "admin_broadcast_handler", "admin_broadcast_confirm_handler",
    "admin_img_panel_handler", "admin_img_set_handler", "admin_img_clear_handler",
    "admin_img_toggle_handler", "admin_global_img_toggle_handler",
    "admin_txt_set_handler", "admin_txt_clear_handler",
]
