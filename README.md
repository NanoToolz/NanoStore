# 🛍️ NanoStore - Telegram Digital Store Bot

A powerful, feature-rich Telegram bot for running a digital store with automated product delivery, payment processing, and comprehensive admin panel.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)]()

---

## ✨ Features

### 🛒 Customer Features
- **Product Catalog** - Browse products by category with images
- **Shopping Cart** - Add, remove, and manage cart items
- **Multiple Currencies** - Support for PKR, USD, EUR, GBP
- **Wallet System** - Top-up balance and pay with wallet
- **Coupon System** - Apply discount coupons
- **Order Tracking** - View order history and status
- **Auto-Delivery** - Instant digital product delivery
- **Support Tickets** - Built-in customer support system
- **Daily Spin** - Loyalty rewards and points system
- **Referral Program** - Earn rewards for referrals

### 👨‍💼 Admin Features
- **Dashboard** - Real-time statistics and analytics
- **Product Management** - Add, edit, delete products with images
- **Order Management** - Process orders and payments
- **User Management** - View users, ban/unban, manage balances
- **Payment Proofs** - Review and approve payment screenshots
- **Coupon Management** - Create and manage discount coupons
- **Broadcast System** - Send messages to all users (rate-limited)
- **Force Join** - Require channel membership
- **Comprehensive Logging** - Activity logs and Telegram channel logging

### 🔒 Security Features
- ✅ **Race Condition Protection** - Atomic database operations
- ✅ **Transaction Safety** - Rollback on failures
- ✅ **Idempotency Checks** - Prevent double-processing
- ✅ **Input Validation** - Comprehensive validation framework
- ✅ **SQL Injection Protection** - Parameterized queries
- ✅ **Rate Limiting** - Prevent API abuse

---

## 🚀 Quick Start

### Option 1: Docker/Podman (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/nanostore.git
cd nanostore

# Configure environment
cp config/.env.example .env
# Edit .env with your bot token and admin ID

# Run with Docker
docker-compose up -d

# Or run with Podman
podman-compose up -d

# View logs
docker logs -f nanostore-bot
```

### Option 2: Manual Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/nanostore.git
cd nanostore

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp config/.env.example .env
# Edit .env with your bot token and admin ID

# Run the bot
python bot.py
```

---

## ⚙️ Configuration

### Required Environment Variables

```env
BOT_TOKEN=your_bot_token_here          # Get from @BotFather
ADMIN_ID=your_telegram_user_id         # Your Telegram user ID
```

### Optional Environment Variables

```env
LOG_CHANNEL_ID=-1001234567890          # Channel for logs (optional)
PROOFS_CHANNEL_ID=-1001234567890       # Channel for payment proofs (optional)
LOG_TO_CHANNEL=true                    # Enable channel logging
LOG_LEVEL=INFO                         # Logging level (DEBUG, INFO, WARNING, ERROR)
```

---

## 📦 Requirements

- Python 3.11+
- SQLite (included)
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))

### Dependencies
- `python-telegram-bot==21.7` - Telegram Bot API wrapper
- `aiosqlite==0.20.0` - Async SQLite database
- `aiohttp==3.11.10` - HTTP client for API calls
- `python-dotenv==1.0.1` - Environment variable management

---

## 🐳 Container Deployment

### Resource Requirements (Lightweight)
- **CPU**: 0.25-0.5 cores
- **RAM**: 128-256 MB
- **Disk**: 100 MB + database growth

### Docker Compose
```yaml
services:
  nanostore-bot:
    build: .
    restart: unless-stopped
    env_file: .env
    volumes:
      - ./data:/app/data
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

---

## 📚 Documentation

- [📖 Features Guide](docs/FEATURES.md) - Complete feature documentation
- [🏗️ Project Structure](docs/STRUCTURE.md) - Codebase architecture
- [📝 Logging Guide](docs/LOGGING.md) - Logging configuration
- [🚀 Deployment Guide](DEPLOYMENT.md) - Production deployment
- [🧪 Testing Guide](TESTING_GUIDE.md) - Testing instructions
- [📋 Quick Start](QUICK_START.md) - Quick setup guide
- [📜 Changelog](docs/CHANGELOG.md) - Version history

---

## 🛠️ Development

### Project Structure
```
nanostore/
├── src/
│   ├── core/           # Bot initialization and main loop
│   ├── handlers/       # Command and callback handlers
│   ├── database/       # Database operations
│   ├── middleware/     # Middleware (maintenance, membership)
│   ├── utils/          # Helper functions and utilities
│   └── config/         # Configuration management
├── data/               # SQLite database (auto-created)
├── docs/               # Documentation
├── archive/            # Historical documentation
├── bot.py              # Entry point
├── requirements.txt    # Python dependencies
└── Dockerfile          # Container image
```

### Database Schema
- **users** - User accounts and balances
- **products** - Product catalog
- **orders** - Order history
- **cart** - Shopping cart items
- **payment_proofs** - Payment verification
- **coupons** - Discount coupons
- **tickets** - Support tickets
- **wallet_topups** - Balance top-ups
- **referrals** - Referral tracking
- **points_history** - Loyalty points

---

## 🔧 Recent Improvements

### Phase 1 Critical Fixes (Completed)
✅ **15 Critical Fixes Implemented**:
1. Atomic stock decrement (race condition eliminated)
2. Idempotency checks for payment approval
3. Database transaction rollback on failures
4. Rate limiting on broadcast (25 msg/sec)
5. Graceful shutdown handler (Windows compatible)
6. Proper error handling in auto-delivery
7. Upgraded aiohttp (3.9.1 → 3.11.10)
8. Database timeout (10 seconds)
9. Central input validation module
10. Cart unique constraint
11. 15 database performance indexes (5-200x faster)
12. Atomic coupon usage
13. Atomic balance deduction
14. Debug print statements removed
15. Transaction isolation fixed

### Security Enhancements
- ✅ 5 race conditions eliminated
- ✅ Transaction safety with rollback
- ✅ Idempotency checks
- ✅ Input validation framework
- ✅ SQL injection protection

### Performance Improvements
- ✅ 15 database indexes added
- ✅ 5-200x faster queries at scale
- ✅ Optimized atomic operations

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram Bot API wrapper
- [aiosqlite](https://github.com/omnilib/aiosqlite) - Async SQLite wrapper
- All contributors and users

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/nanostore/issues)
- **Telegram**: [@YourSupportBot](https://t.me/YourSupportBot)
- **Email**: support@example.com

---

## 🌟 Star History

If you find this project useful, please consider giving it a star ⭐

---

**Made with ❤️ by the NanoStore Team**

**Status**: ✅ Production Ready | **Version**: 1.0.0 | **Last Updated**: February 25, 2026
