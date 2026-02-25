"""Order Notifications — notify users of order updates.

Responsibilities:
- Notify user when order status changes (confirmed/processing/delivered/completed)
- Notify user when payment approved or rejected
- Notify user when delivery sent
- Notify admin when manual delivery needed
- Notify admin channel for logs
"""

# TODO: Extract notification logic scattered across handlers

# async def notify_order_update(bot, user_id, order_id, new_status):
#     """Send order status update to user."""
#     pass

# async def notify_delivery(bot, user_id, order_id, product_name):
#     """Notify user their product has been delivered."""
#     pass
