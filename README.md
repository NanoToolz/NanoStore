# 🤖 NanoStore — Telegram Digital Product Store Bot

A fully functional Telegram bot for selling digital products like eBooks, templates, courses, and software.

## Features
- 📚 Browse products by category
- 🔍 Search products by keyword
- 🛒 Add to cart with quantity tracking
- 💳 Checkout flow with payment info
- 📱 Inline keyboards for smooth UX

## Tech Stack
- Python 3.10+
- python-telegram-bot v20+

## Setup

1. **Clone the repo**
```bash
git clone https://github.com/NanoToolz/NanoStore.git
cd NanoStore
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Create a bot via [@BotFather](https://t.me/BotFather)** and get your token.

4. **Set your bot token**
```bash
cp .env.example .env
# Edit .env and paste your BOT_TOKEN
```

5. **Run the bot**
```bash
python bot.py
```

## Bot Commands
| Command | Description |
|---------|-------------|
| /start | Welcome message & main menu |
| /products | Browse product categories |
| /cart | View your shopping cart |
| /help | Show help info |

## Customization
Edit `products.py` to add, remove, or modify your digital products.

## License
MIT License
