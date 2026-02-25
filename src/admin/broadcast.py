"""Admin Broadcast system.

Responsibilities:
- Compose broadcast message (HTML formatting supported)
- Preview before sending
- Confirm and send to all non-banned users
- Rate limiting: 25 messages/sec (safe below Telegram 30/sec limit)
- Report: sent count vs failed count
"""

# TODO: Move from src/handlers/admin.py:
# admin_broadcast_handler, admin_broadcast_confirm_handler
