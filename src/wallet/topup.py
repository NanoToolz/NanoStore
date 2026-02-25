"""Wallet Top-Up flow (user side).

Responsibilities:
- User selects top-up method (local payment methods)
- User enters amount (within min/max limits from settings)
- User uploads payment proof
- Top-up request saved to DB
- Admin notified of new top-up request (src/admin/topups.py handles approve/reject)
"""

# TODO: Extract top-up user flow from src/handlers/wallet.py
