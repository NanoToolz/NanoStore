"""Membership verification middleware - Force users to join channel before using bot."""

import logging
from telegram import Update, ChatMember
from telegram.ext import ContextTypes
from telegram.error import TelegramError
from database import get_force_join_channels
from utils import force_join_kb

logger = logging.getLogger(__name__)


async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Check if user is member of all required channels.
    
    Returns:
        True if user is member of all channels (or no channels configured)
        False if user needs to join channels
    """
    user = update.effective_user
    if not user:
        return True
    
    # Get required channels
    channels = await get_force_join_channels()
    if not channels:
        return True  # No channels required
    
    # Check membership in each channel
    not_joined = []
    for channel in channels:
        try:
            member = await context.bot.get_chat_member(
                chat_id=channel["channel_id"],
                user_id=user.id
            )
            
            # Check if user is actually a member
            if member.status in [ChatMember.LEFT, ChatMember.KICKED, ChatMember.BANNED]:
                not_joined.append(channel)
                logger.info(f"User {user.id} not member of {channel['name']} (status: {member.status})")
        
        except TelegramError as e:
            # If we can't check (privacy settings, bot not admin, etc.), assume not joined
            logger.warning(f"Failed to check membership for user {user.id} in {channel['name']}: {e}")
            not_joined.append(channel)
    
    if not_joined:
        # User needs to join channels
        logger.info(f"User {user.id} needs to join {len(not_joined)} channel(s)")
        return False
    
    return True


async def enforce_membership(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Enforce channel membership. If user is not a member, show join prompt.
    
    Returns:
        True if user is member (can proceed)
        False if user needs to join (action blocked)
    """
    if await check_membership(update, context):
        return True
    
    # Get channels user needs to join
    channels = await get_force_join_channels()
    
    # Build message
    text = (
        "📢 <b>Join Required Channels</b>\n\n"
        "To use this bot, you must join our channel(s).\n"
        "Click the button(s) below to join, then click 'I've Joined'."
    )
    
    # Send or edit message with join buttons
    if update.callback_query:
        query = update.callback_query
        await query.answer("⚠️ Please join our channel first!", show_alert=True)
        
        try:
            await query.message.edit_text(
                text=text,
                reply_markup=force_join_kb(channels),
                parse_mode="HTML"
            )
        except Exception:
            # If edit fails, send new message
            await query.message.reply_text(
                text=text,
                reply_markup=force_join_kb(channels),
                parse_mode="HTML"
            )
    
    elif update.message:
        await update.message.reply_text(
            text=text,
            reply_markup=force_join_kb(channels),
            parse_mode="HTML"
        )
    
    return False
