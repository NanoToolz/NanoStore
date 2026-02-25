"""Checkout Flow.

Responsibilities:
- Review cart (items, total, coupon discount)
- Select payment method:
    * Crypto (NOWPayments) -> go to src/payments/crypto.py
    * Local (Bank/Jazz/Easypaisa) -> go to src/payments/local.py
- Per-product payment rules: if product restricts certain methods, hide them
- Create order record in DB
- Apply coupon discount to total
- Apply bulk deal discount if qty threshold met
- Clear cart after order created
"""

# TODO: Extract checkout logic from src/handlers/orders.py

# async def checkout_handler(update, context):
#     """Show order summary and payment method selection."""
#     pass

# async def payment_method_select_handler(update, context):
#     """Route to crypto or local payment based on selection."""
#     pass
