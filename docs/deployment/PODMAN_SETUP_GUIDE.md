# 🚀 Podman Deployment Guide - NanoStore Bot

Complete step-by-step guide for deploying NanoStore bot using Podman on your server.

---

## 📋 Prerequisites

### 1. Server Requirements
- **OS**: Linux (Ubuntu 20.04+, CentOS 8+, Fedora, etc.)
- **RAM**: Minimum 512MB (Recommended: 1GB)
- **Storage**: 2GB free space
- **CPU**: 1 core minimum

### 2. Required Software
- Podman installed
- Git installed
- Internet connection

---

## 🔧 Step 1: Install Podman

### For Ubuntu/Debian:
```bash
# Update package list
sudo apt update

# Install Podman
sudo apt install -y podman

# Verify installation
podman --version
```

### For CentOS/RHEL/Fedora:
```bash
# Install Podman
sudo dnf install -y podman

# Verify installation
podman --version
```

### For Other Linux:
```bash
# Check official guide: https://podman.io/getting-started/installation
```

---

## 📥 Step 2: Clone Repository

```bash
# Navigate to your preferred directory
cd /home/your-username

# Clone the repository
git clone https://github.com/NanoToolz/NanoStore.git

# Enter directory
cd NanoStore

# Switch to GPT branch (where all fixes are)
git checkout GPT
```

---

## ⚙️ Step 3: Configure Environment Variables

```bash
# Copy example env file
cp config/.env.example .env

# Edit .env file
nano .env
```

### Required Configuration:
```bash
# Bot Configuration
BOT_TOKEN=your_bot_token_here          # Get from @BotFather
ADMIN_ID=your_telegram_user_id         # Your Telegram user ID

# Logging (Optional but recommended)
LOG_CHANNEL_ID=-1001234567890          # Your log channel ID
PROOFS_CHANNEL_ID=-1001234567890       # Channel for payment proofs
LOG_TO_CHANNEL=true
LOG_LEVEL=INFO
LOG_CHANNEL_LEVEL=INFO
FULL_VERBOSE_TO_CHANNEL=false

# Database
DB_PATH=data/nanostore.db              # Keep as is
```

### How to Get Values:

**BOT_TOKEN:**
1. Open Telegram
2. Search for `@BotFather`
3. Send `/newbot` or use existing bot
4. Copy token (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

**ADMIN_ID:**
1. Open Telegram
2. Search for `@userinfobot`
3. Send `/start`
4. Copy your ID (looks like: `123456789`)

**LOG_CHANNEL_ID:**
1. Create a new Telegram channel
2. Add your bot as admin
3. Forward any message from channel to `@userinfobot`
4. Copy channel ID (looks like: `-1001234567890`)

---

## 🏗️ Step 4: Build Podman Image

```bash
# Build the image (takes 2-3 minutes)
podman build -t nanostore-bot .

# Verify image is created
podman images
```

You should see:
```
REPOSITORY          TAG       IMAGE ID      CREATED        SIZE
nanostore-bot       latest    abc123def     2 minutes ago  180MB
```

---

## 🚀 Step 5: Run Bot with Podman Compose

### Option A: Using Podman Compose (Recommended)

```bash
# Install podman-compose if not installed
pip3 install podman-compose

# Start the bot
podman-compose -f podman-compose.yml up -d

# Check if running
podman-compose ps
```

### Option B: Using Podman Directly

```bash
# Run the container
podman run -d \
  --name nanostore-bot \
  --env-file .env \
  -v ./data:/app/data:Z \
  --memory=256m \
  --cpus=0.5 \
  --restart=always \
  nanostore-bot

# Check if running
podman ps
```

---

## 📊 Step 6: Verify Bot is Running

### Check Container Status:
```bash
# List running containers
podman ps

# Should show:
# CONTAINER ID  IMAGE           COMMAND     CREATED        STATUS        NAMES
# abc123def456  nanostore-bot   python...   2 minutes ago  Up 2 minutes  nanostore-bot
```

### Check Logs:
```bash
# View live logs
podman logs -f nanostore-bot

# You should see:
# INFO - Bot started successfully
# INFO - Listening for updates...
```

### Test Bot:
1. Open Telegram
2. Search for your bot
3. Send `/start`
4. Bot should respond with welcome message

---

## 🔄 Step 7: Managing the Bot

### Stop Bot:
```bash
podman stop nanostore-bot
```

### Start Bot:
```bash
podman start nanostore-bot
```

### Restart Bot:
```bash
podman restart nanostore-bot
```

### View Logs:
```bash
# Last 100 lines
podman logs --tail 100 nanostore-bot

# Live logs (Ctrl+C to exit)
podman logs -f nanostore-bot
```

### Update Bot:
```bash
# Stop container
podman stop nanostore-bot

# Remove container
podman rm nanostore-bot

# Pull latest code
git pull origin GPT

# Rebuild image
podman build -t nanostore-bot .

# Start again
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

## 🔐 Step 8: Security Best Practices

### 1. Protect .env File:
```bash
# Set proper permissions
chmod 600 .env

# Verify
ls -la .env
# Should show: -rw------- (only owner can read/write)
```

### 2. Backup Database:
```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp data/nanostore.db backups/nanostore_$DATE.db
echo "Backup created: nanostore_$DATE.db"
EOF

# Make executable
chmod +x backup.sh

# Create backups directory
mkdir -p backups

# Run backup
./backup.sh
```

### 3. Setup Auto-Backup (Cron):
```bash
# Edit crontab
crontab -e

# Add this line (backup every day at 2 AM)
0 2 * * * /home/your-username/NanoStore/backup.sh
```

---

## 🔍 Step 9: Monitoring

### Check Resource Usage:
```bash
# CPU and Memory usage
podman stats nanostore-bot

# Press Ctrl+C to exit
```

### Check Health:
```bash
# Container health
podman inspect nanostore-bot | grep -A 5 "Health"

# Bot uptime
podman ps --filter name=nanostore-bot --format "{{.Status}}"
```

---

## 🐛 Troubleshooting

### Bot Not Starting:

**Check logs:**
```bash
podman logs nanostore-bot
```

**Common Issues:**

1. **Invalid BOT_TOKEN:**
```
Error: Unauthorized
Fix: Check BOT_TOKEN in .env file
```

2. **Database Permission Error:**
```bash
# Fix permissions
chmod 777 data/
podman restart nanostore-bot
```

3. **Port Already in Use:**
```bash
# Find process using port
sudo lsof -i :8080

# Kill process
sudo kill -9 <PID>
```

### Bot Crashes Frequently:

**Increase memory limit:**
```bash
podman stop nanostore-bot
podman rm nanostore-bot

# Run with more memory
podman run -d \
  --name nanostore-bot \
  --env-file .env \
  -v ./data:/app/data:Z \
  --memory=512m \
  --cpus=1.0 \
  --restart=always \
  nanostore-bot
```

### Database Locked Error:

```bash
# Stop bot
podman stop nanostore-bot

# Remove lock files
rm -f data/nanostore.db-shm data/nanostore.db-wal

# Start bot
podman start nanostore-bot
```

---

## 🔄 Auto-Start on Server Reboot

### Enable Auto-Start:
```bash
# Generate systemd service
podman generate systemd --new --name nanostore-bot > nanostore-bot.service

# Copy to systemd directory
sudo cp nanostore-bot.service /etc/systemd/system/

# Enable service
sudo systemctl enable nanostore-bot.service

# Start service
sudo systemctl start nanostore-bot.service

# Check status
sudo systemctl status nanostore-bot.service
```

Now bot will automatically start when server reboots!

---

## 📈 Performance Optimization

### 1. Limit Resources:
```bash
# Recommended limits for small VPS
--memory=256m      # 256MB RAM
--cpus=0.5         # Half CPU core
```

### 2. Enable Logging Rotation:
```bash
# Create logrotate config
sudo nano /etc/logrotate.d/nanostore

# Add:
/home/your-username/NanoStore/logs/*.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}
```

---

## 🎯 Quick Commands Reference

```bash
# Start bot
podman start nanostore-bot

# Stop bot
podman stop nanostore-bot

# Restart bot
podman restart nanostore-bot

# View logs
podman logs -f nanostore-bot

# Check status
podman ps

# Check resource usage
podman stats nanostore-bot

# Update bot
git pull && podman build -t nanostore-bot . && podman restart nanostore-bot

# Backup database
cp data/nanostore.db backups/backup_$(date +%Y%m%d).db
```

---

## ✅ Verification Checklist

After setup, verify:

- [ ] Podman installed and working
- [ ] Repository cloned
- [ ] .env file configured with correct values
- [ ] Image built successfully
- [ ] Container running (`podman ps` shows it)
- [ ] Bot responds to `/start` in Telegram
- [ ] Logs show no errors
- [ ] Database file created in `data/` folder
- [ ] Auto-restart enabled
- [ ] Backup script created

---

## 📞 Support

If you face any issues:

1. Check logs: `podman logs nanostore-bot`
2. Check container status: `podman ps -a`
3. Verify .env file has correct values
4. Check server resources: `free -h` and `df -h`
5. Restart bot: `podman restart nanostore-bot`

---

## 🎉 Success!

Your NanoStore bot is now running on Podman! 

Test it by:
1. Opening Telegram
2. Searching for your bot
3. Sending `/start`
4. Exploring the shop features

**Bot is production-ready with all critical fixes applied!**

---

**Last Updated**: February 25, 2026  
**Version**: 1.0 (Phase 1 Complete)
