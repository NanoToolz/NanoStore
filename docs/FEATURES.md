# NanoStore Features Documentation

## 🛒 Customer Features

### Product Browsing
- **Category Navigation**: Browse products organized by categories
- **Product Details**: View detailed product information, images, FAQs
- **Product Media**: Access videos, voice notes, and files for products
- **Stock Information**: Real-time stock availability display
- **Search**: Quick product search by name or description

### Shopping Cart
- **Add to Cart**: Add products with quantity selection
- **Cart Management**: Increase/decrease quantities, remove items
- **Cart Total**: Real-time price calculation
- **Clear Cart**: Remove all items at once
- **Persistent Cart**: Cart saved across sessions

### Order Management
- **Checkout Process**: Streamlined checkout flow
- **Coupon System**: Apply discount coupons
- **Wallet Payment**: Pay using wallet balance
- **Multiple Payment Methods**: Choose from configured payment options
- **Payment Proof Upload**: Upload payment screenshot
- **Order Tracking**: Track order status in real-time
- **Order History**: View all past orders

### Wallet System
- **Balance Display**: View current wallet balance
- **Top-up**: Add funds to wallet
- **Preset Amounts**: Quick top-up with preset amounts
- **Custom Amount**: Enter custom top-up amount
- **Payment Methods**: Multiple payment options for top-up
- **Transaction History**: View all wallet transactions
- **Auto-deduction**: Automatic payment from wallet balance

### Support System
- **Create Tickets**: Open support tickets for issues
- **Ticket Replies**: Reply to existing tickets
- **Ticket History**: View all your tickets
- **Real-time Updates**: Get notified of admin replies
- **Ticket Status**: Track ticket status (open/closed)

### User Experience
- **Welcome Splash**: Personalized welcome with user stats
- **Main Menu Hub**: Clean navigation interface
- **Profile Info**: View your ID, balance, order count
- **Daily Rewards**: Claim free balance daily
- **Help Guide**: Built-in help documentation
- **Responsive UI**: Fast and smooth interface

---

## 👨‍💼 Admin Features

### Dashboard
- **Statistics Overview**: Users, orders, revenue at a glance
- **Pending Items**: Quick view of pending proofs, tickets, top-ups
- **Real-time Data**: Live statistics updates

### Category Management
- **Create Categories**: Add new product categories
- **Edit Categories**: Update name, emoji, sort order
- **Category Images**: Set banner images for categories
- **Toggle Active**: Enable/disable categories
- **Delete Categories**: Remove categories (with confirmation)
- **Sort Order**: Control category display order

### Product Management
- **Add Products**: Create new products with details
- **Edit Products**: Update name, description, price
- **Product Images**: Set product images
- **Stock Management**: Set stock levels (unlimited, limited, out of stock)
- **Pricing**: Set product prices
- **FAQs**: Add/remove product FAQs
- **Media Files**: Attach videos, voice notes, documents
- **Delivery Settings**: Configure auto/manual delivery
- **Delivery Data**: Set delivery content (keys, files, instructions)
- **Toggle Active**: Enable/disable products
- **Delete Products**: Remove products

### Order Processing
- **View All Orders**: List all orders with filters
- **Order Details**: View complete order information
- **Update Status**: Change order status (pending, confirmed, processing, shipped, delivered, cancelled)
- **Payment Verification**: Review payment proofs
- **Customer Notifications**: Auto-notify customers of status changes
- **Order Analytics**: Track order metrics

### Payment Management
- **Payment Methods**: Add/remove payment methods
- **Method Details**: Configure payment instructions
- **Proof Review**: Review uploaded payment proofs
- **Approve/Reject**: Verify and approve/reject payments
- **Auto-delivery**: Trigger automatic product delivery on approval
- **Proof Channel**: Post proofs to dedicated channel

### User Management
- **View Users**: List all registered users
- **User Details**: View user profile, balance, orders
- **Ban/Unban**: Block/unblock users
- **User Analytics**: Track user activity
- **Balance Management**: View user wallet balances

### Coupon System
- **Create Coupons**: Add discount coupons
- **Coupon Settings**: Set discount percentage, max uses
- **Toggle Active**: Enable/disable coupons
- **Usage Tracking**: Monitor coupon usage
- **Delete Coupons**: Remove coupons

### Wallet Top-up Management
- **View Top-ups**: List all top-up requests
- **Top-up Details**: View request details and proof
- **Approve/Reject**: Verify and process top-ups
- **Bonus System**: Configure top-up bonus percentage
- **Auto-credit**: Automatic balance credit on approval
- **User Notifications**: Notify users of approval/rejection

### Screen Content Manager
- **Global Banner**: Set one image for all screens
- **Per-Screen Images**: Customize each screen individually
- **Screen Captions**: Add custom text to screens
- **Image Priority**: 3-tier priority system
- **Clear Images**: Remove screen images
- **Clear Captions**: Reset to default text
- **Managed Screens**: Welcome, Shop, Cart, Orders, Wallet, Support, Admin Panel

### Settings Management
- **Bot Name**: Configure store name
- **Currency**: Set currency symbol
- **Welcome Text**: Customize welcome message
- **Minimum Order**: Set minimum order amount
- **Daily Reward**: Configure daily reward amount
- **Top-up Settings**: Min/max amounts, bonus percentage
- **Maintenance Mode**: Enable/disable bot access
- **Auto-delete**: Configure message auto-deletion

### Force Join Channels
- **Add Channels**: Require users to join channels
- **Channel Details**: Set channel name, invite link
- **Remove Channels**: Delete channel requirements
- **Verification**: Auto-verify user membership

### Bulk Operations
- **Bulk Import**: Import multiple products at once
- **Bulk Stock Update**: Update stock for multiple products
- **CSV Format**: Simple format for bulk operations

### Broadcast System
- **Send Messages**: Broadcast to all users
- **HTML Support**: Rich text formatting
- **Delivery Stats**: Track sent/failed messages
- **User Targeting**: Send to all non-banned users

### Support Ticket Management
- **View Tickets**: List all support tickets
- **Ticket Details**: View ticket conversation
- **Reply to Tickets**: Respond to user tickets
- **Close Tickets**: Mark tickets as resolved
- **Reopen Tickets**: Reopen closed tickets
- **User Notifications**: Auto-notify users of replies

### Action Logging
- **Activity Log**: Track all admin actions
- **User Actions**: Log user activities
- **Audit Trail**: Complete action history
- **Log Channel**: Optional logging to Telegram channel

---

## 🎨 UI/UX Features

### Welcome System
- **Welcome Splash**: First-time greeting with user info
- **Profile Display**: Show user ID, balance, order count
- **Custom Welcome Text**: Configurable welcome message
- **Welcome Image**: Custom welcome screen image
- **Single Button**: Clean "Go to Main Menu" button

### Main Menu Hub
- **Navigation Center**: Central hub for all features
- **Balance Display**: Show current wallet balance
- **Cart Counter**: Display cart item count
- **Admin Access**: Admin panel button for admins
- **Clean Design**: Minimal, focused interface

### Image System
- **3-Tier Priority**:
  1. Screen-specific image (e.g., shop_image_id)
  2. Global banner image (global_banner_image_id)
  3. Global UI image (if enabled)
  4. Text-only mode (fallback)
- **Auto-recovery**: Handle invalid images gracefully
- **Admin Notifications**: Alert admin of image issues
- **Fallback Mode**: Never crash, always show content

### Message Management
- **Smart Editing**: Edit messages instead of delete+send
- **Scoped Deletion**: Only delete temporary messages
- **Navigation Preservation**: Keep main navigation message
- **Auto-delete**: Temporary messages auto-delete (7s confirmations, 60s notifications)
- **Clean Chats**: Minimal message clutter

### Restart Notifications
- **Admin Notification**: Detailed restart info
- **Git Information**: Branch and commit hash
- **Timestamp**: Exact restart time
- **Database Status**: DB health check
- **Auto-delete**: Notification removes after 60 seconds
- **User Notifications**: Optional user restart notices

---

## 🔒 Security Features

### Access Control
- **Admin-only Areas**: Protected admin panel
- **User Verification**: Telegram-based authentication
- **Ban System**: Block malicious users
- **Force Join**: Require channel membership

### Data Protection
- **Environment Variables**: Secure configuration
- **No Hardcoded Secrets**: All sensitive data in .env
- **SQLite Permissions**: Database file protection
- **Action Logging**: Audit trail for accountability

### Error Handling
- **Graceful Failures**: No crashes on errors
- **User-friendly Messages**: Clear error messages
- **Admin Notifications**: Alert admin of critical errors
- **Auto-recovery**: Automatic error recovery where possible

---

## 🚀 Performance Features

### Database
- **SQLite with WAL**: Write-Ahead Logging for performance
- **Async Operations**: Non-blocking database queries
- **Connection Pooling**: Efficient connection management
- **Indexed Queries**: Fast data retrieval

### Caching
- **Settings Cache**: Cached bot settings
- **User Data Cache**: Temporary user data storage
- **State Management**: Efficient state tracking

### Optimization
- **Pagination**: Large lists paginated
- **Lazy Loading**: Load data on demand
- **Efficient Queries**: Optimized database queries
- **Minimal API Calls**: Reduce Telegram API usage

---

## 📊 Analytics Features

### Dashboard Metrics
- **Total Users**: Registered user count
- **Total Orders**: Order count
- **Revenue**: Total revenue tracking
- **Pending Items**: Proofs, tickets, top-ups count

### Order Analytics
- **Order Status**: Track order states
- **Payment Status**: Monitor payment states
- **Revenue Tracking**: Calculate total revenue
- **Order History**: Complete order records

### User Analytics
- **User Count**: Total registered users
- **Active Users**: Track user activity
- **Ban Statistics**: Monitor banned users
- **User Balances**: Track wallet balances

---

## 🔧 Developer Features

### Code Organization
- **Modular Structure**: Organized by feature
- **Handler Separation**: Each feature in own file
- **Helper Functions**: Reusable utility functions
- **Keyboard Definitions**: Centralized keyboard management

### Configuration
- **Environment-based**: Easy configuration via .env
- **Database Settings**: Runtime configurable settings
- **Validation**: Config validation on startup

### Logging
- **Python Logging**: Standard logging framework
- **Log Levels**: Debug, info, warning, error
- **Log Channel**: Optional Telegram logging
- **Action Logs**: Database-stored action logs

### Error Recovery
- **Try-Catch Blocks**: Comprehensive error handling
- **Fallback Mechanisms**: Graceful degradation
- **User Notifications**: Inform users of issues
- **Admin Alerts**: Critical error notifications

---

**Total Features: 100+**
**Last Updated: 2026-02-20**
**Version: 2.0.0**
