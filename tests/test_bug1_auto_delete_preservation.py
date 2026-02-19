"""
Bug 1 Preservation Tests: Auto-Delete Baseline Behavior

**Validates: Requirements 3.1, 3.2, 3.3**

IMPORTANT: These tests verify baseline behavior that must be preserved after the fix.
These tests should PASS on UNFIXED code to confirm the baseline behavior.

Preservation Requirements:
- 3.1: Messages with auto_delete=0 remain in chat (no deletion)
- 3.2: auto_delete() with explicit delay parameter uses that delay
- 3.3: Message deletion failures are logged as warnings without crashing

Testing Approach:
- Use property-based testing to generate many test cases
- Test on UNFIXED code to observe baseline behavior
- These tests will continue to pass after the fix (no regressions)
"""

import pytest
import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock, patch, call
from hypothesis import given, strategies as st, settings, Phase
from helpers import auto_delete


class TestAutoDeletePreservation:
    """Preservation tests to verify baseline auto-delete behavior that must be preserved."""

    @pytest.mark.asyncio
    @given(
        setting_value=st.sampled_from([0, "0", None, ""]),
    )
    @settings(
        max_examples=5,
        phases=[Phase.generate, Phase.target],
        deadline=None,
    )
    async def test_property_auto_delete_disabled_no_deletion(self, setting_value):
        """
        Property 1: Auto-Delete Disabled - Messages Remain in Chat
        
        **Validates: Requirement 3.1**
        
        For any auto_delete setting that is 0, None, or empty, the auto_delete()
        function should NOT create a deletion task, and messages should remain in chat.
        
        EXPECTED: This test PASSES on unfixed code (baseline behavior).
        This behavior must be preserved after the fix.
        """
        # Setup: Create a mock message
        mock_message = AsyncMock()
        mock_message.delete = AsyncMock()
        
        # Setup: Set auto_delete setting to the generated value (0, None, or empty)
        with patch('database.get_setting', new_callable=AsyncMock) as mock_get_setting:
            mock_get_setting.return_value = setting_value
            
            # Mock asyncio.create_task to verify it's NOT called
            with patch('asyncio.create_task') as mock_create_task:
                mock_create_task.return_value = MagicMock()
                
                # Call auto_delete without explicit delay (uses database setting)
                await auto_delete(mock_message)
                
                # EXPECTED BEHAVIOR: create_task should NOT be called when setting is 0/None/empty
                assert not mock_create_task.called, (
                    f"auto_delete() with setting={setting_value} should NOT create a deletion task. "
                    f"Messages should remain in chat when auto_delete is disabled."
                )

    @pytest.mark.asyncio
    @given(
        explicit_delay=st.integers(min_value=1, max_value=60),
        db_setting=st.sampled_from([0, "0", "30", "60", None]),
    )
    @settings(
        max_examples=5,
        phases=[Phase.generate, Phase.target],
        deadline=None,
    )
    async def test_property_explicit_delay_overrides_database(self, explicit_delay, db_setting):
        """
        Property 2: Explicit Delay Parameter Overrides Database Setting
        
        **Validates: Requirement 3.2**
        
        For any explicit delay parameter passed to auto_delete(), the function should
        use that delay instead of the database setting, regardless of what the database
        setting is (0, 30, 60, None, etc.).
        
        EXPECTED: This test PASSES on unfixed code (baseline behavior).
        This behavior must be preserved after the fix.
        """
        # Setup: Create a mock message
        mock_message = AsyncMock()
        mock_message.delete = AsyncMock()
        
        # Setup: Set database auto_delete setting (should be ignored)
        with patch('database.get_setting', new_callable=AsyncMock) as mock_get_setting:
            mock_get_setting.return_value = db_setting
            
            # Mock asyncio.create_task to verify it's called with explicit delay
            with patch('asyncio.create_task') as mock_create_task:
                mock_create_task.return_value = MagicMock()
                
                # Call auto_delete WITH explicit delay parameter
                await auto_delete(mock_message, delay=explicit_delay)
                
                # EXPECTED BEHAVIOR: create_task should be called (explicit delay > 0)
                assert mock_create_task.called, (
                    f"auto_delete() with explicit delay={explicit_delay} should create a deletion task, "
                    f"even if database setting is {db_setting}"
                )
                
                # EXPECTED BEHAVIOR: database setting should NOT be queried when explicit delay is provided
                assert not mock_get_setting.called, (
                    f"auto_delete() with explicit delay={explicit_delay} should NOT query database setting. "
                    f"Explicit delay should override database setting."
                )

    @pytest.mark.asyncio
    async def test_message_deletion_failure_logged_without_crash(self):
        """
        Test: Message Deletion Failures Are Logged Without Crashing
        
        **Validates: Requirement 3.3**
        
        When a message deletion fails (due to message age, permissions, etc.),
        the error should be logged as a warning without crashing the handler.
        
        EXPECTED: This test PASSES on unfixed code (baseline behavior).
        This behavior must be preserved after the fix.
        """
        # Setup: Create a mock message that fails to delete
        mock_message = AsyncMock()
        mock_message.delete = AsyncMock(side_effect=Exception("Message too old to delete"))
        
        # Setup: Set auto_delete setting to positive value
        with patch('database.get_setting', new_callable=AsyncMock) as mock_get_setting:
            mock_get_setting.return_value = "1"  # 1 second delay
            
            # Mock logger to verify warning is logged
            with patch('helpers.logger') as mock_logger:
                # Call auto_delete
                await auto_delete(mock_message)
                
                # Wait for the deletion task to execute (1 second + buffer)
                await asyncio.sleep(1.2)
                
                # EXPECTED BEHAVIOR: Warning should be logged
                assert mock_logger.warning.called, (
                    "Message deletion failure should be logged as a warning"
                )
                
                # Verify the warning message contains "auto_delete failed"
                warning_calls = [str(call) for call in mock_logger.warning.call_args_list]
                assert any("auto_delete failed" in str(call) for call in warning_calls), (
                    "Warning message should indicate auto_delete failure"
                )
                
                # EXPECTED BEHAVIOR: No exception should be raised (no crash)
                # If we reach here, the test passed (no crash occurred)

    @pytest.mark.asyncio
    async def test_runtime_error_handled_gracefully(self):
        """
        Test: RuntimeError When No Event Loop Is Handled Gracefully
        
        **Validates: Requirement 3.3**
        
        When asyncio.create_task() raises RuntimeError (no running event loop),
        the error should be caught and logged without crashing.
        
        EXPECTED: This test PASSES on unfixed code (baseline behavior).
        This behavior must be preserved after the fix.
        """
        # Setup: Create a mock message
        mock_message = AsyncMock()
        mock_message.delete = AsyncMock()
        
        # Setup: Set auto_delete setting to positive value
        with patch('database.get_setting', new_callable=AsyncMock) as mock_get_setting:
            mock_get_setting.return_value = "30"
            
            # Mock asyncio.create_task to raise RuntimeError
            with patch('asyncio.create_task', side_effect=RuntimeError("No running event loop")):
                # Mock logger to verify warning is logged
                with patch('helpers.logger') as mock_logger:
                    # Call auto_delete - should NOT crash
                    await auto_delete(mock_message)
                    
                    # EXPECTED BEHAVIOR: Warning should be logged
                    assert mock_logger.warning.called, (
                        "RuntimeError should be logged as a warning"
                    )
                    
                    # Verify the warning message mentions "no running loop"
                    warning_calls = [str(call) for call in mock_logger.warning.call_args_list]
                    assert any("no running loop" in str(call).lower() for call in warning_calls), (
                        "Warning message should indicate no running event loop"
                    )
                    
                    # EXPECTED BEHAVIOR: No exception should be raised (no crash)
                    # If we reach here, the test passed (no crash occurred)

    @pytest.mark.asyncio
    @given(
        delay_value=st.integers(min_value=1, max_value=10),
    )
    @settings(
        max_examples=5,
        phases=[Phase.generate, Phase.target],
        deadline=None,
    )
    async def test_property_explicit_delay_zero_disables_deletion(self, delay_value):
        """
        Property 3: Explicit Delay of 0 Disables Deletion
        
        **Validates: Requirement 3.1**
        
        When auto_delete() is called with explicit delay=0, no deletion task
        should be created, even if the database setting is positive.
        
        EXPECTED: This test PASSES on unfixed code (baseline behavior).
        This behavior must be preserved after the fix.
        """
        # Setup: Create a mock message
        mock_message = AsyncMock()
        mock_message.delete = AsyncMock()
        
        # Setup: Set database auto_delete setting to positive value (should be overridden)
        with patch('database.get_setting', new_callable=AsyncMock) as mock_get_setting:
            mock_get_setting.return_value = str(delay_value)  # Positive value in DB
            
            # Mock asyncio.create_task to verify it's NOT called
            with patch('asyncio.create_task') as mock_create_task:
                mock_create_task.return_value = MagicMock()
                
                # Call auto_delete WITH explicit delay=0
                await auto_delete(mock_message, delay=0)
                
                # EXPECTED BEHAVIOR: create_task should NOT be called when explicit delay=0
                assert not mock_create_task.called, (
                    f"auto_delete() with explicit delay=0 should NOT create a deletion task, "
                    f"even if database setting is {delay_value}"
                )
                
                # EXPECTED BEHAVIOR: database setting should NOT be queried when explicit delay is provided
                assert not mock_get_setting.called, (
                    "auto_delete() with explicit delay=0 should NOT query database setting"
                )

    @pytest.mark.asyncio
    async def test_none_message_handled_gracefully(self):
        """
        Test: None Message Is Handled Gracefully
        
        **Validates: Requirement 3.3**
        
        When auto_delete() is called with message=None, the function should
        return early without attempting to delete or create tasks.
        
        EXPECTED: This test PASSES on unfixed code (baseline behavior).
        This behavior must be preserved after the fix.
        """
        # Setup: Mock database and asyncio
        with patch('database.get_setting', new_callable=AsyncMock) as mock_get_setting:
            mock_get_setting.return_value = "30"
            
            with patch('asyncio.create_task') as mock_create_task:
                mock_create_task.return_value = MagicMock()
                
                # Call auto_delete with None message
                await auto_delete(None)
                
                # EXPECTED BEHAVIOR: Should return early without querying database
                assert not mock_get_setting.called, (
                    "auto_delete(None) should return early without querying database"
                )
                
                # EXPECTED BEHAVIOR: Should not create any tasks
                assert not mock_create_task.called, (
                    "auto_delete(None) should not create any deletion tasks"
                )
                
                # EXPECTED BEHAVIOR: No exception should be raised
                # If we reach here, the test passed (no crash occurred)


# SUMMARY OF PRESERVATION REQUIREMENTS:
#
# These tests verify that the following baseline behaviors are preserved after the fix:
#
# 1. Messages with auto_delete=0 (or None, or empty) remain in chat - no deletion occurs
# 2. Explicit delay parameter overrides database setting in all cases
# 3. Message deletion failures are logged as warnings without crashing
# 4. RuntimeError (no event loop) is caught and logged without crashing
# 5. Explicit delay=0 disables deletion even if database setting is positive
# 6. None message is handled gracefully without errors
#
# All these tests should PASS on unfixed code, confirming the baseline behavior.
# After implementing the fix, these tests should continue to PASS, ensuring no regressions.
