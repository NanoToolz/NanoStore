"""NOWPayments Crypto Payment integration.

Responsibilities:
- Create payment via POST /v1/payment (NOWPayments API)
- Generate wallet address + amount for selected coin
- Get available currencies list (BTC, ETH, USDT, LTC etc)
- Check payment status via GET /v1/payment/{id}
- Store payment ID in DB linked to order
- Show wallet address + QR to user with expiry timer
- Supported coins: configurable from admin panel settings

API Base: https://api.nowpayments.io/v1
Auth: x-api-key header
"""

# TODO: Implement NOWPayments API calls
# Required env vars: NOWPAYMENTS_API_KEY

NOWPAYMENTS_BASE = "https://api.nowpayments.io/v1"

# async def create_crypto_payment(order_id, amount, currency, pay_currency):
#     """Create payment on NOWPayments. Returns payment_id + wallet address."""
#     pass

# async def get_payment_status(payment_id):
#     """Check payment status from NOWPayments API."""
#     pass

# async def get_available_currencies():
#     """Get list of available coins from NOWPayments."""
#     pass
