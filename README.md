# 🚀 NanoStore - Telegram Digital Store Bot

Professional e-commerce bot for Telegram with complete order management, payment processing, and customer data collection.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)]()

---

## ✨ Features

- 🛍️ **Product Management** - Categories, products, stock tracking
- 💳 **Payment System** - Multiple payment methods, proof verification
- 📊 **Customer Data** - Complete order history and customer tracking
- 🎁 **Rewards System** - Referrals, daily spin, coupons
- 👥 **Admin Panel** - Full control over store operations
- 🔐 **Security** - All 23 critical security fixes applied
- 📱 **Professional UI** - Clean, intuitive interface

---

## 🎯 Quick Setup

### Automated Setup (Recommended)

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

**Windows:**
```powershell
.\setup.ps1
```

The setup wizard will guide you through:
```
════════════════════════════════════════════════════════════════
▶ STEP 1: Checking Prerequisites
════════════════════════════════════════════════════════════════
✓ Podman installed
✓ Git installed
✓ Available disk space: 50GB

Progress: [████████████████████] 100%
Step 8 of 8

╔════════════════════════════════════════════════════════════════╗
║                  ✓ SETUP COMPLETED SUCCESSFULLY! ✓            ║
╚════════════════════════════════════════════════════════════════╝
```

---

## 📋 Manual Setup

### 1. Configure Environment
```bash
cp config/.env.example .env
nano .env  # Add BOT_TOKEN and ADMIN_ID
```

### 2. Deploy with Podman
```bash
podman build -t nanostore-bot .
podman run -d --name nanostore-bot --env-file .env -v ./data:/app/data:Z --memory=256m --restart=always nanostore-bot
```

### 3. Verify
```bash
podman logs -f nanostore-bot
```

---

## 📊 Customer Data Collection

All customer data is automatically saved in `data/nanostore.db`:
- ✅ Customer details (name, username, user_id)
- ✅ Complete order history
- ✅ Payment proofs and timestamps
- ✅ Purchase patterns

### Export Customer Data
```bash
# Backup database
cp data/nanostore.db backups/backup_$(date +%Y%m%d).db

# View with SQLite
sqlite3 data/nanostore.db "SELECT * FROM orders;"
```

---

## 🛠️ Management Commands

```bash
# View logs
podman logs -f nanostore-bot

# Restart bot
podman restart nanostore-bot

# Stop bot
podman stop nanostore-bot

# Update bot
git pull origin GPT
podman build -t nanostore-bot .
podman restart nanostore-bot

# Backup database
cp data/nanostore.db backups/backup_$(date +%Y%m%d).db
```

---

## ⚙️ Configuration

### Required (.env file)
```bash
BOT_TOKEN=your_bot_token_here          # Get from @BotFather
ADMIN_ID=your_telegram_user_id         # Get from @userinfobot
```

### Optional
```bash
LOG_CHANNEL_ID=-1001234567890          # Logging channel
PROOFS_CHANNEL_ID=-1001234567890       # Payment proofs channel
LOG_TO_CHANNEL=true                    # Enable channel logging
LOG_LEVEL=INFO                         # Logging level
```

---

## 📚 Documentation

- **Setup Guide**: `docs/deployment/PODMAN_SETUP_GUIDE.md`
- **Urdu Guide**: `docs/deployment/PODMAN_SETUP_URDU.md`
- **Features**: `docs/FEATURES.md`
- **Quick Start**: `QUICK_START.md`
- **Structure**: `docs/STRUCTURE.md`

---

## 🐳 Container Deployment

### Resource Requirements (Lightweight)
- **CPU**: 0.25-0.5 cores
- **RAM**: 128-256 MB
- **Disk**: 100 MB + database

### Docker/Podman
```bash
# Build
podman build -t nanostore-bot .

# Run
podman run -d \
  --name nanostore-bot \
  --env-file .env \
  -v ./data:/app/data:Z \
  --memory=256m \
  --cpus=0.5 \
  --restart=always \
  nanostore-bot
```

---

## ✅ Production Ready

- ✓ All critical security fixes applied
- ✓ Cross-platform compatible (Windows/Linux/macOS)
- ✓ Lightweight (256MB RAM)
- ✓ Auto-restart enabled
- ✓ Professional setup wizard
- ✓ Customer data collection
- ✓ Complete order tracking

---

## 🔧 Recent Updates

### Phase 1 Complete ✅
- Atomic stock decrement (race condition eliminated)
- Idempotency checks for payments
- Transaction safety with rollback
- Rate limiting (25 msg/sec)
- Windows compatibility
- 15 database indexes (5-200x faster)
- Security hardening
- Repository cleaned
- Professional setup scripts

---

## 📞 Support

For issues or questions, check the logs:
```bash
podman logs nanostore-bot
```

Or refer to documentation in `docs/` folder.

---

## 📝 License

MIT License - see [LICENSE](LICENSE)

---

**Version**: 1.0 (Production Ready)  
**Last Updated**: February 25, 2026  
**Made with ❤️ for digital store owners**
