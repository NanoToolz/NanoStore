# Implementation Plan: Admin Image Settings Enhancement

## Overview

This implementation adds auto-deletion for admin sent images and confirmation messages, introduces section-specific image settings for 7 bot sections (Welcome, Shop, Cart, Orders, Wallet, Support, Admin Panel), and provides an enhanced admin settings panel with status indicators. The implementation leverages the existing auto_delete() helper and extends the database schema with new image setting keys.

## Tasks

- [ ] 1. Extend database schema and initialization
  - Add default entries for new section image keys (shop_image_id, cart_image_id, orders_image_id, wallet_image_id, support_image_id, admin_panel_image_id) in init_db() using INSERT OR IGNORE
  - Ensure welcome_image_id remains for backward compatibility
  - _Requirements: 3.3, 6.1, 6.3_

- [ ] 2. Create admin image settings keyboard function
  - [ ] 2.1 Implement admin_image_settings_kb() in keyboards.py
    - Accept image_statuses dictionary parameter
    - Generate inline keyboard with 7 section buttons showing status indicators (✅/❌)
    - Include back navigation button to admin settings
    - _Requirements: 3.1, 3.5, 5.1, 5.2, 5.4_
  
  - [ ] 2.2 Write property test for keyboard generation
    - **Property 5: Status Indicator Accuracy**
    - **Validates: Requirements 3.5, 5.2**

- [ ] 3. Implement admin_image_settings_handler
  - [ ] 3.1 Create handler in handlers/admin.py
    - Query database for all 7 section image settings
    - Build image_statuses dictionary
    - Display categorized panel with user sections and admin sections
    - Use admin_image_settings_kb() for keyboard
    - _Requirements: 3.1, 3.5, 5.1, 5.2, 5.4_
  
  - [ ] 3.2 Write unit tests for handler
    - Test panel displays all sections correctly
    - Test status indicators reflect database state
    - _Requirements: 5.1, 5.2_

- [ ] 4. Implement admin_section_image_handler
  - [ ] 4.1 Create handler in handlers/admin.py
    - Extract section identifier from callback_data
    - Set session state to "adm_section_img:{section}"
    - Display prompt with section name and current status
    - Provide back navigation to image settings panel
    - _Requirements: 3.2, 5.3, 7.1_
  
  - [ ] 4.2 Write property test for state transition
    - **Property 3: Section Selection State Transition**
    - **Validates: Requirements 3.2, 5.3**
  
  - [ ] 4.3 Write property test for session state round-trip
    - **Property 11: Session State Round-Trip**
    - **Validates: Requirements 7.1, 7.2**

- [ ] 5. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 6. Modify admin_photo_router for section image routing
  - [ ] 6.1 Add section image routing logic to admin_photo_router() in handlers/admin.py
    - Check if state starts with "adm_section_img:"
    - Extract section identifier from state
    - Map section to settings key (e.g., "shop" → "shop_image_id")
    - Store file_id using set_setting()
    - Send confirmation message with section name
    - Schedule auto-deletion for confirmation message using auto_delete()
    - Schedule auto-deletion for admin's image message using auto_delete()
    - Clear session state after processing
    - Log action with add_action_log()
    - _Requirements: 1.1, 1.2, 2.1, 2.2, 2.4, 3.3, 3.4, 7.2, 7.3_
  
  - [ ] 6.2 Write property test for admin image auto-deletion
    - **Property 1: Admin Image Auto-Deletion**
    - **Validates: Requirements 1.1, 1.2**
  
  - [ ] 6.3 Write property test for confirmation message auto-deletion
    - **Property 2: Confirmation Message Auto-Deletion**
    - **Validates: Requirements 2.1, 2.2, 2.4**
  
  - [ ] 6.4 Write property test for section image storage isolation
    - **Property 4: Section Image Storage Isolation**
    - **Validates: Requirements 3.4**
  
  - [ ] 6.5 Write property test for section image unique storage
    - **Property 6: Section Image Unique Storage**
    - **Validates: Requirements 3.3**
  
  - [ ] 6.6 Write property test for state cleanup
    - **Property 10: State Cleanup After Processing**
    - **Validates: Requirements 7.3**
  
  - [ ] 6.7 Write unit tests for router
    - Test section image routing with valid state
    - Test router ignores uploads without active state
    - Test auto-delete skipped when delay is 0
    - Test confirmation message includes section name
    - _Requirements: 1.3, 2.3, 7.4_

- [ ] 7. Update Welcome section handler (handlers/start.py)
  - [ ] 7.1 Modify start handler to retrieve and display welcome_image_id
    - Query welcome_image_id from database
    - Display photo with caption if image exists
    - Display text-only if image not configured
    - _Requirements: 4.1, 4.8, 6.1_
  
  - [ ] 7.2 Write unit tests for Welcome section display
    - Test displays welcome image when configured
    - Test displays text-only when not configured
    - Test handles invalid file_id gracefully
    - _Requirements: 4.1, 4.8_

- [ ] 8. Update Shop section handler (handlers/catalog.py)
  - [ ] 8.1 Modify catalog handler to retrieve and display shop_image_id with fallback
    - Query shop_image_id from database
    - If not set, fall back to welcome_image_id
    - Display photo with caption if image exists
    - Display text-only if no image configured
    - _Requirements: 4.2, 4.8, 6.2_
  
  - [ ] 8.2 Write property test for backward compatibility
    - **Property 8: Backward Compatibility Preservation**
    - **Validates: Requirements 6.1, 6.2, 6.3**
  
  - [ ] 8.3 Write unit tests for Shop section display
    - Test displays shop image when configured
    - Test falls back to welcome image when shop not configured
    - Test displays text-only when neither configured
    - _Requirements: 4.2, 6.2_

- [ ] 9. Update Cart section handler (handlers/cart.py)
  - [ ] 9.1 Modify cart handler to retrieve and display cart_image_id
    - Query cart_image_id from database
    - Display photo with caption if image exists
    - Display text-only if image not configured
    - _Requirements: 4.3, 4.8_
  
  - [ ] 9.2 Write unit tests for Cart section display
    - Test displays cart image when configured
    - Test displays text-only when not configured
    - _Requirements: 4.3, 4.8_

- [ ] 10. Update Orders section handler (handlers/orders.py)
  - [ ] 10.1 Modify orders handler to retrieve and display orders_image_id
    - Query orders_image_id from database
    - Display photo with caption if image exists
    - Display text-only if image not configured
    - _Requirements: 4.4, 4.8_
  
  - [ ] 10.2 Write unit tests for Orders section display
    - Test displays orders image when configured
    - Test displays text-only when not configured
    - _Requirements: 4.4, 4.8_

- [ ] 11. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 12. Update Wallet section handler (handlers/wallet.py)
  - [ ] 12.1 Modify wallet handler to retrieve and display wallet_image_id
    - Query wallet_image_id from database
    - Display photo with caption if image exists
    - Display text-only if image not configured
    - _Requirements: 4.5, 4.8_
  
  - [ ] 12.2 Write unit tests for Wallet section display
    - Test displays wallet image when configured
    - Test displays text-only when not configured
    - _Requirements: 4.5, 4.8_

- [ ] 13. Update Support section handler (handlers/tickets.py)
  - [ ] 13.1 Modify support handler to retrieve and display support_image_id
    - Query support_image_id from database
    - Display photo with caption if image exists
    - Display text-only if image not configured
    - _Requirements: 4.6, 4.8_
  
  - [ ] 13.2 Write unit tests for Support section display
    - Test displays support image when configured
    - Test displays text-only when not configured
    - _Requirements: 4.6, 4.8_

- [ ] 14. Update Admin Panel section handler (handlers/admin.py)
  - [ ] 14.1 Modify admin panel handler to retrieve and display admin_panel_image_id
    - Query admin_panel_image_id from database
    - Display photo with caption if image exists
    - Display text-only if image not configured
    - _Requirements: 4.7, 4.8_
  
  - [ ] 14.2 Write property test for graceful missing image handling
    - **Property 9: Graceful Missing Image Handling**
    - **Validates: Requirements 4.8, 6.4**
  
  - [ ] 14.3 Write unit tests for Admin Panel section display
    - Test displays admin panel image when configured
    - Test displays text-only when not configured
    - _Requirements: 4.7, 4.8_

- [ ] 15. Register handlers and wire components
  - [ ] 15.1 Register new handlers in bot.py
    - Register admin_image_settings_handler with callback pattern "adm_img_settings"
    - Register admin_section_image_handler with callback pattern "adm_section_img:*"
    - Ensure handlers are registered in correct order
    - _Requirements: 3.1, 3.2_
  
  - [ ] 15.2 Update admin settings keyboard to include Image Settings button
    - Add button linking to admin_image_settings_handler
    - _Requirements: 5.1_
  
  - [ ] 15.3 Write property test for panel status update
    - **Property 7: Panel Status Update After Upload**
    - **Validates: Requirements 5.5**
  
  - [ ] 15.4 Write property test for session isolation
    - **Property 12: Session Isolation Between Admins**
    - **Validates: Requirements 7.5**
  
  - [ ] 15.5 Write integration tests
    - Test complete flow: panel → section selection → image upload → confirmation
    - Test concurrent admin sessions remain isolated
    - Test backward compatibility with existing welcome_image_id
    - _Requirements: 5.5, 6.1, 7.5_

- [ ] 16. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests use hypothesis library with minimum 100 iterations
- Auto-deletion leverages existing auto_delete() helper in helpers.py
- All section handlers follow the same pattern: query image → display photo or text
- Shop section has special fallback logic to welcome_image_id for backward compatibility
- Session state format: "adm_section_img:{section_name}"
- Database uses INSERT OR IGNORE for new keys to preserve existing data
