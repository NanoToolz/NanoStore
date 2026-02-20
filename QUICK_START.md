# Quick Start Guide - New Features

## 🚀 Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

New dependency added: `aiohttp` for currency API

### 2. Start the Bot
```bash
python bot.py
```

The bot will automatically:
- Create new database tables
- Add new columns to existing tables
- Initialize default settings

### 3. Test New Features

---

## 🎯 Feature Testing Guide

### Welcome Screen
1. Send `/start` to the bot
2. You should see:
   - Your full profile (name, username, ID)
   - Member since date
   - Balance, Total Spent, Total Deposited
   - Order statistics
   - Daily Spin status
   - Referral count

### Main Menu
New layout:
```
🛍️ Shop
🛒 Cart | 📦 My Orders
💳 Wallet | 🎫 Support
🎰 Daily Spin | 👥 Referral
⚙️ Admin Panel (admin only)
```

### Daily Spin
1. Click "🎰 Daily Spin"
2. First time: You'll win random points (50-2,000)
3. See rarity tier (Common/Rare/Epic/Legendary)
4. Try again: Shows cooldown timer
5. Wait 24 hours to spin again

### Referral System
1. Click "👥 Referral"
2. Copy your referral link
3. Share with friends
4. When they join:
   - They get 500 points
   - You get 1,000 points
   - You get a notification
5. Click "📊 Referral History" to see who joined

### Multi-Currency
1. Click "💳 Wallet"
2. Click "⚙️ Preferences"
3. Click "💱 Currency: PKR 🇵🇰"
4. Select your preferred currency
5. All prices now show in your currency

### Points System
- Earn points from:
  - Daily Spin (50-2,000 pts)
  - Referrals (1,000 pts per friend)
  - New user bonus (500 pts)
- Points are separate from wallet balance
- Can be used for up to 20% off orders (future feature)

---

## 🔧 Admin Testing

### Track User Spending
1. Go to Admin Panel → Orders
2. Select an order
3. Change status to "completed" or "delivered"
4. User's "Total Spent" will update automatically

### Track User Deposits
1. Go to Admin Panel → Top-Ups
2. Approve a pending top-up
3. User's "Total Deposited" will update automatically

### View User Stats
1. Users with Total Spent > 10,000 PKR get "⭐ VIP Member" status
2. Visible on their welcome screen

---

## 📊 Monitoring

### Check Points System
```sql
-- View points history
SELECT * FROM points_history ORDER BY created_at DESC LIMIT 10;

-- Check user points
SELECT user_id, full_name, points FROM users WHERE points > 0;
```

### Check Referrals
```sql
-- View referrals
SELECT * FROM referrals ORDER BY created_at DESC;

-- Top referrers
SELECT referrer_id, COUNT(*) as count 
FROM referrals 
GROUP BY referrer_id 
ORDER BY count DESC;
```

### Check Currency Rates
```sql
-- View cached rates
SELECT * FROM currency_rates;
```

---

## 🐛 Troubleshooting

### Issue: Currency API not working
**Solution:** Bot will use fallback rates from database. Default rates:
- USD: 280 PKR
- AED: 76 PKR
- SAR: 75 PKR
- GBP: 355 PKR

### Issue: Referral link not working
**Check:**
1. Bot username is correct
2. Link format: `https://t.me/YourBotUsername?start=ref_123456789`
3. User can't refer themselves

### Issue: Daily spin not resetting
**Check:**
1. Verify `last_spin` timestamp in database
2. Should reset after 24 hours
3. Check server timezone

### Issue: Points not showing
**Check:**
1. Database has `points` column
2. Run migration if needed
3. Check `points_history` table for transactions

---

## 📝 Configuration

### Currency API
- Uses CoinGecko free API (no key needed)
- Rates cached for 5 minutes
- Automatic fallback to database cache

### Points Conversion
- 1 point = Rs 0.28
- Based on: $1 = 1000 pts, $1 = Rs 280
- Adjustable in code if needed

### Spin Probabilities
- Common (60%): 50-200 pts
- Rare (25%): 201-500 pts
- Epic (12%): 501-1000 pts
- Legendary (3%): 1001-2000 pts

### VIP Threshold
- Default: 10,000 PKR total spent
- Adjustable in `src/handlers/start.py` line ~85

---

## 🎉 What's New Summary

✅ **Welcome Screen:** Comprehensive user stats with VIP status
✅ **Main Menu:** Cleaner layout with Daily Spin and Referral
✅ **Points System:** Earn points separate from wallet
✅ **Daily Spin:** Random rewards with rarity tiers
✅ **Referral System:** Unique links with automatic rewards
✅ **Multi-Currency:** 5 currencies with live rates
✅ **User Preferences:** Currency selection
✅ **Auto-Tracking:** Total spent and deposited

---

## 📚 Documentation

- `IMPLEMENTATION_SUMMARY.md` - Detailed feature documentation
- `DATABASE_MIGRATION.md` - Database changes and migration
- `README.md` - General bot documentation
- `docs/FEATURES.md` - Feature list
- `docs/STRUCTURE.md` - Project structure

---

## 🆘 Support

If you encounter issues:
1. Check bot logs for errors
2. Verify database migration completed
3. Test with a fresh user account
4. Check all dependencies installed
5. Verify .env configuration

---

## 🚀 Next Steps

After testing, you can:
1. Implement points usage in checkout
2. Move search inside shop section
3. Add birthday bonus system
4. Create leaderboards
5. Add more currencies
6. Customize spin probabilities
7. Adjust VIP threshold

Enjoy the new features! 🎉
