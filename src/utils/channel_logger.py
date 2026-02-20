"""Channel Activity Logger - Post all bot activities to Telegram channel for audit trail."""

import logging
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
from telegram import Bot
from telegram.error import TelegramError
import pytz

logger = logging.getLogger(__name__)

# Timezone for timestamps
TIMEZONE = pytz.timezone('Asia/Karachi')


class ChannelActivityLogger:
    """
    Centralized logger that posts all bot activities to a Telegram channel.
    Provides audit trail for owner to see what happened, when, by whom.
    """
    
    def __init__(self, bot: Bot, channel_id: str, enabled: bool = True):
        """
        Initialize channel logger.
        
        Args:
            bot: Telegram bot instance
            channel_id: Channel ID to post logs (must start with -100)
            enabled: Enable/disable channel logging
        """
        self.bot = bot
        self.channel_id = channel_id
        self.enabled = enabled
        self.failed_logs = []  # Queue for failed logs to retry
        
        # Validate channel ID
        if channel_id and not channel_id.startswith('-100'):
            logger.error(f"Invalid channel ID: {channel_id}. Must start with -100")
            self.enabled = False
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in Asia/Karachi timezone."""
        return datetime.now(TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')
    
    def _format_user(self, user_id: int, full_name: str = "", username: str = "") -> str:
        """Format user information."""
        parts = []
        if full_name:
            parts.append(full_name)
        if username:
            parts.append(f"@{username}")
        parts.append(f"ID: {user_id}")
        return " | ".join(parts)
    
    async def _send_to_channel(self, message: str, parse_mode: str = "HTML") -> bool:
        """
        Send message to channel with retry logic.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.channel_id:
            return False
        
        try:
            await self.bot.send_message(
                chat_id=self.channel_id,
                text=message,
                parse_mode=parse_mode
            )
            logger.debug(f"Posted to channel: {message[:100]}...")
            return True
        
        except TelegramError as e:
            logger.error(f"Failed to post to channel: {e}")
            # Store failed log for retry
            self.failed_logs.append({
                'message': message,
                'timestamp': self._get_timestamp(),
                'error': str(e)
            })
            return False
        
        except Exception as e:
            logger.error(f"Unexpected error posting to channel: {e}")
            return False
    
    async def log_user_start(self, user_id: int, full_name: str, username: str, args: list = None):
        """Log /start command."""
        message = (
            f"🚀 <b>EVENT: USER_START</b>\n"
            f"⏰ Time: {self._get_timestamp()}\n"
            f"👤 User: {self._format_user(user_id, full_name, username)}\n"
            f"📝 Action: Executed /start command\n"
        )
        if args:
            message += f"🔗 Args: {' '.join(args)}\n"
        message += f"✅ Result: Welcome screen shown"
        
        await self._send_to_channel(message)
    
    async def log_message_received(self, user_id: int, full_name: str, username: str, text: str):
        """Log text message received."""
        # Truncate long messages
        display_text = text[:100] + "..." if len(text) > 100 else text
        
        message = (
            f"💬 <b>EVENT: MESSAGE_RECEIVED</b>\n"
            f"⏰ Time: {self._get_timestamp()}\n"
            f"👤 User: {self._format_user(user_id, full_name, username)}\n"
            f"📝 Message: {display_text}\n"
            f"✅ Result: Processed"
        )
        
        await self._send_to_channel(message)
    
    async def log_button_click(
        self,
        user_id: int,
        full_name: str,
        username: str,
        callback_data: str,
        button_name: str = "",
        result: str = "Processed"
    ):
        """Log button/callback click."""
        message = (
            f"🔘 <b>EVENT: BUTTON_CLICK</b>\n"
            f"⏰ Time: {self._get_timestamp()}\n"
            f"👤 User: {self._format_user(user_id, full_name, username)}\n"
            f"🎯 Button: {button_name or callback_data}\n"
            f"📊 Callback Data: {callback_data}\n"
            f"✅ Result: {result}"
        )
        
        await self._send_to_channel(message)
    
    async def log_menu_navigation(
        self,
        user_id: int,
        full_name: str,
        username: str,
        from_menu: str,
        to_menu: str
    ):
        """Log menu navigation."""
        message = (
            f"🧭 <b>EVENT: MENU_NAVIGATION</b>\n"
            f"⏰ Time: {self._get_timestamp()}\n"
            f"👤 User: {self._format_user(user_id, full_name, username)}\n"
            f"📍 From: {from_menu}\n"
            f"📍 To: {to_menu}\n"
            f"✅ Result: Navigation successful"
        )
        
        await self._send_to_channel(message)
    
    async def log_membership_check(
        self,
        user_id: int,
        full_name: str,
        username: str,
        status: str,
        channel_name: str = ""
    ):
        """Log membership check result."""
        emoji = "✅" if status == "member" else "⚠️"
        
        message = (
            f"{emoji} <b>EVENT: MEMBERSHIP_CHECK</b>\n"
            f"⏰ Time: {self._get_timestamp()}\n"
            f"👤 User: {self._format_user(user_id, full_name, username)}\n"
            f"📢 Channel: {channel_name}\n"
            f"📊 Status: {status}\n"
            f"✅ Result: {'Allowed' if status == 'member' else 'Blocked'}"
        )
        
        await self._send_to_channel(message)
    
    async def log_order_event(
        self,
        event_type: str,
        order_id: int,
        user_id: int,
        full_name: str,
        username: str,
        amount: float = 0,
        currency: str = "Rs",
        details: str = ""
    ):
        """Log order-related events."""
        emoji_map = {
            "created": "🛒",
            "updated": "📝",
            "cancelled": "❌",
            "completed": "✅",
            "paid": "💳"
        }
        emoji = emoji_map.get(event_type.lower(), "📦")
        
        message = (
            f"{emoji} <b>EVENT: ORDER_{event_type.upper()}</b>\n"
            f"⏰ Time: {self._get_timestamp()}\n"
            f"👤 User: {self._format_user(user_id, full_name, username)}\n"
            f"🆔 Order ID: #{order_id}\n"
        )
        if amount > 0:
            message += f"💰 Amount: {currency} {amount}\n"
        if details:
            message += f"📝 Details: {details}\n"
        message += f"✅ Result: Order {event_type}"
        
        await self._send_to_channel(message)
    
    async def log_topup_event(
        self,
        event_type: str,
        topup_id: int,
        user_id: int,
        full_name: str,
        username: str,
        amount: float,
        currency: str = "Rs",
        details: str = ""
    ):
        """Log top-up related events."""
        emoji_map = {
            "requested": "💳",
            "approved": "✅",
            "rejected": "❌"
        }
        emoji = emoji_map.get(event_type.lower(), "💰")
        
        message = (
            f"{emoji} <b>EVENT: TOPUP_{event_type.upper()}</b>\n"
            f"⏰ Time: {self._get_timestamp()}\n"
            f"👤 User: {self._format_user(user_id, full_name, username)}\n"
            f"🆔 Top-Up ID: #{topup_id}\n"
            f"💰 Amount: {currency} {amount}\n"
        )
        if details:
            message += f"📝 Details: {details}\n"
        message += f"✅ Result: Top-up {event_type}"
        
        await self._send_to_channel(message)
    
    async def log_balance_change(
        self,
        user_id: int,
        full_name: str,
        username: str,
        old_balance: float,
        new_balance: float,
        currency: str = "Rs",
        reason: str = ""
    ):
        """Log balance changes."""
        change = new_balance - old_balance
        emoji = "📈" if change > 0 else "📉"
        
        message = (
            f"{emoji} <b>EVENT: BALANCE_CHANGE</b>\n"
            f"⏰ Time: {self._get_timestamp()}\n"
            f"👤 User: {self._format_user(user_id, full_name, username)}\n"
            f"💰 Old Balance: {currency} {old_balance}\n"
            f"💰 New Balance: {currency} {new_balance}\n"
            f"📊 Change: {'+' if change > 0 else ''}{currency} {change}\n"
        )
        if reason:
            message += f"📝 Reason: {reason}\n"
        message += f"✅ Result: Balance updated"
        
        await self._send_to_channel(message)
    
    async def log_admin_action(
        self,
        admin_id: int,
        action: str,
        details: str = "",
        target: str = ""
    ):
        """Log admin actions."""
        message = (
            f"⚙️ <b>EVENT: ADMIN_ACTION</b>\n"
            f"⏰ Time: {self._get_timestamp()}\n"
            f"👤 Admin: ID {admin_id}\n"
            f"🎯 Action: {action}\n"
        )
        if target:
            message += f"📍 Target: {target}\n"
        if details:
            message += f"📝 Details: {details}\n"
        message += f"✅ Result: Action completed"
        
        await self._send_to_channel(message)
    
    async def log_config_change(
        self,
        admin_id: int,
        setting_key: str,
        old_value: str,
        new_value: str
    ):
        """Log configuration changes."""
        # Truncate long values
        old_display = old_value[:50] + "..." if len(old_value) > 50 else old_value
        new_display = new_value[:50] + "..." if len(new_value) > 50 else new_value
        
        message = (
            f"🔧 <b>EVENT: CONFIG_CHANGE</b>\n"
            f"⏰ Time: {self._get_timestamp()}\n"
            f"👤 Admin: ID {admin_id}\n"
            f"🔑 Setting: {setting_key}\n"
            f"📊 Old Value: {old_display}\n"
            f"📊 New Value: {new_display}\n"
            f"✅ Result: Configuration updated"
        )
        
        await self._send_to_channel(message)
    
    async def log_error(
        self,
        error_type: str,
        error_message: str,
        user_id: Optional[int] = None,
        context: str = ""
    ):
        """Log errors and exceptions."""
        message = (
            f"❌ <b>EVENT: ERROR</b>\n"
            f"⏰ Time: {self._get_timestamp()}\n"
            f"🚨 Type: {error_type}\n"
            f"📝 Message: {error_message[:200]}\n"
        )
        if user_id:
            message += f"👤 User ID: {user_id}\n"
        if context:
            message += f"📍 Context: {context}\n"
        message += f"⚠️ Result: Error logged"
        
        await self._send_to_channel(message)
    
    async def log_maintenance_toggle(self, admin_id: int, enabled: bool):
        """Log maintenance mode toggle."""
        status = "ENABLED" if enabled else "DISABLED"
        emoji = "🔴" if enabled else "🟢"
        
        message = (
            f"{emoji} <b>EVENT: MAINTENANCE_{status}</b>\n"
            f"⏰ Time: {self._get_timestamp()}\n"
            f"👤 Admin: ID {admin_id}\n"
            f"🔧 Action: Maintenance mode {status.lower()}\n"
            f"✅ Result: Bot {'stopped' if enabled else 'resumed'}"
        )
        
        await self._send_to_channel(message)
    
    async def log_bot_startup(self):
        """Log bot startup."""
        message = (
            f"🚀 <b>EVENT: BOT_STARTUP</b>\n"
            f"⏰ Time: {self._get_timestamp()}\n"
            f"✅ Result: Bot started successfully\n"
            f"📊 Channel logging: {'Enabled' if self.enabled else 'Disabled'}"
        )
        
        await self._send_to_channel(message)
    
    async def test_channel_post(self) -> bool:
        """Test channel posting capability."""
        message = (
            f"🧪 <b>TEST: CHANNEL_POST</b>\n"
            f"⏰ Time: {self._get_timestamp()}\n"
            f"✅ Result: Channel posting is working!\n"
            f"📊 Channel ID: {self.channel_id}"
        )
        
        return await self._send_to_channel(message)
    
    async def retry_failed_logs(self):
        """Retry sending failed logs."""
        if not self.failed_logs:
            return
        
        logger.info(f"Retrying {len(self.failed_logs)} failed logs...")
        
        retry_queue = self.failed_logs.copy()
        self.failed_logs.clear()
        
        for log_entry in retry_queue:
            success = await self._send_to_channel(log_entry['message'])
            if not success:
                # Still failing, keep in queue
                self.failed_logs.append(log_entry)
        
        if self.failed_logs:
            logger.warning(f"{len(self.failed_logs)} logs still failing after retry")


# Global instance (initialized in bot.py)
channel_logger: Optional[ChannelActivityLogger] = None


def get_channel_logger() -> Optional[ChannelActivityLogger]:
    """Get global channel logger instance."""
    return channel_logger


def set_channel_logger(logger_instance: ChannelActivityLogger):
    """Set global channel logger instance."""
    global channel_logger
    channel_logger = logger_instance
