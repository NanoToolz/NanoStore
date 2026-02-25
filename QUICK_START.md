# ⚡ Quick Start - NanoStore Bot

Fast deployment guide for Podman.

---

## 🚀 5-Minute Setup

### 1. Install Podman
```bash
sudo apt install -y podman  # Ubuntu/Debian
# OR
sudo dnf install -y podman  # CentOS/Fedora
```

### 2. Clone & Configure
```bash
git clone https://github.com/NanoToolz/NanoStore.git
cd NanoStore
git checkout GPT
cp config/.env.example .env
nano .env  # Add BOT_TOKEN and ADMIN_ID
```

### 3. Build & Run
```bash
podman build -t nanostore-bot .
podman run -d --name nanostore-bot --env-file .env -v ./data:/app/data:Z --memory=256m --restart=always nanostore-bot
```

### 4. Verify
```bash
podman logs -f nanostore-bot
# Open Telegram → Search your bot → Send /start
```

---

## 📋 Essential Commands

```bash
# Start/Stop/Restart
podman start nanostore-bot
podman stop nanostore-bot
podman restart nanostore-bot

# Logs
podman logs -f nanostore-bot

# Status
podman ps

# Update
git pull && podman build -t nanostore-bot . && podman restart nanostore-bot

# Backup
cp data/nanostore.db backups/backup_$(date +%Y%m%d).db
```

---

## 🔧 Configuration (.env)

Required values:
```bash
BOT_TOKEN=your_token_from_botfather
ADMIN_ID=your_telegram_user_id
DB_PATH=data/nanostore.db
```

Get values:
- **BOT_TOKEN**: @BotFather on Telegram
- **ADMIN_ID**: @userinfobot on Telegram

---

## 📚 Full Documentation

- **English**: `docs/deployment/PODMAN_SETUP_GUIDE.md`
- **Urdu/Hindi**: `docs/deployment/PODMAN_SETUP_URDU.md`
- **Deployment**: `docs/deployment/DEPLOYMENT.md`

---

## ✅ Status

- Phase 1: ✅ Complete (23/23 critical fixes)
- Production Ready: ✅ Yes
- Container Ready: ✅ Yes (Docker/Podman)
- Platform: ✅ Cross-platform (Windows/Linux/macOS)

---

**Need help?** Check logs: `podman logs nanostore-bot`
