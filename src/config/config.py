"""Load configuration from environment variables."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file in root directory
root_dir = Path(__file__).parent.parent.parent  # Go up from config/ -> src/ -> root/
env_path = root_dir / '.env'
load_dotenv(env_path)

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
LOG_CHANNEL_ID = os.getenv("LOG_CHANNEL_ID", "")
PROOFS_CHANNEL_ID = os.getenv("PROOFS_CHANNEL_ID", "")

# Database Configuration
DB_PATH = str(root_dir / "data" / "nanostore.db")

# Validate required settings
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set in .env file")
if not ADMIN_ID:
    raise ValueError("ADMIN_ID not set in .env file")
