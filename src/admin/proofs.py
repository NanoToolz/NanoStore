"""Admin Payment Proofs verification queue.

Responsibilities:
- List all pending proofs
- Proof detail: order info, user, amount, payment method, proof photo
- Approve proof -> triggers auto-delivery (if product delivery_type=auto)
- Reject proof with reason -> notify user
- Post proof photo to proofs channel
- Idempotency check (prevent double approval)
- Log manual delivery needed if product is manual type
"""

# TODO: Move from src/handlers/admin.py:
# admin_proofs_handler, admin_proof_detail_handler
# admin_proof_approve_handler, admin_proof_reject_handler
# admin_proof_post_handler
# _deliver_product_to_user() -> move to src/payments/delivery.py
