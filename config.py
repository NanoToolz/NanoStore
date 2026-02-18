"""NanoStore configuration — loads environment variables."""

import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Bot token from @BotFather
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")

# Telegram user ID of the admin
ADMIN_ID: int = int(os.getenv("ADMIN_ID", "0"))

# Channel ID for action logs (optional)
LOG_CHANNEL_ID: str = os.getenv("LOG_CHANNEL_ID", "")

# Channel ID for posting approved payment proofs (optional)
PROOFS_CHANNEL_ID: str = os.getenv("PROOFS_CHANNEL_ID", "")

# SQLite database file path
DB_PATH: str = "nanostore.db"
