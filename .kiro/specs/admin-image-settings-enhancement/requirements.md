# Requirements Document

## Introduction

This feature enhances the admin image settings functionality in the Telegram bot to address message cleanup issues and expand image configuration capabilities. Currently, when admins set a welcome image, the bot fails to auto-delete the admin's sent image message and the confirmation message. Additionally, the system only supports a single welcome image that appears across all sections. This enhancement will fix the auto-deletion issues and introduce section-specific image settings for Welcome, Shop, Cart, Orders, Wallet, Support, and Admin Panel sections.

## Glossary

- **Admin**: A user with administrative privileges who can configure bot settings
- **Image_Handler**: The system component that processes and stores uploaded images from admins
- **Message_Cleanup_Service**: The system component responsible for auto-deleting messages
- **Section_Image**: An image configured for a specific bot section (Welcome, Shop, Cart, Orders, Wallet, Support, Admin Panel)
- **Confirmation_Message**: A message sent by the bot to confirm successful image upload
- **Admin_Sent_Image**: The original image message sent by the admin to set as a section image
- **Auto_Delete_Delay**: The configurable time period (in seconds) before a message is automatically deleted
- **Image_Settings_Panel**: The admin interface for managing section-specific images

## Requirements

### Requirement 1: Auto-Delete Admin Sent Images

**User Story:** As an admin, I want my sent image messages to be automatically deleted after the bot receives them, so that the chat remains clean and uncluttered.

#### Acceptance Criteria

1. WHEN an admin sends an image to set as a section image, THE Message_Cleanup_Service SHALL delete the Admin_Sent_Image after the Image_Handler successfully receives the image file ID
2. THE Message_Cleanup_Service SHALL apply the Auto_Delete_Delay setting before deleting the Admin_Sent_Image
3. IF the Auto_Delete_Delay setting is 0 or invalid, THEN THE Message_Cleanup_Service SHALL skip auto-deletion of the Admin_Sent_Image
4. WHEN the Image_Handler fails to process the uploaded image, THE Message_Cleanup_Service SHALL NOT delete the Admin_Sent_Image

### Requirement 2: Auto-Delete Confirmation Messages

**User Story:** As an admin, I want confirmation messages to be automatically deleted after a few seconds, so that the chat stays clean after I configure settings.

#### Acceptance Criteria

1. WHEN the Image_Handler successfully sets a section image, THE Message_Cleanup_Service SHALL send a Confirmation_Message and schedule it for auto-deletion
2. THE Message_Cleanup_Service SHALL delete the Confirmation_Message after the Auto_Delete_Delay period expires
3. IF the Auto_Delete_Delay setting is 0 or invalid, THEN THE Message_Cleanup_Service SHALL skip auto-deletion of the Confirmation_Message
4. THE Confirmation_Message SHALL include the section name and confirmation status before being deleted

### Requirement 3: Section-Specific Image Configuration

**User Story:** As an admin, I want to configure separate images for each major bot section, so that users see contextually relevant images in different areas of the bot.

#### Acceptance Criteria

1. THE Image_Settings_Panel SHALL provide image configuration options for Welcome, Shop, Cart, Orders, Wallet, Support, and Admin Panel sections
2. WHEN an admin selects a section from the Image_Settings_Panel, THE System SHALL prompt the admin to send an image for that specific section
3. THE Image_Handler SHALL store each section image with a unique identifier (welcome_image_id, shop_image_id, cart_image_id, orders_image_id, wallet_image_id, support_image_id, admin_panel_image_id)
4. WHEN an admin uploads an image for a section, THE Image_Handler SHALL update only that section's image setting without affecting other sections
5. THE Image_Settings_Panel SHALL display the current status (Set/Not Set) for each section's image

### Requirement 4: Display Section-Specific Images

**User Story:** As a user, I want to see different images in different sections of the bot, so that each area has its own visual identity.

#### Acceptance Criteria

1. WHEN a user navigates to the Welcome section, THE System SHALL display the welcome_image_id if configured
2. WHEN a user navigates to the Shop section, THE System SHALL display the shop_image_id if configured, otherwise fall back to welcome_image_id
3. WHEN a user navigates to the Cart section, THE System SHALL display the cart_image_id if configured
4. WHEN a user navigates to the Orders section, THE System SHALL display the orders_image_id if configured
5. WHEN a user navigates to the Wallet section, THE System SHALL display the wallet_image_id if configured
6. WHEN a user navigates to the Support section, THE System SHALL display the support_image_id if configured
7. WHEN an admin navigates to the Admin Panel section, THE System SHALL display the admin_panel_image_id if configured
8. IF a section-specific image is not configured, THEN THE System SHALL display text-only content without an image

### Requirement 5: Image Settings Management Interface

**User Story:** As an admin, I want an organized interface to manage all section images, so that I can easily see which sections have images configured and update them.

#### Acceptance Criteria

1. THE Image_Settings_Panel SHALL display all available sections in a categorized layout
2. FOR EACH section in the Image_Settings_Panel, THE System SHALL show an indicator (✅ Set or ❌ Not Set) for the image status
3. WHEN an admin clicks on a section in the Image_Settings_Panel, THE System SHALL transition to the image upload prompt for that section
4. THE Image_Settings_Panel SHALL provide a back navigation option to return to the main admin settings
5. WHEN an admin sets an image for a section, THE System SHALL update the Image_Settings_Panel to reflect the new status without requiring a manual refresh

### Requirement 6: Backward Compatibility

**User Story:** As a system administrator, I want the enhanced image settings to work with existing welcome image configurations, so that the upgrade doesn't break existing functionality.

#### Acceptance Criteria

1. IF welcome_image_id exists in the database before the enhancement, THE System SHALL continue to use it for the Welcome section
2. THE System SHALL maintain the existing fallback behavior where shop_image_id falls back to welcome_image_id if not set
3. THE Image_Handler SHALL support the existing database schema while adding new section image fields
4. WHEN a section-specific image is not configured, THE System SHALL gracefully handle the missing image without errors

### Requirement 7: Image Upload State Management

**User Story:** As an admin, I want the bot to correctly track which section I'm uploading an image for, so that my image goes to the right section.

#### Acceptance Criteria

1. WHEN an admin initiates image upload for a section, THE System SHALL store the section identifier in the admin's session state
2. WHEN the Image_Handler receives an image upload, THE System SHALL retrieve the section identifier from the admin's session state
3. THE System SHALL clear the session state after successfully processing the image upload
4. IF an admin sends an image without an active image upload session, THEN THE Image_Handler SHALL ignore the upload
5. THE System SHALL maintain separate session states for different admins uploading images concurrently
