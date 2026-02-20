"""Test script to demonstrate Telegram log channel streaming."""

import asyncio
import logging
from src.config.config import BOT_TOKEN, LOG_CHANNEL_ID, LOG_TO_CHANNEL, LOG_CHANNEL_LEVEL, FULL_VERBOSE_TO_CHANNEL
from src.utils.telegram_logger import setup_telegram_logging
from src.utils.activity_logger import log_activity, log_command, log_callback_click, log_setting_update, log_order_action

logger = logging.getLogger(__name__)


async def test_logging():
    """Test the logging system."""
    
    print("=" * 60)
    print("TELEGRAM LOG CHANNEL TEST")
    print("=" * 60)
    print(f"Bot Token: {BOT_TOKEN[:20]}...")
    print(f"Log Channel ID: {LOG_CHANNEL_ID}")
    print(f"Log to Channel: {LOG_TO_CHANNEL}")
    print(f"Channel Level: {LOG_CHANNEL_LEVEL}")
    print(f"Full Verbose: {FULL_VERBOSE_TO_CHANNEL}")
    print("=" * 60)
    
    # Setup logging
    telegram_handler = setup_telegram_logging(
        bot_token=BOT_TOKEN,
        channel_id=LOG_CHANNEL_ID,
        enabled=LOG_TO_CHANNEL,
        channel_level=LOG_CHANNEL_LEVEL,
        file_level="DEBUG",
        full_verbose=FULL_VERBOSE_TO_CHANNEL,
    )
    
    if not telegram_handler:
        print("❌ Telegram logging not enabled or failed to initialize")
        return
    
    # Start the handler
    telegram_handler.start()
    print("✅ Telegram log handler started")
    
    # Wait a moment for initialization
    await asyncio.sleep(1)
    
    print("\n📤 Sending test logs to channel...")
    print("-" * 60)
    
    # Test 1: /start command
    print("Test 1: /start command")
    log_command("start", 123456789, "testuser", [])
    logger.info("User 123456789 (@testuser) executed /start command")
    await asyncio.sleep(2)
    
    # Test 2: Admin panel click
    print("Test 2: Admin panel click")
    log_callback_click("admin", 123456789, "testuser")
    logger.info("Admin panel accessed by user 123456789")
    await asyncio.sleep(2)
    
    # Test 3: Settings update
    print("Test 3: Settings update")
    log_setting_update("bot_name", "OldStore", "NanoStore", 123456789)
    logger.info("Setting 'bot_name' updated from 'OldStore' to 'NanoStore'")
    await asyncio.sleep(2)
    
    # Test 4: Order action
    print("Test 4: Order created")
    log_order_action("CREATED", 42, 123456789, "Total: Rs 1500")
    logger.info("Order #42 created by user 123456789 | Total: Rs 1500")
    await asyncio.sleep(2)
    
    # Test 5: Warning
    print("Test 5: Warning message")
    logger.warning("This is a test warning message")
    await asyncio.sleep(2)
    
    # Test 6: Error with exception
    print("Test 6: Error with exception")
    try:
        raise ValueError("This is a test exception for logging")
    except Exception as e:
        logger.error("Test exception occurred", exc_info=e)
    await asyncio.sleep(2)
    
    # Test 7: Activity logs
    print("Test 7: Various activity logs")
    log_activity("USER_START", "User 987654321 started the bot")
    log_activity("ADMIN_CLICK", "admin_settings by 123456789")
    log_activity("PAYMENT_TOPUP", "Amount: 1000 by user 123456789")
    await asyncio.sleep(2)
    
    # Test 8: Debug (only if FULL_VERBOSE is enabled)
    print("Test 8: Debug message (only if FULL_VERBOSE=true)")
    logger.debug("This is a debug message - only visible if FULL_VERBOSE_TO_CHANNEL=true")
    await asyncio.sleep(2)
    
    print("-" * 60)
    print("✅ All test logs sent!")
    print(f"📊 Stats: Sent={telegram_handler.messages_sent}, Failed={telegram_handler.messages_failed}")
    
    # Wait for queue to flush
    print("\n⏳ Waiting for queue to flush...")
    await asyncio.sleep(5)
    
    # Stop handler
    telegram_handler.stop()
    print("✅ Telegram log handler stopped")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("Check your Telegram log channel for the messages!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_logging())
