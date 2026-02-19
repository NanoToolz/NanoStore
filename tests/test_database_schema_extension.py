"""
Test Database Schema Extension for Admin Image Settings Enhancement

**Validates: Requirements 3.3, 6.1, 6.3**

This test verifies that the database initialization properly creates default entries
for all section-specific image settings while maintaining backward compatibility.
"""

import pytest
import os
import tempfile
from database import init_db, get_setting, set_setting, get_db


@pytest.fixture
async def temp_db():
    """Create a temporary database for testing."""
    # Create a temporary file for the test database
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    # Temporarily override the DB_PATH
    import config
    original_path = config.DB_PATH
    config.DB_PATH = path
    
    # Reset the global connection
    import database
    database._db = None
    
    # Initialize the database
    await init_db()
    
    yield path
    
    # Cleanup
    config.DB_PATH = original_path
    database._db = None
    
    # Close any open connections and remove the temp file
    try:
        db = await get_db()
        await db.close()
    except:
        pass
    
    try:
        os.unlink(path)
    except:
        pass


class TestDatabaseSchemaExtension:
    """Tests for database schema extension with new section image keys."""

    @pytest.mark.asyncio
    async def test_all_section_image_keys_initialized(self, temp_db):
        """
        Test that all section image keys are initialized with default empty values.
        
        **Validates: Requirements 3.3, 6.3**
        
        Verifies that init_db() creates default entries for all 7 section image keys:
        - welcome_image_id (existing, for backward compatibility)
        - shop_image_id (new)
        - cart_image_id (new)
        - orders_image_id (new)
        - wallet_image_id (new)
        - support_image_id (new)
        - admin_panel_image_id (new)
        """
        section_keys = [
            "welcome_image_id",
            "shop_image_id",
            "cart_image_id",
            "orders_image_id",
            "wallet_image_id",
            "support_image_id",
            "admin_panel_image_id",
        ]
        
        for key in section_keys:
            value = await get_setting(key, None)
            assert value is not None, f"Setting '{key}' should exist in database"
            assert value == "", f"Setting '{key}' should default to empty string"

    @pytest.mark.asyncio
    async def test_welcome_image_id_backward_compatibility(self, temp_db):
        """
        Test that welcome_image_id remains for backward compatibility.
        
        **Validates: Requirements 6.1**
        
        Verifies that the existing welcome_image_id setting is preserved
        and continues to work as expected.
        """
        # Verify welcome_image_id exists
        value = await get_setting("welcome_image_id", None)
        assert value is not None, "welcome_image_id should exist for backward compatibility"
        assert value == "", "welcome_image_id should default to empty string"
        
        # Test that we can set and retrieve welcome_image_id
        test_file_id = "AgACAgIAAxkBAAIBCGZxYzQ1NjY3ODkw"
        await set_setting("welcome_image_id", test_file_id)
        
        retrieved = await get_setting("welcome_image_id")
        assert retrieved == test_file_id, "welcome_image_id should be retrievable after setting"

    @pytest.mark.asyncio
    async def test_insert_or_ignore_preserves_existing_data(self, temp_db):
        """
        Test that INSERT OR IGNORE preserves existing data during re-initialization.
        
        **Validates: Requirements 6.3**
        
        Verifies that running init_db() multiple times doesn't overwrite
        existing section image settings.
        """
        # Set a custom value for shop_image_id
        test_file_id = "AgACAgIAAxkBAAIBCGZxYzQ1NjY3ODkw"
        await set_setting("shop_image_id", test_file_id)
        
        # Verify it was set
        value = await get_setting("shop_image_id")
        assert value == test_file_id, "shop_image_id should be set to test value"
        
        # Re-initialize the database (simulates upgrade scenario)
        await init_db()
        
        # Verify the custom value is preserved
        value_after = await get_setting("shop_image_id")
        assert value_after == test_file_id, (
            "shop_image_id should be preserved after re-initialization (INSERT OR IGNORE)"
        )

    @pytest.mark.asyncio
    async def test_section_image_keys_independent(self, temp_db):
        """
        Test that section image keys are independent and don't interfere with each other.
        
        **Validates: Requirements 3.3**
        
        Verifies that setting one section's image doesn't affect other sections.
        """
        # Set different values for different sections
        test_values = {
            "welcome_image_id": "file_id_welcome",
            "shop_image_id": "file_id_shop",
            "cart_image_id": "file_id_cart",
            "orders_image_id": "file_id_orders",
            "wallet_image_id": "file_id_wallet",
            "support_image_id": "file_id_support",
            "admin_panel_image_id": "file_id_admin",
        }
        
        # Set all values
        for key, value in test_values.items():
            await set_setting(key, value)
        
        # Verify all values are correctly stored and independent
        for key, expected_value in test_values.items():
            actual_value = await get_setting(key)
            assert actual_value == expected_value, (
                f"Setting '{key}' should have value '{expected_value}', got '{actual_value}'"
            )

    @pytest.mark.asyncio
    async def test_other_settings_unaffected(self, temp_db):
        """
        Test that adding new section image keys doesn't affect other settings.
        
        **Validates: Requirements 6.3**
        
        Verifies that existing settings like currency, bot_name, etc. remain intact.
        """
        # Check that other default settings exist and have correct values
        other_settings = {
            "currency": "Rs",
            "bot_name": "NanoStore",
            "welcome_text": "Welcome to NanoStore!",
            "min_order": "0",
            "auto_delete": "0",
        }
        
        for key, expected_value in other_settings.items():
            actual_value = await get_setting(key)
            assert actual_value == expected_value, (
                f"Setting '{key}' should have value '{expected_value}', got '{actual_value}'"
            )
