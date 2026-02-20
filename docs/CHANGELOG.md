# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-02-20

### Added
- **Screen Content Manager** - Customize images and text for all screens
- **Global Banner System** - Set one image for all screens with 3-tier priority
- **Welcome Splash** - Personalized welcome screen with user profile
- **Main Menu Hub** - Clean navigation interface separate from welcome
- **Auto-Recovery System** - Handles invalid/expired Telegram file IDs gracefully
- **Restart Notifications** - Detailed admin notifications with auto-delete
- **Stock Overview** - View all product stock at a glance
- **Scoped Message Deletion** - Only temporary messages deleted, navigation preserved

### Changed
- **UI/UX Redesign** - Complete separation of Welcome Splash and Main Menu
- **Image Handling** - Improved with fallback and error recovery
- **Message Management** - Smart deletion policy for cleaner chats
- **Admin Panel** - Added Screen Content button

### Fixed
- **Stock Overview Button** - Handler registration fixed (P0 bug)
- **Git Pull Issues** - WAL files now properly ignored
- **Invalid Images** - No longer crash the bot, auto-cleared with admin notification
- **Message Deletion** - Navigation messages no longer deleted accidentally

### Security
- Admin-only access for Screen Content Manager
- Improved error handling for file operations

## [1.0.0] - 2025-XX-XX

### Added
- Initial release
- Product catalog with categories
- Shopping cart functionality
- Order management system
- Payment proof upload
- Wallet system with top-up
- Support ticket system
- Admin panel with full management
- User management and banning
- Coupon system
- Broadcast messaging
- Daily rewards
- Search functionality
- Force join channels
- Bulk operations

### Features
- Multi-payment method support
- Order tracking
- Payment verification
- User analytics
- Action logging
- Maintenance mode
- Customizable settings

---

## Version History

- **2.0.0** - UI/UX Redesign & Screen Content Manager
- **1.0.0** - Initial Release

## Upgrade Guide

### From 1.x to 2.0

1. **Backup your database:**
   ```bash
   cp nanostore.db nanostore.db.backup
   ```

2. **Stop the bot:**
   ```bash
   sudo systemctl stop nanostore
   ```

3. **Pull latest code:**
   ```bash
   git pull origin main
   ```

4. **Remove WAL files:**
   ```bash
   rm -f nanostore.db-wal nanostore.db-shm
   ```

5. **Start the bot:**
   ```bash
   sudo systemctl start nanostore
   ```

6. **Verify:**
   - Check restart notification in admin DM
   - Test Screen Content Manager
   - Verify all screens load properly

### Breaking Changes

None. Version 2.0 is fully backward compatible with 1.x databases.

### New Settings

The following settings are automatically added on first run:
- `global_banner_image_id` - Global banner image for all screens

All existing settings and data are preserved.
