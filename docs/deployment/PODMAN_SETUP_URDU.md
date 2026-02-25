# 🚀 Podman Setup Guide (Urdu/Hindi)

NanoStore bot ko apne server pe Podman se kaise chalayein - Step by step.

---

## 📋 Zarurat Ki Cheezein

### Server:
- Linux OS (Ubuntu/CentOS/Fedora)
- 512MB RAM (1GB better hai)
- 2GB storage
- Internet connection

---

## 🔧 Step 1: Podman Install Karein

### Ubuntu/Debian pe:
```bash
sudo apt update
sudo apt install -y podman
podman --version
```

### CentOS/Fedora pe:
```bash
sudo dnf install -y podman
podman --version
```

---

## 📥 Step 2: Code Download Karein

```bash
# Apne folder mein jao
cd /home/your-username

# Code download karo
git clone https://github.com/NanoToolz/NanoStore.git

# Folder mein jao
cd NanoStore

# GPT branch pe jao (yahan sab fixes hain)
git checkout GPT
```

---

## ⚙️ Step 3: Bot Ki Settings Karein

```bash
# .env file banao
cp config/.env.example .env

# Edit karo
nano .env
```

### Ye values bharein:

```bash
# Bot ka token (@BotFather se milega)
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Aapka Telegram ID (@userinfobot se milega)
ADMIN_ID=123456789

# Log channel ID (optional)
LOG_CHANNEL_ID=-1001234567890

# Database path (aise hi rakho)
DB_PATH=data/nanostore.db
```

### Values kahan se milein:

**BOT_TOKEN:**
1. Telegram pe `@BotFather` search karo
2. `/newbot` bhejo
3. Token copy karo

**ADMIN_ID:**
1. Telegram pe `@userinfobot` search karo
2. `/start` bhejo
3. ID copy karo

**LOG_CHANNEL_ID:**
1. Naya channel banao
2. Bot ko admin banao
3. Channel se koi message `@userinfobot` ko forward karo
4. ID copy karo

---

## 🏗️ Step 4: Image Banao

```bash
# Image build karo (2-3 minute lagega)
podman build -t nanostore-bot .

# Check karo bana ya nahi
podman images
```

---

## 🚀 Step 5: Bot Chalao

### Tarika 1: Podman Compose se (Easy):

```bash
# Podman compose install karo (agar nahi hai)
pip3 install podman-compose

# Bot start karo
podman-compose -f podman-compose.yml up -d

# Check karo chal raha hai
podman-compose ps
```

### Tarika 2: Seedha Podman se:

```bash
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

## ✅ Step 6: Check Karein Bot Chal Raha Hai

### Container dekho:
```bash
podman ps
```

### Logs dekho:
```bash
podman logs -f nanostore-bot
```

### Telegram pe test karo:
1. Apna bot search karo
2. `/start` bhejo
3. Bot reply karega!

---

## 🔄 Bot Ko Manage Karein

### Bot band karo:
```bash
podman stop nanostore-bot
```

### Bot chalu karo:
```bash
podman start nanostore-bot
```

### Bot restart karo:
```bash
podman restart nanostore-bot
```

### Logs dekho:
```bash
# Last 100 lines
podman logs --tail 100 nanostore-bot

# Live logs (Ctrl+C se band karo)
podman logs -f nanostore-bot
```

### Bot update karo:
```bash
# Bot band karo
podman stop nanostore-bot
podman rm nanostore-bot

# Naya code download karo
git pull origin GPT

# Naya image banao
podman build -t nanostore-bot .

# Phir se chalu karo
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

## 🔐 Security Tips

### .env file ko protect karo:
```bash
chmod 600 .env
```

### Database ka backup lo:
```bash
# Backup folder banao
mkdir -p backups

# Backup lo
cp data/nanostore.db backups/backup_$(date +%Y%m%d).db
```

### Automatic backup setup karo:
```bash
# Crontab edit karo
crontab -e

# Ye line add karo (har roz 2 AM pe backup)
0 2 * * * cp /home/your-username/NanoStore/data/nanostore.db /home/your-username/NanoStore/backups/backup_$(date +\%Y\%m\%d).db
```

---

## 🔄 Server Restart Pe Auto-Start

```bash
# Systemd service banao
podman generate systemd --new --name nanostore-bot > nanostore-bot.service

# Service copy karo
sudo cp nanostore-bot.service /etc/systemd/system/

# Enable karo
sudo systemctl enable nanostore-bot.service

# Start karo
sudo systemctl start nanostore-bot.service
```

Ab server restart hone pe bot khud start hoga!

---

## 🐛 Agar Problem Aaye

### Bot start nahi ho raha:

**Logs check karo:**
```bash
podman logs nanostore-bot
```

**Common problems:**

1. **Token galat hai:**
   - .env file mein BOT_TOKEN check karo
   - @BotFather se naya token lo

2. **Database permission error:**
```bash
chmod 777 data/
podman restart nanostore-bot
```

3. **Memory kam hai:**
```bash
# Zyada memory do
podman stop nanostore-bot
podman rm nanostore-bot

podman run -d \
  --name nanostore-bot \
  --env-file .env \
  -v ./data:/app/data:Z \
  --memory=512m \
  --cpus=1.0 \
  --restart=always \
  nanostore-bot
```

---

## 🎯 Quick Commands (Yaad Rakho)

```bash
# Bot start
podman start nanostore-bot

# Bot stop
podman stop nanostore-bot

# Bot restart
podman restart nanostore-bot

# Logs dekho
podman logs -f nanostore-bot

# Status check
podman ps

# Resource usage
podman stats nanostore-bot

# Backup
cp data/nanostore.db backups/backup_$(date +%Y%m%d).db
```

---

## ✅ Final Checklist

Setup ke baad ye sab check karo:

- [ ] Podman install hai
- [ ] Code download hua
- [ ] .env file sahi values se bhari hai
- [ ] Image ban gayi
- [ ] Container chal raha hai
- [ ] Bot Telegram pe reply kar raha hai
- [ ] Logs mein koi error nahi
- [ ] Database file ban gayi
- [ ] Auto-restart enable hai
- [ ] Backup script bana di

---

## 🎉 Mubarak Ho!

Aapka NanoStore bot ab live hai! 

Test karo:
1. Telegram kholo
2. Apna bot search karo
3. `/start` bhejo
4. Shop explore karo

**Bot production-ready hai with all security fixes!**

---

## 📞 Help Chahiye?

Agar koi problem aaye:

1. Logs dekho: `podman logs nanostore-bot`
2. Container status: `podman ps -a`
3. .env file check karo
4. Server resources: `free -h` aur `df -h`
5. Bot restart karo: `podman restart nanostore-bot`

---

**Last Updated**: 25 February 2026  
**Version**: 1.0 (Phase 1 Complete - All 23 Critical Fixes Applied)
