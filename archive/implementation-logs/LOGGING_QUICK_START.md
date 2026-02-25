# Telegram Log Channel - Quick Start Guide

## 🚀 5-Minute Setup

### Step 1: Create Channel
1. Open Telegram
2. Create new channel (private recommended)
3. Name it "NanoStore Logs" or similar

### Step 2: Add Bot as Admin
1. Open channel settings → Administrators
2. Add your bot
3. Enable "Post Messages" permission
4. Save

### Step 3: Get Channel ID
1. Forward any message from the channel to @userinfobot
2. Copy the channel ID (example: `-1001234567890`)
3. **IMPORTANT**: Must start with `-100`

### Step 4: Update .env
```bash
# Add these lines to your .env file
LOG_TO_CHANNEL=true
LOG_CHANNEL_ID=-1001234567890  # Your channel ID here
LOG_CHANNEL_LEVEL=INFO
FULL_VERBOSE_TO_CHANNEL=false
```

### Step 5: Test
```bash
# Run test script
python test_logging.py

# Check your channel for test messages
```

### Step 6: Start Bot
```bash
python bot.py
```

You should see logs streaming to your channel! 🎉

---

## 📋 .env Settings Explained

```bash
# Enable/disable channel logging
LOG_TO_CHANNEL=true          # true = enabled, false = disabled

# Your channel ID (get from @userinfobot)
LOG_CHANNEL_ID=-1001234567890  # MUST start with -100

# What level of logs to send to channel
LOG_CHANNEL_LEVEL=INFO       # INFO = important events only
                             # WARNING = warnings and errors only
                             # ERROR = errors only
                             # DEBUG = everything (not recommended)

# Console/file log level
LOG_LEVEL=DEBUG              # DEBUG = see everything in console

# Send ALL logs to channel (including debug)
FULL_VERBOSE_TO_CHANNEL=false  # false = recommended
                               # true = spam warning!
```

---

## 📊 What You'll See in Channel

### User Actions
```
ℹ️ [INFO] 14:23:45
📦 start.start_handler
💬 User 123456789 (@username) executed /start command
```

### Button Clicks
```
ℹ️ [INFO] 14:24:12
📦 activity_logger.log_callback_click
💬 [CLICK] admin by 123456789 (@username)
```

### Settings Updates
```
ℹ️ [INFO] 14:25:33
📦 database.set_setting
💬 [DB_UPDATE] Setting: bot_name = NanoStore
```

### Errors
```
❌ [ERROR] 14:26:01
📦 admin.admin_handler
💬 Error: ValueError: Invalid input
⚡ Traceback...
```

---

## 🔧 Troubleshooting

### ❌ No logs appearing?

**Check 1: Channel ID format**
```bash
# Must start with -100
LOG_CHANNEL_ID=-1001234567890  ✅ Correct
LOG_CHANNEL_ID=-1234567890     ❌ Wrong
LOG_CHANNEL_ID=1234567890      ❌ Wrong
```

**Check 2: Bot is admin**
- Open channel → Administrators
- Your bot should be in the list
- "Post Messages" must be enabled

**Check 3: .env syntax**
```bash
LOG_TO_CHANNEL=true   ✅ Correct (lowercase)
LOG_TO_CHANNEL=True   ❌ Wrong
LOG_TO_CHANNEL=TRUE   ❌ Wrong
```

**Check 4: Run test**
```bash
python test_logging.py
# Should show "✅ All test logs sent!"
```

### 📬 Too many logs?

**Solution 1: Increase level**
```bash
LOG_CHANNEL_LEVEL=WARNING  # Only warnings and errors
```

**Solution 2: Disable verbose**
```bash
FULL_VERBOSE_TO_CHANNEL=false
```

### ⏱️ Logs delayed?

**Normal behavior:**
- Logs are batched every 1 second
- This is intentional (rate limiting)
- Reduces Telegram API calls

---

## 🎯 Recommended Settings

### For Production
```bash
LOG_TO_CHANNEL=true
LOG_CHANNEL_LEVEL=INFO
LOG_LEVEL=INFO
FULL_VERBOSE_TO_CHANNEL=false
```

### For Development
```bash
LOG_TO_CHANNEL=true
LOG_CHANNEL_LEVEL=DEBUG
LOG_LEVEL=DEBUG
FULL_VERBOSE_TO_CHANNEL=true
```

### For Debugging Issues
```bash
LOG_TO_CHANNEL=true
LOG_CHANNEL_LEVEL=DEBUG
LOG_LEVEL=DEBUG
FULL_VERBOSE_TO_CHANNEL=true
```

---

## 📚 Full Documentation

See `docs/LOGGING.md` for:
- Complete API reference
- Advanced configuration
- Custom formatters
- Security best practices
- Performance tuning

---

## ✅ Verification Checklist

- [ ] Channel created
- [ ] Bot added as admin with "Post Messages" permission
- [ ] Channel ID obtained (starts with -100)
- [ ] .env updated with correct channel ID
- [ ] LOG_TO_CHANNEL=true
- [ ] Test script runs successfully
- [ ] Logs appearing in channel
- [ ] Bot starts without errors

---

## 🆘 Still Having Issues?

1. Check console output for errors
2. Verify bot token is correct
3. Ensure channel is not deleted
4. Try creating a new channel
5. Check bot permissions in channel
6. Run: `python test_logging.py` and check output

---

## 🎉 Success!

Once setup, you'll see:
- Every /start command
- All button clicks
- Admin actions
- Settings changes
- Orders and payments
- Errors with full context

All in real-time in your Telegram channel! 📱
