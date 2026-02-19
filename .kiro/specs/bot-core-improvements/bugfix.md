# Bugfix Requirements Document

## Introduction

This document addresses five critical bugs in the NanoStore Telegram e-commerce bot that affect user experience, admin functionality, and data integrity. The bugs span message management (auto-delete), UI feedback (typing indicators), admin operations (bulk stock updates and settings), and inventory management (stock race conditions).

The fixes will improve chat cleanliness, reduce unnecessary UI noise, enhance admin productivity, provide comprehensive bot configuration, and ensure data consistency in concurrent order scenarios.

## Bug Analysis

### Current Behavior (Defect)

#### 1. Auto-Delete Messages

1.1 WHEN auto_delete() is called on a message THEN the message is not deleted even when the auto_delete setting is configured with a positive value

1.2 WHEN the /start command is sent THEN auto_delete() is called but the command message remains in the chat

1.3 WHEN temporary prompt messages are sent (e.g., "Send product name") THEN these messages are not auto-deleted and clutter the chat

1.4 WHEN the auto_delete setting is retrieved from the database THEN it may return None or invalid values that break the deletion logic

#### 2. Typing Indicator Overuse

2.1 WHEN a callback query is answered (button press) THEN send_typing() is called even though the response is instant

2.2 WHEN the admin panel is opened THEN send_typing() is called unnecessarily for an instant UI update

2.3 WHEN the dashboard stats are displayed THEN send_typing() is called even though it's a simple database query with instant response

2.4 WHEN any admin handler processes a callback query THEN send_typing() is called regardless of whether there's actual processing delay

#### 3. Bulk Stock Update Missing

3.1 WHEN an admin needs to update stock for multiple products THEN there is no bulk update functionality available

3.2 WHEN admin_bulk_stock_handler is called THEN it prompts for input but the corresponding text processing handler is incomplete

3.3 WHEN an admin wants to set stock for 10+ products THEN they must manually navigate to each product individually, which is time-consuming

#### 4. Settings System Incomplete

4.1 WHEN the admin opens the settings panel THEN only 7 basic settings are available (bot_name, currency, welcome_image_id, min_order, daily_reward, maintenance, auto_delete)

4.2 WHEN an admin wants to configure payment instructions THEN this setting exists in the handler but is not displayed in the settings panel

4.3 WHEN an admin wants to configure maintenance_text THEN this setting exists but is not accessible through the settings UI

4.4 WHEN an admin wants to configure topup settings (topup_enabled, topup_min_amount, topup_max_amount, topup_bonus_percent) THEN these settings are not exposed in the admin panel

#### 5. Stock Management Race Conditions

5.1 WHEN two users simultaneously add the same product to cart THEN no stock validation occurs at cart addition time

5.2 WHEN stock is decremented during order confirmation THEN the decrement_stock function uses "stock = stock - ?" with a WHERE clause "stock > 0" which can result in negative stock if not properly locked

5.3 WHEN a product has stock = 5 and two users each try to order quantity = 5 THEN both orders may be confirmed, resulting in stock = -5

5.4 WHEN add_to_cart is called THEN there is no check to verify if sufficient stock is available before adding to cart

5.5 WHEN cart_inc_handler increases quantity THEN it checks stock limits but this check is not atomic with the actual order confirmation

### Expected Behavior (Correct)

#### 1. Auto-Delete Messages

2.1 WHEN auto_delete() is called on a message AND the auto_delete setting is greater than 0 THEN the message SHALL be deleted after the specified delay in seconds

2.2 WHEN the /start command is sent THEN the command message SHALL be auto-deleted based on the auto_delete setting

2.3 WHEN temporary prompt messages are sent to admin during multi-step flows THEN these messages SHALL be auto-deleted to keep chats clean

2.4 WHEN the auto_delete setting is retrieved THEN it SHALL default to "0" if not set and SHALL handle None values gracefully

2.5 WHEN auto_delete() creates an asyncio task THEN it SHALL handle RuntimeError exceptions when no event loop is running

#### 2. Typing Indicator Optimization

2.2 WHEN a callback query is answered with instant data THEN send_typing() SHALL NOT be called

2.3 WHEN there is actual processing time (database queries, API calls, file operations) exceeding 1 second THEN send_typing() SHALL be called

2.4 WHEN the admin panel displays cached or instant data THEN send_typing() SHALL NOT be called

2.5 WHEN processing payment proofs, broadcasts, or bulk operations THEN send_typing() SHALL be called due to longer processing time

#### 3. Bulk Stock Update Implementation

2.6 WHEN an admin selects "Bulk Stock Update" THEN they SHALL be prompted with format: "product_id|stock" (one per line)

2.7 WHEN the admin sends bulk stock data in correct format THEN all valid product stocks SHALL be updated atomically

2.8 WHEN bulk stock update encounters an invalid product_id THEN it SHALL skip that line and continue processing other lines

2.9 WHEN bulk stock update completes THEN it SHALL report success count and error count to the admin

2.10 WHEN bulk stock data includes stock = -1 THEN it SHALL set the product to unlimited stock

2.11 WHEN bulk stock data includes stock = 0 THEN it SHALL set the product to out of stock

#### 4. Settings System Enhancement

2.12 WHEN the admin opens settings panel THEN all configurable settings SHALL be displayed in organized categories

2.13 WHEN the admin wants to configure payment_instructions THEN this setting SHALL be accessible in the settings panel

2.14 WHEN the admin wants to configure maintenance_text THEN this setting SHALL be editable through the settings UI

2.15 WHEN the admin wants to configure topup settings THEN topup_enabled, topup_min_amount, topup_max_amount, and topup_bonus_percent SHALL be accessible

2.16 WHEN settings are displayed THEN they SHALL be grouped into categories: Store Settings, Order Settings, Wallet Settings, System Settings

2.17 WHEN a boolean setting (like topup_enabled) is edited THEN it SHALL provide a toggle interface rather than text input

#### 5. Stock Management Validation

2.18 WHEN add_to_cart is called THEN it SHALL verify that sufficient stock is available before adding to cart

2.19 WHEN stock is not sufficient for the requested quantity THEN add_to_cart SHALL return an error and NOT add the item

2.20 WHEN decrement_stock is called THEN it SHALL use atomic database operations to prevent race conditions

2.21 WHEN stock would go negative after decrement THEN the operation SHALL fail and the order SHALL be rejected

2.22 WHEN confirm_order_handler processes an order THEN it SHALL re-validate stock availability before decrementing

2.23 WHEN multiple concurrent orders attempt to purchase the same product THEN only orders with sufficient stock SHALL succeed

2.24 WHEN a product has unlimited stock (stock = -1) THEN no stock validation or decrement SHALL occur

### Unchanged Behavior (Regression Prevention)

#### 1. Auto-Delete Messages

3.1 WHEN auto_delete setting is 0 or not configured THEN messages SHALL CONTINUE TO remain in chat (no deletion)

3.2 WHEN auto_delete() is called with an explicit delay parameter THEN it SHALL CONTINUE TO use that delay instead of the database setting

3.3 WHEN a message deletion fails due to message age or permissions THEN the error SHALL CONTINUE TO be logged as a warning without crashing

#### 2. Typing Indicator

3.4 WHEN send_typing() is called on the /start command (text message handler) THEN it SHALL CONTINUE TO show typing indicator for user feedback

3.5 WHEN send_typing() fails due to permissions or chat issues THEN it SHALL CONTINUE TO log a warning without affecting the handler flow

#### 3. Bulk Operations

3.6 WHEN bulk product import (admin_bulk_handler) is used THEN it SHALL CONTINUE TO work as currently implemented

3.7 WHEN individual product stock updates are performed THEN they SHALL CONTINUE TO work through the existing admin_prod_stock_handler

#### 4. Settings System

3.8 WHEN existing settings are modified THEN their current behavior SHALL CONTINUE TO work unchanged

3.9 WHEN get_setting() is called with a default value THEN it SHALL CONTINUE TO return the default if the key doesn't exist

3.10 WHEN set_setting() is called THEN it SHALL CONTINUE TO use INSERT OR REPLACE to update settings

#### 5. Stock Management

3.11 WHEN a product has unlimited stock (stock = -1) THEN it SHALL CONTINUE TO allow unlimited purchases without decrement

3.12 WHEN cart quantity is increased through cart_inc_handler THEN it SHALL CONTINUE TO check stock limits before allowing the increase

3.13 WHEN an order is cancelled THEN stock SHALL CONTINUE TO NOT be restored (current behavior - manual admin adjustment required)

3.14 WHEN get_cart displays items THEN it SHALL CONTINUE TO show current stock status for each product

3.15 WHEN a product is out of stock (stock = 0) THEN it SHALL CONTINUE TO display "🔴 Out of Stock" in the catalog
