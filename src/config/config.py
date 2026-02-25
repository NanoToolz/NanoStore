"""Load configuration from environment variables."""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Setup logger for config module
logger = logging.getLogger(__name__)

# Load environment variables from .env file in root directory
root_dir = Path(__file__).parent.parent.parent  # Go up from config/ -> src/ -> root/
env_path = root_dir / '.env'
load_dotenv(env_path)

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# Load LOG_CHANNEL_ID and convert to int if present
_log_channel_raw = os.getenv("LOG_CHANNEL_ID", "")

if _log_channel_raw and _log_channel_raw.strip():
    try:
        LOG_CHANNEL_ID = int(_log_channel_raw.strip())
        logger.debug(f"Loaded LOG_CHANNEL_ID: {LOG_CHANNEL_ID}")
    except ValueError:
        logger.error(f"Invalid LOG_CHANNEL_ID format: {_log_channel_raw}")
        LOG_CHANNEL_ID = None
else:
    LOG_CHANNEL_ID = None

PROOFS_CHANNEL_ID = os.getenv("PROOFS_CHANNEL_ID", "")

# Logging Configuration
LOG_TO_CHANNEL = os.getenv("LOG_TO_CHANNEL", "true").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()
LOG_CHANNEL_LEVEL = os.getenv("LOG_CHANNEL_LEVEL", "INFO").upper()
FULL_VERBOSE_TO_CHANNEL = os.getenv("FULL_VERBOSE_TO_CHANNEL", "false").lower() == "true"

# Database Configuration
DB_PATH = str(root_dir / "data" / "nanostore.db")

# Validate required settings
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set in .env file")
if not ADMIN_ID:
    raise ValueError("ADMIN_ID not set in .env file")
