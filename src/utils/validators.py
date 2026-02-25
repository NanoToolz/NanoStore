"""Input validation utilities for NanoStore bot."""

import re
from typing import Optional, Tuple


def validate_price(price_str: str) -> Tuple[bool, Optional[float], str]:
    """
    Validate price input.
    
    Returns:
        (is_valid, price_value, error_message)
    """
    try:
        price = float(price_str)
        
        if price < 0:
            return False, None, "❌ Price cannot be negative."
        
        if price > 1000000:
            return False, None, "❌ Price too high (max: Rs 1,000,000)."
        
        # Round to 2 decimal places
        price = round(price, 2)
        
        return True, price, ""
        
    except ValueError:
        return False, None, "❌ Invalid price format. Use numbers only (e.g., 100 or 99.99)."


def validate_stock(stock_str: str) -> Tuple[bool, Optional[int], str]:
    """
    Validate stock input.
    
    Returns:
        (is_valid, stock_value, error_message)
    """
    try:
        stock = int(stock_str)
        
        if stock < 0:
            return False, None, "❌ Stock cannot be negative."
        
        if stock > 1000000:
            return False, None, "❌ Stock too high (max: 1,000,000)."
        
        return True, stock, ""
        
    except ValueError:
        return False, None, "❌ Invalid stock format. Use whole numbers only (e.g., 100)."


def validate_quantity(qty_str: str) -> Tuple[bool, Optional[int], str]:
    """
    Validate quantity input.
    
    Returns:
        (is_valid, quantity_value, error_message)
    """
    try:
        qty = int(qty_str)
        
        if qty <= 0:
            return False, None, "❌ Quantity must be at least 1."
        
        if qty > 1000:
            return False, None, "❌ Quantity too high (max: 1,000)."
        
        return True, qty, ""
        
    except ValueError:
        return False, None, "❌ Invalid quantity format. Use whole numbers only (e.g., 5)."


def validate_discount(discount_str: str) -> Tuple[bool, Optional[float], str]:
    """
    Validate discount percentage.
    
    Returns:
        (is_valid, discount_value, error_message)
    """
    try:
        discount = float(discount_str)
        
        if discount < 0:
            return False, None, "❌ Discount cannot be negative."
        
        if discount > 100:
            return False, None, "❌ Discount cannot exceed 100%."
        
        # Round to 2 decimal places
        discount = round(discount, 2)
        
        return True, discount, ""
        
    except ValueError:
        return False, None, "❌ Invalid discount format. Use numbers only (e.g., 10 or 15.5)."


def validate_amount(amount_str: str, min_amount: float = 0, max_amount: float = 1000000) -> Tuple[bool, Optional[float], str]:
    """
    Validate monetary amount.
    
    Returns:
        (is_valid, amount_value, error_message)
    """
    try:
        amount = float(amount_str)
        
        if amount < min_amount:
            return False, None, f"❌ Amount must be at least {min_amount}."
        
        if amount > max_amount:
            return False, None, f"❌ Amount too high (max: {max_amount})."
        
        # Round to 2 decimal places
        amount = round(amount, 2)
        
        return True, amount, ""
        
    except ValueError:
        return False, None, "❌ Invalid amount format. Use numbers only (e.g., 100 or 99.99)."


def validate_coupon_code(code: str) -> Tuple[bool, str, str]:
    """
    Validate coupon code format.
    
    Returns:
        (is_valid, normalized_code, error_message)
    """
    # Remove whitespace and convert to uppercase
    code = code.strip().upper()
    
    if len(code) < 3:
        return False, "", "❌ Coupon code too short (min: 3 characters)."
    
    if len(code) > 20:
        return False, "", "❌ Coupon code too long (max: 20 characters)."
    
    # Allow only alphanumeric and underscore
    if not re.match(r'^[A-Z0-9_]+$', code):
        return False, "", "❌ Coupon code can only contain letters, numbers, and underscores."
    
    return True, code, ""


def validate_channel_id(channel_id_str: str) -> Tuple[bool, Optional[int], str]:
    """
    Validate Telegram channel ID.
    
    Returns:
        (is_valid, channel_id, error_message)
    """
    try:
        # Remove @ if present
        if channel_id_str.startswith('@'):
            return False, None, "❌ Use numeric channel ID (e.g., -1001234567890), not username."
        
        channel_id = int(channel_id_str)
        
        # Telegram channel IDs are negative and typically start with -100
        if channel_id >= 0:
            return False, None, "❌ Channel ID must be negative (e.g., -1001234567890)."
        
        return True, channel_id, ""
        
    except ValueError:
        return False, None, "❌ Invalid channel ID format. Use numbers only (e.g., -1001234567890)."


def validate_text_length(text: str, min_len: int = 1, max_len: int = 4096) -> Tuple[bool, str]:
    """
    Validate text length.
    
    Returns:
        (is_valid, error_message)
    """
    text_len = len(text)
    
    if text_len < min_len:
        return False, f"❌ Text too short (min: {min_len} characters)."
    
    if text_len > max_len:
        return False, f"❌ Text too long (max: {max_len} characters)."
    
    return True, ""


def sanitize_html(text: str) -> str:
    """
    Sanitize HTML input - allow only safe tags.
    
    Allowed tags: <b>, <i>, <u>, <s>, <code>, <pre>, <a>
    """
    from html import escape
    
    # For now, just escape all HTML to prevent injection
    # In future, can implement whitelist-based sanitization
    return escape(text)


def validate_user_id(user_id_str: str) -> Tuple[bool, Optional[int], str]:
    """
    Validate Telegram user ID.
    
    Returns:
        (is_valid, user_id, error_message)
    """
    try:
        user_id = int(user_id_str)
        
        if user_id <= 0:
            return False, None, "❌ User ID must be positive."
        
        if user_id > 9999999999:  # Telegram user IDs are typically 9-10 digits
            return False, None, "❌ Invalid user ID."
        
        return True, user_id, ""
        
    except ValueError:
        return False, None, "❌ Invalid user ID format. Use numbers only."


def validate_order_id(order_id_str: str) -> Tuple[bool, Optional[int], str]:
    """
    Validate order ID.
    
    Returns:
        (is_valid, order_id, error_message)
    """
    try:
        order_id = int(order_id_str)
        
        if order_id <= 0:
            return False, None, "❌ Order ID must be positive."
        
        return True, order_id, ""
        
    except ValueError:
        return False, None, "❌ Invalid order ID format. Use numbers only."
