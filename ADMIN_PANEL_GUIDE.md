# 🎛️ Admin Panel - Complete Guide

## 📋 Table of Contents
1. [Main Dashboard](#main-dashboard)
2. [Categories Management](#categories-management)
3. [Products Management](#products-management)
4. [Orders Management](#orders-management)
5. [Users Management](#users-management)
6. [Payments & Proofs](#payments--proofs)
7. [Coupons System](#coupons-system)
8. [Settings](#settings)
9. [Broadcast](#broadcast)
10. [Statistics](#statistics)

---

## 🏠 Main Dashboard

**Access**: `/start` → Admin Panel button (only visible to admin)

**File**: `src/handlers/admin.py` - Line 62-108

### Main Menu Options:
```
📂 Categories      - Manage product categories
📦 Products        - Manage products
📋 Orders          - View and manage orders
👥 Users           - User management
💳 Payments        - Payment methods
📸 Proofs          - Payment proof verification
🎟️ Coupons        - Discount coupons
⚙️ Settings        - Bot configuration
📣 Broadcast       - Send messages to all users
📊 Statistics      - View analytics
```

---

## 📂 Categories Management

**File**: `src/handlers/admin.py` - Lines 143-254

### Features:

#### 1. View All Categories
- Shows list of all categories
- Displays emoji + name
- Click to view details

#### 2. Add Category
**Flow**:
```
Click "➕ Add Category"
  ↓
Enter category name
  ↓
Upload category image (optional)
  ↓
Category created ✓
```

**Code Location**: Line 154-169

#### 3. Edit Category
- Edit name
- Edit emoji
- Change image
- Delete category

**Code Location**: Line 193-210

#### 4. Delete Category
**Warning**: Deletes all products in that category!

**Code Location**: Line 211-231

---

## 📦 Products Management

**File**: `src/handlers/admin.py` - Lines 255-485

### Features:

#### 1. View Products by Category
- Shows all products in selected category
- Displays: Name, Price, Stock
- Click to view details

**Code Location**: Line 255-275

#### 2. Add Product (3-Step Process)
```
Step 1: Enter product name
  ↓
Step 2: Enter description (or skip with -)
  ↓
Step 3: Enter price
  ↓
Product created ✓
```

**Code Location**: Line 276-292

**Text Handler**: Line 1771-1870

#### 3. Product Details View
Shows:
- 🆔 Product ID
- 💰 Price
- 📊 Stock
- 📂 Category
- 🖼️ Image status
- 🚀 Delivery type (Auto/Manual)
- 📝 Description

**Code Location**: Line 293-328

#### 4. Edit Product
Options:
- ✏️ Edit Name
- ✏️ Edit Description
- ✏️ Edit Price
- 🖼️ Set Image
- 📦 Set Stock
- 🚀 Set Delivery

**Code Location**: Line 329-347

#### 5. Set Product Image
Upload photo to set as product image

**Code Location**: Line 372-386

#### 6. Set Stock
Enter number to set available stock

**Code Location**: Line 387-405

#### 7. Delivery System
**Two Types**:

**A. Auto Delivery** (Instant):
- Upload file/image/text
- Automatically sent to customer after payment
- Best for: Digital products, files, codes

**B. Manual Delivery**:
- Admin manually delivers
- Best for: Physical products, custom services

**Code Location**: Line 406-485

#### 8. Delete Product
Removes product from store

**Code Location**: Line 348-371

---

## 📋 Orders Management

**File**: `src/handlers/admin.py` - Lines 486-586

### Features:

#### 1. View All Orders
Shows:
- Order ID
- Customer name
- Total amount
- Status (pending/confirmed/completed)
- Payment status (unpaid/pending_review/paid)

**Code Location**: Line 486-500

#### 2. Order Details
Click on order to see:
- Customer info
- Items purchased
- Payment method
- Payment proof (if uploaded)
- Timestamps

**Code Location**: Line 501-537

#### 3. Change Order Status
Options:
- ⏳ Pending
- ✅ Confirmed
- 📦 Completed
- ❌ Cancelled

**Code Location**: Line 538-586

---

## 👥 Users Management

**File**: `src/handlers/admin.py` - Lines 587-662

### Features:

#### 1. View All Users
Shows:
- User ID
- Full name
- Username
- Join date
- Total spent
- Order count

**Code Location**: Line 587-601

#### 2. User Details
Click on user to see:
- 👤 Profile info
- 💰 Balance
- 📊 Total spent
- 📦 Orders count
- 🎁 Referrals
- 🎟️ Tickets

**Code Location**: Line 602-631

#### 3. Ban/Unban User
- Ban user from using bot
- Unban to restore access

**Code Location**: Line 632-662

---

## 💳 Payments & Proofs

**File**: `src/handlers/admin.py` - Lines 729-1061

### Payment Methods

#### 1. View Payment Methods
Shows all available payment methods

**Code Location**: Line 729-742

#### 2. Add Payment Method
**Flow**:
```
Click "➕ Add Payment"
  ↓
Enter payment method name (e.g., "Bank Transfer")
  ↓
Enter payment details (account number, etc.)
  ↓
Payment method added ✓
```

**Code Location**: Line 743-757

#### 3. Delete Payment Method
Remove payment option

**Code Location**: Line 758-776

### Payment Proofs Verification

#### 1. View Pending Proofs
Shows all payment proofs waiting for review

**Code Location**: Line 777-790

#### 2. Proof Details
Click to see:
- 📸 Payment screenshot
- 👤 Customer info
- 💰 Amount
- 📋 Order details
- 💳 Payment method used

**Code Location**: Line 791-841

#### 3. Approve Proof
**What Happens**:
1. ✅ Proof marked as approved
2. 💰 Order marked as paid
3. 🚀 Auto-delivery triggered (if enabled)
4. 📧 Customer notified

**Code Location**: Line 842-928

**Auto-Delivery Function**: Line 929-1016

#### 4. Reject Proof
**What Happens**:
1. ❌ Proof marked as rejected
2. 📧 Customer notified
3. Customer can upload new proof

**Code Location**: Line 1017-1031

#### 5. Post Proof to Channel
Forward proof to proofs channel for record

**Code Location**: Line 1032-1061

---

## 🎟️ Coupons System

**File**: `src/handlers/admin.py` - Lines 663-728

### Features:

#### 1. View All Coupons
Shows:
- Coupon code
- Discount percentage
- Max uses
- Used count
- Active status

**Code Location**: Line 663-676

#### 2. Add Coupon
**Flow**:
```
Click "➕ Add Coupon"
  ↓
Enter coupon code (e.g., "SAVE20")
  ↓
Enter discount percentage (e.g., 20)
  ↓
Enter max uses (0 = unlimited)
  ↓
Coupon created ✓
```

**Code Location**: Line 677-692

#### 3. Toggle Coupon (Enable/Disable)
Activate or deactivate coupon

**Code Location**: Line 693-709

#### 4. Delete Coupon
Remove coupon from system

**Code Location**: Line 710-728

---

## ⚙️ Settings

**File**: `src/handlers/admin.py` - Lines 1062-1188

### Configurable Settings:

#### 1. Store Settings
- 🏪 **Store Name**: Your store name
- 💱 **Currency**: Rs, $, €, etc.
- 💰 **Min Order**: Minimum order amount
- 🎁 **Referral Reward**: Points for referrals
- 🎰 **Daily Spin**: Enable/disable daily spin

**Code Location**: Line 1062-1102

#### 2. Edit Setting
**Flow**:
```
Click on setting to edit
  ↓
Enter new value
  ↓
Setting updated ✓
```

**Code Location**: Line 1103-1188

#### 3. Test Channel Connection
Test if log channel is working

**Code Location**: Line 1189-1209

---

## 📣 Broadcast

**File**: `src/handlers/admin.py` - Lines 1528-1626

### Features:

#### 1. Send Broadcast Message
**Flow**:
```
Click "📣 Broadcast"
  ↓
Enter message text (supports HTML)
  ↓
Confirm broadcast
  ↓
Message sent to all users ✓
```

**Features**:
- ✅ Rate limited (25 messages/second)
- ✅ Shows success/failed count
- ✅ Supports HTML formatting
- ✅ Safe from Telegram ban

**Code Location**: Line 1528-1626

**Rate Limiting**: Line 1582-1626

---

## 📊 Statistics

**File**: `src/handlers/admin.py` - Line 115-142

### Dashboard Stats:

Shows:
- 👥 **Total Users**: All registered users
- 📦 **Total Orders**: All orders
- 💰 **Total Revenue**: Sum of all paid orders
- 📊 **Pending Orders**: Orders awaiting payment
- 🎟️ **Active Coupons**: Enabled coupons
- 📦 **Products**: Total products
- 📂 **Categories**: Total categories

**Code Location**: Line 115-142

---

## 🎨 Image Management

**File**: `src/handlers/admin.py` - Lines 1210-1479

### Features:

#### 1. Welcome Image
Set image shown on /start

**Code Location**: Line 1210-1237

#### 2. Global Image Panel
Manage images for:
- 🏪 Shop
- 🛒 Cart
- 📦 Orders
- 💳 Wallet
- 🎫 Support
- 🎰 Daily Spin
- 👥 Referral

**Code Location**: Line 1238-1300

#### 3. Set Image for Section
Upload image for specific section

**Code Location**: Line 1301-1342

#### 4. Clear Image
Remove image from section

**Code Location**: Line 1343-1370

#### 5. Toggle Image (Show/Hide)
Enable or disable image for section

**Code Location**: Line 1371-1388

#### 6. Global Image Toggle
Enable/disable all images at once

**Code Location**: Line 1389-1408

---

## 📝 Text Management

**File**: `src/handlers/admin.py` - Lines 1409-1479

### Features:

#### 1. Set Custom Text
Customize text for:
- Welcome message
- Shop description
- Cart message
- Order confirmation
- etc.

**Code Location**: Line 1409-1450

#### 2. Clear Custom Text
Reset to default text

**Code Location**: Line 1451-1479

---

## 🔧 Bulk Operations

**File**: `src/handlers/admin.py` - Lines 1528-1564

### Features:

#### 1. Bulk Stock Update
Update stock for multiple products at once

**Code Location**: Line 1547-1564

---

## 💾 Database Tables Used

### Admin Panel Uses These Tables:

1. **categories** - Product categories
2. **products** - All products
3. **orders** - Customer orders
4. **users** - All users
5. **payment_methods** - Payment options
6. **payment_proofs** - Payment screenshots
7. **coupons** - Discount codes
8. **settings** - Bot configuration
9. **tickets** - Support tickets
10. **referrals** - Referral tracking

**Database File**: `src/database/database.py`

---

## 🎯 Quick Reference

### Most Used Functions:

```python
# Categories
await get_all_categories()
await add_category(name, emoji)
await update_category(cat_id, **kwargs)
await delete_category(cat_id)

# Products
await get_products_by_category(cat_id)
await add_product(cat_id, name, desc, price)
await update_product(prod_id, **kwargs)
await delete_product(prod_id)

# Orders
await get_all_orders(limit)
await get_order(order_id)
await update_order(order_id, **kwargs)

# Users
await get_all_users(limit)
await get_user(user_id)
await ban_user(user_id)
await unban_user(user_id)

# Payments
await get_all_payment_methods()
await add_payment_method(name, details)
await get_payment_proof(proof_id)
await update_proof(proof_id, **kwargs)

# Coupons
await get_all_coupons()
await add_coupon(code, discount, max_uses)
await toggle_coupon(coupon_id)

# Settings
await get_setting(key, default)
await update_setting(key, value)
```

---

## 🔐 Security Features

### Admin-Only Access:
```python
def _is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID
```

Every admin handler checks this first!

### Delete Confirmations:
- ✅ Category deletion requires confirmation
- ✅ Product deletion requires confirmation
- ✅ Prevents accidental deletions

### Input Validation:
- ✅ Price validation (no negative, max limit)
- ✅ Stock validation (no negative, integer only)
- ✅ Quantity validation (min 1, max 1000)

**Validators File**: `src/utils/validators.py`

---

## 📱 Admin Panel Flow Chart

```
/start (Admin)
    ↓
Admin Panel Button
    ↓
┌─────────────────────────────────────┐
│         ADMIN DASHBOARD             │
├─────────────────────────────────────┤
│ 📂 Categories → Add/Edit/Delete     │
│ 📦 Products → Add/Edit/Stock/Image  │
│ 📋 Orders → View/Status/Details     │
│ 👥 Users → View/Ban/Details         │
│ 💳 Payments → Methods/Proofs        │
│ 🎟️ Coupons → Add/Toggle/Delete     │
│ ⚙️ Settings → Configure Bot         │
│ 📣 Broadcast → Message All Users    │
│ 📊 Statistics → View Analytics      │
└─────────────────────────────────────┘
```

---

## 🎓 Tips for Admin

1. **Always set product images** - Better conversion
2. **Use auto-delivery** - Faster fulfillment
3. **Create coupons** - Boost sales
4. **Check proofs daily** - Happy customers
5. **Monitor statistics** - Track growth
6. **Backup database** - Safety first!

---

## 📞 Need Help?

Check logs for any issues:
```bash
podman logs -f nanostore-bot
```

---

**Last Updated**: February 25, 2026  
**Admin Panel Version**: 1.0 (Production Ready)
