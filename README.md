# \ud83e\udd16 NanoStore \u2014 Telegram Digital Product Store Bot

A full-featured Telegram bot for selling digital products. Built with Python, fully controlled via inline buttons, optimized for 512MB RAM servers.

## \u2728 Features

### User Side
- \ud83d\uddbc\ufe0f Welcome image + greeting on `/start`
- \ud83d\udcc2 Browse products by category
- \ud83d\udd0d Search products by keyword
- \ud83d\uded2 Cart with \u2795/\u2796 quantity, remove, clear
- \ud83c\udff7\ufe0f Apply coupon codes at checkout
- \ud83d\udce6 Order placement + order history with status tracking
- \u2753 Help section
- \u26d4 Banned user detection

### Admin Panel (via bot)
- \ud83d\udcca Dashboard \u2014 users, products, orders, revenue stats
- \ud83d\udcc2 Category CRUD \u2014 add/edit/delete categories
- \ud83d\udce6 Product CRUD \u2014 add/edit name, price, description, image/delete
- \ud83d\uded2 Order management \u2014 view all orders, update status
- \ud83d\udc65 User management \u2014 view users, ban/unban
- \ud83d\udce3 Broadcast \u2014 send text or photo to ALL users
- \ud83c\udff7\ufe0f Coupon system \u2014 create/delete discount codes
- \u2699\ufe0f Settings \u2014 set welcome image from bot

### Technical
- 100% inline button navigation
- Async SQLite database (aiosqlite)
- Lightweight \u2014 runs on 512MB RAM
- Only 3 dependencies

## \ud83d\udcc1 Project Structure

```
NanoStore/
\u251c\u2500\u2500 bot.py              # Main entry point
\u251c\u2500\u2500 config.py           # Settings & constants
\u251c\u2500\u2500 database.py         # SQLite CRUD operations
\u251c\u2500\u2500 keyboards.py        # All inline keyboards
\u251c\u2500\u2500 handlers/
\u2502   \u251c\u2500\u2500 __init__.py
\u2502   \u251c\u2500\u2500 start.py        # Welcome + main menu
\u2502   \u251c\u2500\u2500 catalog.py      # Shop, categories, product detail
\u2502   \u251c\u2500\u2500 cart.py         # Cart management
\u2502   \u251c\u2500\u2500 orders.py       # Checkout, orders, coupons
\u2502   \u251c\u2500\u2500 search.py       # Product search
\u2502   \u2514\u2500\u2500 admin.py        # Full admin panel
\u251c\u2500\u2500 assets/
\u2502   \u2514\u2500\u2500 welcome.jpg     # Welcome banner (optional)
\u251c\u2500\u2500 requirements.txt
\u251c\u2500\u2500 .env.example
\u2514\u2500\u2500 .gitignore
```

## \ud83d\ude80 Setup

### 1. Clone the repo
```bash
git clone https://github.com/NanoToolz/NanoStore.git
cd NanoStore
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Create bot & get token
- Open [@BotFather](https://t.me/BotFather) on Telegram
- Create a new bot and copy the token

### 4. Get your Telegram user ID
- Open [@userinfobot](https://t.me/userinfobot) on Telegram
- Copy your numeric user ID

### 5. Configure environment
```bash
cp .env.example .env
```
Edit `.env` and fill in:
```
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_user_id
```

### 6. (Optional) Add welcome image
Place a `welcome.jpg` in the `assets/` folder.

### 7. Run the bot
```bash
python bot.py
```

## \ud83d\udcf1 Bot Commands

| Command | Description |
|---------|-------------|
| /start  | Welcome message + main menu |

Everything else is handled via inline buttons!

## \ud83d\udee0\ufe0f Tech Stack

| Package | Purpose |
|---------|----------|
| `python-telegram-bot` v20+ | Async bot framework |
| `aiosqlite` | Lightweight async SQLite |
| `python-dotenv` | Environment variables |

## \ud83d\udcdd Admin Quick Start

1. Start the bot and press **\ud83d\udc64 Admin Panel**
2. Go to **\ud83d\udcc2 Categories** \u2192 Add your categories (e.g. `\ud83d\udcda eBooks`)
3. Go to **\ud83d\udce6 Products** \u2192 Add products with name, description, price
4. Send product images via **Edit Image** button
5. Create coupons in **\ud83c\udff7\ufe0f Coupons** section
6. Set welcome image in **\u2699\ufe0f Settings**
7. Use **\ud83d\udce3 Broadcast** to message all users

## License

MIT License \u2014 Built by [NanoToolz](https://github.com/NanoToolz)
