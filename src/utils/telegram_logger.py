"""Telegram Log Channel Handler - Stream logs to Telegram channel with batching and rate limiting."""

import asyncio
import logging
import re
from datetime import datetime
from queue import Queue
from typing import Optional
from telegram import Bot
from telegram.error import TelegramError


class TelegramLogHandler(logging.Handler):
    """
    Custom logging handler that sends logs to a Telegram channel.
    
    Features:
    - Batches multiple log records into single messages (up to 3500 chars)
    - Rate limiting: max 1 message/sec
    - Background worker to avoid blocking
    - Masks sensitive data (tokens, passwords, etc.)
    - Graceful failure: never crashes the bot
    """
    
    # Secrets to mask in logs
    SECRETS_PATTERNS = [
        (re.compile(r'\d{10}:[A-Za-z0-9_-]{35}'), '[BOT_TOKEN]'),  # Bot tokens
        (re.compile(r'BOT_TOKEN=[\w:-]+'), 'BOT_TOKEN=[REDACTED]'),
        (re.compile(r'password["\']?\s*[:=]\s*["\']?[\w@#$%^&*]+', re.IGNORECASE), 'password=[REDACTED]'),
        (re.compile(r'api[_-]?key["\']?\s*[:=]\s*["\']?[\w-]+', re.IGNORECASE), 'api_key=[REDACTED]'),
        (re.compile(r'secret["\']?\s*[:=]\s*["\']?[\w-]+', re.IGNORECASE), 'secret=[REDACTED]'),
    ]
    
    def __init__(
        self,
        bot_token: str,
        channel_id: str,
        level: int = logging.INFO,
        batch_size: int = 3500,
        rate_limit: float = 1.0,
    ):
        """
        Initialize Telegram log handler.
        
        Args:
            bot_token: Telegram bot token
            channel_id: Channel ID (must start with -100)
            level: Minimum log level to send to channel
            batch_size: Max characters per message (default: 3500)
            rate_limit: Min seconds between messages (default: 1.0)
        """
        super().__init__(level)
        
        self.bot = Bot(token=bot_token)
        self.channel_id = channel_id
        self.batch_size = batch_size
        self.rate_limit = rate_limit
        
        # Validate channel ID
        if not channel_id.startswith('-100'):
            raise ValueError(f"Invalid channel ID: {channel_id}. Must start with -100")
        
        # Queue for log records
        self.queue: Queue = Queue()
        
        # Background worker
        self.worker_task: Optional[asyncio.Task] = None
        self.running = False
        
        # Batching state
        self.batch_buffer = []
        self.last_send_time = 0
        
        # Stats
        self.messages_sent = 0
        self.messages_failed = 0
    
    def emit(self, record: logging.LogRecord) -> None:
        """Add log record to queue (non-blocking)."""
        try:
            # Format the record
            msg = self.format(record)
            
            # Mask secrets
            msg = self._mask_secrets(msg)
            
            # Add to queue
            self.queue.put(msg)
        except Exception:
            # Never crash on logging
            self.handleError(record)
    
    def _mask_secrets(self, text: str) -> str:
        """Mask sensitive data in log messages."""
        for pattern, replacement in self.SECRETS_PATTERNS:
            text = pattern.sub(replacement, text)
        return text
    
    async def _send_message(self, text: str) -> bool:
        """
        Send message to Telegram channel.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            await self.bot.send_message(
                chat_id=self.channel_id,
                text=text,
                parse_mode=None,  # Plain text to avoid HTML/Markdown issues
            )
            self.messages_sent += 1
            return True
        except TelegramError as e:
            self.messages_failed += 1
            # Log to console/file only (avoid recursion)
            print(f"[TelegramLogHandler] Failed to send log: {e}")
            return False
        except Exception as e:
            self.messages_failed += 1
            print(f"[TelegramLogHandler] Unexpected error: {e}")
            return False
    
    async def _worker(self) -> None:
        """Background worker that processes log queue and sends batched messages."""
        while self.running:
            try:
                # Collect messages from queue (non-blocking)
                batch = []
                batch_length = 0
                
                while not self.queue.empty() and batch_length < self.batch_size:
                    msg = self.queue.get_nowait()
                    msg_length = len(msg) + 1  # +1 for newline
                    
                    # If adding this message exceeds batch size, send current batch first
                    if batch and batch_length + msg_length > self.batch_size:
                        break
                    
                    batch.append(msg)
                    batch_length += msg_length
                
                # Send batch if we have messages
                if batch:
                    # Rate limiting
                    now = asyncio.get_event_loop().time()
                    time_since_last = now - self.last_send_time
                    if time_since_last < self.rate_limit:
                        await asyncio.sleep(self.rate_limit - time_since_last)
                    
                    # Combine batch into single message
                    combined = '\n'.join(batch)
                    
                    # Split if still too long (safety check)
                    if len(combined) > 4000:
                        # Split into chunks
                        chunks = [combined[i:i+3500] for i in range(0, len(combined), 3500)]
                        for chunk in chunks:
                            await self._send_message(chunk)
                            await asyncio.sleep(self.rate_limit)
                    else:
                        await self._send_message(combined)
                    
                    self.last_send_time = asyncio.get_event_loop().time()
                
                # Sleep briefly before next iteration
                await asyncio.sleep(0.1)
                
            except Exception as e:
                print(f"[TelegramLogHandler] Worker error: {e}")
                await asyncio.sleep(1)
    
    def start(self, loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
        """Start the background worker."""
        if self.running:
            return
        
        self.running = True
        
        if loop is None:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        
        self.worker_task = loop.create_task(self._worker())
    
    def stop(self) -> None:
        """Stop the background worker."""
        self.running = False
        if self.worker_task:
            self.worker_task.cancel()
    
    def close(self) -> None:
        """Close the handler and stop worker."""
        self.stop()
        super().close()


class TelegramLogFormatter(logging.Formatter):
    """Custom formatter for Telegram logs with emoji and structured output."""
    
    LEVEL_EMOJI = {
        'DEBUG': '🔍',
        'INFO': 'ℹ️',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '🚨',
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with emoji, timestamp, and module info."""
        emoji = self.LEVEL_EMOJI.get(record.levelname, '📝')
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S')
        
        # Build message
        parts = [
            f"{emoji} [{record.levelname}] {timestamp}",
            f"📦 {record.module}.{record.funcName}",
        ]
        
        # Add message
        if record.getMessage():
            parts.append(f"💬 {record.getMessage()}")
        
        # Add exception info if present
        if record.exc_info:
            parts.append(f"⚡ {self.formatException(record.exc_info)[:500]}")
        
        return '\n'.join(parts)


def setup_telegram_logging(
    bot_token: str,
    channel_id: str,
    enabled: bool = True,
    channel_level: str = 'INFO',
    file_level: str = 'DEBUG',
    full_verbose: bool = False,
) -> Optional[TelegramLogHandler]:
    """
    Setup logging with Telegram channel streaming.
    
    Args:
        bot_token: Telegram bot token
        channel_id: Channel ID for logs
        enabled: Enable Telegram logging
        channel_level: Log level for channel (DEBUG/INFO/WARNING/ERROR)
        file_level: Log level for file/console
        full_verbose: Send all logs to channel (including debug)
    
    Returns:
        TelegramLogHandler instance or None if disabled
    """
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Capture everything
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler (always enabled)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, file_level.upper()))
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # Telegram handler (optional)
    telegram_handler = None
    if enabled and channel_id:
        try:
            # Validate channel ID
            if not channel_id.startswith('-100'):
                print(f"[WARNING] Invalid LOG_CHANNEL_ID: {channel_id}. Must start with -100")
                return None
            
            # Determine level
            if full_verbose:
                level = logging.DEBUG
            else:
                level = getattr(logging, channel_level.upper())
            
            # Create handler
            telegram_handler = TelegramLogHandler(
                bot_token=bot_token,
                channel_id=channel_id,
                level=level,
            )
            
            # Set formatter
            telegram_formatter = TelegramLogFormatter()
            telegram_handler.setFormatter(telegram_formatter)
            
            # Add to root logger
            root_logger.addHandler(telegram_handler)
            
            print(f"[INFO] Telegram logging enabled: channel={channel_id}, level={channel_level}")
            
        except Exception as e:
            print(f"[ERROR] Failed to setup Telegram logging: {e}")
            telegram_handler = None
    
    return telegram_handler
