"""Helper utilities for NanoStore Bot."""

from telegram.error import BadRequest
import logging

logger = logging.getLogger(__name__)


async def safe_edit(query, text, **kwargs):
    """Safely edit a message, handling photo messages, parse errors, and unchanged content.
    
    Priority:
    1. Try edit_message_text (works for text messages)
    2. Try edit_message_caption (works for photo/media messages)
    3. Delete old message and send new one (final fallback)
    
    Also handles:
    - ParseMode errors (retries without parse_mode)
    - 'Message is not modified' errors (silently ignored)
    """
    # Attempt 1: edit_message_text
    try:
        return await query.edit_message_text(text, **kwargs)
    except BadRequest as e:
        error_msg = str(e).lower()
        
        # Message is not modified — no changes needed
        if "message is not modified" in error_msg:
            return None
        
        # Can't parse entities — retry without parse_mode
        if "can't parse entities" in error_msg:
            kwargs_no_parse = {k: v for k, v in kwargs.items() if k != "parse_mode"}
            try:
                return await query.edit_message_text(text, **kwargs_no_parse)
            except BadRequest:
                pass
        
        # No text in message (it's a photo/media message) — try caption
        if "there is no text in the message" in error_msg or "message can't be edited" in error_msg:
            pass  # Fall through to Attempt 2
        else:
            # Unknown BadRequest, still try caption
            logger.warning(f"safe_edit: edit_message_text failed: {e}")
    except Exception as e:
        logger.warning(f"safe_edit: edit_message_text unexpected error: {e}")

    # Attempt 2: edit_message_caption (for photo messages)
    try:
        return await query.edit_message_caption(caption=text, **kwargs)
    except BadRequest as e:
        error_msg = str(e).lower()
        
        if "message is not modified" in error_msg:
            return None
        
        if "can't parse entities" in error_msg:
            kwargs_no_parse = {k: v for k, v in kwargs.items() if k != "parse_mode"}
            try:
                return await query.edit_message_caption(caption=text, **kwargs_no_parse)
            except BadRequest:
                pass
        
        logger.warning(f"safe_edit: edit_message_caption failed: {e}")
    except Exception as e:
        logger.warning(f"safe_edit: edit_message_caption unexpected error: {e}")

    # Attempt 3: Delete old message and send a new one
    try:
        chat = query.message.chat
        try:
            await query.message.delete()
        except Exception:
            pass  # Message might already be deleted
        
        try:
            return await chat.send_message(text, **kwargs)
        except BadRequest as e:
            if "can't parse entities" in str(e).lower():
                kwargs_no_parse = {k: v for k, v in kwargs.items() if k != "parse_mode"}
                return await chat.send_message(text, **kwargs_no_parse)
            raise
    except Exception as e:
        logger.error(f"safe_edit: all attempts failed: {e}")
        return None
