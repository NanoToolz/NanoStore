# 🛍️ NanoStore - Telegram Digital Store Bot

A powerful, feature-rich Telegram bot for running a digital store with automated product delivery, payment processing, and comprehensive admin panel.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)]()

---

## ✨ Key Features

- 🛒 **Product Catalog** - Browse products by category with images
- 💳 **Payment Processing** - Multiple payment methods with proof verification
- 🚀 **Auto-Delivery** - Instant digital product delivery
- 👨‍💼 **Admin Panel** - Comprehensive management dashboard
- 💰 **Wallet System** - Balance top-up and payments
- 🎟️ **Coupon System** - Discount codes and promotions
- 🎰 **Loyalty Rewards** - Daily spin and referral program
- 🎫 **Support Tickets** - Built-in customer support
- 📊 **Analytics** - Real-time statistics and reporting
- 🔒 **Secure** - Race condition protection, transaction safety

---

## � Quick Start

### Using Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/yourusername/nanostore.git
cd nanostore

# Configure
cp config/.env.example .env
# Edit .env with your BOT_TOKEN and ADMIN_ID

# Run
docker-compose up -d

# View logs
docker logs -f nanostore-bot
```

### Using Podman

```bash
podman-compose up -d
podman logs -f nanostore-bot
```

### Manual Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Configure
cp config/.env.example .env
# Edit .env

# Run
python bot.py
```

---

## ⚙️ Configuration

### Required Environment Variables

```env
BOT_TOKEN=your_bot_token_here          # From @BotFather
ADMIN_ID=your_telegram_user_id         # Your Telegram ID
```

### Optional Variables

```env
LOG_CHANNEL_ID=-1001234567890          # Logging channel
PROOFS_CHANNEL_ID=-1001234567890       # Payment proofs channel
LOG_TO_CHANNEL=true                    # Enable channel logging
LOG_LEVEL=INFO                         # Logging level
```

---

## 📦 Requirements

- Python 3.11+
- SQLite (included)
- Telegram Bot Token

### Dependencies
- `python-telegram-bot==21.7`
- `aiosqlite==0.20.0`
- `aiohttp==3.11.10`
- `python-dotenv==1.0.1`

---

## 🐳 Container Deployment

### Resource Requirements (Lightweight)
- **CPU**: 0.25-0.5 cores
- **RAM**: 128-256 MB
- **Disk**: 100 MB + database

### Docker Compose
```yaml
services:
  nanostore-bot:
    build: .
    restart: unless-stopped
    env_file: .env
    volumes:
      - ./data:/app/data
```

---

## 📚 Documentation

- [📖 Features Guide](docs/FEATURES.md) - Complete feature list
- [🏗️ Project Structure](docs/STRUCTURE.md) - Code architecture
- [📝 Logging Guide](docs/LOGGING.md) - Logging setup
- [📜 Changelog](CHANGELOG.md) - Version history
- [📋 Deployment Guides](docs/deployment/) - Production deployment
- [🧪 Testing Guides](docs/guides/) - Testing instructions

---

## 🛠️ Project Structure

```
nanostore/
├── src/
│   ├── core/           # Bot initialization
│   ├── handlers/       # Command handlers
│   ├── database/       # Database operations
│   ├── middleware/     # Middleware
│   └── utils/          # Utilities
├── data/               # Database (auto-created)
├── docs/               # Documentation
├── bot.py              # Entry point
├── requirements.txt    # Dependencies
└── Dockerfile          # Container image
```

---

## 🔧 Recent Improvements

### Phase 1 Critical Fixes ✅
- Atomic stock decrement (race condition eliminated)
- Idempotency checks for payments
- Transaction safety with rollback
- Rate limiting (25 msg/sec)
- Windows compatibility
- 15 database indexes (5-200x faster)
- Security hardening

---

## 🤝 Contributing

Contributions welcome! See [docs/guides/CONTRIBUTING.md](docs/guides/CONTRIBUTING.md)

---

## 📝 License

MIT License - see [LICENSE](LICENSE)

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/nanostore/issues)
- **Documentation**: [docs/](docs/)

---

**Made with ❤️ by the NanoStore Team**

**Version**: 1.0.0 | **Status**: ✅ Production Ready
