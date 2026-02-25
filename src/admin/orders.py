"""Admin Orders management.

Responsibilities:
- List all orders (recent 20)
- Order detail: items, total, user, status, payment_status, coupon
- Update order status (pending/confirmed/processing/delivered/completed/cancelled)
- Notify user on status change
- Track user spending when order completed
- Manual delivery: admin marks as delivered, adds note
"""

# TODO: Move from src/handlers/admin.py:
# admin_orders_handler, admin_order_detail_handler, admin_order_status_handler
