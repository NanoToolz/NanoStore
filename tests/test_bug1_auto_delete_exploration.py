"""
Bug 1 Exploration Test: Auto-Delete Messages Not Working

**Validates: Requirements 1.1, 1.2, 1.3, 1.4**

CRITICAL: This test MUST FAIL on unfixed code - failure confirms the bug exists.
DO NOT attempt to fix the test or the code when it fails.

This test encodes the expected behavior - it will validate the fix when it passes after implementation.

GOAL: Surface counterexamples that demonstrate the bug exists.

ROOT CAUSE IDENTIFIED:
- The auto_delete() function itself works correctly (handles None, RuntimeError, etc.)
- The BUG is that auto_delete() is NOT CALLED on admin prompt messages
- Admin prompts like "Send product name", "Send description", etc. remain in chat
- These temporary messages clutter the chat and should be auto-deleted

Test Strategy:
- Test that admin prompt messages DO NOT call auto_delete() (this is the bug)
- Test that the auto_delete() function itself works correctly (preservation)
- Verify that /start command calls auto_delete() correctly
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch, call
from hypothesis import given, strategies as st, settings, Phase
from helpers import auto_delete


class TestAutoDeleteExploration:
    """Exploration tests to surface counterexamples demonstrating the auto-delete bug."""

    @pytest.mark.asyncio
    async def test_admin_prompt_messages_not_auto_deleted(self):
        """
        Test that admin prompt messages DO NOT call auto_delete().
        
        **Validates: Requirements 1.3**
        
        EXPECTED: This test FAILS on unfixed code (auto_delete not called on prompts).
        This failure confirms the bug exists - admin prompts are not auto-deleted.
        
        ROOT CAUSE: The bug is NOT in auto_delete() function itself, but in the
        handlers that send admin prompt messages. They don't call auto_delete().
        """
        from handlers.admin import admin_text_router
        
        # Setup: Create mock update and context for product creation flow
        mock_update = MagicMock()
        mock_update.effective_user.id = 12345  # Assume this is admin
        mock_update.message = AsyncMock()
        mock_update.message.text = "Test Product"
        mock_update.message.reply_text = AsyncMock(return_value=AsyncMock())
        
        mock_context = MagicMock()
        mock_context.user_data = {
            "state": "adm_prod_name:1",  # Product creation state
            "temp": {}
        }
        
        # Mock auto_delete to track if it's called
        with patch('helpers.auto_delete', new_callable=AsyncMock) as mock_auto_delete:
            # Call the admin text router (simulates admin sending product name)
            await admin_text_router(mock_update, mock_context)
            
            # EXPECTED BEHAVIOR: auto_delete should be called on the prompt message
            # BUG: auto_delete is NOT called on admin prompt messages
            # The prompt "Step 2/3: Send the product description" remains in chat
            
            # Check if auto_delete was called
            if not mock_auto_delete.called:
                pytest.fail(
                    "Bug confirmed: Admin prompt messages do NOT call auto_delete(). "
                    "The prompt message 'Step 2/3: Send the product description' should be auto-deleted "
                    "to keep the chat clean, but auto_delete() was never called."
                )

    @pytest.mark.asyncio
    async def test_start_command_calls_auto_delete(self):
        """
        Test that /start command DOES call auto_delete().
        
        **Validates: Requirements 1.2**
        
        EXPECTED: This test PASSES on unfixed code (start handler already calls auto_delete).
        This is preservation behavior - /start command correctly calls auto_delete().
        """
        from handlers.start import start_handler
        
        # Setup: Create mock update and context
        mock_update = MagicMock()
        mock_update.effective_user.id = 12345
        mock_update.effective_user.first_name = "TestUser"
        mock_update.effective_user.username = "testuser"
        mock_update.message = AsyncMock()
        mock_update.message.chat_id = 12345
        mock_update.message.reply_text = AsyncMock(return_value=AsyncMock())
        
        mock_context = MagicMock()
        mock_context.bot = AsyncMock()
        
        # Mock database and helper functions
        with patch('handlers.start.ensure_user', new_callable=AsyncMock), \
             patch('handlers.start.is_user_banned', new_callable=AsyncMock, return_value=False), \
             patch('handlers.start.get_setting', new_callable=AsyncMock) as mock_get_setting, \
             patch('handlers.start.check_force_join', new_callable=AsyncMock, return_value=[]), \
             patch('handlers.start.send_typing', new_callable=AsyncMock), \
             patch('handlers.start.add_action_log', new_callable=AsyncMock), \
             patch('handlers.start.notify_log_channel', new_callable=AsyncMock), \
             patch('handlers.start.get_user_order_count', new_callable=AsyncMock, return_value=0), \
             patch('handlers.start.get_user_balance', new_callable=AsyncMock, return_value=0), \
             patch('helpers.auto_delete', new_callable=AsyncMock) as mock_auto_delete:
            
            mock_get_setting.side_effect = lambda key, default="": {
                "bot_name": "TestBot",
                "welcome_image_id": "",
                "maintenance": "off",
                "currency": "Rs",
                "welcome_text": ""
            }.get(key, default)
            
            # Call start handler
            await start_handler(mock_update, mock_context)
            
            # EXPECTED BEHAVIOR: auto_delete should be called on the /start message
            assert mock_auto_delete.called, (
                "/start command should call auto_delete() on the command message"
            )
            # Verify it was called with the correct message
            assert mock_auto_delete.call_args[0][0] == mock_update.message, (
                "auto_delete() should be called with update.message"
            )

    @pytest.mark.asyncio
    async def test_auto_delete_function_works_correctly(self):
        """
        Test that the auto_delete() function itself works correctly.
        
        **Validates: Requirements 2.1, 2.4, 2.5**
        
        EXPECTED: This test PASSES on both unfixed and fixed code.
        This is preservation behavior - the auto_delete() function is correctly implemented.
        """
        # Setup: Create a mock message
        mock_message = AsyncMock()
        mock_message.delete = AsyncMock()
        
        # Test 1: None handling
        with patch('database.get_setting', new_callable=AsyncMock) as mock_get_setting:
            mock_get_setting.return_value = None
            
            # Should handle None gracefully (no exception)
            await auto_delete(mock_message)
            # If we get here, None was handled correctly

        # Test 2: Positive setting creates task
        with patch('database.get_setting', new_callable=AsyncMock) as mock_get_setting:
            mock_get_setting.return_value = "1"
            
            with patch('asyncio.create_task') as mock_create_task:
                mock_create_task.return_value = MagicMock()
                await auto_delete(mock_message)
                assert mock_create_task.called, "Should create task when setting > 0"

        # Test 3: RuntimeError handling
        with patch('database.get_setting', new_callable=AsyncMock) as mock_get_setting:
            mock_get_setting.return_value = "30"
            
            with patch('asyncio.create_task', side_effect=RuntimeError("No event loop")):
                # Should catch RuntimeError and not crash
                await auto_delete(mock_message)
                # If we get here, RuntimeError was handled correctly

        # Test 4: Zero setting does not create task
        with patch('database.get_setting', new_callable=AsyncMock) as mock_get_setting:
            mock_get_setting.return_value = "0"
            
            with patch('asyncio.create_task') as mock_create_task:
                await auto_delete(mock_message)
                assert not mock_create_task.called, "Should NOT create task when setting=0"

    @pytest.mark.asyncio
    @given(
        auto_delete_setting=st.integers(min_value=1, max_value=60),
    )
    @settings(
        max_examples=5,
        phases=[Phase.generate, Phase.target],
        deadline=None,
    )
    async def test_property_auto_delete_function_creates_tasks(self, auto_delete_setting):
        """
        Property 1: Auto-Delete Function Creates Tasks for Positive Settings
        
        **Validates: Requirements 2.1**
        
        For any positive auto_delete setting, the auto_delete() function should create
        an asyncio task to delete the message after the specified delay.
        
        This property test verifies the function works correctly across many input values.
        """
        # Setup: Create a mock message
        mock_message = AsyncMock()
        mock_message.delete = AsyncMock()
        
        # Setup: Set auto_delete setting to the generated value
        with patch('database.get_setting', new_callable=AsyncMock) as mock_get_setting:
            mock_get_setting.return_value = str(auto_delete_setting)
            
            # Mock asyncio.create_task to verify it's called
            with patch('asyncio.create_task') as mock_create_task:
                mock_create_task.return_value = MagicMock()
                
                # Call auto_delete
                await auto_delete(mock_message)
                
                # EXPECTED BEHAVIOR: create_task should be called for any positive setting
                assert mock_create_task.called, (
                    f"auto_delete() with setting={auto_delete_setting} should create an asyncio task"
                )


# SUMMARY OF FINDINGS:
# 
# The auto_delete() function in helpers.py is CORRECTLY IMPLEMENTED:
# - Handles None values gracefully with `int(raw or 0)`
# - Catches RuntimeError when no event loop is running
# - Creates asyncio tasks correctly for positive settings
# - Respects setting=0 (disabled) and explicit delay parameters
#
# The ACTUAL BUG is in the handlers:
# - Admin prompt messages (in handlers/admin.py) DO NOT call auto_delete()
# - These temporary prompts like "Send product name", "Send description", etc.
#   remain in the chat and clutter it
# - The /start command (in handlers/start.py) DOES call auto_delete() correctly
#
# FIX REQUIRED:
# - Add auto_delete() calls to all admin prompt messages in handlers/admin.py
# - Specifically in admin_text_router where prompts are sent during multi-step flows
# - Examples: product creation, category creation, settings updates, etc.
