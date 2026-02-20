# Telegram Log Channel Streaming

Ultra-detailed activity logging system that streams all bot activities to a Telegram channel in real-time.

## Features

### 🎯 Core Capabilities
- **Real-time streaming**: All logs sent to Telegram channel instantly
- **Batching**: Combines multiple logs into single messages (up to 3500 chars)
- **Rate limiting**: Max 1 message/sec to avoid Telegram limits
- **Non-blocking**: Background worker, never blocks bot operations
- **Secret masking**: Automatically hides BOT_TOKEN, passwords, API keys
- **Graceful failure**: Never crashes the bot, falls back to file logging

### 📊 What Gets Logged

#### User Activities
- `/start` commands with user ID, username, and args
- All button clicks (callback_data) with user info
- Menu navigation
- Search queries
- Cart operations
- Order creation and updates

#### Admin Activities
- Admin panel access
- Settings updates (old → new values)
- Image/text content updates
- User bans/unbans
- Product/category management
- Order status changes
- Payment proof approvals

#### System Events
- Bot startup/shutdown
- Database operations
- Currency rate updates
- Auto-delivery executions
- Scheduled task completions

#### Errors & Exceptions
- Full stack traces
- User context (ID, username, current state)
- Update context (message/callback data)
- Handler name that failed

## Configuration

### Environment Variables (.env)

```bash
# ════════════════════════════════════════
# Logging Configuration
# ════════════════════════════════════════

# Enable/disable Telegram channel logging (true/false)
LOG_TO_CHANNEL=true

# Channel ID for logs (MUST start with -100)
# Get this from @userinfobot by forwarding a channel message
LOG_CHANNEL_ID=-1001234567890

# Console/file log level (DEBUG/INFO/WARNING/ERROR)
LOG_LEVEL=DEBUG

# Telegram channel log level (DEBUG/INFO/WARNING/ERROR)
# Recommended: INFO (only important events)
LOG_CHANNEL_LEVEL=INFO

# Send ALL logs to channel including debug (true/false)
# WARNING: This will spam the channel with every internal operation
# Only enable for deep debugging
FULL_VERBOSE_TO_CHANNEL=false
```

### Setup Steps

1. **Create a Telegram Channel**
   ```
   - Open Telegram
   - Create new channel (private or public)
   - Add your bot as admin with "Post Messages" permission
   ```

2. **Get Channel ID**
   ```
   - Forward any message from the channel to @userinfobot
   - Copy the channel ID (starts with -100)
   - Example: -1001234567890
   ```

3. **Update .env**
   ```bash
   LOG_CHANNEL_ID=-1001234567890
   LOG_TO_CHANNEL=true
   LOG_CHANNEL_LEVEL=INFO
   ```

4. **Restart Bot**
   ```bash
   python bot.py
   ```

5. **Verify**
   - Check channel for "Bot starting..." message
   - Run test: `python test_logging.py`

## Log Format

### Standard Log Entry
```
ℹ️ [INFO] 14:23:45
📦 start.start_handler
💬 User 123456789 (@username) executed /start command
```

### Callback Click
```
ℹ️ [INFO] 14:24:12
📦 activity_logger.log_callback_click
💬 [CLICK] admin by 123456789 (@username)
```

### Setting Update
```
ℹ️ [INFO] 14:25:33
📦 database.set_setting
💬 [DB_UPDATE] Setting: bot_name = NanoStore
```

### Error with Context
```
❌ [ERROR] 14:26:01
📦 admin.admin_handler
💬 Error: ValueError: Invalid input
⚡ Traceback (most recent call last):
  File "admin.py", line 123, in admin_handler
    raise ValueError("Invalid input")
ValueError: Invalid input
```

## Log Levels

### DEBUG
- Internal operations
- Database queries
- Cache hits/misses
- Function entry/exit
- **Not sent to channel by default**

### INFO
- User commands
- Button clicks
- Settings updates
- Order creation
- Payment actions
- **Default channel level**

### WARNING
- Failed operations (non-critical)
- Fallback to defaults
- Invalid user input
- Rate limit warnings

### ERROR
- Exceptions with stack traces
- Failed database operations
- Telegram API errors
- Critical failures

### CRITICAL
- Bot shutdown
- Database corruption
- Unrecoverable errors

## Security

### Secret Masking
The following patterns are automatically masked in logs:

- **Bot Tokens**: `1234567890:ABC...` → `[BOT_TOKEN]`
- **Passwords**: `password=secret123` → `password=[REDACTED]`
- **API Keys**: `api_key=abc123` → `api_key=[REDACTED]`
- **Secrets**: `secret=xyz789` → `secret=[REDACTED]`

### Privacy
- User messages are truncated to 100 chars
- Full names are logged (needed for admin tracking)
- Private data (passwords, tokens) never logged
- Payment details logged as amounts only (no card numbers)

## Performance

### Batching
- Logs are batched into single messages (up to 3500 chars)
- Reduces Telegram API calls by ~80%
- Messages sent every 1 second (rate limit)

### Background Worker
- Non-blocking queue-based system
- Never delays bot responses
- Graceful degradation on failures

### Resource Usage
- Memory: ~5MB for queue (10,000 logs)
- CPU: <1% (background worker)
- Network: ~1 request/sec to Telegram

## Troubleshooting

### Logs Not Appearing in Channel

1. **Check Channel ID**
   ```bash
   # Must start with -100
   LOG_CHANNEL_ID=-1001234567890
   ```

2. **Verify Bot is Admin**
   - Open channel settings
   - Check administrators list
   - Bot must have "Post Messages" permission

3. **Check .env Settings**
   ```bash
   LOG_TO_CHANNEL=true  # Not "True" or "TRUE"
   ```

4. **Test Manually**
   ```bash
   python test_logging.py
   ```

### Too Many Logs

1. **Increase Channel Level**
   ```bash
   LOG_CHANNEL_LEVEL=WARNING  # Only warnings and errors
   ```

2. **Disable Verbose Mode**
   ```bash
   FULL_VERBOSE_TO_CHANNEL=false
   ```

3. **Filter by Module**
   - Edit `src/utils/telegram_logger.py`
   - Add module filters in `emit()` method

### Logs Delayed

- Normal: Logs batched every 1 second
- Check queue size: `telegram_handler.queue.qsize()`
- If queue > 1000, increase rate limit or reduce log level

## Testing

### Run Test Script
```bash
python test_logging.py
```

This will send:
1. /start command log
2. Admin panel click
3. Settings update
4. Order creation
5. Warning message
6. Error with exception
7. Various activity logs
8. Debug message (if FULL_VERBOSE=true)

### Expected Output
Check your log channel for 8 messages within 10 seconds.

## API Reference

### Activity Logger Functions

```python
from utils.activity_logger import (
    log_activity,
    log_command,
    log_callback_click,
    log_setting_update,
    log_order_action,
    log_payment_action,
    log_admin_action,
    log_error_context,
)

# Log generic activity
log_activity("USER_START", "User 123 started bot")

# Log command
log_command("start", user_id=123, username="john", args=["ref_456"])

# Log button click
log_callback_click("admin", user_id=123, username="john")

# Log setting update
log_setting_update("bot_name", "OldName", "NewName", admin_id=123)

# Log order action
log_order_action("CREATED", order_id=42, user_id=123, details="Total: Rs 1500")

# Log payment
log_payment_action("TOPUP", amount=1000, user_id=123, details="Method: JazzCash")

# Log admin action
log_admin_action("BAN_USER", admin_id=123, target="user_456", details="Spam")

# Log error with context
try:
    raise ValueError("Test error")
except Exception as e:
    log_error_context(e, update, context)
```

### Decorator for Auto-Logging

```python
from utils.activity_logger import activity_logged

@activity_logged("ADMIN_PANEL")
async def admin_handler(update, context):
    # Function automatically logged on entry
    pass
```

## Examples

### Log User Registration
```python
from utils.activity_logger import log_activity

await ensure_user(user_id, name, username)
log_activity("USER_REGISTERED", f"New user: {user_id} (@{username})")
```

### Log Order Completion
```python
from utils.activity_logger import log_order_action

await update_order(order_id, status="completed")
log_order_action("COMPLETED", order_id, user_id, f"Total: Rs {total}")
```

### Log Admin Ban
```python
from utils.activity_logger import log_admin_action

await ban_user(target_user_id)
log_admin_action("BAN_USER", admin_id, target=target_user_id, details="Violation")
```

## Best Practices

1. **Use Appropriate Levels**
   - DEBUG: Internal operations
   - INFO: User actions
   - WARNING: Recoverable errors
   - ERROR: Exceptions
   - CRITICAL: System failures

2. **Keep Messages Concise**
   - Truncate long strings
   - Use abbreviations
   - Focus on key info

3. **Mask Sensitive Data**
   - Never log passwords
   - Mask tokens/keys
   - Truncate user messages

4. **Batch Related Logs**
   - Group related operations
   - Use single log for multi-step actions
   - Avoid log spam

5. **Monitor Channel**
   - Check for errors daily
   - Set up alerts for CRITICAL logs
   - Archive old messages

## Advanced Configuration

### Custom Log Formatter

Edit `src/utils/telegram_logger.py`:

```python
class CustomFormatter(TelegramLogFormatter):
    def format(self, record):
        # Custom formatting logic
        return f"🤖 {record.getMessage()}"
```

### Module-Specific Levels

```python
# In bot.py
logging.getLogger('database').setLevel(logging.WARNING)
logging.getLogger('admin').setLevel(logging.INFO)
```

### Custom Filters

```python
class AdminOnlyFilter(logging.Filter):
    def filter(self, record):
        return 'admin' in record.module.lower()

telegram_handler.addFilter(AdminOnlyFilter())
```

## Maintenance

### Clear Old Logs
- Telegram channels auto-delete after 1 year (free)
- Or manually delete old messages
- No impact on bot operation

### Monitor Queue Size
```python
# In bot.py
if telegram_handler.queue.qsize() > 1000:
    logger.warning("Log queue backing up!")
```

### Rotate Log Files
```python
# Add to bot.py
from logging.handlers import RotatingFileHandler

file_handler = RotatingFileHandler(
    'bot.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
```

## Support

For issues or questions:
1. Check this documentation
2. Run `python test_logging.py`
3. Check console output for errors
4. Verify .env settings
5. Check bot is admin in channel
