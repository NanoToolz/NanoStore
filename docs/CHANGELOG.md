# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - 2026-02-20

### Added - Major Feature Update 🎉

**Gamification & Engagement:**
- **Points System** - Separate from wallet, earned via spin/referrals (not purchases)
- **Daily Spin** - Random rewards (50-2,000 pts) with rarity tiers (Common/Rare/Epic/Legendary)
- **Referral System** - Unique links with automatic rewards (500 pts new user, 1,000 pts referrer)
- **Referral Tracking** - View referred users, stats, and history
- **Points History** - Track all points transactions

**Multi-Currency Support:**
- **5 Currencies** - PKR, USD, AED, SAR, GBP with flags
- **Live Exchange Rates** - Fetched from CoinGecko API every 5 minutes
- **Auto-Conversion** - All prices shown in user's selected currency
- **Fallback System** - Uses cached rates if API fails
- **User Preferences** - Easy currency switching from wallet

**Enhanced Welcome Screen:**
- **Comprehensive Stats** - Balance, spent, deposited, orders, referrals
- **VIP Status** - Automatic recognition for high spenders (>10k PKR)
- **Member Since** - Shows join date
- **Spin Status** - Real-time availability display
- **Referral Count** - See how many friends joined
- **Order Summary** - Total, completed, and pending orders

**Database Schema:**
- New tables: `points_history`, `referrals`, `currency_rates`
- New user columns: `points`, `currency`, `last_spin`, `referrer_id`, `total_spent`, `total_deposited`
- Automatic tracking of spending and deposits

**New Handlers:**
- `src/handlers/referral.py` - Referral program management
- `src/handlers/preferences.py` - User preferences and currency selection
- `src/handlers/rewards.py` - Completely rewritten for daily spin system

### Changed

**Main Menu Layout:**
- Row 1: 🛍️ Shop (full width)
- Row 2: 🛒 Cart | 📦 My Orders
- Row 3: 💳 Wallet | 🎫 Support
- Row 4: 🎰 Daily Spin | 👥 Referral (NEW!)
- Removed: ❓ Help, 🔍 Search buttons

**Welcome Screen:**
- Now shows comprehensive user statistics
- Displays VIP status for high spenders
- Shows spin availability and referral count
- All amounts in user's selected currency

**Daily Reward → Daily Spin:**
- Replaced fixed daily reward with gamified spin system
- Random rewards with rarity tiers
- Visual feedback with rarity indicators
- 24-hour cooldown with exact time display

**Wallet Menu:**
- Added "⚙️ Preferences" button
- Access to currency selection

**Language:**
- Bot is now English-only (removed language system)
- All messages hardcoded in English

### Fixed
- Referral link detection in /start command
- Currency conversion in all price displays
- Spending/deposit tracking on order completion and topup approval

### Dependencies
- Added `aiohttp==3.9.1` for currency API calls

### Documentation
- `IMPLEMENTATION_SUMMARY.md` - Detailed feature documentation
- `DATABASE_MIGRATION.md` - Migration guide and SQL scripts
- `QUICK_START.md` - Quick start guide for new features
- Updated `README.md` with new features section

### Migration Notes
- Database migration is automatic on first run
- Existing users get default values (0 points, PKR currency)
- Optional backfill scripts available for total_spent and total_deposited
- See `DATABASE_MIGRATION.md` for details

### Breaking Changes
- Daily reward system replaced with daily spin (different mechanics)
- Main menu layout changed (removed Help and Search buttons)
- Language selection removed (English only)

### Known Limitations
- Points usage in checkout not yet implemented (max 20% discount)
- Search functionality not yet moved inside shop
- Birthday bonus system not yet implemented

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
