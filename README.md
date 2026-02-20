# 🛍️ NanoStore - Telegram E-Commerce Bot

A feature-rich Telegram bot for running a complete digital store with automated order management, payment processing, and customer support.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![python-telegram-bot](https://img.shields.io/badge/python--telegram--bot-21.0+-blue.svg)](https://python-telegram-bot.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## ✨ Features

### 🛒 Customer Features

**Shopping Experience:**
- **Product Catalog** - Browse categories with custom images and emojis
- **Product Details** - View descriptions, prices, stock, images, FAQs, and media
- **Shopping Cart** - Add, remove, increment/decrement quantities
- **Stock Tracking** - Real-time stock availability (Unlimited, In Stock, Low Stock, Out of Stock)
- **Product Search** - Find products by name or description
- **Category Images** - Each category can have a custom banner image

**Order Management:**
- **Smart Checkout** - Review order, apply coupons, use wallet balance
- **Multiple Payment Methods** - Support for various payment options
- **Payment Proof Upload** - Upload screenshot for verification
- **Order Tracking** - Track status: Pending → Confirmed → Processing → Delivered
- **Order History** - View all past orders with pagination
- **Order Details** - See itemized breakdown, payment status, dates

**Wallet System:**
- **Balance Management** - Top-up and use wallet for payments
- **Multiple Top-Up Amounts** - Preset amounts or custom input
- **Top-Up Bonus** - Optional bonus percentage on top-ups
- **Transaction History** - View all top-up requests and status
- **Partial Payment** - Use wallet + payment method combination

**Coupon System:**
- **Discount Codes** - Apply percentage-based discount coupons
- **Usage Limits** - Coupons can have max usage limits
- **Validation** - Automatic validation and expiry checking
- **One-time Use** - Prevents duplicate coupon usage per order

**Support System:**
- **Ticket Creation** - Create support tickets with subject and message
- **Ticket Tracking** - View all your tickets and their status
- **Conversation Thread** - Reply to admin responses
- **Status Indicators** - Open (🟢) or Closed (🔴)

**Daily Rewards:**
- **Free Balance** - Claim daily reward (configurable amount)
- **24-Hour Cooldown** - One claim per day
- **Automatic Credit** - Instantly added to wallet

**User Interface:**
- **Welcome Splash** - Personalized greeting with user profile (ID, username, orders, balance)
- **Main Menu Hub** - Clean navigation with balance display
- **Custom Images** - Each screen can have unique images
- **HTML Formatting** - Rich text support for descriptions
- **Emoji Support** - Visual indicators for status, categories, features

### 👨‍💼 Admin Features

**Dashboard & Analytics:**
- **Statistics Overview** - Total users, orders, revenue, pending items
- **Real-time Counts** - Pending proofs, open tickets, pending top-ups
- **Quick Navigation** - Direct access to all admin features
- **Action Logging** - Track all admin actions for audit trail

**Category Management:**
- **CRUD Operations** - Create, Read, Update, Delete categories
- **Custom Images** - Upload banner images for each category
- **Emoji Support** - Add emojis to category names
- **Sort Order** - Control display order
- **Active/Inactive** - Toggle category visibility
- **Product Count** - See how many products in each category

**Product Management:**
- **Full CRUD** - Complete product lifecycle management
- **Rich Descriptions** - HTML-formatted product descriptions
- **Image Upload** - Product thumbnail images
- **Stock Management** - Set stock levels (unlimited, limited, out of stock)
- **Pricing** - Flexible pricing with currency support
- **FAQ System** - Add multiple Q&A pairs per product
- **Media Gallery** - Attach videos, files, voice notes
- **Delivery Types**:
  - **Auto Delivery** - Instant delivery after payment approval
  - **Manual Delivery** - Admin manually delivers
- **Delivery Data** - Store license keys, download links, or files

**Order Processing:**
- **Order List** - View all orders with pagination
- **Order Details** - Complete order breakdown with user info
- **Status Management** - Update order status with user notifications
- **Payment Tracking** - Monitor payment status
- **User Notifications** - Automatic notifications on status changes

**Payment Verification:**
- **Proof Review** - View payment screenshots with order details
- **Approve/Reject** - Process payments with optional notes
- **Channel Posting** - Auto-post approved proofs to channel
- **Admin Notifications** - Instant alerts for new proofs
- **Proof History** - Track all payment proofs

**Wallet Top-Up Management:**
- **Top-Up Queue** - View pending top-up requests
- **Proof Verification** - Review payment screenshots
- **Approve/Reject** - Process with admin notes
- **Balance Credit** - Automatic balance addition on approval
- **Bonus Calculation** - Optional bonus percentage
- **User Notifications** - Automatic status updates

**User Management:**
- **User List** - View all registered users
- **User Details** - Profile, balance, order count, join date
- **Ban/Unban** - Control user access
- **User Search** - Find users by ID or username
- **Activity Tracking** - Monitor user actions

**Coupon Management:**
- **Create Coupons** - Set code, discount %, max uses
- **Toggle Active** - Enable/disable coupons
- **Usage Tracking** - Monitor how many times used
- **Delete Coupons** - Remove expired or unused coupons
- **Unlimited Uses** - Set max_uses to 0 for unlimited

**Payment Method Management:**
- **Add Methods** - Create payment options with details
- **Custom Details** - Bank info, wallet addresses, instructions
- **Emoji Icons** - Visual identification
- **Active/Inactive** - Control availability
- **Delete Methods** - Remove unused options

**Screen Content Manager:**
- **7 Customizable Screens** - Welcome, Shop, Cart, Orders, Wallet, Support, Admin Panel
- **Image Upload** - Set custom images per screen
- **Text Customization** - Override default text with custom captions
- **HTML Support** - Rich formatting for text
- **Clear Options** - Reset to defaults
- **Global Banner** - Set one image for all screens
- **Preview Mode** - Test changes before users see them

**Settings Configuration:**
- **Bot Name** - Customize store name
- **Currency** - Set currency symbol (Rs, $, €, etc.)
- **Welcome Text** - Custom welcome message
- **Minimum Order** - Set minimum order amount
- **Daily Reward** - Configure daily reward amount
- **Top-Up Settings**:
  - Min/Max amounts
  - Bonus percentage
  - Enable/Disable
- **UI Settings**:
  - Global image toggle
  - Per-screen image toggle
  - Auto-delete timers
- **Maintenance Mode** - Temporarily disable bot

**Force Join System:**
- **Channel Requirements** - Require users to join channels
- **Multiple Channels** - Add multiple required channels
- **Invite Links** - Auto-generate join buttons
- **Verification** - Check membership before access

**Bulk Operations:**
- **Bulk Stock Update** - Update multiple products at once
- **Product Import** - Import products from CSV/JSON
- **Export Data** - Export orders, users, products

**Broadcast System:**
- **Mass Messaging** - Send messages to all users
- **Rich Content** - Support for text, images, formatting
- **Delivery Stats** - Track successful/failed deliveries
- **Confirmation** - Preview before sending

**Support Ticket Management:**
- **Ticket Queue** - View all tickets or open only
- **Ticket Details** - Full conversation thread
- **Reply System** - Respond to user tickets
- **Close/Reopen** - Manage ticket status
- **User Notifications** - Auto-notify on admin replies

### 🎨 UI/UX Features

**Visual Design:**
- **Welcome Splash** - Professional first impression with user profile
- **Main Menu Hub** - Clean, organized navigation
- **Custom Images** - Per-screen or global banner images
- **Emoji Indicators** - Visual status indicators (✅ ⏳ ❌ 🟢 🔴)
- **HTML Formatting** - Bold, italic, code blocks, links
- **Responsive Keyboards** - Dynamic buttons based on context

**User Experience:**
- **Auto-Recovery** - Handles invalid images gracefully
- **Smart Deletion** - Cleans up temporary messages automatically
- **Inline Editing** - Updates messages in-place (no spam)
- **Pagination** - Handles large lists efficiently
- **Loading States** - Typing indicators for long operations
- **Error Handling** - User-friendly error messages
- **Confirmation Dialogs** - Prevent accidental actions

**Navigation:**
- **Breadcrumb Navigation** - Always know where you are
- **Back Buttons** - Easy navigation to previous screens
- **Home Button** - Quick return to main menu
- **Context-Aware** - Buttons change based on state

**Performance:**
- **Async Operations** - Non-blocking database queries
- **Connection Pooling** - Efficient database connections
- **WAL Mode** - Better concurrent access
- **Lazy Loading** - Load data only when needed
- **Caching** - Reduce redundant database queries

### 🔒 Security Features

**Access Control:**
- **Admin-Only Functions** - Strict permission checking
- **User Ban System** - Block malicious users
- **Session Management** - Secure state handling
- **Input Validation** - Prevent injection attacks

**Data Protection:**
- **Environment Variables** - No hardcoded secrets
- **SQLite Encryption** - Optional database encryption
- **Secure File Handling** - Safe file ID storage
- **Audit Logging** - Track all admin actions

**Error Handling:**
- **Graceful Degradation** - Fallback to safe states
- **Error Logging** - Detailed error tracking
- **Admin Notifications** - Alert on critical errors
- **User-Friendly Messages** - No technical jargon exposed

## 📋 Requirements

- Python 3.9 or higher
- SQLite 3
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/NanoToolz/NanoStore.git
cd NanoStore
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `config/.env.example` to `.env` in the root directory:

```bash
cp config/.env.example .env
```

Edit `.env`:

```env
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_user_id
LOG_CHANNEL_ID=your_log_channel_id  # Optional
PROOFS_CHANNEL_ID=your_proofs_channel_id  # Optional
```

**How to get your values:**
- `BOT_TOKEN`: Create a bot with [@BotFather](https://t.me/BotFather) and copy the token
- `ADMIN_ID`: Send a message to [@userinfobot](https://t.me/userinfobot) to get your user ID
- `LOG_CHANNEL_ID`: Create a channel, add your bot as admin, forward a message to [@userinfobot](https://t.me/userinfobot)
- `PROOFS_CHANNEL_ID`: Same as LOG_CHANNEL_ID (can be the same channel or different)

### 4. Run the Bot

```bash
python bot.py
```

The bot will:
- Initialize the SQLite database automatically
- Create all required tables in `data/` folder
- Set default settings
- Send a restart notification to the admin
- Start polling for updates

**First-time setup:**
1. Start the bot: `/start`
2. Access Admin Panel (you'll see it in the main menu)
3. Configure your store settings
4. Add categories and products
5. Set up payment methods

## 📁 Project Structure

```
NanoStore/
├── bot.py               # Main entry point (run this file)
├── requirements.txt     # Python dependencies
├── .env                 # Environment configuration (create from config/.env.example)
├── .gitignore          # Git ignore rules
├── LICENSE             # MIT License
├── README.md           # This file
│
├── src/                # Source code directory (organized by category)
│   ├── core/          # Core bot functionality
│   │   └── bot.py    # Bot initialization and handler registration
│   │
│   ├── config/        # Configuration management
│   │   └── config.py # Environment loader
│   │
│   ├── database/      # Database layer
│   │   └── database.py # SQLite operations (14 tables, all CRUD)
│   │
│   ├── utils/         # Utilities and helpers
│   │   ├── helpers.py  # Helper functions (render_screen, safe_edit, etc.)
│   │   └── keyboards.py # Telegram inline keyboards
│   │
│   └── handlers/      # Business logic handlers
│       ├── start.py          # Start, main menu, help, welcome
│       ├── catalog.py        # Shop, categories, products, FAQs
│       ├── cart.py           # Shopping cart operations
│       ├── orders.py         # Checkout, payment, order tracking
│       ├── wallet.py         # Wallet balance, top-up, history
│       ├── tickets.py        # Support ticket system
│       ├── search.py         # Product search
│       ├── rewards.py        # Daily reward system
│       ├── admin.py          # Admin panel (all admin features)
│       └── admin_content.py  # Screen Content Manager
│
├── config/             # Configuration files
│   └── .env.example   # Environment template
│
├── docs/              # Documentation
│   ├── CHANGELOG.md   # Version history and updates
│   ├── FEATURES.md    # Detailed feature documentation
│   └── STRUCTURE.md   # Project structure details
│
└── data/              # Database storage (auto-created)
    └── nanostore.db   # SQLite database (auto-created on first run)
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `BOT_TOKEN` | Your Telegram bot token from BotFather | Yes |
| `ADMIN_ID` | Your Telegram user ID (admin access) | Yes |
| `LOG_CHANNEL_ID` | Channel ID for logging (optional) | No |
| `PROOFS_CHANNEL_ID` | Channel ID for payment proofs (optional) | No |

### Database Settings

The bot uses SQLite with the following configurable settings (via Admin Panel):

- **Bot Name** - Store name
- **Currency** - Currency symbol (Rs, $, €, etc.)
- **Welcome Text** - Custom welcome message
- **Minimum Order** - Minimum order amount
- **Daily Reward** - Daily reward amount
- **Top-up Settings** - Min/max amounts, bonus percentage
- **Maintenance Mode** - Enable/disable bot access

## � Screenshots

### User Interface
- Welcome Splash with user profile
- Main Menu Hub with navigation
- Product catalog with categories
- Shopping cart with item management
- Order tracking and history

### Admin Interface
- Dashboard with statistics
- Category and product management
- Order processing and verification
- Screen Content Manager
- User management and analytics

## 🎯 Usage

### For Customers

**Getting Started:**
1. Start the bot: `/start`
2. View welcome screen with your profile info
3. Tap "Go to Main Menu" to access the hub

**Shopping:**
1. Browse products: Tap "🛍️ Browse Shop"
2. Select category: Choose from available categories
3. View product: Tap on any product to see details
4. Add to cart: Tap "🛒 Add to Cart"
5. Adjust quantity: Use +/- buttons in cart
6. Checkout: Tap "✅ Checkout" when ready

**Payment:**
1. Review order summary
2. Apply coupon (optional): Tap "🎫 Apply Coupon"
3. Use wallet balance (optional): Tap "💳 Use Balance"
4. Confirm order: Tap "✅ Confirm Order"
5. Select payment method
6. Upload payment proof (screenshot)
7. Wait for admin approval

**Order Tracking:**
1. Go to "📦 My Orders"
2. View all your orders
3. Tap on any order to see details
4. Check status: Pending → Confirmed → Processing → Delivered

**Wallet Management:**
1. Go to "💳 My Wallet"
2. View current balance
3. Tap "💰 Top-Up" to add funds
4. Select amount (preset or custom)
5. Choose payment method
6. Upload payment proof
7. Wait for admin approval

**Support:**
1. Go to "🎫 Support"
2. Tap "➕ New Ticket"
3. Enter subject and message
4. Submit ticket
5. View replies in "📋 My Tickets"
6. Reply to admin responses

### For Admins

**Dashboard:**
1. Access: Main Menu → "⚙️ Admin Panel"
2. View statistics: Users, Orders, Revenue, Pending items
3. Quick access to all admin features

**Category Management:**
1. Admin Panel → "📂 Categories"
2. Add category: Tap "➕ Add Category"
3. Edit category: Select category → Edit details
4. Set image: Upload category banner
5. Delete category: Removes category and all products

**Product Management:**
1. Admin Panel → "📂 Categories" → Select category
2. Add product: Tap "➕ Add Product"
3. Set details: Name, description, price, stock
4. Upload image: Product thumbnail
5. Add FAQs: Common questions and answers
6. Add media: Videos, files, voice notes
7. Set delivery: Auto (instant) or Manual
8. Set delivery data: License keys, download links, files

**Order Processing:**
1. Admin Panel → "🛒 Orders"
2. View all orders
3. Select order to review
4. Update status: Pending → Confirmed → Processing → Delivered
5. User receives notification automatically

**Payment Verification:**
1. Admin Panel → "📸 Proofs" (shows pending count)
2. View payment screenshot
3. Check order details
4. Approve: Marks order as paid, notifies user
5. Reject: Notifies user with reason
6. Post to channel: Share proof in proofs channel

**Wallet Top-Up Approval:**
1. Admin Panel → "💳 Top-Ups"
2. View pending top-up requests
3. Check payment proof
4. Approve: Adds balance to user wallet
5. Reject: Notifies user with reason

**User Management:**
1. Admin Panel → "👥 Users"
2. View all registered users
3. Select user to see details
4. Ban/Unban users
5. View user's order history and balance

**Coupon System:**
1. Admin Panel → "🎫 Coupons"
2. Add coupon: Code, discount %, max uses
3. Toggle active/inactive
4. Delete expired coupons
5. Track usage statistics

**Screen Customization:**
1. Admin Panel → "🎨 Screen Content"
2. Select screen to customize
3. Upload image: Tap "🖼️ Set Image"
4. Set text: Tap "📝 Edit Text" (supports HTML)
5. Clear: Remove custom image/text
6. Preview: Test in user mode

**Settings:**
1. Admin Panel → "⚙️ Settings"
2. Configure bot name, currency
3. Set minimum order amount
4. Configure wallet top-up limits
5. Enable/disable features
6. Set daily reward amount
7. Configure force join channels

**Broadcast:**
1. Admin Panel → "📢 Broadcast"
2. Send message to all users
3. Supports text, images, and formatting
4. Shows delivery statistics

**Support Tickets:**
1. Admin Panel → "🎫 Tickets" (shows open count)
2. View all tickets or open only
3. Select ticket to view conversation
4. Reply to user
5. Close/Reopen tickets

## 🛠️ Advanced Features

### Screen Content Manager

Customize images and text for each screen:

1. Admin Panel → "🎨 Screen Content"
2. Select screen (Welcome, Shop, Cart, Orders, Wallet, Support, Admin Panel)
3. Set image and/or custom text
4. Use Global Banner for all screens or per-screen images

**Available Screens:**
- **Welcome** - First screen users see after /start
- **Shop** - Product catalog main screen
- **Cart** - Shopping cart view
- **Orders** - Order history and tracking
- **Wallet** - Wallet balance and top-up
- **Support** - Support ticket system
- **Admin Panel** - Admin dashboard

### 3-Tier Image Priority System

The bot uses an intelligent 3-tier fallback system for images:

1. **Screen-specific image** (e.g., `shop_image_id`) - Highest priority
2. **Global banner image** (`global_banner_image_id`) - Second priority
3. **Global UI image** (`global_ui_image_id`) - Third priority (if enabled)
4. **Text-only mode** - Final fallback

**Example:**
- If Shop screen has no specific image, it uses Global Banner
- If Global Banner is not set, it uses Global UI Image (if enabled)
- If none are set, displays text-only

### Auto-Recovery System

The bot automatically handles invalid or expired Telegram file IDs:

- **Detection**: Catches "wrong file identifier" errors
- **Auto-clear**: Removes corrupted image settings
- **Admin notification**: Sends DM to admin with details
- **Graceful fallback**: Switches to text-only mode
- **No crashes**: Users never see errors

**How it works:**
1. Bot tries to send image
2. If file_id is invalid, catches error
3. Clears the setting from database
4. Notifies admin via DM (auto-deletes after 60s)
5. Falls back to text-only rendering
6. User experience remains smooth

### Smart Message Management

The bot intelligently manages messages to keep chats clean:

- **Navigation messages**: Kept and edited in-place
- **Temporary prompts**: Auto-deleted after user responds
- **Confirmation messages**: Auto-deleted after 7 seconds
- **Admin notifications**: Auto-deleted after 60 seconds
- **User uploads**: Deleted after processing

**Benefits:**
- Clean chat history
- No message spam
- Professional appearance
- Better user experience

## 🔒 Security

- Admin-only access control for sensitive operations
- User ban system
- Payment proof verification
- Action logging for audit trail
- Environment-based configuration (no hardcoded secrets)

## 🐛 Troubleshooting

### Bot not starting?

```bash
# Check Python version
python --version  # Should be 3.9+

# Verify dependencies
pip install -r requirements.txt

# Check .env file
cat .env  # Ensure BOT_TOKEN and ADMIN_ID are set
```

### Database issues?

```bash
# Remove WAL files (when bot is stopped)
rm -f nanostore.db-wal nanostore.db-shm

# Backup database
cp nanostore.db nanostore.db.backup
```

### Git pull blocked by WAL files?

```bash
# Stop bot first
sudo systemctl stop nanostore

# Remove WAL files
rm -f nanostore.db-wal nanostore.db-shm nanostore.db-journal

# Pull updates
git pull origin main

# Start bot
sudo systemctl start nanostore
```

## 📝 Development

### Architecture

**Design Pattern: MVC-like Structure**
- **Models**: `database.py` - Data layer with async SQLite operations
- **Views**: `keyboards.py` + `helpers.py` - UI rendering and formatting
- **Controllers**: `handlers/` - Business logic and user interactions
- **Config**: `config.py` - Environment and settings management

**Key Components:**

1. **Bot Core** (`src/bot.py`)
   - Application initialization
   - Handler registration
   - Error handling
   - Post-init hooks (database setup, admin notifications)

2. **Database Layer** (`src/database.py`)
   - Async SQLite with aiosqlite
   - 14 tables: users, categories, products, orders, payments, etc.
   - CRUD operations for all entities
   - Transaction management
   - Foreign key constraints

3. **Helper Functions** (`src/helpers.py`)
   - `render_screen()` - 3-tier image rendering with fallback
   - `safe_edit()` - Error-safe message editing
   - `resolve_image_id()` - Image priority resolution
   - `schedule_delete()` - Auto-delete messages
   - `send_restart_notification()` - Admin notifications
   - Formatting utilities (HTML escape, status emojis, etc.)

4. **Keyboards** (`src/keyboards.py`)
   - Dynamic inline keyboard generation
   - Context-aware button layouts
   - Pagination support
   - Callback data encoding

5. **Handlers** (`src/handlers/`)
   - Modular handler organization
   - Async callback query handlers
   - State management via `context.user_data`
   - Text/photo routers for multi-step flows

**Database Schema:**

```sql
-- Core Tables
users (user_id, full_name, username, balance, banned, joined_at)
categories (id, name, emoji, image_id, sort_order, active, created_at)
products (id, category_id, name, description, price, stock, image_id, active, delivery_type, delivery_data)
product_faqs (id, product_id, question, answer)
product_media (id, product_id, media_type, file_id)

-- Shopping Tables
cart (id, user_id, product_id, quantity, added_at)
orders (id, user_id, items_json, total, status, payment_status, payment_method_id, payment_proof_id, coupon_code, created_at)

-- Payment Tables
payment_methods (id, name, details, emoji, active)
payment_proofs (id, user_id, order_id, method_id, file_id, status, reviewed_by, admin_note, created_at)
wallet_topups (id, user_id, amount, method_id, proof_file_id, status, admin_note, reviewed_by, created_at)

-- System Tables
coupons (code, discount_percent, max_uses, used_count, active, created_at)
settings (key, value)
force_join_channels (id, channel_id, name, invite_link)
tickets (id, user_id, subject, message, status, created_at)
ticket_replies (id, ticket_id, sender, message, created_at)
action_logs (id, action, user_id, details, created_at)
```

**State Management:**

The bot uses `context.user_data` for temporary state:

```python
# Example: Multi-step product creation
context.user_data["state"] = "adm_prod_name:123"
context.user_data["temp"] = {"cat_id": 123, "name": "Product Name"}

# Example: Order checkout
context.user_data["temp"] = {
    "order_id": 456,
    "original_total": 100.0,
    "discount": 10.0,
    "balance_used": 20.0
}
```

**Message Flow:**

1. User clicks button → CallbackQuery
2. Handler processes query
3. `render_screen()` or `safe_edit()` updates message
4. Keyboard provides next actions
5. Temporary messages auto-deleted
6. Navigation messages edited in-place

### Running in Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run with debug logging
python bot.py

# Or with custom log level
LOG_LEVEL=DEBUG python bot.py
```

**Development Tips:**

1. **Testing Changes:**
   ```bash
   # Compile check all files
   python -m py_compile src/*.py src/handlers/*.py
   
   # Run bot in test mode
   python bot.py
   ```

2. **Database Inspection:**
   ```bash
   # Open database
   sqlite3 nanostore.db
   
   # View tables
   .tables
   
   # Query data
   SELECT * FROM users LIMIT 10;
   SELECT * FROM settings;
   ```

3. **Debugging:**
   - Check logs in console
   - Use `logger.info()` for debugging
   - Test with your own Telegram account
   - Use separate test bot for development

4. **Hot Reload:**
   - Stop bot (Ctrl+C)
   - Make changes
   - Restart bot
   - Database persists between restarts

### Code Style

**Python Standards:**
- Follow PEP 8 guidelines
- Use type hints where possible
- Document functions with docstrings
- Keep functions focused and small (< 50 lines)
- Use async/await for I/O operations

**Naming Conventions:**
- Functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private functions: `_leading_underscore`

**Example:**
```python
async def product_detail_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show full product details.
    
    Args:
        update: Telegram update object
        context: Bot context with user_data
    
    Returns:
        None
    """
    query = update.callback_query
    await query.answer()
    
    product_id = int(query.data.split(":")[1])
    product = await get_product(product_id)
    
    if not product:
        await safe_edit(query, "❌ Product not found.", reply_markup=back_kb("shop"))
        return
    
    # ... rest of handler
```

**Error Handling:**
```python
try:
    await risky_operation()
except BadRequest as e:
    logger.warning(f"BadRequest: {e}")
    await query.answer("⚠️ Operation failed.", show_alert=True)
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    await query.answer("❌ An error occurred.", show_alert=True)
```

### Testing

**Manual Testing Checklist:**

User Flow:
- [ ] /start command works
- [ ] Welcome screen displays correctly
- [ ] Main menu navigation works
- [ ] Can browse categories
- [ ] Can view products
- [ ] Can add to cart
- [ ] Can checkout
- [ ] Can upload payment proof
- [ ] Can view orders
- [ ] Can top-up wallet
- [ ] Can create support ticket

Admin Flow:
- [ ] Can access admin panel
- [ ] Can add category
- [ ] Can add product
- [ ] Can upload images
- [ ] Can process orders
- [ ] Can verify payments
- [ ] Can approve top-ups
- [ ] Can customize screens
- [ ] Can broadcast messages
- [ ] Can manage users

**Database Testing:**
```bash
# Check database integrity
sqlite3 nanostore.db "PRAGMA integrity_check;"

# Verify foreign keys
sqlite3 nanostore.db "PRAGMA foreign_key_check;"

# Count records
sqlite3 nanostore.db "SELECT 
    (SELECT COUNT(*) FROM users) as users,
    (SELECT COUNT(*) FROM products) as products,
    (SELECT COUNT(*) FROM orders) as orders;"
```

### Deployment

**Production Setup:**

1. **Server Requirements:**
   - Ubuntu 20.04+ or similar Linux
   - Python 3.9+
   - 1GB RAM minimum
   - 10GB disk space

2. **Install Dependencies:**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip git
   pip3 install -r requirements.txt
   ```

3. **Configure Environment:**
   ```bash
   cp config/.env.example .env
   nano .env  # Edit with your values
   ```

4. **Create Systemd Service:**
   ```bash
   sudo nano /etc/systemd/system/nanostore.service
   ```
   
   ```ini
   [Unit]
   Description=NanoStore Telegram Bot
   After=network.target
   
   [Service]
   Type=simple
   User=your_user
   WorkingDirectory=/path/to/NanoStore
   ExecStart=/usr/bin/python3 /path/to/NanoStore/bot.py
   Restart=always
   RestartSec=10
   
   [Install]
   WantedBy=multi-user.target
   ```

5. **Start Service:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable nanostore
   sudo systemctl start nanostore
   sudo systemctl status nanostore
   ```

6. **View Logs:**
   ```bash
   sudo journalctl -u nanostore -f
   ```

**Backup Strategy:**

```bash
# Backup database
cp nanostore.db backups/nanostore-$(date +%Y%m%d).db

# Backup .env
cp .env backups/.env-$(date +%Y%m%d)

# Automated daily backup (crontab)
0 2 * * * cd /path/to/NanoStore && cp nanostore.db backups/nanostore-$(date +\%Y\%m\%d).db
```

**Update Procedure:**

```bash
# Stop bot
sudo systemctl stop nanostore

# Backup database
cp nanostore.db nanostore.db.backup

# Pull updates
git pull origin main

# Install new dependencies
pip3 install -r requirements.txt

# Start bot
sudo systemctl start nanostore

# Check status
sudo systemctl status nanostore
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [python-telegram-bot](https://python-telegram-bot.org/) - Telegram Bot API wrapper
- [aiosqlite](https://github.com/omnilib/aiosqlite) - Async SQLite interface
- All contributors and users of NanoStore

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/NanoToolz/NanoStore/issues)
- **Telegram**: [@NanoToolz](https://t.me/NanoToolz)
- **Email**: support@nanotoolz.com

## 🗺️ Roadmap

- [ ] Multi-language support
- [ ] Cryptocurrency payment integration
- [ ] Advanced analytics dashboard
- [ ] Product reviews and ratings
- [ ] Referral system
- [ ] Subscription products
- [ ] API for external integrations

---

**Made with ❤️ by NanoToolz**

⭐ Star this repo if you find it useful!
