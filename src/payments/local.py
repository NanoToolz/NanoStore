"""Local Payment methods (Bank / Easypaisa / JazzCash etc).

Responsibilities:
- Show available local payment methods from DB (added via admin panel)
- Display payment details to user (account number, name, instructions)
- User uploads proof screenshot
- Store proof in DB with order_id, user_id, method_id, file_id
- Notify admin of new proof in verification queue
- User sees 'pending verification' status
"""

# TODO: Implement local payment flow
# Connects to: src/admin/proofs.py (admin side)

# async def local_payment_handler(update, context):
#     """Show local payment methods list."""
#     pass

# async def proof_upload_handler(update, context):
#     """Handle user proof photo upload."""
#     pass
