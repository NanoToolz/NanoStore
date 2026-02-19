# Bot Core Improvements Bugfix Design

## Overview

This design addresses five critical bugs in the NanoStore Telegram e-commerce bot that affect message management, UI feedback, admin operations, and data integrity. The bugs span multiple subsystems:

1. **Auto-Delete Messages** - Messages are not being deleted despite auto_delete setting being configured
2. **Typing Indicator Overuse** - Typing indicators shown unnecessarily for instant operations
3. **Bulk Stock Update Missing** - Incomplete implementation of bulk stock update functionality
4. **Settings System Incomplete** - Many settings exist in database but are not exposed in admin UI
5. **Stock Management Race Conditions** - Concurrent orders can result in negative stock due to lack of atomic validation

The fixes will improve chat cleanliness, reduce UI noise, enhance admin productivity, provide comprehensive bot configuration, and ensure data consistency in concurrent scenarios.

## Glossary

- **auto_delete()**: Function in `helpers.py` that schedules message deletion after a configurable delay
- **send_typing()**: Function in `helpers.py` that displays typing indicator to users
- **Bug_Condition (C)**: The condition that triggers each specific bug
- **Property (P)**: The desired correct behavior when the bug condition holds
- **Preservation**: Existing functionality that must remain unchanged by the fixes
- **admin_settings_handler**: Handler in `handlers/admin.py` that displays the settings panel
- **admin_bulk_stock_handler**: Handler in `handlers/admin.py` for bulk stock updates
- **decrement_stock()**: Function in `database.py` that reduces product stock during order confirmation
- **add_to_cart()**: Function in `database.py` that adds products to user cart
- **confirm_order_handler**: Handler in `handlers/orders.py` that processes order confirmation
- **Atomic Operation**: Database operation that completes entirely or not at all, preventing race conditions


## Bug Details

### Bug 1: Auto-Delete Messages

#### Fault Condition

The bug manifests when auto_delete() is called on a message AND the auto_delete setting is configured with a positive value. The auto_delete() function in helpers.py is correctly implemented, but messages are not being deleted because:
1. The function may not be called in all necessary locations
2. The database setting may return None or invalid values
3. RuntimeError exceptions when no event loop is running are not handled

**Formal Specification:**
```
FUNCTION isBugCondition_AutoDelete(input)
  INPUT: input of type (message, auto_delete_setting)
  OUTPUT: boolean
  
  RETURN input.message IS NOT NULL
         AND input.auto_delete_setting > 0
         AND auto_delete() is called
         AND message is NOT deleted after delay
END FUNCTION
```

#### Examples

- **Example 1**: User sends /start command → auto_delete() is called → auto_delete setting is "30" → Expected: message deleted after 30s → Actual: message remains in chat
- **Example 2**: Admin receives prompt "Send product name" during product creation → Expected: prompt auto-deleted → Actual: prompt remains, cluttering chat
- **Example 3**: auto_delete setting is None in database → Expected: default to 0 (disabled) → Actual: int(None) raises exception
- **Edge Case**: auto_delete() called when no event loop running → Expected: log warning and skip → Actual: RuntimeError crashes handler


### Bug 2: Typing Indicator Overuse

#### Fault Condition

The bug manifests when send_typing() is called for callback query handlers that return instant responses (button presses with no processing delay). The send_typing() function is being called indiscriminately in handlers, even when:
1. The response is instant (cached data, simple UI updates)
2. The operation is a callback query answer (button press) with no actual processing
3. Database queries are simple and fast (< 1 second)

**Formal Specification:**
```
FUNCTION isBugCondition_TypingOveruse(input)
  INPUT: input of type (handler_type, processing_time)
  OUTPUT: boolean
  
  RETURN input.handler_type == "callback_query"
         AND input.processing_time < 1.0
         AND send_typing() is called
END FUNCTION
```

#### Examples

- **Example 1**: Admin clicks "Dashboard" button → send_typing() called → dashboard stats displayed instantly → Expected: no typing indicator → Actual: typing indicator flashes unnecessarily
- **Example 2**: User clicks "Cart" button → send_typing() called → cart displayed instantly → Expected: no typing indicator → Actual: typing indicator shown
- **Example 3**: Admin clicks "Settings" button → send_typing() called → settings panel displayed instantly → Expected: no typing indicator → Actual: typing indicator shown
- **Edge Case**: Broadcast message handler processes 1000 users → Expected: typing indicator shown (long operation) → Actual: should continue showing typing


### Bug 3: Bulk Stock Update Missing

#### Fault Condition

The bug manifests when an admin needs to update stock for multiple products. The admin_bulk_stock_handler exists and prompts for input, but the corresponding text processing handler in admin_text_router is incomplete or missing. The handler should:
1. Parse input in format "product_id|stock" (one per line)
2. Validate each product_id exists
3. Update stock atomically for all valid products
4. Report success/error counts

**Formal Specification:**
```
FUNCTION isBugCondition_BulkStock(input)
  INPUT: input of type (admin_action, bulk_data)
  OUTPUT: boolean
  
  RETURN input.admin_action == "bulk_stock_update"
         AND input.bulk_data IS NOT NULL
         AND bulk_data contains valid format "product_id|stock"
         AND stock is NOT updated for products
END FUNCTION
```

#### Examples

- **Example 1**: Admin sends "1|50\n2|100\n3|-1" → Expected: products 1,2,3 stock updated, success message → Actual: no processing occurs
- **Example 2**: Admin sends "1|50\n999|100" (product 999 doesn't exist) → Expected: product 1 updated, product 999 skipped with error → Actual: no processing
- **Example 3**: Admin sends "5|-1" → Expected: product 5 set to unlimited stock → Actual: no processing
- **Edge Case**: Admin sends "10|0" → Expected: product 10 set to out of stock → Actual: no processing


### Bug 4: Settings System Incomplete

#### Fault Condition

The bug manifests when an admin opens the settings panel and only sees 7 basic settings, while many other settings exist in the database and handlers but are not exposed in the UI. The admin_settings_handler only displays:
- bot_name, currency, welcome_image_id, min_order, daily_reward, maintenance, auto_delete

But these settings exist and are not accessible:
- payment_instructions, maintenance_text, topup_enabled, topup_min_amount, topup_max_amount, topup_bonus_percent

**Formal Specification:**
```
FUNCTION isBugCondition_SettingsIncomplete(input)
  INPUT: input of type (setting_key, exists_in_db, exposed_in_ui)
  OUTPUT: boolean
  
  RETURN input.exists_in_db == TRUE
         AND input.exposed_in_ui == FALSE
         AND setting is used in handlers
END FUNCTION
```

#### Examples

- **Example 1**: Admin wants to configure payment_instructions → Opens settings panel → Expected: payment_instructions editable → Actual: not shown in UI
- **Example 2**: Admin wants to set maintenance_text → Opens settings panel → Expected: maintenance_text editable → Actual: not shown in UI
- **Example 3**: Admin wants to configure topup_enabled → Opens settings panel → Expected: topup_enabled toggle → Actual: not shown in UI
- **Edge Case**: Admin wants to set topup_bonus_percent to 5% → Expected: editable field → Actual: not accessible


### Bug 5: Stock Management Race Conditions

#### Fault Condition

The bug manifests when two users simultaneously attempt to purchase the same product. The stock validation and decrement operations are not atomic, leading to race conditions where:
1. add_to_cart() does not validate stock availability before adding to cart
2. cart_inc_handler checks stock but this check is not atomic with order confirmation
3. decrement_stock() uses "UPDATE products SET stock = stock - ? WHERE id = ? AND stock > 0" which can result in negative stock if two orders execute simultaneously
4. confirm_order_handler does not re-validate stock before decrementing

**Formal Specification:**
```
FUNCTION isBugCondition_StockRace(input)
  INPUT: input of type (product_id, stock, concurrent_orders)
  OUTPUT: boolean
  
  RETURN input.product_id EXISTS
         AND input.stock >= 0
         AND input.concurrent_orders.count >= 2
         AND SUM(concurrent_orders.quantities) > input.stock
         AND stock validation is NOT atomic with decrement
         AND result.stock < 0
END FUNCTION
```

#### Examples

- **Example 1**: Product has stock=5 → User A orders qty=5 → User B orders qty=5 → Both orders confirmed → Expected: one order fails → Actual: stock becomes -5
- **Example 2**: Product has stock=1 → User A adds to cart → User B adds to cart → Both checkout → Expected: second order fails → Actual: both succeed, stock becomes -1
- **Example 3**: User adds product to cart when stock=10 → Stock drops to 0 before checkout → User confirms order → Expected: order fails with stock error → Actual: order succeeds, stock becomes -1
- **Edge Case**: Product has stock=-1 (unlimited) → Multiple concurrent orders → Expected: all succeed, stock stays -1 → Actual: should continue working


## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**

**Bug 1 - Auto-Delete:**
- When auto_delete setting is 0 or not configured, messages must continue to remain in chat (no deletion)
- When auto_delete() is called with an explicit delay parameter, it must continue to use that delay instead of the database setting
- When a message deletion fails due to message age or permissions, the error must continue to be logged as a warning without crashing

**Bug 2 - Typing Indicator:**
- When send_typing() is called on the /start command (text message handler), it must continue to show typing indicator for user feedback
- When send_typing() fails due to permissions or chat issues, it must continue to log a warning without affecting the handler flow
- Long-running operations (broadcasts, payment proof processing, bulk operations) must continue to show typing indicators

**Bug 3 - Bulk Operations:**
- When bulk product import (admin_bulk_handler) is used, it must continue to work as currently implemented
- When individual product stock updates are performed, they must continue to work through the existing admin_prod_stock_handler

**Bug 4 - Settings System:**
- When existing settings are modified, their current behavior must continue to work unchanged
- When get_setting() is called with a default value, it must continue to return the default if the key doesn't exist
- When set_setting() is called, it must continue to use INSERT OR REPLACE to update settings

**Bug 5 - Stock Management:**
- When a product has unlimited stock (stock = -1), it must continue to allow unlimited purchases without decrement
- When cart quantity is increased through cart_inc_handler, it must continue to check stock limits before allowing the increase
- When an order is cancelled, stock must continue to NOT be restored (current behavior - manual admin adjustment required)
- When get_cart displays items, it must continue to show current stock status for each product
- When a product is out of stock (stock = 0), it must continue to display "🔴 Out of Stock" in the catalog

**Scope:**
All functionality not directly related to the five bugs must remain completely unchanged. This includes:
- All other handler behaviors
- Database schema (no structural changes)
- User-facing UI for non-affected features
- Payment processing flows
- Ticket system
- Wallet system
- Coupon system


## Hypothesized Root Cause

### Bug 1: Auto-Delete Messages

Based on the bug description and code analysis, the most likely issues are:

1. **Missing auto_delete() Calls**: The auto_delete() function exists and is correctly implemented in helpers.py, but it may not be called in all necessary locations where temporary messages are sent (admin prompts, user notifications, etc.)

2. **None Value Handling**: The get_setting("auto_delete", "0") may return None from the database, and int(None) will raise a TypeError, causing the function to fail silently or crash

3. **Event Loop Issues**: The asyncio.create_task() call may fail with RuntimeError when no event loop is running, which is caught but may prevent deletion in edge cases

4. **Default Setting Not Initialized**: The auto_delete setting may not be initialized in the database defaults during init_db(), causing it to return None

### Bug 2: Typing Indicator Overuse

Based on the code analysis, the root cause is:

1. **Indiscriminate Usage**: send_typing() is called at the start of almost every callback query handler (admin_handler, back_admin_handler, admin_dashboard_handler, etc.) without considering whether the operation is instant or requires processing time

2. **Callback Query Pattern**: Callback queries (button presses) typically have instant responses because they're just UI updates or simple database queries, but send_typing() is still called

3. **No Processing Time Check**: There's no logic to determine if an operation will take > 1 second before calling send_typing()

4. **Copy-Paste Pattern**: The pattern "await send_typing(query.message.chat_id, context.bot)" appears to have been copy-pasted across handlers without consideration for necessity


### Bug 3: Bulk Stock Update Missing

Based on the code analysis, the root cause is:

1. **Incomplete Handler**: The admin_bulk_stock_handler exists and sets the state to "adm_bulk_stock_data", but the corresponding processing logic in admin_text_router is missing or incomplete

2. **Missing Text Router Logic**: The admin_text_router function needs a case for "adm_bulk_stock_data" state that parses the input and updates stock

3. **No Validation Logic**: There's no code to validate the format "product_id|stock", check if products exist, or handle errors

4. **No Feedback Mechanism**: There's no code to report success/error counts back to the admin

### Bug 4: Settings System Incomplete

Based on the code analysis, the root cause is:

1. **Hardcoded Settings Display**: The admin_settings_handler only displays 7 specific settings (bot_name, currency, welcome_image_id, min_order, daily_reward, maintenance, auto_delete) and doesn't include other settings that exist in the database

2. **Missing Keyboard Entries**: The admin_settings_kb() keyboard (in keyboards.py) doesn't include buttons for payment_instructions, maintenance_text, topup_enabled, topup_min_amount, topup_max_amount, topup_bonus_percent

3. **Missing Handler Cases**: The admin_set_handler has labels and hints for some missing settings (payment_instructions, maintenance_text) but they're not accessible from the UI

4. **No Categorization**: Settings are displayed in a flat list rather than organized categories (Store Settings, Order Settings, Wallet Settings, System Settings)


### Bug 5: Stock Management Race Conditions

Based on the code analysis, the root cause is:

1. **No Stock Validation in add_to_cart()**: The add_to_cart() function in database.py does not check if sufficient stock is available before adding items to cart. It only checks if the item already exists in cart and increments quantity.

2. **Non-Atomic Stock Check**: The cart_inc_handler checks stock limits before incrementing cart quantity, but this check is separate from the actual order confirmation, creating a time-of-check-to-time-of-use (TOCTOU) race condition.

3. **Unsafe decrement_stock()**: The decrement_stock() function uses "UPDATE products SET stock = stock - ? WHERE id = ? AND stock > 0", which checks stock > 0 but doesn't verify stock >= quantity. Two concurrent updates can both pass the stock > 0 check and both decrement, resulting in negative stock.

4. **No Re-validation in confirm_order_handler**: The confirm_order_handler calls decrement_stock() for each item without re-validating that sufficient stock is still available. The stock could have been depleted between cart addition and order confirmation.

5. **No Database Locking**: SQLite supports transactions but the code doesn't use BEGIN IMMEDIATE or BEGIN EXCLUSIVE to lock rows during stock checks and decrements, allowing concurrent transactions to interfere.


## Correctness Properties

Property 1: Fault Condition - Auto-Delete Messages Work Correctly

_For any_ message where auto_delete() is called AND the auto_delete setting is greater than 0, the fixed auto_delete function SHALL delete the message after the specified delay in seconds, handling None values gracefully by defaulting to 0, and catching RuntimeError exceptions when no event loop is running.

**Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**

Property 2: Fault Condition - Typing Indicators Only for Long Operations

_For any_ callback query handler where the processing time is less than 1 second (instant data display, simple UI updates), the fixed handlers SHALL NOT call send_typing(), while handlers with actual processing time exceeding 1 second (broadcasts, payment proofs, bulk operations) SHALL continue to call send_typing().

**Validates: Requirements 2.2, 2.3, 2.4, 2.5**

Property 3: Fault Condition - Bulk Stock Update Processes Input

_For any_ bulk stock update input where the format is "product_id|stock" (one per line), the fixed admin_text_router SHALL parse the input, validate each product_id exists, update stock atomically for all valid products, skip invalid lines, and report success count and error count to the admin.

**Validates: Requirements 2.6, 2.7, 2.8, 2.9, 2.10, 2.11**

Property 4: Fault Condition - All Settings Exposed in UI

_For any_ setting that exists in the database and is used by handlers (payment_instructions, maintenance_text, topup_enabled, topup_min_amount, topup_max_amount, topup_bonus_percent), the fixed admin_settings_handler SHALL display these settings in organized categories (Store Settings, Order Settings, Wallet Settings, System Settings) with appropriate edit interfaces.

**Validates: Requirements 2.12, 2.13, 2.14, 2.15, 2.16, 2.17**

Property 5: Fault Condition - Stock Validation Prevents Negative Stock

_For any_ order confirmation where products have limited stock (stock >= 0), the fixed confirm_order_handler SHALL re-validate stock availability atomically before decrementing, and the fixed add_to_cart function SHALL verify sufficient stock is available before adding to cart, preventing negative stock in all concurrent scenarios.

**Validates: Requirements 2.18, 2.19, 2.20, 2.21, 2.22, 2.23, 2.24**

Property 6: Preservation - Existing Functionality Unchanged

_For any_ input that does not involve the five specific bugs (auto-delete with setting=0, typing indicators on text messages, individual stock updates, existing settings, unlimited stock products), the fixed code SHALL produce exactly the same behavior as the original code, preserving all existing functionality.

**Validates: Requirements 3.1-3.15**


## Fix Implementation

### Bug 1: Auto-Delete Messages

Assuming our root cause analysis is correct:

**File**: `helpers.py`

**Function**: `auto_delete()`

**Specific Changes**:
1. **Add None Handling**: Modify the get_setting call to ensure it never returns None
   - Change: `raw = await get_setting("auto_delete", "0")` 
   - To: `raw = await get_setting("auto_delete", "0") or "0"`
   - This ensures that if the database returns None, we default to "0"

2. **Improve Exception Handling**: The RuntimeError catch is already present, but ensure it logs appropriately

**File**: `database.py`

**Function**: `init_db()`

**Specific Changes**:
3. **Add Default Setting**: Add "auto_delete": "0" to the defaults dictionary in init_db()
   - This ensures the setting is always initialized in the database

**File**: `handlers/admin.py` (and other handlers as needed)

**Function**: Various admin prompt handlers

**Specific Changes**:
4. **Add auto_delete() Calls**: Identify all locations where temporary prompt messages are sent to admins and add auto_delete() calls
   - Example: After sending "Send product name" prompt, call `await auto_delete(msg)`
   - This requires reviewing admin_text_router and identifying all prompt messages

5. **Verify Existing Calls**: Ensure /start command and other user-facing messages already call auto_delete() (they should based on requirements)


### Bug 2: Typing Indicator Optimization

Assuming our root cause analysis is correct:

**File**: `handlers/admin.py`

**Function**: Multiple callback query handlers

**Specific Changes**:
1. **Remove Unnecessary send_typing() Calls**: Remove send_typing() from callback query handlers that return instant data
   - Remove from: `admin_handler`, `back_admin_handler`, `admin_dashboard_handler`, `admin_cats_handler`, `admin_settings_handler`, etc.
   - These handlers just display UI or fetch simple data from database (< 1s)

2. **Keep send_typing() for Long Operations**: Retain send_typing() in handlers that perform long operations
   - Keep in: `admin_broadcast_confirm_handler` (processes many users)
   - Keep in: `admin_proof_approve_handler` (delivers products, sends notifications)
   - Keep in: `admin_topup_approve_handler` (updates balance, sends notifications)
   - Keep in: Any handler that processes files, sends multiple messages, or performs bulk operations

**File**: `handlers/start.py`

**Function**: `start_handler`

**Specific Changes**:
3. **Preserve Text Message Typing**: Keep send_typing() in text message handlers like start_handler
   - This provides immediate feedback for text commands
   - Only remove from callback query handlers with instant responses

**Decision Rule**: 
- Callback query + instant response (< 1s) = NO send_typing()
- Callback query + long operation (> 1s) = YES send_typing()
- Text message command = YES send_typing() (for immediate feedback)


### Bug 3: Bulk Stock Update Implementation

Assuming our root cause analysis is correct:

**File**: `handlers/admin.py`

**Function**: `admin_text_router`

**Specific Changes**:
1. **Add Bulk Stock Processing Logic**: Add a case for "adm_bulk_stock_data" state in admin_text_router
   ```python
   elif state == "adm_bulk_stock_data":
       # Parse input: product_id|stock (one per line)
       lines = update.message.text.strip().split('\n')
       success_count = 0
       error_count = 0
       errors = []
       
       for line in lines:
           line = line.strip()
           if not line or '|' not in line:
               continue
           
           parts = line.split('|')
           if len(parts) != 2:
               errors.append(f"Invalid format: {line}")
               error_count += 1
               continue
           
           try:
               prod_id = int(parts[0])
               stock = int(parts[1])
               
               # Validate product exists
               prod = await get_product(prod_id)
               if not prod:
                   errors.append(f"Product {prod_id} not found")
                   error_count += 1
                   continue
               
               # Validate stock value
               if stock < -1:
                   errors.append(f"Invalid stock for product {prod_id}: {stock}")
                   error_count += 1
                   continue
               
               # Update stock
               await update_product(prod_id, stock=stock)
               success_count += 1
               
           except ValueError:
               errors.append(f"Invalid numbers: {line}")
               error_count += 1
       
       # Report results
       result_text = f"✅ Bulk Stock Update Complete\n\n"
       result_text += f"✅ Success: {success_count}\n"
       result_text += f"❌ Errors: {error_count}\n"
       if errors:
           result_text += f"\nErrors:\n" + "\n".join(errors[:10])
       
       await update.message.reply_text(result_text)
       await auto_delete(update.message)
       context.user_data.pop("state", None)
   ```

2. **Add Input Validation**: Validate format, product existence, and stock value range (-1 for unlimited, 0 for out of stock, positive for available)

3. **Add Error Reporting**: Collect errors and report them to admin with success/error counts

4. **Add Auto-Delete**: Call auto_delete() on the admin's input message and the response to keep chat clean


### Bug 4: Settings System Enhancement

Assuming our root cause analysis is correct:

**File**: `handlers/admin.py`

**Function**: `admin_settings_handler`

**Specific Changes**:
1. **Add Missing Settings to Display**: Fetch and display all missing settings
   ```python
   # Add these fetches:
   payment_inst = await get_setting("payment_instructions", "")
   maint_text = await get_setting("maintenance_text", "")
   topup_enabled = await get_setting("topup_enabled", "on")
   topup_min = await get_setting("topup_min_amount", "100")
   topup_max = await get_setting("topup_max_amount", "10000")
   topup_bonus = await get_setting("topup_bonus_percent", "0")
   ```

2. **Organize Settings by Category**: Group settings into categories in the display text
   ```python
   text = (
       f"⚙️ <b>Bot Settings</b>\n"
       f"{separator()}\n\n"
       f"🏪 <b>Store Settings</b>\n"
       f"  • Store Name: {bot_name}\n"
       f"  • Currency: {currency}\n"
       f"  • Welcome Image: {img_badge}\n\n"
       f"🛒 <b>Order Settings</b>\n"
       f"  • Min Order: {currency} {min_order}\n"
       f"  • Payment Instructions: {payment_inst[:20]}...\n\n"
       f"💰 <b>Wallet Settings</b>\n"
       f"  • Daily Reward: {currency} {daily_reward}\n"
       f"  • Top-up Enabled: {topup_enabled}\n"
       f"  • Top-up Min: {currency} {topup_min}\n"
       f"  • Top-up Max: {currency} {topup_max}\n"
       f"  • Top-up Bonus: {topup_bonus}%\n\n"
       f"🔧 <b>System Settings</b>\n"
       f"  • Maintenance: {maint_badge}\n"
       f"  • Maintenance Text: {maint_text[:20]}...\n"
       f"  • Auto-Delete: {autodel_badge}\n\n"
       "👇 Tap a setting to edit:"
   )
   ```

**File**: `keyboards.py`

**Function**: `admin_settings_kb()`

**Specific Changes**:
3. **Add Keyboard Buttons**: Add buttons for all missing settings
   - Add button for "payment_instructions"
   - Add button for "maintenance_text"
   - Add button for "topup_enabled" (toggle)
   - Add button for "topup_min_amount"
   - Add button for "topup_max_amount"
   - Add button for "topup_bonus_percent"

4. **Organize Keyboard by Category**: Group buttons by category for better UX

**File**: `handlers/admin.py`

**Function**: `admin_set_handler`

**Specific Changes**:
5. **Add Toggle Logic for topup_enabled**: Add special case for topup_enabled similar to maintenance
   ```python
   if key == "topup_enabled":
       current = await get_setting("topup_enabled", "on")
       new_val = "on" if current == "off" else "off"
       await set_setting("topup_enabled", new_val)
       badge = "✅ ON" if new_val == "on" else "❌ OFF"
       await query.answer(f"✅ Top-up: {badge}", show_alert=True)
       await admin_settings_handler(update, context)
       return
   ```

6. **Ensure Labels and Hints Exist**: The labels and hints for payment_instructions and maintenance_text already exist, just need to be accessible


### Bug 5: Stock Management Validation

Assuming our root cause analysis is correct:

**File**: `database.py`

**Function**: `add_to_cart`

**Specific Changes**:
1. **Add Stock Validation Before Adding to Cart**: Check if sufficient stock is available
   ```python
   async def add_to_cart(user_id: int, product_id: int, quantity: int = 1) -> int:
       db = await get_db()
       
       # Get product to check stock
       prod = await get_product(product_id)
       if not prod:
           raise ValueError("Product not found")
       
       # Check stock availability (skip for unlimited stock)
       if prod["stock"] != -1:
           cur = await db.execute(
               "SELECT id, quantity FROM cart WHERE user_id = ? AND product_id = ?",
               (user_id, product_id),
           )
           existing = await cur.fetchone()
           
           total_qty = quantity
           if existing:
               total_qty = existing["quantity"] + quantity
           
           if total_qty > prod["stock"]:
               raise ValueError(f"Insufficient stock. Available: {prod['stock']}")
       
       # Rest of existing logic...
   ```

**File**: `database.py`

**Function**: `decrement_stock`

**Specific Changes**:
2. **Make Stock Decrement Atomic and Safe**: Use a transaction with proper validation
   ```python
   async def decrement_stock(product_id: int, quantity: int) -> bool:
       db = await get_db()
       
       # Use a transaction for atomicity
       await db.execute("BEGIN IMMEDIATE")
       
       try:
           # Get current stock
           cur = await db.execute(
               "SELECT stock FROM products WHERE id = ?",
               (product_id,)
           )
           row = await cur.fetchone()
           
           if not row:
               await db.rollback()
               return False
           
           current_stock = row["stock"]
           
           # Skip decrement for unlimited stock
           if current_stock == -1:
               await db.commit()
               return True
           
           # Check if sufficient stock available
           if current_stock < quantity:
               await db.rollback()
               return False
           
           # Decrement stock
           await db.execute(
               "UPDATE products SET stock = stock - ? WHERE id = ?",
               (quantity, product_id)
           )
           
           await db.commit()
           return True
           
       except Exception:
           await db.rollback()
           raise
   ```

3. **Return Success/Failure**: Change return type to bool to indicate success


**File**: `handlers/orders.py`

**Function**: `confirm_order_handler`

**Specific Changes**:
4. **Re-validate Stock Before Decrement**: Check stock availability and handle failures
   ```python
   # Decrement stock with validation
   items = json.loads(order["items_json"])
   stock_errors = []
   
   for item in items:
       success = await decrement_stock(item["product_id"], item["quantity"])
       if not success:
           prod = await get_product(item["product_id"])
           stock_errors.append(f"{prod['name']} (insufficient stock)")
   
   if stock_errors:
       # Rollback: restore balance and coupon if they were used
       if balance_used > 0:
           await update_user_balance(user_id, balance_used)
       
       # Note: Coupon usage cannot be easily rolled back, consider this in design
       
       error_text = (
           f"❌ <b>Order Failed</b>\n"
           f"{separator()}\n\n"
           f"The following items are out of stock:\n"
           + "\n".join(f"• {err}" for err in stock_errors) +
           f"\n\nYour balance has been restored.\n"
           "Please update your cart and try again."
       )
       await safe_edit(query, error_text, reply_markup=back_kb("cart"))
       return
   ```

5. **Handle Stock Validation Failures**: If any item fails stock validation, rollback balance changes and notify user

**File**: `handlers/catalog.py`

**Function**: `add_to_cart_handler`

**Specific Changes**:
6. **Handle Stock Validation Errors**: Catch ValueError from add_to_cart and display error to user
   ```python
   try:
       await add_to_cart(user_id, prod_id, quantity=1)
       await query.answer("✅ Added to cart!", show_alert=True)
   except ValueError as e:
       await query.answer(f"❌ {str(e)}", show_alert=True)
       return
   ```

**Database Schema Changes**: None required - using existing schema with improved logic


## Testing Strategy

### Validation Approach

The testing strategy follows a two-phase approach: first, surface counterexamples that demonstrate each bug on unfixed code, then verify the fixes work correctly and preserve existing behavior. Each bug will be tested independently with its own exploratory, fix checking, and preservation checking phases.

### Exploratory Fault Condition Checking

**Goal**: Surface counterexamples that demonstrate each bug BEFORE implementing the fix. Confirm or refute the root cause analysis. If we refute, we will need to re-hypothesize.

#### Bug 1: Auto-Delete Messages

**Test Plan**: Write tests that call auto_delete() with various settings and verify messages are deleted. Run these tests on the UNFIXED code to observe failures.

**Test Cases**:
1. **Auto-Delete with Setting=30**: Set auto_delete to "30", send message, call auto_delete(), wait 31s, verify message deleted (will fail on unfixed code)
2. **Auto-Delete with None Setting**: Database returns None for auto_delete, call auto_delete(), verify no crash and message not deleted (may fail on unfixed code)
3. **Auto-Delete on /start**: Send /start command, verify auto_delete() is called, verify message deleted after delay (will fail if not called)
4. **Auto-Delete with No Event Loop**: Call auto_delete() when no event loop running, verify RuntimeError caught and logged (may fail on unfixed code)

**Expected Counterexamples**:
- Messages not deleted even when auto_delete setting is positive
- TypeError when database returns None
- RuntimeError crashes when no event loop

#### Bug 2: Typing Indicator Overuse

**Test Plan**: Monitor send_typing() calls in callback query handlers and measure response times. Run on UNFIXED code to observe unnecessary typing indicators.

**Test Cases**:
1. **Dashboard Button**: Click admin dashboard button, verify send_typing() is called, measure response time < 1s (will show unnecessary typing on unfixed code)
2. **Settings Button**: Click settings button, verify send_typing() is called, measure response time < 1s (will show unnecessary typing on unfixed code)
3. **Cart Button**: Click cart button, verify send_typing() is called, measure response time < 1s (will show unnecessary typing on unfixed code)
4. **Broadcast Confirm**: Click broadcast confirm, verify send_typing() is called, measure response time > 1s (should keep typing indicator)

**Expected Counterexamples**:
- send_typing() called for instant operations (< 1s response time)
- Typing indicator flashes unnecessarily on button presses


#### Bug 3: Bulk Stock Update Missing

**Test Plan**: Attempt to use bulk stock update feature and verify it processes input. Run on UNFIXED code to observe missing functionality.

**Test Cases**:
1. **Valid Bulk Input**: Send "1|50\n2|100\n3|-1", verify stock updated for products 1,2,3 (will fail on unfixed code - no processing)
2. **Invalid Product ID**: Send "1|50\n999|100", verify product 1 updated, product 999 skipped with error (will fail on unfixed code)
3. **Unlimited Stock**: Send "5|-1", verify product 5 set to unlimited (will fail on unfixed code)
4. **Out of Stock**: Send "10|0", verify product 10 set to out of stock (will fail on unfixed code)

**Expected Counterexamples**:
- No processing occurs when bulk stock data is sent
- State "adm_bulk_stock_data" not handled in admin_text_router
- No feedback to admin

#### Bug 4: Settings System Incomplete

**Test Plan**: Open settings panel and verify which settings are displayed. Run on UNFIXED code to observe missing settings.

**Test Cases**:
1. **Payment Instructions Missing**: Open settings, verify payment_instructions not displayed (will fail on unfixed code)
2. **Maintenance Text Missing**: Open settings, verify maintenance_text not displayed (will fail on unfixed code)
3. **Topup Settings Missing**: Open settings, verify topup_enabled, topup_min_amount, topup_max_amount, topup_bonus_percent not displayed (will fail on unfixed code)
4. **Only 7 Settings Shown**: Count settings displayed, verify only 7 shown (will confirm bug on unfixed code)

**Expected Counterexamples**:
- Only 7 settings displayed in UI
- Settings exist in database and handlers but not accessible
- No categorization of settings

#### Bug 5: Stock Management Race Conditions

**Test Plan**: Simulate concurrent orders for the same product and verify stock behavior. Run on UNFIXED code to observe race conditions.

**Test Cases**:
1. **Concurrent Orders Exceed Stock**: Product has stock=5, simulate 2 concurrent orders of qty=5 each, verify one fails (will fail on unfixed code - both succeed, stock becomes -5)
2. **Add to Cart Without Stock Check**: Product has stock=0, attempt to add to cart, verify error (will fail on unfixed code - allows adding)
3. **Stock Changes Between Cart and Checkout**: Add product to cart when stock=10, reduce stock to 0, attempt checkout, verify order fails (will fail on unfixed code - order succeeds)
4. **Unlimited Stock Concurrent Orders**: Product has stock=-1, simulate 10 concurrent orders, verify all succeed and stock stays -1 (should work on unfixed code)

**Expected Counterexamples**:
- Negative stock after concurrent orders
- No stock validation when adding to cart
- No re-validation during order confirmation
- Race conditions in decrement_stock()


### Fix Checking

**Goal**: Verify that for all inputs where each bug condition holds, the fixed functions produce the expected behavior.

#### Bug 1: Auto-Delete Messages

**Pseudocode:**
```
FOR ALL input WHERE isBugCondition_AutoDelete(input) DO
  result := auto_delete_fixed(input.message, input.setting)
  ASSERT message is deleted after delay
  ASSERT no exceptions raised
  ASSERT None values handled gracefully
END FOR
```

**Test Cases**:
- Auto-delete with setting=30 → message deleted after 30s
- Auto-delete with setting=0 → message not deleted
- Auto-delete with None setting → defaults to 0, message not deleted
- Auto-delete with no event loop → RuntimeError caught, logged, no crash

#### Bug 2: Typing Indicator Optimization

**Pseudocode:**
```
FOR ALL handler WHERE handler.type == "callback_query" AND handler.response_time < 1.0 DO
  result := handler_fixed(input)
  ASSERT send_typing() NOT called
END FOR

FOR ALL handler WHERE handler.type == "callback_query" AND handler.response_time > 1.0 DO
  result := handler_fixed(input)
  ASSERT send_typing() IS called
END FOR
```

**Test Cases**:
- Dashboard button (< 1s) → send_typing() not called
- Settings button (< 1s) → send_typing() not called
- Broadcast confirm (> 1s) → send_typing() called
- /start command (text message) → send_typing() called

#### Bug 3: Bulk Stock Update

**Pseudocode:**
```
FOR ALL input WHERE isBugCondition_BulkStock(input) DO
  result := admin_text_router_fixed(input)
  ASSERT valid products updated
  ASSERT invalid products skipped
  ASSERT success/error counts reported
END FOR
```

**Test Cases**:
- Valid input "1|50\n2|100" → both products updated, success=2, errors=0
- Mixed input "1|50\n999|100" → product 1 updated, 999 skipped, success=1, errors=1
- Unlimited stock "5|-1" → product 5 set to unlimited
- Out of stock "10|0" → product 10 set to 0


#### Bug 4: Settings System

**Pseudocode:**
```
FOR ALL setting WHERE setting.exists_in_db AND setting.used_in_handlers DO
  result := admin_settings_handler_fixed()
  ASSERT setting displayed in UI
  ASSERT setting editable
  ASSERT setting categorized correctly
END FOR
```

**Test Cases**:
- Open settings → payment_instructions displayed and editable
- Open settings → maintenance_text displayed and editable
- Open settings → topup_enabled displayed with toggle
- Open settings → topup_min_amount, topup_max_amount, topup_bonus_percent displayed and editable
- Settings organized in categories: Store, Order, Wallet, System

#### Bug 5: Stock Management

**Pseudocode:**
```
FOR ALL order WHERE order.products.stock >= 0 AND order.concurrent DO
  result := confirm_order_handler_fixed(order)
  ASSERT stock never negative
  ASSERT insufficient stock orders fail
  ASSERT successful orders decrement correctly
END FOR

FOR ALL cart_add WHERE product.stock >= 0 DO
  result := add_to_cart_fixed(cart_add)
  ASSERT stock validated before adding
  ASSERT insufficient stock raises error
END FOR
```

**Test Cases**:
- Concurrent orders (stock=5, 2 orders of qty=5) → one succeeds, one fails, stock=0
- Add to cart (stock=0) → raises ValueError, not added
- Order confirmation (stock changed to 0) → order fails, balance restored
- Unlimited stock (stock=-1) → all operations succeed, stock stays -1


### Preservation Checking

**Goal**: Verify that for all inputs where the bug conditions do NOT hold, the fixed functions produce the same result as the original functions.

**Pseudocode:**
```
FOR ALL input WHERE NOT (isBugCondition_AutoDelete(input) OR 
                         isBugCondition_TypingOveruse(input) OR 
                         isBugCondition_BulkStock(input) OR 
                         isBugCondition_SettingsIncomplete(input) OR 
                         isBugCondition_StockRace(input)) DO
  ASSERT original_behavior(input) = fixed_behavior(input)
END FOR
```

**Testing Approach**: Property-based testing is recommended for preservation checking because:
- It generates many test cases automatically across the input domain
- It catches edge cases that manual unit tests might miss
- It provides strong guarantees that behavior is unchanged for all non-buggy inputs

**Test Plan**: Observe behavior on UNFIXED code first for non-affected features, then write property-based tests capturing that behavior.

**Test Cases**:

1. **Auto-Delete Preservation**: 
   - Observe that messages with auto_delete=0 remain in chat on unfixed code
   - Write test to verify this continues after fix
   - Observe that explicit delay parameter works on unfixed code
   - Write test to verify this continues after fix

2. **Typing Indicator Preservation**:
   - Observe that /start command shows typing on unfixed code
   - Write test to verify this continues after fix
   - Observe that long operations show typing on unfixed code
   - Write test to verify this continues after fix

3. **Bulk Operations Preservation**:
   - Observe that bulk product import works on unfixed code
   - Write test to verify this continues after fix
   - Observe that individual stock updates work on unfixed code
   - Write test to verify this continues after fix

4. **Settings Preservation**:
   - Observe that existing 7 settings work correctly on unfixed code
   - Write test to verify these continue working after fix
   - Observe that get_setting() with defaults works on unfixed code
   - Write test to verify this continues after fix

5. **Stock Management Preservation**:
   - Observe that unlimited stock (stock=-1) allows unlimited purchases on unfixed code
   - Write test to verify this continues after fix
   - Observe that cart display shows stock status on unfixed code
   - Write test to verify this continues after fix
   - Observe that out of stock products display correctly on unfixed code
   - Write test to verify this continues after fix


### Unit Tests

**Bug 1: Auto-Delete Messages**
- Test auto_delete() with setting=0 (disabled)
- Test auto_delete() with setting=30 (enabled)
- Test auto_delete() with None setting (defaults to 0)
- Test auto_delete() with explicit delay parameter
- Test auto_delete() with RuntimeError (no event loop)
- Test that /start command calls auto_delete()

**Bug 2: Typing Indicator Optimization**
- Test that callback query handlers with instant responses don't call send_typing()
- Test that callback query handlers with long operations call send_typing()
- Test that text message handlers call send_typing()
- Test that send_typing() failures are logged without crashing

**Bug 3: Bulk Stock Update**
- Test bulk stock update with valid input (all products exist)
- Test bulk stock update with invalid product IDs (some don't exist)
- Test bulk stock update with invalid format (missing pipe, invalid numbers)
- Test bulk stock update with unlimited stock (-1)
- Test bulk stock update with out of stock (0)
- Test bulk stock update with mixed valid/invalid lines

**Bug 4: Settings System**
- Test that all settings are displayed in admin panel
- Test that settings are organized by category
- Test that payment_instructions is editable
- Test that maintenance_text is editable
- Test that topup_enabled toggles correctly
- Test that topup amount settings are editable
- Test that existing settings continue to work

**Bug 5: Stock Management**
- Test add_to_cart() validates stock before adding
- Test add_to_cart() raises error when insufficient stock
- Test add_to_cart() allows unlimited stock (-1)
- Test decrement_stock() is atomic (uses transaction)
- Test decrement_stock() validates stock >= quantity
- Test decrement_stock() returns False when insufficient stock
- Test confirm_order_handler re-validates stock
- Test confirm_order_handler handles stock validation failures
- Test concurrent orders don't result in negative stock


### Property-Based Tests

**Bug 1: Auto-Delete Messages**
- Generate random auto_delete settings (0 to 300 seconds)
- Generate random messages
- Verify that messages are deleted when setting > 0
- Verify that messages remain when setting = 0
- Verify that None values are handled gracefully

**Bug 2: Typing Indicator Optimization**
- Generate random callback query handlers
- Measure response times
- Verify send_typing() called only when response_time > 1s
- Verify send_typing() not called when response_time < 1s

**Bug 3: Bulk Stock Update**
- Generate random bulk stock input (valid and invalid lines)
- Verify that all valid products are updated
- Verify that invalid products are skipped
- Verify that success/error counts are accurate
- Verify that stock values are correctly applied (-1, 0, positive)

**Bug 4: Settings System**
- Generate random setting values
- Verify that all settings can be read and written
- Verify that settings are displayed in correct categories
- Verify that toggle settings work correctly
- Verify that text settings accept any valid input

**Bug 5: Stock Management**
- Generate random product stocks (0 to 1000, and -1 for unlimited)
- Generate random order quantities
- Simulate concurrent orders
- Verify that stock never goes negative (except for unlimited)
- Verify that orders fail when insufficient stock
- Verify that successful orders decrement stock correctly
- Verify that unlimited stock (-1) is never decremented


### Integration Tests

**Bug 1: Auto-Delete Messages**
- Test full /start command flow with auto-delete enabled
- Test admin product creation flow with auto-delete on prompts
- Test that auto-delete works across different message types (text, photos, etc.)
- Test that auto-delete respects user vs admin settings

**Bug 2: Typing Indicator Optimization**
- Test full admin panel navigation (dashboard → categories → products)
- Test user shopping flow (catalog → product → cart → checkout)
- Test that typing indicators appear only for long operations
- Test that UI remains responsive without unnecessary typing indicators

**Bug 3: Bulk Stock Update**
- Test full bulk stock update flow from admin panel
- Test bulk update with 50+ products
- Test bulk update followed by individual product view
- Test that stock changes are immediately reflected in catalog

**Bug 4: Settings System**
- Test full settings configuration flow for all settings
- Test that settings changes are immediately applied
- Test that settings persist across bot restarts
- Test that settings affect bot behavior correctly (e.g., topup_enabled disables topup feature)

**Bug 5: Stock Management**
- Test full order flow with stock validation (browse → add to cart → checkout → confirm)
- Test concurrent user scenarios (2+ users ordering same product)
- Test stock depletion scenarios (product goes from in-stock to out-of-stock)
- Test that cart displays accurate stock information
- Test that orders fail gracefully when stock is insufficient
- Test that unlimited stock products work correctly in all scenarios
- Test that stock changes during checkout are handled correctly
