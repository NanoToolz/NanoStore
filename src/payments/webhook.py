"""NOWPayments IPN Webhook handler.

Responsibilities:
- Receive POST from NOWPayments at /nowpayments/ipn
- Verify HMAC-SHA512 signature using IPN_SECRET
- Check payment_status == 'finished' or 'confirmed'
- Find order by payment_id in DB
- Mark order as paid
- Trigger auto-delivery via src/payments/delivery.py
- Notify user: payment confirmed + delivery
- Log to admin channel
- Handle duplicate IPN (idempotency check)

Required env vars: NOWPAYMENTS_IPN_SECRET, WEBHOOK_PORT

IPN Payload fields:
- payment_id: str
- payment_status: 'waiting'|'confirming'|'confirmed'|'sending'|'partially_paid'|'finished'|'failed'|'refunded'|'expired'
- order_id: str (our internal order ID)
- actually_paid: float
- pay_amount: float
- pay_currency: str
"""

# TODO: Implement IPN webhook receiver
# Use aiohttp or FastAPI alongside python-telegram-bot

# async def nowpayments_ipn_handler(request):
#     """Receive and process NOWPayments IPN callback."""
#     pass

# def verify_ipn_signature(payload_bytes, received_hmac, ipn_secret):
#     """Verify HMAC-SHA512 signature from NOWPayments."""
#     pass
