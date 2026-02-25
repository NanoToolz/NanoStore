# Database Migration Guide

## Overview
The new features require database schema changes. The bot will automatically create new tables and columns on first run, but existing users will have default values.

---

## Automatic Migration

When you run the bot for the first time after this update:

1. **New Tables Created:**
   - `points_history` - Points transaction log
   - `referrals` - Referral relationships
   - `currency_rates` - Exchange rate cache

2. **New Columns Added to Users Table:**
   - `points` (default: 0)
   - `currency` (default: 'PKR')
   - `last_spin` (default: NULL)
   - `referrer_id` (default: NULL)
   - `total_spent` (default: 0.0)
   - `total_deposited` (default: 0.0)

---

## Manual Migration (If Needed)

If automatic migration fails, run these SQL commands manually:

```sql
-- Add new columns to users table
ALTER TABLE users ADD COLUMN points INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN currency TEXT DEFAULT 'PKR';
ALTER TABLE users ADD COLUMN last_spin TEXT DEFAULT NULL;
ALTER TABLE users ADD COLUMN referrer_id INTEGER DEFAULT NULL;
ALTER TABLE users ADD COLUMN total_spent REAL DEFAULT 0.0;
ALTER TABLE users ADD COLUMN total_deposited REAL DEFAULT 0.0;

-- Create points_history table
CREATE TABLE IF NOT EXISTS points_history (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    amount      INTEGER NOT NULL,
    reason      TEXT NOT NULL,
    created_at  TEXT DEFAULT (datetime('now'))
);

-- Create referrals table
CREATE TABLE IF NOT EXISTS referrals (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    referrer_id     INTEGER NOT NULL,
    referred_id     INTEGER NOT NULL,
    created_at      TEXT DEFAULT (datetime('now')),
    UNIQUE(referred_id)
);

-- Create currency_rates table
CREATE TABLE IF NOT EXISTS currency_rates (
    currency    TEXT PRIMARY KEY,
    rate_vs_pkr REAL NOT NULL,
    updated_at  TEXT DEFAULT (datetime('now'))
);
```

---

## Backfilling Data (Optional)

### Calculate Total Spent
If you want to backfill `total_spent` for existing users based on completed orders:

```sql
UPDATE users
SET total_spent = (
    SELECT COALESCE(SUM(total), 0)
    FROM orders
    WHERE orders.user_id = users.user_id
    AND orders.status IN ('completed', 'delivered')
);
```

### Calculate Total Deposited
If you want to backfill `total_deposited` for existing users based on approved topups:

```sql
UPDATE users
SET total_deposited = (
    SELECT COALESCE(SUM(amount), 0)
    FROM wallet_topups
    WHERE wallet_topups.user_id = users.user_id
    AND wallet_topups.status = 'approved'
);
```

---

## Verification

After migration, verify the changes:

```sql
-- Check users table structure
PRAGMA table_info(users);

-- Check new tables exist
SELECT name FROM sqlite_master WHERE type='table' AND name IN ('points_history', 'referrals', 'currency_rates');

-- Check user data
SELECT user_id, points, currency, total_spent, total_deposited FROM users LIMIT 5;
```

---

## Rollback (If Needed)

If you need to rollback the changes:

```sql
-- Remove new columns from users table
-- Note: SQLite doesn't support DROP COLUMN directly
-- You'll need to recreate the table without these columns

-- Drop new tables
DROP TABLE IF EXISTS points_history;
DROP TABLE IF EXISTS referrals;
DROP TABLE IF EXISTS currency_rates;
```

---

## Notes

1. **Backup First:** Always backup your database before migration
2. **Automatic:** The bot handles migration automatically via `init_db()`
3. **Safe:** New columns have default values, won't break existing data
4. **Idempotent:** Can run multiple times safely (uses IF NOT EXISTS)
5. **No Downtime:** Migration happens on bot startup

---

## Testing Migration

1. Backup current database:
   ```bash
   cp data/nanostore.db data/nanostore.db.backup
   ```

2. Start the bot:
   ```bash
   python bot.py
   ```

3. Check logs for migration messages:
   ```
   Database initialized with all tables.
   ```

4. Test new features:
   - /start (should show new welcome screen)
   - Daily Spin button
   - Referral button
   - User Preferences

5. If issues occur, restore backup:
   ```bash
   cp data/nanostore.db.backup data/nanostore.db
   ```

---

## Database Location

Default: `data/nanostore.db`

Can be changed in `.env`:
```
DB_PATH=data/nanostore.db
```
