# Implementation Plan

## Bug 1: Auto-Delete Messages

- [x] 1.1 Write bug condition exploration test for auto-delete
  - **Property 1: Fault Condition** - Auto-Delete Messages Not Working
  - **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bug exists
  - **DO NOT attempt to fix the test or the code when it fails**
  - **NOTE**: This test encodes the expected behavior - it will validate the fix when it passes after implementation
  - **GOAL**: Surface counterexamples that demonstrate the bug exists
  - **Scoped PBT Approach**: Test with auto_delete setting > 0 and verify messages are not deleted
  - Test that auto_delete() is called with setting=30 but message is not deleted after 31 seconds
  - Test that auto_delete() with None setting raises TypeError or fails silently
  - Test that /start command calls auto_delete() but message remains in chat
  - Test that admin prompt messages are not auto-deleted
  - Run test on UNFIXED code
  - **EXPECTED OUTCOME**: Test FAILS (this is correct - it proves the bug exists)
  - Document counterexamples found to understand root cause
  - Mark task complete when test is written, run, and failure is documented
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 1.2 Write preservation property tests for auto-delete (BEFORE implementing fix)
  - **Property 2: Preservation** - Auto-Delete Disabled and Explicit Delay
  - **IMPORTANT**: Follow observation-first methodology
  - Observe behavior on UNFIXED code for non-buggy inputs
  - Observe: Messages with auto_delete=0 remain in chat on unfixed code
  - Observe: auto_delete() with explicit delay parameter uses that delay on unfixed code
  - Observe: Message deletion failures are logged as warnings without crashing on unfixed code
  - Write property-based tests capturing observed behavior patterns from Preservation Requirements
  - Property-based testing generates many test cases for stronger guarantees
  - Run tests on UNFIXED code
  - **EXPECTED OUTCOME**: Tests PASS (this confirms baseline behavior to preserve)
  - Mark task complete when tests are written, run, and passing on unfixed code
  - _Requirements: 3.1, 3.2, 3.3_

- [ ] 1.3 Fix auto-delete messages functionality

  - [x] 1.3.1 Implement the fix in helpers.py and database.py
    - Modify auto_delete() in helpers.py to handle None values: `raw = await get_setting("auto_delete", "0") or "0"`
    - Ensure RuntimeError exception handling is robust and logs appropriately
    - Add "auto_delete": "0" to defaults dictionary in init_db() in database.py
    - Add auto_delete() calls to all admin prompt messages in handlers/admin.py
    - Verify /start command already calls auto_delete()
    - _Bug_Condition: isBugCondition_AutoDelete(input) where auto_delete() is called AND setting > 0 AND message is NOT deleted_
    - _Expected_Behavior: Message SHALL be deleted after specified delay, None values default to "0", RuntimeError caught_
    - _Preservation: Messages with setting=0 remain in chat, explicit delay parameter works, deletion failures logged_
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3_

  - [ ] 1.3.2 Verify bug condition exploration test now passes
    - **Property 1: Expected Behavior** - Auto-Delete Messages Work Correctly
    - **IMPORTANT**: Re-run the SAME test from task 1.1 - do NOT write a new test
    - The test from task 1.1 encodes the expected behavior
    - When this test passes, it confirms the expected behavior is satisfied
    - Run bug condition exploration test from step 1.1
    - **EXPECTED OUTCOME**: Test PASSES (confirms bug is fixed)
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

  - [ ] 1.3.3 Verify preservation tests still pass
    - **Property 2: Preservation** - Auto-Delete Disabled and Explicit Delay
    - **IMPORTANT**: Re-run the SAME tests from task 1.2 - do NOT write new tests
    - Run preservation property tests from step 1.2
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions)
    - Confirm all tests still pass after fix (no regressions)
    - _Requirements: 3.1, 3.2, 3.3_

## Bug 2: Typing Indicator Overuse

- [ ] 2.1 Write bug condition exploration test for typing indicator overuse
  - **Property 1: Fault Condition** - Typing Indicators on Instant Operations
  - **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bug exists
  - **DO NOT attempt to fix the test or the code when it fails**
  - **NOTE**: This test encodes the expected behavior - it will validate the fix when it passes after implementation
  - **GOAL**: Surface counterexamples that demonstrate the bug exists
  - **Scoped PBT Approach**: Test callback query handlers with response time < 1s
  - Test that admin_handler (dashboard button) calls send_typing() even though response is instant
  - Test that admin_settings_handler calls send_typing() even though response is instant
  - Test that callback query handlers with < 1s response time call send_typing()
  - Measure response times and document unnecessary typing indicators
  - Run test on UNFIXED code
  - **EXPECTED OUTCOME**: Test FAILS (this is correct - it proves the bug exists)
  - Document counterexamples found to understand root cause
  - Mark task complete when test is written, run, and failure is documented
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [ ] 2.2 Write preservation property tests for typing indicators (BEFORE implementing fix)
  - **Property 2: Preservation** - Typing Indicators on Text Messages and Long Operations
  - **IMPORTANT**: Follow observation-first methodology
  - Observe behavior on UNFIXED code for non-buggy inputs
  - Observe: /start command (text message) shows typing indicator on unfixed code
  - Observe: Long operations (broadcasts, payment proofs) show typing indicator on unfixed code
  - Observe: send_typing() failures are logged without crashing on unfixed code
  - Write property-based tests capturing observed behavior patterns from Preservation Requirements
  - Property-based testing generates many test cases for stronger guarantees
  - Run tests on UNFIXED code
  - **EXPECTED OUTCOME**: Tests PASS (this confirms baseline behavior to preserve)
  - Mark task complete when tests are written, run, and passing on unfixed code
  - _Requirements: 3.4, 3.5_

- [ ] 2.3 Fix typing indicator overuse

  - [ ] 2.3.1 Implement the fix in handlers/admin.py and other handlers
    - Remove send_typing() from callback query handlers with instant responses (< 1s)
    - Remove from: admin_handler, back_admin_handler, admin_dashboard_handler, admin_cats_handler, admin_settings_handler
    - Keep send_typing() in handlers with long operations (> 1s)
    - Keep in: admin_broadcast_confirm_handler, admin_proof_approve_handler, admin_topup_approve_handler
    - Preserve send_typing() in text message handlers like start_handler
    - _Bug_Condition: isBugCondition_TypingOveruse(input) where handler_type == "callback_query" AND processing_time < 1.0 AND send_typing() is called_
    - _Expected_Behavior: send_typing() SHALL NOT be called for instant operations, SHALL be called for operations > 1s_
    - _Preservation: Text message handlers show typing, long operations show typing, failures logged_
    - _Requirements: 2.2, 2.3, 2.4, 2.5, 3.4, 3.5_

  - [ ] 2.3.2 Verify bug condition exploration test now passes
    - **Property 1: Expected Behavior** - Typing Indicators Only for Long Operations
    - **IMPORTANT**: Re-run the SAME test from task 2.1 - do NOT write a new test
    - The test from task 2.1 encodes the expected behavior
    - When this test passes, it confirms the expected behavior is satisfied
    - Run bug condition exploration test from step 2.1
    - **EXPECTED OUTCOME**: Test PASSES (confirms bug is fixed)
    - _Requirements: 2.2, 2.3, 2.4, 2.5_

  - [ ] 2.3.3 Verify preservation tests still pass
    - **Property 2: Preservation** - Typing Indicators on Text Messages and Long Operations
    - **IMPORTANT**: Re-run the SAME tests from task 2.2 - do NOT write new tests
    - Run preservation property tests from step 2.2
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions)
    - Confirm all tests still pass after fix (no regressions)
    - _Requirements: 3.4, 3.5_

## Bug 3: Bulk Stock Update Missing

- [ ] 3.1 Write bug condition exploration test for bulk stock update
  - **Property 1: Fault Condition** - Bulk Stock Update Not Processing Input
  - **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bug exists
  - **DO NOT attempt to fix the test or the code when it fails**
  - **NOTE**: This test encodes the expected behavior - it will validate the fix when it passes after implementation
  - **GOAL**: Surface counterexamples that demonstrate the bug exists
  - **Scoped PBT Approach**: Test with valid bulk stock input format "product_id|stock"
  - Test that admin_bulk_stock_handler prompts for input but no processing occurs
  - Test that sending "1|50\n2|100\n3|-1" does not update product stocks
  - Test that state "adm_bulk_stock_data" is not handled in admin_text_router
  - Test that no feedback is provided to admin
  - Run test on UNFIXED code
  - **EXPECTED OUTCOME**: Test FAILS (this is correct - it proves the bug exists)
  - Document counterexamples found to understand root cause
  - Mark task complete when test is written, run, and failure is documented
  - _Requirements: 3.1, 3.2, 3.3_

- [ ] 3.2 Write preservation property tests for bulk operations (BEFORE implementing fix)
  - **Property 2: Preservation** - Bulk Product Import and Individual Stock Updates
  - **IMPORTANT**: Follow observation-first methodology
  - Observe behavior on UNFIXED code for non-buggy inputs
  - Observe: Bulk product import (admin_bulk_handler) works correctly on unfixed code
  - Observe: Individual product stock updates work through admin_prod_stock_handler on unfixed code
  - Write property-based tests capturing observed behavior patterns from Preservation Requirements
  - Property-based testing generates many test cases for stronger guarantees
  - Run tests on UNFIXED code
  - **EXPECTED OUTCOME**: Tests PASS (this confirms baseline behavior to preserve)
  - Mark task complete when tests are written, run, and passing on unfixed code
  - _Requirements: 3.6, 3.7_

- [ ] 3.3 Fix bulk stock update functionality

  - [ ] 3.3.1 Implement the fix in handlers/admin.py
    - Add case for "adm_bulk_stock_data" state in admin_text_router
    - Parse input format "product_id|stock" (one per line)
    - Validate each product_id exists using get_product()
    - Validate stock value range (>= -1, where -1 is unlimited)
    - Update stock atomically for all valid products using update_product()
    - Skip invalid lines and collect errors
    - Report success count and error count to admin
    - Call auto_delete() on admin's input message and response
    - Clear state after processing
    - _Bug_Condition: isBugCondition_BulkStock(input) where admin_action == "bulk_stock_update" AND bulk_data is valid format AND stock is NOT updated_
    - _Expected_Behavior: Parse input, validate products, update stock atomically, skip invalid lines, report success/error counts_
    - _Preservation: Bulk product import works, individual stock updates work_
    - _Requirements: 2.6, 2.7, 2.8, 2.9, 2.10, 2.11, 3.6, 3.7_

  - [ ] 3.3.2 Verify bug condition exploration test now passes
    - **Property 1: Expected Behavior** - Bulk Stock Update Processes Input
    - **IMPORTANT**: Re-run the SAME test from task 3.1 - do NOT write a new test
    - The test from task 3.1 encodes the expected behavior
    - When this test passes, it confirms the expected behavior is satisfied
    - Run bug condition exploration test from step 3.1
    - **EXPECTED OUTCOME**: Test PASSES (confirms bug is fixed)
    - _Requirements: 2.6, 2.7, 2.8, 2.9, 2.10, 2.11_

  - [ ] 3.3.3 Verify preservation tests still pass
    - **Property 2: Preservation** - Bulk Product Import and Individual Stock Updates
    - **IMPORTANT**: Re-run the SAME tests from task 3.2 - do NOT write new tests
    - Run preservation property tests from step 3.2
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions)
    - Confirm all tests still pass after fix (no regressions)
    - _Requirements: 3.6, 3.7_

## Bug 4: Settings System Incomplete

- [ ] 4.1 Write bug condition exploration test for settings system
  - **Property 1: Fault Condition** - Settings Exist But Not Exposed in UI
  - **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bug exists
  - **DO NOT attempt to fix the test or the code when it fails**
  - **NOTE**: This test encodes the expected behavior - it will validate the fix when it passes after implementation
  - **GOAL**: Surface counterexamples that demonstrate the bug exists
  - **Scoped PBT Approach**: Test that settings exist in database but are not displayed in admin panel
  - Test that admin_settings_handler only displays 7 settings
  - Test that payment_instructions exists in database but is not shown in UI
  - Test that maintenance_text exists but is not accessible
  - Test that topup settings (topup_enabled, topup_min_amount, topup_max_amount, topup_bonus_percent) are not exposed
  - Test that settings are not organized by category
  - Run test on UNFIXED code
  - **EXPECTED OUTCOME**: Test FAILS (this is correct - it proves the bug exists)
  - Document counterexamples found to understand root cause
  - Mark task complete when test is written, run, and failure is documented
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ] 4.2 Write preservation property tests for settings system (BEFORE implementing fix)
  - **Property 2: Preservation** - Existing Settings Functionality
  - **IMPORTANT**: Follow observation-first methodology
  - Observe behavior on UNFIXED code for non-buggy inputs
  - Observe: Existing 7 settings work correctly on unfixed code
  - Observe: get_setting() with default value returns default if key doesn't exist on unfixed code
  - Observe: set_setting() uses INSERT OR REPLACE to update settings on unfixed code
  - Write property-based tests capturing observed behavior patterns from Preservation Requirements
  - Property-based testing generates many test cases for stronger guarantees
  - Run tests on UNFIXED code
  - **EXPECTED OUTCOME**: Tests PASS (this confirms baseline behavior to preserve)
  - Mark task complete when tests are written, run, and passing on unfixed code
  - _Requirements: 3.8, 3.9, 3.10_

- [ ] 4.3 Fix settings system to expose all settings

  - [ ] 4.3.1 Implement the fix in handlers/admin.py and keyboards.py
    - Add fetches for missing settings in admin_settings_handler: payment_instructions, maintenance_text, topup_enabled, topup_min_amount, topup_max_amount, topup_bonus_percent
    - Organize settings display by category: Store Settings, Order Settings, Wallet Settings, System Settings
    - Add keyboard buttons in admin_settings_kb() for all missing settings
    - Organize keyboard buttons by category for better UX
    - Add toggle logic for topup_enabled in admin_set_handler (similar to maintenance)
    - Ensure labels and hints exist for all settings in admin_set_handler
    - _Bug_Condition: isBugCondition_SettingsIncomplete(input) where setting exists_in_db AND exposed_in_ui == FALSE AND setting is used in handlers_
    - _Expected_Behavior: All settings displayed in organized categories, all settings editable, toggle interface for boolean settings_
    - _Preservation: Existing settings work unchanged, get_setting() with defaults works, set_setting() uses INSERT OR REPLACE_
    - _Requirements: 2.12, 2.13, 2.14, 2.15, 2.16, 2.17, 3.8, 3.9, 3.10_

  - [ ] 4.3.2 Verify bug condition exploration test now passes
    - **Property 1: Expected Behavior** - All Settings Exposed in UI
    - **IMPORTANT**: Re-run the SAME test from task 4.1 - do NOT write a new test
    - The test from task 4.1 encodes the expected behavior
    - When this test passes, it confirms the expected behavior is satisfied
    - Run bug condition exploration test from step 4.1
    - **EXPECTED OUTCOME**: Test PASSES (confirms bug is fixed)
    - _Requirements: 2.12, 2.13, 2.14, 2.15, 2.16, 2.17_

  - [ ] 4.3.3 Verify preservation tests still pass
    - **Property 2: Preservation** - Existing Settings Functionality
    - **IMPORTANT**: Re-run the SAME tests from task 4.2 - do NOT write new tests
    - Run preservation property tests from step 4.2
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions)
    - Confirm all tests still pass after fix (no regressions)
    - _Requirements: 3.8, 3.9, 3.10_

## Bug 5: Stock Management Race Conditions

- [ ] 5.1 Write bug condition exploration test for stock race conditions
  - **Property 1: Fault Condition** - Concurrent Orders Result in Negative Stock
  - **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bug exists
  - **DO NOT attempt to fix the test or the code when it fails**
  - **NOTE**: This test encodes the expected behavior - it will validate the fix when it passes after implementation
  - **GOAL**: Surface counterexamples that demonstrate the bug exists
  - **Scoped PBT Approach**: Simulate concurrent orders for same product
  - Test that product with stock=5 allows 2 concurrent orders of qty=5 each, resulting in stock=-5
  - Test that add_to_cart() does not validate stock availability before adding
  - Test that product with stock=0 can be added to cart
  - Test that stock changes between cart addition and checkout are not re-validated
  - Test that decrement_stock() can result in negative stock with concurrent updates
  - Run test on UNFIXED code
  - **EXPECTED OUTCOME**: Test FAILS (this is correct - it proves the bug exists)
  - Document counterexamples found to understand root cause
  - Mark task complete when test is written, run, and failure is documented
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 5.2 Write preservation property tests for stock management (BEFORE implementing fix)
  - **Property 2: Preservation** - Unlimited Stock and Existing Stock Behavior
  - **IMPORTANT**: Follow observation-first methodology
  - Observe behavior on UNFIXED code for non-buggy inputs
  - Observe: Products with unlimited stock (stock=-1) allow unlimited purchases without decrement on unfixed code
  - Observe: cart_inc_handler checks stock limits before allowing increase on unfixed code
  - Observe: Cancelled orders do not restore stock on unfixed code
  - Observe: get_cart displays current stock status for each product on unfixed code
  - Observe: Out of stock products (stock=0) display "🔴 Out of Stock" in catalog on unfixed code
  - Write property-based tests capturing observed behavior patterns from Preservation Requirements
  - Property-based testing generates many test cases for stronger guarantees
  - Run tests on UNFIXED code
  - **EXPECTED OUTCOME**: Tests PASS (this confirms baseline behavior to preserve)
  - Mark task complete when tests are written, run, and passing on unfixed code
  - _Requirements: 3.11, 3.12, 3.13, 3.14, 3.15_

- [ ] 5.3 Fix stock management race conditions

  - [ ] 5.3.1 Implement the fix in database.py
    - Modify add_to_cart() to validate stock availability before adding to cart
    - Get product and check if stock >= requested quantity (skip for unlimited stock=-1)
    - Raise ValueError if insufficient stock
    - Modify decrement_stock() to use atomic transaction with BEGIN IMMEDIATE
    - Get current stock within transaction
    - Check if current_stock >= quantity (return False if insufficient)
    - Decrement stock and commit transaction
    - Return bool to indicate success/failure
    - Handle unlimited stock (stock=-1) by skipping validation and decrement
    - _Bug_Condition: isBugCondition_StockRace(input) where concurrent_orders AND SUM(quantities) > stock AND validation is NOT atomic_
    - _Expected_Behavior: add_to_cart validates stock, decrement_stock is atomic, insufficient stock returns error, negative stock prevented_
    - _Preservation: Unlimited stock works, cart_inc_handler checks limits, cancelled orders don't restore stock, cart displays stock, out of stock displays correctly_
    - _Requirements: 2.18, 2.19, 2.20, 2.21, 2.24, 3.11, 3.12, 3.13, 3.14, 3.15_

  - [ ] 5.3.2 Implement the fix in handlers/orders.py
    - Modify confirm_order_handler to re-validate stock before decrementing
    - Call decrement_stock() for each item and check return value
    - Collect stock errors for items that fail validation
    - If any stock errors, rollback balance changes and notify user
    - Display error message with list of out-of-stock items
    - _Bug_Condition: isBugCondition_StockRace(input) where stock changes between cart and checkout_
    - _Expected_Behavior: Re-validate stock during order confirmation, fail order if insufficient stock, restore balance on failure_
    - _Preservation: Unlimited stock works, existing order flow preserved_
    - _Requirements: 2.22, 2.23, 3.11_

  - [ ] 5.3.3 Implement the fix in handlers/catalog.py
    - Modify add_to_cart_handler to catch ValueError from add_to_cart()
    - Display error message to user when insufficient stock
    - Use query.answer() with show_alert=True for error feedback
    - _Bug_Condition: isBugCondition_StockRace(input) where add_to_cart is called without stock validation_
    - _Expected_Behavior: Display error when insufficient stock, prevent adding to cart_
    - _Preservation: Existing cart functionality preserved_
    - _Requirements: 2.18, 2.19_

  - [ ] 5.3.4 Verify bug condition exploration test now passes
    - **Property 1: Expected Behavior** - Stock Validation Prevents Negative Stock
    - **IMPORTANT**: Re-run the SAME test from task 5.1 - do NOT write a new test
    - The test from task 5.1 encodes the expected behavior
    - When this test passes, it confirms the expected behavior is satisfied
    - Run bug condition exploration test from step 5.1
    - **EXPECTED OUTCOME**: Test PASSES (confirms bug is fixed)
    - _Requirements: 2.18, 2.19, 2.20, 2.21, 2.22, 2.23, 2.24_

  - [ ] 5.3.5 Verify preservation tests still pass
    - **Property 2: Preservation** - Unlimited Stock and Existing Stock Behavior
    - **IMPORTANT**: Re-run the SAME tests from task 5.2 - do NOT write new tests
    - Run preservation property tests from step 5.2
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions)
    - Confirm all tests still pass after fix (no regressions)
    - _Requirements: 3.11, 3.12, 3.13, 3.14, 3.15_

## Final Checkpoint

- [ ] 6. Checkpoint - Ensure all tests pass
  - Ensure all exploration tests pass (bugs are fixed)
  - Ensure all preservation tests pass (no regressions)
  - Run full test suite to verify all 5 bugs are resolved
  - Ask the user if questions arise
