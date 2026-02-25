# 🚀 NanoStore Bot - Deployment Guide

## 🐳 Podman/Docker Deployment (Recommended)

### Prerequisites
- Podman or Docker installed
- `.env` file configured with your bot token

### Quick Start with Podman

```bash
# Build the image
podman build -t nanostore-bot .

# Run with podman-compose (recommended)
podman-compose up -d

# Or run directly
podman run -d \
  --name nanostore-bot \
  --env-file .env \
  -v ./data:/app/data:Z \
  --restart unless-stopped \
  nanostore-bot
```

### Quick Start with Docker

```bash
# Build the image
docker build -t nanostore-bot .

# Run with docker-compose (recommended)
docker-compose up -d

# Or run directly
docker run -d \
  --name nanostore-bot \
  --env-file .env \
  -v ./data:/app/data \
  --restart unless-stopped \
  nanostore-bot
```

### Container Management

```bash
# View logs
podman logs -f nanostore-bot
# or
docker logs -f nanostore-bot

# Stop the bot
podman-compose down
# or
docker-compose down

# Restart the bot
podman-compose restart
# or
docker-compose restart

# Update and rebuild
podman-compose down
podman-compose build --no-cache
podman-compose up -d
```

---

## 💻 Manual Deployment (Without Container)

### Prerequisites
- Python 3.11+
- pip

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp config/.env.example .env
# Edit .env with your bot token and admin ID

# Run the bot
python bot.py
```

---

## 🔧 Configuration

### Required Environment Variables

```env
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_user_id
```

### Optional Environment Variables

```env
LOG_CHANNEL_ID=-1001234567890
PROOFS_CHANNEL_ID=-1001234567890
LOG_TO_CHANNEL=true
LOG_LEVEL=INFO
LOG_CHANNEL_LEVEL=INFO
FULL_VERBOSE_TO_CHANNEL=false
```

---

## 📊 Resource Requirements

### Lightweight Configuration (Recommended)
- **CPU**: 0.25-0.5 cores
- **RAM**: 128-256 MB
- **Disk**: 100 MB + database growth
- **Network**: Minimal (Telegram API only)

### Production Configuration
- **CPU**: 1 core
- **RAM**: 512 MB
- **Disk**: 1 GB
- **Network**: Stable internet connection

---

## 🔒 Security Best Practices

1. **Never commit `.env` file** - Already in `.gitignore`
2. **Use read-only mounts** for config files
3. **Limit container resources** - Prevents resource exhaustion
4. **Regular backups** of `data/nanostore.db`
5. **Keep dependencies updated** - Run `pip install --upgrade -r requirements.txt`

---

## 🐛 Troubleshooting

### Bot not starting
```bash
# Check logs
podman logs nanostore-bot

# Common issues:
# 1. BOT_TOKEN not set → Check .env file
# 2. Database locked → Stop other instances
# 3. Port conflict → Check if another bot is running
```

### Database issues
```bash
# Backup database
cp data/nanostore.db data/nanostore.db.backup

# Reset database (WARNING: Deletes all data)
rm data/nanostore.db
python bot.py  # Will recreate database
```

### Container issues
```bash
# Remove and recreate container
podman-compose down
podman-compose up -d --force-recreate

# Check container status
podman ps -a
podman inspect nanostore-bot
```

---

## 📈 Monitoring

### Health Check
```bash
# Check if bot is running
podman ps | grep nanostore-bot

# Check health status
podman inspect nanostore-bot | grep Health
```

### Logs
```bash
# Real-time logs
podman logs -f nanostore-bot

# Last 100 lines
podman logs --tail 100 nanostore-bot

# Logs with timestamps
podman logs -t nanostore-bot
```

---

## 🔄 Updates

### Update bot code
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
podman-compose down
podman-compose build --no-cache
podman-compose up -d
```

### Update dependencies
```bash
# Update requirements.txt
pip install --upgrade -r requirements.txt

# Rebuild container
podman-compose build --no-cache
podman-compose up -d
```

---

## 💾 Backup & Restore

### Backup
```bash
# Backup database
cp data/nanostore.db backups/nanostore-$(date +%Y%m%d).db

# Backup entire data directory
tar -czf backups/data-$(date +%Y%m%d).tar.gz data/
```

### Restore
```bash
# Restore database
cp backups/nanostore-20260225.db data/nanostore.db

# Restart bot
podman-compose restart
```

---

## 🚀 Production Deployment

### Using systemd (Linux)
```bash
# Create systemd service
sudo nano /etc/systemd/system/nanostore-bot.service
```

```ini
[Unit]
Description=NanoStore Telegram Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/nanostore
ExecStart=/usr/bin/python3 /path/to/nanostore/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable nanostore-bot
sudo systemctl start nanostore-bot
sudo systemctl status nanostore-bot
```

---

## 📞 Support

For issues or questions:
1. Check logs first
2. Review troubleshooting section
3. Check GitHub issues
4. Contact admin

---

**Last Updated**: February 25, 2026  
**Version**: 1.0.0  
**Status**: Production Ready ✅
