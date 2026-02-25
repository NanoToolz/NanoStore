"""Auto Delivery engine.

Responsibilities:
- Check product delivery_type: 'auto' or 'manual'
- Auto delivery: pick item from stock, send to user (text / photo / document)
- Reduce stock by quantity ordered
- Handle delivery failure: notify admin, log error
- Manual delivery: notify admin 'manual delivery needed' with order details
- Bulk delivery: deliver each item in order
- Delivery formats supported:
    * Plain text (license key, download link, instructions)
    * Photo (file_id)
    * Document/file (file_id)
"""

# TODO: Move _deliver_product_to_user() from src/handlers/admin.py here
# This becomes the central delivery engine for both crypto and local payments

# async def deliver_order(bot, order_id, user_id):
#     """Main delivery function called after payment confirmed."""
#     pass

# async def deliver_product(bot, user_id, product, item, currency):
#     """Deliver a single product to user."""
#     pass
