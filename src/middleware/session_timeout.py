"""Session timeout middleware for NanoStore bot."""

import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes, BaseHandler

logger = logging.getLogger(__name__)

# Session timeout duration (1 hour)
SESSION_TIMEOUT = timedelta(hours=1)


async def check_session_timeout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Check if user session has expired and clear stale data.
    
    Returns:
        True if session is valid, False if expired
    """
    if not update.effective_user:
        return True
    
    user_id = update.effective_user.id
    last_activity = context.user_data.get("last_activity")
    
    if last_activity:
        # Check if session has expired
        if datetime.utcnow() - last_activity > SESSION_TIMEOUT:
            logger.info(f"Session expired for user {user_id}")
            
            # Clear expired session data
            context.user_data.clear()
            
            # Notify user if they had pending state
            if update.message:
                try:
                    await update.message.reply_text(
                        "⏱️ Your session has expired due to inactivity.\n"
                        "Please start again with /start"
                    )
                except Exception as e:
                    logger.error(f"Failed to notify user about session expiry: {e}")
            
            return False
    
    # Update last activity timestamp
    context.user_data["last_activity"] = datetime.utcnow()
    return True


class SessionTimeoutMiddleware(BaseHandler):
    """Middleware to check session timeout on every update."""
    
    def check_update(self, update: object) -> bool:
        """Check if this handler should process the update."""
        return isinstance(update, Update)
    
    async def handle_update(
        self,
        update: Update,
        application,
        check_result,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """Check session timeout before processing update."""
        await check_session_timeout(update, context)
