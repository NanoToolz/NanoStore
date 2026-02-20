# NanoStore Project Structure

## Overview

NanoStore is organized as a professional Python project with clear separation of concerns:

- **Root Level**: Entry point and configuration
- **src/**: All source code
- **config/**: Configuration templates and guides
- **docs/**: Documentation files

## Directory Structure

```
NanoStore/
├── bot.py                   # Main entry point - run this to start the bot
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (create from config/.env.example)
├── .gitignore              # Git ignore rules (includes data/ folder)
├── LICENSE                 # MIT License
├── README.md              # Main documentation
│
├── src/                   # Source code directory
│   ├── bot.py            # Bot initialization, handler registration, error handling
│   ├── config.py         # Environment configuration loader
│   ├── database.py       # Database operations (14 tables, all CRUD operations)
│   ├── helpers.py        # Helper functions (render_screen, safe_edit, formatting)
│   ├── keyboards.py      # Telegram inline keyboard generators
│   └── handlers/         # Command and callback handlers
│       ├── __init__.py
│       ├── start.py          # /start, welcome, main menu, help
│       ├── catalog.py        # Shop, categories, products, FAQs, media
│       ├── cart.py           # Shopping cart operations
│       ├── orders.py         # Checkout, payment, order tracking
│       ├── wallet.py         # Wallet balance, top-up, history
│       ├── tickets.py        # Support ticket system
│       ├── search.py         # Product search
│       ├── rewards.py        # Daily reward system
│       ├── admin.py          # Admin panel (all admin features)
│       └── admin_content.py  # Screen Content Manager
│
├── config/               # Configuration files
│   └── .env.example     # Environment template with all required variables
│
├── docs/                # Documentation
│   ├── CHANGELOG.md     # Version history and updates
│   ├── FEATURES.md      # Detailed feature documentation (100+ features)
│   └── STRUCTURE.md     # This file - project structure details
│
└── data/                # Database storage (auto-created, gitignored)
    ├── .gitkeep        # Keeps folder in git
    └── nanostore.db    # SQLite database (auto-created on first run)
```

## File Descriptions

### Root Level Files

**bot.py**
- Main entry point for the application
- Adds `src/` to Python path
- Imports and runs `main()` from `src/bot.py`
- Usage: `python bot.py`

**.env**
- Environment configuration (not in git)
- Contains: BOT_TOKEN, ADMIN_ID, LOG_CHANNEL_ID, PROOFS_CHANNEL_ID
- Create from `config/.env.example`

**.gitignore**
- Git ignore rules
- Excludes: `__pycache__/`, `.env`, `*.db-wal`, `*.db-shm`, `*.db-journal`
- Includes database file for development

**requirements.txt**
- Python dependencies
- Main packages: python-telegram-bot, aiosqlite, python-dotenv

**nanostore.db**
- SQLite database (auto-created)
- 14 tables with foreign key constraints
- WAL mode enabled for better concurrency

### Source Code (src/)

**bot.py** (Main Bot File)
- Application initialization with `Application.builder()`
- Handler registration (100+ handlers)
- Error handling with global error handler
- Post-init hook for database setup and admin notifications
- Text/photo routers for multi-step flows
- Main entry point: `main()` function

**config.py** (Configuration)
- Loads environment variables from `.env`
- Validates required settings (BOT_TOKEN, ADMIN_ID)
- Provides: BOT_TOKEN, ADMIN_ID, LOG_CHANNEL_ID, PROOFS_CHANNEL_ID, DB_PATH
- Uses pathlib for cross-platform path handling

**database.py** (Database Layer)
- Async SQLite operations with aiosqlite
- 14 tables: users, categories, products, orders, payments, etc.
- CRUD operations for all entities
- Transaction management
- Foreign key constraints
- WAL mode for concurrency
- Default settings initialization

**helpers.py** (Helper Functions)
- `render_screen()` - 3-tier image rendering with fallback
- `safe_edit()` - Error-safe message editing
- `resolve_image_id()` - Image priority resolution
- `schedule_delete()` - Auto-delete messages
- `send_restart_notification()` - Admin notifications
- Formatting utilities: `sep()`, `html_escape()`, `format_stock()`, `status_emoji()`

**keyboards.py** (Keyboard Generators)
- Dynamic inline keyboard generation
- Context-aware button layouts
- Pagination support
- Callback data encoding
- Constants: CONTENT_SCREENS for Screen Content Manager

### Handlers (src/handlers/)

**start.py** - Entry Point
- `/start` command handler
- Welcome splash with user profile
- Main menu hub
- Help screen
- Force join verification

**catalog.py** - Shopping
- Shop categories list
- Category products with pagination
- Product details with images
- Product FAQs
- Product media (videos, files, voice)
- Add to cart
- Stock overview

**cart.py** - Shopping Cart
- View cart with items
- Increment/decrement quantities
- Remove items
- Clear cart
- Cart total calculation

**orders.py** - Order Management
- Checkout flow
- Coupon application
- Wallet balance usage
- Payment method selection
- Payment proof upload
- Order tracking
- Order history with pagination

**wallet.py** - Wallet System
- View balance
- Top-up with preset/custom amounts
- Payment method selection
- Proof upload
- Top-up history

**tickets.py** - Support System
- Create tickets
- View ticket list
- Ticket conversation thread
- Reply to admin
- Admin ticket management

**search.py** - Product Search
- Search by name or description
- Display results with prices

**rewards.py** - Daily Rewards
- Claim daily reward
- 24-hour cooldown
- Automatic balance credit

**admin.py** - Admin Panel
- Dashboard with statistics
- Category CRUD operations
- Product CRUD operations
- Order processing
- Payment proof verification
- User management (ban/unban)
- Coupon management
- Payment method management
- Settings configuration
- Force join management
- Broadcast system
- Bulk operations

**admin_content.py** - Screen Content Manager
- Manage images for 7 screens
- Manage text for 7 screens
- Clear images/text
- Preview changes

### Configuration (config/)

**config/.env.example**
- Template for environment variables
- Contains all required and optional variables
- Instructions for obtaining values

### Documentation (docs/)

**docs/CHANGELOG.md**
- Version history
- Update notes
- Breaking changes

**docs/FEATURES.md**
- Detailed feature documentation
- 100+ features listed
- User and admin features
- UI/UX features
- Security features

**docs/STRUCTURE.md**
- This file
- Project structure details
- File descriptions
- Architecture overview

## Import Structure

All imports use relative imports from the `src/` directory:

```python
# In src/handlers/start.py
from config import ADMIN_ID
from database import ensure_user, get_setting
from helpers import safe_edit, html_escape
from keyboards import main_menu_kb, back_kb
```

This works because `run.py` adds `src/` to the Python path:

```python
# In run.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
```

## Database Schema

### Core Tables

**users**
- user_id (PRIMARY KEY)
- full_name, username
- balance (REAL)
- banned (INTEGER)
- joined_at (TEXT)

**categories**
- id (PRIMARY KEY)
- name, emoji
- image_id (TEXT)
- sort_order, active
- created_at

**products**
- id (PRIMARY KEY)
- category_id (FOREIGN KEY)
- name, description
- price (REAL), stock (INTEGER)
- image_id, active
- delivery_type, delivery_data
- created_at

**product_faqs**
- id (PRIMARY KEY)
- product_id (FOREIGN KEY)
- question, answer

**product_media**
- id (PRIMARY KEY)
- product_id (FOREIGN KEY)
- media_type, file_id

### Shopping Tables

**cart**
- id (PRIMARY KEY)
- user_id, product_id (FOREIGN KEY)
- quantity
- added_at

**orders**
- id (PRIMARY KEY)
- user_id
- items_json (TEXT)
- total (REAL)
- status, payment_status
- payment_method_id, payment_proof_id
- coupon_code
- created_at

### Payment Tables

**payment_methods**
- id (PRIMARY KEY)
- name, details, emoji
- active

**payment_proofs**
- id (PRIMARY KEY)
- user_id, order_id, method_id
- file_id
- status, reviewed_by, admin_note
- created_at

**wallet_topups**
- id (PRIMARY KEY)
- user_id, amount, method_id
- proof_file_id
- status, admin_note, reviewed_by
- created_at

### System Tables

**coupons**
- code (PRIMARY KEY)
- discount_percent, max_uses, used_count
- active
- created_at

**settings**
- key (PRIMARY KEY)
- value (TEXT)

**force_join_channels**
- id (PRIMARY KEY)
- channel_id, name, invite_link

**tickets**
- id (PRIMARY KEY)
- user_id, subject, message
- status
- created_at

**ticket_replies**
- id (PRIMARY KEY)
- ticket_id (FOREIGN KEY)
- sender, message
- created_at

**action_logs**
- id (PRIMARY KEY)
- action, user_id, details
- created_at

## State Management

The bot uses `context.user_data` for temporary state:

```python
# Multi-step flows
context.user_data["state"] = "adm_prod_name:123"
context.user_data["temp"] = {"cat_id": 123}

# Order checkout
context.user_data["temp"] = {
    "order_id": 456,
    "original_total": 100.0,
    "discount": 10.0,
    "balance_used": 20.0
}

# Image upload
context.user_data["state"] = "adm_img_wait:shop_image_id"
context.user_data["adm_img_prompt_msg_id"] = 12345
```

## Message Flow

1. User clicks button → CallbackQuery
2. Handler processes query
3. `render_screen()` or `safe_edit()` updates message
4. Keyboard provides next actions
5. Temporary messages auto-deleted
6. Navigation messages edited in-place

## Key Design Patterns

**3-Tier Image Priority:**
1. Screen-specific image (e.g., `shop_image_id`)
2. Global banner image (`global_banner_image_id`)
3. Global UI image (`global_ui_image_id` if enabled)
4. Text-only fallback

**Auto-Recovery:**
- Detects invalid Telegram file IDs
- Auto-clears corrupted settings
- Notifies admin via DM
- Falls back to text-only mode
- No user-facing errors

**Smart Message Management:**
- Navigation messages: Edited in-place
- Temporary prompts: Auto-deleted after response
- Confirmation messages: Auto-deleted after 7s
- Admin notifications: Auto-deleted after 60s
- User uploads: Deleted after processing

## Development Workflow

1. **Make Changes**: Edit files in `src/` or `src/handlers/`
2. **Test Locally**: `python bot.py`
3. **Check Compilation**: `python -m py_compile src/*.py`
4. **Test Features**: Use your Telegram account
5. **Commit Changes**: `git add . && git commit -m "message"`
6. **Deploy**: Pull on server and restart service

## Deployment

**Systemd Service:**
```ini
[Unit]
Description=NanoStore Telegram Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/NanoStore
ExecStart=/usr/bin/python3 /path/to/NanoStore/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Commands:**
```bash
sudo systemctl start nanostore
sudo systemctl stop nanostore
sudo systemctl restart nanostore
sudo systemctl status nanostore
sudo journalctl -u nanostore -f
```

## Backup Strategy

```bash
# Daily backup (crontab)
0 2 * * * cd /path/to/NanoStore && cp nanostore.db backups/nanostore-$(date +\%Y\%m\%d).db

# Manual backup
cp nanostore.db nanostore.db.backup
cp .env .env.backup
```

## Update Procedure

```bash
# Stop bot
sudo systemctl stop nanostore

# Backup
cp nanostore.db nanostore.db.backup

# Pull updates
git pull origin main

# Install dependencies
pip3 install -r requirements.txt

# Start bot
sudo systemctl start nanostore
```

---

**Last Updated**: 2024
**Version**: 2.0
**Author**: NanoToolz
