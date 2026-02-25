"""Admin Products & Categories management.

Responsibilities:
- Categories: list, add, edit, delete, set image
- Products: list per category, add (multi-step), edit (name/desc/price), delete with confirm, set image
- Stock: set per product (number / 0 out-of-stock / -1 unlimited)
- Delivery: set delivery type (auto/manual), set delivery data (text/photo/file)
- Per-product payment rules: which methods allowed, crypto instant ON/OFF
- Bulk import: paste multiple products at once
- Bulk stock update: paste product_id|stock lines
- Bulk stock via .txt file upload
"""

# TODO: Move from src/handlers/admin.py:
# admin_cats_handler, admin_cat_add_handler, admin_cat_detail_handler
# admin_cat_edit_handler, admin_cat_del_handler, admin_cat_img_handler
# admin_prods_handler, admin_prod_add_handler, admin_prod_detail_handler
# admin_prod_edit_handler, admin_prod_del_handler, admin_prod_img_handler
# admin_prod_stock_handler, admin_prod_delivery_handler
# admin_prod_deltype_handler, admin_prod_deldata_handler
# admin_bulk_handler, admin_bulk_stock_handler
# admin_prod_faq_add_handler, admin_prod_faq_del_handler
# admin_prod_media_add_handler, admin_prod_media_del_handler
