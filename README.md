# 🛍️ NanoStore — Telegram Store Bot

A complete Telegram e-commerce bot built with Python. Manage products, process orders, handle payments, and support customers — all within Telegram.

## ✨ Features

### 👤 Customer Features
- **Shop** — Browse categories, view products with images, FAQ & media
- **Search** — Find products instantly by name or description
- **Cart** — Add/remove items, adjust quantities, clear cart
- **Orders** — Checkout with coupon & balance support, track order status
- **Payments** — Multiple payment methods, upload proof screenshots
- **Support** — Create tickets, track conversations, get replies
- **Force Join** — Require channel membership before using bot

### ⚙️ Admin Features
- **Dashboard** — Live stats (users, orders, revenue, pending proofs)
- **Category CRUD** — Add/edit/delete categories with emoji & images
- **Product CRUD** — Full product management with stock, FAQ, media
- **Order Management** — View orders, change status, notify users
- **User Management** — View users, ban/unban
- **Coupon System** — Create/toggle/delete percentage coupons
- **Payment Methods** — Add/remove payment methods
- **Proof Review** — Approve/reject payment proofs, post to channel
- **Support Tickets** — Reply to tickets, close/reopen
- **Settings** — Edit currency, bot name, welcome text, etc.
- **Force Join** — Manage required channels
- **Bulk Operations** — Import products, update stock in bulk
- **Broadcast** — Send messages to all users with preview

## 📁 Project Structure

```
NanoStore/
├── bot.py                  # Main entry point, handler registration
├── config.py               # Environment config (BOT_TOKEN, ADMIN_ID, etc.)
├── database.py             # aiosqlite DB — 15 tables, 65 functions
├── helpers.py              # safe_edit, formatting, logging, validation
├── keyboards.py            # 30 inline keyboard builders
├── requirements.txt        # Python dependencies
├── .env.example            # Environment template
├── handlers/
│   ├── __init__.py
│   ├── start.py            # /start, main menu, help, force join
│   ├── catalog.py          # Shop, categories, products, FAQ, media
│   ├── cart.py             # Cart operations
│   ├── search.py           # Product search
│   ├── orders.py           # Checkout, payments, order tracking
│   ├── admin.py            # Complete admin panel (~40 handlers)
│   └── tickets.py          # Support ticket system (user + admin)
```

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/NanoToolz/NanoStore.git
cd NanoStore
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
```bash
cp .env.example .env
# Edit .env with your bot token and admin ID
```

### 4. Run the bot
```bash
python bot.py
```

The database is automatically created on first run with all tables and default settings.

## ⚙️ Configuration

| Variable | Required | Description |
|---|---|---|
| `BOT_TOKEN` | ✅ | Bot token from [@BotFather](https://t.me/BotFather) |
| `ADMIN_ID` | ✅ | Your Telegram user ID |
| `LOG_CHANNEL_ID` | ❌ | Channel for error/action logs |
| `DB_PATH` | ❌ | Database file path (default: `nanostore.db`) |

## 💾 Database

- **Engine**: SQLite with aiosqlite (async)
- **Mode**: WAL (Write-Ahead Logging) for concurrent reads
- **Tables**: 15 tables with foreign keys and CASCADE deletes
- **Auto-init**: Tables + default settings created on first run

### Tables

| Table | Purpose |
|---|---|
| `users` | User profiles, balance, ban status |
| `categories` | Product categories |
| `products` | Products with stock, images |
| `product_faqs` | Per-product FAQ entries |
| `product_media` | Product videos, files, voice |
| `cart` | Shopping cart per user |
| `orders` | Order records with items JSON |
| `payment_methods` | Admin-defined payment options |
| `payment_proofs` | User payment screenshots |
| `coupons` | Discount coupon codes |
| `settings` | Bot settings (key-value) |
| `force_join_channels` | Required channels |
| `tickets` | Support tickets |
| `ticket_replies` | Ticket conversation threads |
| `action_logs` | Audit trail |

## 🔒 Security

- Admin handlers check `ADMIN_ID` on every request
- User ban checking on `/start`
- HTML escaping on all user inputs
- Safe message editing (handles all Telegram API edge cases)
- Global error handler with log channel reporting

## 📋 Bot Commands

| Command | Description |
|---|---|
| `/start` | Start the bot / Main menu |

All other interactions use inline keyboards — no additional commands needed.

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.10+ |
| Framework | python-telegram-bot 21.7 |
| Database | SQLite via aiosqlite |
| Config | python-dotenv |
| Architecture | Async, callback-based |

## 📄 License

MIT License — use freely for personal and commercial projects.
