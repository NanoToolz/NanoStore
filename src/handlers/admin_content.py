"""NanoStore Admin Screen Content Manager — manage images and text for all screens."""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_ID
from database import get_setting, set_setting
from utils import safe_edit, html_escape, separator, schedule_delete
from utils import admin_content_kb, admin_content_screen_kb, CONTENT_SCREENS, back_kb

logger = logging.getLogger(__name__)


def _is_admin(user_id: int) -> bool:
    """Check if user is admin."""
    return user_id == ADMIN_ID


async def admin_content_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show Screen Content Manager main menu - list all screens."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        await query.answer("⛔ Access denied.", show_alert=True)
        return

    text = (
        f"🎨 <b>Screen Content Manager</b>\n"
        f"{separator()}\n\n"
        "Manage images and text for each screen.\n\n"
        "👇 Select a screen to edit:"
    )

    await safe_edit(query, text, reply_markup=admin_content_kb())


async def admin_content_screen_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show edit options for a specific screen."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        await query.answer("⛔ Access denied.", show_alert=True)
        return

    screen_key = query.data.split(":")[1]
    
    # Find screen label
    screen_label = screen_key
    for key, label in CONTENT_SCREENS:
        if key == screen_key:
            screen_label = label
            break

    # Get current status
    image_key = f"{screen_key}_image_id"
    text_key = f"{screen_key}_text"
    
    image_id = await get_setting(image_key, "")
    text_content = await get_setting(text_key, "")
    
    img_status = "✅ Set" if image_id else "❌ Not set"
    txt_status = "✅ Set" if text_content else "❌ Using default"

    text = (
        f"🎨 <b>{screen_label}</b>\n"
        f"{separator()}\n\n"
        f"🖼️ Image: <b>{img_status}</b>\n"
        f"📝 Text: <b>{txt_status}</b>\n\n"
        "Choose an action:"
    )

    await safe_edit(query, text, reply_markup=admin_content_screen_kb(screen_key))


async def admin_content_img_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompt admin to send a photo for this screen."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        await query.answer("⛔ Access denied.", show_alert=True)
        return

    screen_key = query.data.split(":")[1]
    
    # Find screen label
    screen_label = screen_key
    for key, label in CONTENT_SCREENS:
        if key == screen_key:
            screen_label = label
            break

    context.user_data["state"] = f"adm_img_wait:{screen_key}_image_id"
    
    text = (
        f"🖼️ <b>Set Image: {screen_label}</b>\n"
        f"{separator()}\n\n"
        "📸 Send a photo to use for this screen.\n\n"
        "<i>The photo will be shown with the screen text as a caption.</i>"
    )
    
    msg = await safe_edit(query, text, reply_markup=back_kb(f"adm_content_screen:{screen_key}"))
    
    # Store prompt message_id for deletion after photo is received
    if msg:
        context.user_data["adm_img_prompt_msg_id"] = msg.message_id


async def admin_content_txt_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompt admin to send text for this screen."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        await query.answer("⛔ Access denied.", show_alert=True)
        return

    screen_key = query.data.split(":")[1]
    
    # Find screen label
    screen_label = screen_key
    for key, label in CONTENT_SCREENS:
        if key == screen_key:
            screen_label = label
            break

    text_key = f"{screen_key}_text"
    current = await get_setting(text_key, "")
    status = f"Current: <code>{html_escape(current[:100])}</code>" if current else "❌ Not set (using default)"

    context.user_data["state"] = f"adm_txt_wait:{text_key}"
    
    text = (
        f"✍️ <b>Edit Text: {screen_label}</b>\n"
        f"{separator()}\n\n"
        f"{status}\n\n"
        "📝 Send the new text/caption for this screen.\n\n"
        "<i>HTML formatting supported: &lt;b&gt;bold&lt;/b&gt;, &lt;i&gt;italic&lt;/i&gt;</i>\n\n"
        "💡 Leave empty to use default generated text."
    )
    
    msg = await safe_edit(query, text, reply_markup=back_kb(f"adm_content_screen:{screen_key}"))
    
    # Store prompt message_id for deletion after text is received
    if msg:
        context.user_data["adm_txt_prompt_msg_id"] = msg.message_id


async def admin_content_img_clear_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear image for this screen."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        await query.answer("⛔ Access denied.", show_alert=True)
        return

    screen_key = query.data.split(":")[1]
    image_key = f"{screen_key}_image_id"
    
    await set_setting(image_key, "")
    
    # Find screen label
    screen_label = screen_key
    for key, label in CONTENT_SCREENS:
        if key == screen_key:
            screen_label = label
            break
    
    await query.answer(f"✅ {screen_label} image cleared!", show_alert=True)
    
    # Refresh screen detail
    query.data = f"adm_content_screen:{screen_key}"
    await admin_content_screen_handler(update, context)


async def admin_content_txt_clear_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear text for this screen (back to default)."""
    query = update.callback_query
    await query.answer()

    if not _is_admin(update.effective_user.id):
        await query.answer("⛔ Access denied.", show_alert=True)
        return

    screen_key = query.data.split(":")[1]
    text_key = f"{screen_key}_text"
    
    await set_setting(text_key, "")
    
    # Find screen label
    screen_label = screen_key
    for key, label in CONTENT_SCREENS:
        if key == screen_key:
            screen_label = label
            break
    
    await query.answer(f"✅ {screen_label} text reset to default!", show_alert=True)
    
    # Refresh screen detail
    query.data = f"adm_content_screen:{screen_key}"
    await admin_content_screen_handler(update, context)
