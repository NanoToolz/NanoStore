"""Activity Logger - Ultra-detailed logging for all bot activities."""

import logging
from functools import wraps
from typing import Optional, Callable, Any
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


def log_activity(activity_type: str, details: str = "") -> None:
    """
    Log activity with structured format.
    
    Args:
        activity_type: Type of activity (e.g., "USER_START", "ADMIN_CLICK", "SETTING_UPDATE")
        details: Additional details
    """
    logger.info(f"[{activity_type}] {details}")


def log_update(update: Update, context: ContextTypes.DEFAULT_TYPE, handler_name: str = "") -> None:
    """
    Log detailed information about an update.
    
    Args:
        update: Telegram update object
        context: Context object
        handler_name: Name of the handler processing this update
    """
    try:
        user = update.effective_user
        chat = update.effective_chat
        
        # Build log message
        parts = []
        
        # User info
        if user:
            username = f"@{user.username}" if user.username else "no_username"
            parts.append(f"User: {user.id} ({user.first_name} {username})")
        
        # Chat info
        if chat:
            parts.append(f"Chat: {chat.id} ({chat.type})")
        
        # Update type and content
        if update.message:
            msg = update.message
            if msg.text:
                parts.append(f"Message: {msg.text[:100]}")
            elif msg.photo:
                parts.append("Message: [PHOTO]")
            elif msg.document:
                parts.append("Message: [DOCUMENT]")
            else:
                parts.append("Message: [OTHER]")
        
        elif update.callback_query:
            query = update.callback_query
            parts.append(f"Callback: {query.data}")
        
        # Handler name
        if handler_name:
            parts.append(f"Handler: {handler_name}")
        
        # User state
        state = context.user_data.get("state")
        if state:
            parts.append(f"State: {state}")
        
        # Log it
        log_activity("UPDATE", " | ".join(parts))
        
    except Exception as e:
        logger.warning(f"Failed to log update: {e}")


def log_callback_click(callback_data: str, user_id: int, username: Optional[str] = None) -> None:
    """
    Log callback button click.
    
    Args:
        callback_data: Callback data from button
        user_id: User ID
        username: Username (optional)
    """
    user_str = f"{user_id}"
    if username:
        user_str += f" (@{username})"
    
    log_activity("CLICK", f"{callback_data} by {user_str}")


def log_command(command: str, user_id: int, username: Optional[str] = None, args: list = None) -> None:
    """
    Log command execution.
    
    Args:
        command: Command name (e.g., "start")
        user_id: User ID
        username: Username (optional)
        args: Command arguments
    """
    user_str = f"{user_id}"
    if username:
        user_str += f" (@{username})"
    
    details = f"/{command} by {user_str}"
    if args:
        details += f" args={args}"
    
    log_activity("COMMAND", details)


def log_db_action(action: str, details: str) -> None:
    """
    Log database action.
    
    Args:
        action: Action type (e.g., "INSERT", "UPDATE", "DELETE")
        details: Details about the action
    """
    log_activity(f"DB_{action}", details)


def log_setting_update(key: str, old_value: Any, new_value: Any, admin_id: int) -> None:
    """
    Log setting update.
    
    Args:
        key: Setting key
        old_value: Old value
        new_value: New value
        admin_id: Admin user ID
    """
    # Truncate long values
    old_str = str(old_value)[:50] if old_value else "None"
    new_str = str(new_value)[:50] if new_value else "None"
    
    log_activity(
        "SETTING_UPDATE",
        f"{key}: {old_str} → {new_str} by admin {admin_id}"
    )


def log_order_action(action: str, order_id: int, user_id: int, details: str = "") -> None:
    """
    Log order-related action.
    
    Args:
        action: Action type (e.g., "CREATED", "PAID", "COMPLETED")
        order_id: Order ID
        user_id: User ID
        details: Additional details
    """
    msg = f"Order #{order_id} by user {user_id}"
    if details:
        msg += f" | {details}"
    
    log_activity(f"ORDER_{action}", msg)


def log_payment_action(action: str, amount: float, user_id: int, details: str = "") -> None:
    """
    Log payment-related action.
    
    Args:
        action: Action type (e.g., "TOPUP", "REFUND")
        amount: Amount
        user_id: User ID
        details: Additional details
    """
    msg = f"Amount: {amount} by user {user_id}"
    if details:
        msg += f" | {details}"
    
    log_activity(f"PAYMENT_{action}", msg)


def log_admin_action(action: str, admin_id: int, target: str = "", details: str = "") -> None:
    """
    Log admin action.
    
    Args:
        action: Action type (e.g., "BAN_USER", "DELETE_PRODUCT")
        admin_id: Admin user ID
        target: Target of action (e.g., user_id, product_id)
        details: Additional details
    """
    msg = f"Admin {admin_id}"
    if target:
        msg += f" → {target}"
    if details:
        msg += f" | {details}"
    
    log_activity(f"ADMIN_{action}", msg)


def log_error_context(error: Exception, update: Optional[Update] = None, context: Optional[ContextTypes.DEFAULT_TYPE] = None) -> None:
    """
    Log error with full context.
    
    Args:
        error: Exception object
        update: Update object (optional)
        context: Context object (optional)
    """
    parts = [f"Error: {type(error).__name__}: {str(error)}"]
    
    if update:
        user = update.effective_user
        if user:
            parts.append(f"User: {user.id}")
        
        if update.message:
            parts.append(f"Message: {update.message.text[:50] if update.message.text else '[non-text]'}")
        elif update.callback_query:
            parts.append(f"Callback: {update.callback_query.data}")
    
    if context:
        state = context.user_data.get("state")
        if state:
            parts.append(f"State: {state}")
    
    logger.error(" | ".join(parts), exc_info=error)


def activity_logged(activity_type: str):
    """
    Decorator to automatically log function calls.
    
    Usage:
        @activity_logged("ADMIN_PANEL")
        async def admin_handler(update, context):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            # Log before execution
            user = update.effective_user
            user_str = f"{user.id}" if user else "unknown"
            if user and user.username:
                user_str += f" (@{user.username})"
            
            log_activity(activity_type, f"{func.__name__} by {user_str}")
            
            # Execute function
            try:
                result = await func(update, context, *args, **kwargs)
                return result
            except Exception as e:
                log_error_context(e, update, context)
                raise
        
        return wrapper
    return decorator


def log_handler_execution(handler_name: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Log handler execution with full context.
    
    Args:
        handler_name: Name of the handler
        update: Update object
        context: Context object
    """
    log_update(update, context, handler_name)
