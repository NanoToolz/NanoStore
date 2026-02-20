# Testing Guide - 2-Message UX Model

## Quick Start

```bash
# Activate virtual environment
source venv/bin/activate

# Run the bot
python bot.py
```

---

## Test Checklist

### 1. Basic Flow ✓
- [ ] Send `/start` to bot
- [ ] Verify 2 messages appear:
  - MESSAGE A: Detailed welcome with stats
  - MESSAGE B: Simple main menu with buttons
- [ ] Wait 60 seconds
- [ ] Verify MESSAGE A disappears
- [ ] Verify MESSAGE B stays

### 2. Navigation ✓
- [ ] Click "🛍️ Shop" → MESSAGE B updates (not deleted)
- [ ] Click "🏠 Main Menu" → Returns to main menu
- [ ] Click "🛒 Cart" → MESSAGE B updates
- [ ] Click "📦 My Orders" → MESSAGE B updates
- [ ] Click "💳 Wallet" → MESSAGE B updates
- [ ] Click "🎫 Support" → MESSAGE B updates
- [ ] Click "🎰 Daily Spin" → MESSAGE B updates
- [ ] Click "👥 Referral" → MESSAGE B updates

### 3. Welcome Message Content ✓
Verify MESSAGE A shows:
- [ ] Store name and greeting
- [ ] Full name, username, user ID
- [ ] Join date (format: "Jan 2026")
- [ ] VIP status (if spent > 50,000) or "Regular Member"
- [ ] Balance
- [ ] Total Spent
- [ ] Total Deposited
- [ ] Orders: Total, Completed, Pending (pending hidden if 0)
- [ ] Daily Spin status (Ready ✅ or Come back in Xh Xm ⏳)
- [ ] Referral count
- [ ] "Instant Auto-Delivery" message

### 4. Main Menu Layout ✓
Verify MESSAGE B has buttons in this order:
- [ ] Row 1: 🛍️ Shop (full width)
- [ ] Row 2: 🛒 Cart | 📦 My Orders
- [ ] Row 3: 💳 Wallet | 🎫 Support
- [ ] Row 4: 🎰 Daily Spin | 👥 Referral
- [ ] Row 5: ⚙️ Admin Panel (only if you're admin)

### 5. Removed Features ✓
Verify these are NOT in main menu:
- [ ] ❓ Help button (removed)
- [ ] 🔍 Search button (removed)

### 6. Referral System ✓
- [ ] Click "👥 Referral"
- [ ] Verify referral link shows: `https://t.me/YourBotUsername?start=ref_YOUR_USER_ID`
- [ ] Copy the link
- [ ] Open in another account (or ask friend)
- [ ] Send `/start ref_YOUR_USER_ID`
- [ ] Verify new user gets 500 points
- [ ] Verify you get 1,000 points
- [ ] Verify you get notification
- [ ] Check referral history

### 7. Daily Spin ✓
- [ ] Click "🎰 Daily Spin"
- [ ] If first time: Verify you can spin
- [ ] Verify points awarded (50-2,000)
- [ ] Verify rarity shown (Common/Rare/Epic/Legendary)
- [ ] Try spinning again
- [ ] Verify cooldown message shows
- [ ] Verify time remaining displayed

### 8. Admin Panel ✓
If you're admin:
- [ ] Verify "⚙️ Admin Panel" button visible
- [ ] Click it
- [ ] Verify all admin features work
- [ ] Navigate back to main menu

If you're NOT admin:
- [ ] Verify "⚙️ Admin Panel" button NOT visible

### 9. Edge Cases ✓
- [ ] User with no username → Shows "no username"
- [ ] User with 0 pending orders → Pending line hidden
- [ ] User with spent > 50,000 → Shows "⭐ VIP Member"
- [ ] User with spent ≤ 50,000 → Shows "Regular Member"
- [ ] Spin available → Shows "Ready to Spin! ✅"
- [ ] Spin not available → Shows "Come back in Xh Xm ⏳"

### 10. Existing Features ✓
Verify all existing features still work:
- [ ] Shop/Browse products
- [ ] Add to cart
- [ ] Checkout
- [ ] Payment proof upload
- [ ] Order tracking
- [ ] Wallet top-up
- [ ] Support tickets
- [ ] Admin panel (all features)

---

## Expected Behavior

### On /start:
```
[User sends: /start]
[Bot deletes /start command]

[MESSAGE A appears - detailed welcome]
🛍️ NanoStore
Hey John, Welcome Back! 👋

👤 John Doe  •  @johndoe  •  ID: 123456789
📅 Member since Feb 2026  •  Regular Member

💳 Balance: Rs 1,000
💸 Total Spent: Rs 5,000
💰 Total Deposited: Rs 10,000

📦 Orders: 5   ✅ Done: 3   ⏳ Pending: 2

🎰 Daily Spin — Ready to Spin! ✅
👥 Referrals — 2 friends joined 🎉

⚡ Instant Auto-Delivery on all products!

[MESSAGE B appears - main menu]
🏠 NanoStore — Main Menu

Welcome back, John! Choose an option below:

[Buttons: Shop, Cart, Orders, Wallet, Support, Spin, Referral]

[After 60 seconds: MESSAGE A disappears]
[MESSAGE B stays forever]
```

### On Button Click:
```
[User clicks "🛍️ Shop"]
[MESSAGE B updates to show shop]
[No new message sent]
[No message deleted]
```

### On Main Menu Button:
```
[User clicks "🏠 Main Menu" from any screen]
[MESSAGE B updates back to main menu]
[Same message, just edited]
```

---

## Troubleshooting

### MESSAGE A doesn't disappear after 60s
- Check logs for deletion errors
- Verify asyncio.create_task() is working
- Bot needs message deletion permissions

### MESSAGE B gets deleted
- Check if any handler is calling delete_message()
- All handlers should use safe_edit() only
- Never send new messages for navigation

### Referral not working
- Verify referrals table exists in database
- Check if user joined within last 10 seconds
- Verify points are being awarded
- Check referrer notification

### Spin status not showing correctly
- Verify last_spin column exists in users table
- Check get_spin_status() function
- Verify 24-hour calculation

### VIP status not showing
- Check if total_spent > 50,000
- Verify get_user_total_spent() returns correct value
- Check completed orders in database

---

## Database Verification

```sql
-- Check if new columns exist
PRAGMA table_info(users);
-- Should show: points, currency, last_spin, referrer_id, total_spent, total_deposited

-- Check if referrals table exists
SELECT name FROM sqlite_master WHERE type='table' AND name='referrals';

-- Check user stats
SELECT user_id, points, last_spin, total_spent, total_deposited FROM users LIMIT 5;

-- Check referrals
SELECT * FROM referrals LIMIT 5;

-- Check points history
SELECT * FROM points_history ORDER BY created_at DESC LIMIT 10;
```

---

## Success Criteria

✅ 2 messages on /start (welcome + menu)
✅ Welcome auto-deletes after 60s
✅ Menu never deletes
✅ All buttons edit the same message
✅ Main Menu button on every screen
✅ Clean navigation (no message spam)
✅ Referral system working
✅ Daily spin working
✅ All existing features intact

---

## Support

If you encounter issues:
1. Check bot logs for errors
2. Verify database migration completed
3. Test with fresh user account
4. Check all dependencies installed
5. Verify .env configuration correct

Enjoy the new clean UX! 🎉
