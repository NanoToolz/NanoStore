# Design Document: Admin Image Settings Enhancement

## Overview

This design addresses three critical issues in the admin image settings functionality:

1. **Auto-deletion of admin sent images**: Currently, when admins upload images to configure bot sections, their original image messages remain in the chat, creating clutter.

2. **Auto-deletion of confirmation messages**: Confirmation messages sent after successful image uploads persist indefinitely, adding to chat clutter.

3. **Section-specific image configuration**: The system currently only supports a single `welcome_image_id` that appears across all sections. This enhancement introduces dedicated image settings for seven distinct bot sections: Welcome, Shop, Cart, Orders, Wallet, Support, and Admin Panel.

The solution leverages the existing `auto_delete()` helper function and extends the database schema to support multiple section-specific image fields. The design maintains backward compatibility with existing welcome image configurations.

## Architecture

### System Components

The enhancement integrates with the existing NanoStore bot architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                     Telegram Bot Layer                       │
│  (bot.py - Message routing & handler registration)          │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ├──► Admin Handlers (handlers/admin.py)
                 │    ├─ admin_image_settings_handler()
                 │    ├─ admin_section_image_handler()
                 │    └─ admin_photo_router() [MODIFIED]
                 │
                 ├──► Message Cleanup Service
                 │    └─ auto_delete() helper (helpers.py)
                 │
                 └──► Database Layer (database.py)
                      ├─ Settings table [SCHEMA EXTENDED]
                      └─ get_setting() / set_setting()
```

### Data Flow

**Image Upload Flow:**
```
1. Admin clicks section button in Image Settings Panel
   ↓
2. State is set with section identifier (e.g., "adm_section_img:shop")
   ↓
3. Admin sends photo
   ↓
4. admin_photo_router() reads state, stores image to correct field
   ↓
5. Confirmation message sent and scheduled for auto-deletion
   ↓
6. Admin's image message scheduled for auto-deletion
   ↓
7. State cleared, panel updated
```

**Image Display Flow:**
```
1. User navigates to section (e.g., Shop)
   ↓
2. Handler retrieves section-specific image_id
   ↓
3. If section image exists → display it
   ↓
4. If not, check fallback (shop falls back to welcome)
   ↓
5. If no image → display text-only content
```

## Components and Interfaces

### 1. Database Schema Extensions

**Current Schema:**
```sql
CREATE TABLE IF NOT EXISTS settings (
    key     TEXT PRIMARY KEY,
    value   TEXT DEFAULT ''
);
```

**New Settings Keys:**
- `welcome_image_id` (existing - maintained for backward compatibility)
- `shop_image_id` (new)
- `cart_image_id` (new)
- `orders_image_id` (new)
- `wallet_image_id` (new)
- `support_image_id` (new)
- `admin_panel_image_id` (new)

**Default Values:**
All new image fields default to empty string `""` to indicate "not set".

**Migration Strategy:**
No migration required. The `init_db()` function will be updated to include default entries for new keys using `INSERT OR IGNORE`, ensuring existing data is preserved.

### 2. Admin Handlers Module (handlers/admin.py)

#### New Handler: `admin_image_settings_handler()`

**Purpose:** Display the image settings management panel

**Signature:**
```python
async def admin_image_settings_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None
```

**Behavior:**
- Queries database for all section image settings
- Displays categorized list of sections with status indicators (✅ Set / ❌ Not Set)
- Provides navigation buttons for each section
- Shows back button to return to main admin settings

**UI Layout:**
```
🖼️ Image Settings
━━━━━━━━━━━━━━━━━━━

📱 User Sections:
  🏠 Welcome: ✅ Set
  🛍️ Shop: ❌ Not Set
  🛒 Cart: ❌ Not Set
  📦 Orders: ✅ Set
  💰 Wallet: ❌ Not Set
  💬 Support: ❌ Not Set

⚙️ Admin Sections:
  🔧 Admin Panel: ❌ Not Set

[◀️ Back to Settings]
```

#### New Handler: `admin_section_image_handler()`

**Purpose:** Prompt admin to upload image for specific section

**Signature:**
```python
async def admin_section_image_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None
```

**Parameters (from callback_data):**
- Section identifier (e.g., "shop", "cart", "orders")

**Behavior:**
- Extracts section identifier from callback query data
- Sets user state to `adm_section_img:{section}`
- Displays prompt with section name and current status
- Provides back navigation to image settings panel

**State Management:**
```python
context.user_data["state"] = f"adm_section_img:{section}"
```

#### Modified Handler: `admin_photo_router()`

**Current Functionality:**
- Routes welcome image uploads
- Routes product image uploads
- Routes category image uploads
- Routes product delivery data uploads
- Routes product media uploads

**New Functionality:**
Adds routing for section-specific image uploads:

```python
async def admin_photo_router(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Route admin photo/file uploads based on active state."""
    
    if not _is_admin(update.effective_user.id):
        return

    state = context.user_data.get("state", "")
    
    # Extract file_id from message
    file_id = None
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
    elif update.message.document:
        file_id = update.message.document.file_id
    
    if not file_id:
        return
    
    # NEW: Section image routing
    if state.startswith("adm_section_img:"):
        section = state.split(":")[1]
        context.user_data.pop("state", None)
        
        # Map section to settings key
        setting_key = f"{section}_image_id"
        await set_setting(setting_key, file_id)
        
        # Send confirmation message
        section_names = {
            "welcome": "Welcome",
            "shop": "Shop",
            "cart": "Cart",
            "orders": "Orders",
            "wallet": "Wallet",
            "support": "Support",
            "admin_panel": "Admin Panel"
        }
        section_display = section_names.get(section, section)
        
        msg = await update.message.reply_text(
            f"✅ <b>{section_display} image updated!</b>\n\n"
            f"📸 This image will now appear in the {section_display} section.",
            parse_mode="HTML",
        )
        
        # Schedule auto-deletion
        await auto_delete(msg)
        await auto_delete(update.message)
        
        await add_action_log(
            "section_image_set",
            ADMIN_ID,
            f"{section}:{file_id[:30]}"
        )
        return
    
    # ... existing routing logic continues ...
```

### 3. Message Cleanup Service

**Implementation:** Leverages existing `auto_delete()` helper in `helpers.py`

**Current Implementation:**
```python
async def auto_delete(message, delay: int | None = None) -> None:
    """Schedule auto-deletion of a message.
    
    If delay is None, reads the `auto_delete` setting from DB (seconds).
    0 or invalid values disable auto-delete.
    """
    if message is None:
        return

    from database import get_setting

    try:
        if delay is None:
            raw = await get_setting("auto_delete", "0") or "0"
            delay = int(raw)
        else:
            delay = int(delay)
    except Exception:
        delay = 0

    if delay <= 0:
        return

    async def _delete_later() -> None:
        try:
            await asyncio.sleep(delay)
            await message.delete()
        except Exception as e:
            logger.warning("auto_delete failed: %s", e)

    asyncio.create_task(_delete_later())
```

**Usage Pattern:**
```python
# After successful image upload
confirmation_msg = await update.message.reply_text("✅ Image updated!")
await auto_delete(confirmation_msg)  # Uses DB setting
await auto_delete(update.message)     # Deletes admin's image message
```

**Configuration:**
The `auto_delete` setting in the database controls the delay:
- `0` = disabled (no auto-deletion)
- `> 0` = delay in seconds before deletion

### 4. Keyboard Module (keyboards.py)

**New Function:** `admin_image_settings_kb()`

**Purpose:** Generate inline keyboard for image settings panel

**Signature:**
```python
def admin_image_settings_kb(image_statuses: dict) -> InlineKeyboardMarkup
```

**Parameters:**
- `image_statuses`: Dictionary mapping section names to boolean status

**Returns:**
Inline keyboard with buttons for each section and status indicators

**Implementation:**
```python
def admin_image_settings_kb(image_statuses: dict) -> InlineKeyboardMarkup:
    """Generate keyboard for image settings panel."""
    
    sections = [
        ("welcome", "🏠 Welcome"),
        ("shop", "🛍️ Shop"),
        ("cart", "🛒 Cart"),
        ("orders", "📦 Orders"),
        ("wallet", "💰 Wallet"),
        ("support", "💬 Support"),
        ("admin_panel", "🔧 Admin Panel"),
    ]
    
    rows = []
    for section_key, section_label in sections:
        status = "✅" if image_statuses.get(section_key) else "❌"
        rows.append([
            Btn(
                f"{section_label} {status}",
                callback_data=f"adm_section_img:{section_key}"
            )
        ])
    
    rows.append([Btn("◀️ Back to Settings", callback_data="adm_settings")])
    
    return InlineKeyboardMarkup(rows)
```

### 5. Section Display Handlers

**Affected Handlers:**
- `handlers/start.py` - Welcome section
- `handlers/catalog.py` - Shop section
- `handlers/cart.py` - Cart section
- `handlers/orders.py` - Orders section
- `handlers/wallet.py` - Wallet section
- `handlers/tickets.py` - Support section
- `handlers/admin.py` - Admin Panel section

**Modification Pattern:**

Each handler that displays a section view needs to retrieve and display the appropriate section image:

```python
async def section_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display section with appropriate image."""
    
    # Retrieve section-specific image
    section_image_id = await get_setting("section_image_id", "")
    
    # Fallback logic (example for shop)
    if not section_image_id and section == "shop":
        section_image_id = await get_setting("welcome_image_id", "")
    
    # Display with image or text-only
    if section_image_id:
        await query.message.reply_photo(
            photo=section_image_id,
            caption=section_text,
            reply_markup=section_keyboard,
            parse_mode="HTML"
        )
    else:
        await query.message.reply_text(
            text=section_text,
            reply_markup=section_keyboard,
            parse_mode="HTML"
        )
```

## Data Models

### Settings Table Entry

**Structure:**
```python
{
    "key": str,      # Setting identifier (e.g., "shop_image_id")
    "value": str     # Telegram file_id or empty string
}
```

**Section Image Keys:**
```python
SECTION_IMAGE_KEYS = {
    "welcome": "welcome_image_id",
    "shop": "shop_image_id",
    "cart": "cart_image_id",
    "orders": "orders_image_id",
    "wallet": "wallet_image_id",
    "support": "support_image_id",
    "admin_panel": "admin_panel_image_id",
}
```

### Session State Model

**Structure:**
```python
context.user_data = {
    "state": str,  # Format: "adm_section_img:{section_name}"
    "temp": dict   # Temporary data (not used for this feature)
}
```

**State Values:**
- `"adm_section_img:welcome"` - Awaiting welcome image upload
- `"adm_section_img:shop"` - Awaiting shop image upload
- `"adm_section_img:cart"` - Awaiting cart image upload
- `"adm_section_img:orders"` - Awaiting orders image upload
- `"adm_section_img:wallet"` - Awaiting wallet image upload
- `"adm_section_img:support"` - Awaiting support image upload
- `"adm_section_img:admin_panel"` - Awaiting admin panel image upload

**State Lifecycle:**
1. Set when admin clicks section button
2. Read when photo is received
3. Cleared after successful processing


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

After analyzing all acceptance criteria, I identified the following redundancies:
- Properties 3.5 and 5.2 both test status indicator display - consolidated into Property 5
- Properties 3.2 and 5.3 both test section selection state transition - consolidated into Property 3
- Properties 4.8 and 6.4 both test graceful handling of missing images - consolidated into Property 9
- Properties 7.1 and 7.2 test state storage and retrieval - combined into round-trip Property 11

### Property 1: Admin Image Auto-Deletion

*For any* admin-sent image message that is successfully processed by the Image_Handler, the Message_Cleanup_Service should schedule that message for deletion according to the configured Auto_Delete_Delay.

**Validates: Requirements 1.1, 1.2**

### Property 2: Confirmation Message Auto-Deletion

*For any* successful section image upload, the system should send a confirmation message containing the section name and schedule it for deletion according to the configured Auto_Delete_Delay.

**Validates: Requirements 2.1, 2.2, 2.4**

### Property 3: Section Selection State Transition

*For any* section selected from the Image_Settings_Panel, the system should transition to the image upload prompt state with the correct section identifier stored in the session.

**Validates: Requirements 3.2, 5.3**

### Property 4: Section Image Storage Isolation

*For any* section image upload, updating that section's image should not modify any other section's image settings.

**Validates: Requirements 3.4**

### Property 5: Status Indicator Accuracy

*For any* section in the Image_Settings_Panel, the displayed status indicator (✅ Set or ❌ Not Set) should accurately reflect whether that section has an image configured in the database.

**Validates: Requirements 3.5, 5.2**

### Property 6: Section Image Unique Storage

*For any* section image upload, the image should be stored with its unique section-specific key (welcome_image_id, shop_image_id, cart_image_id, orders_image_id, wallet_image_id, support_image_id, admin_panel_image_id).

**Validates: Requirements 3.3**

### Property 7: Panel Status Update After Upload

*For any* section image upload, after successful processing, the Image_Settings_Panel should reflect the updated status without requiring manual refresh.

**Validates: Requirements 5.5**

### Property 8: Backward Compatibility Preservation

*For any* existing welcome_image_id in the database before the enhancement, the system should continue to use it for the Welcome section and as fallback for Shop section when shop_image_id is not set.

**Validates: Requirements 6.1, 6.2, 6.3**

### Property 9: Graceful Missing Image Handling

*For any* section navigation where the section-specific image is not configured, the system should display text-only content without errors.

**Validates: Requirements 4.8, 6.4**

### Property 10: State Cleanup After Processing

*For any* successful image upload, the system should clear the admin's session state after processing is complete.

**Validates: Requirements 7.3**

### Property 11: Session State Round-Trip

*For any* section image upload flow, storing the section identifier in session state and then retrieving it during image processing should yield the same section identifier.

**Validates: Requirements 7.1, 7.2**

### Property 12: Session Isolation Between Admins

*For any* two different admins uploading images concurrently, each admin's session state should remain independent and not interfere with the other.

**Validates: Requirements 7.5**

## Error Handling

### Auto-Delete Failure Scenarios

**Scenario:** Message deletion fails due to message already deleted or permissions
**Handling:** 
- Log warning with `logger.warning()`
- Continue execution without blocking
- Do not retry deletion

**Scenario:** Auto_Delete_Delay setting is invalid (non-numeric)
**Handling:**
- Default to 0 (disabled)
- Log warning
- Continue without auto-deletion

**Scenario:** Auto_Delete_Delay is 0
**Handling:**
- Skip auto-deletion entirely
- This is expected behavior, not an error

### Image Upload Failure Scenarios

**Scenario:** Admin sends non-photo content when photo expected
**Handling:**
- Check message type before processing
- If not photo/document, silently ignore
- Do not clear state, allowing retry

**Scenario:** Database write fails during image storage
**Handling:**
- Catch exception in `set_setting()`
- Log error with details
- Send error message to admin
- Do not delete admin's image message
- Do not clear session state

**Scenario:** Admin sends image without active session state
**Handling:**
- Check for state before processing
- If no state, ignore upload silently
- This prevents accidental image processing

### State Management Failure Scenarios

**Scenario:** Session state is corrupted or malformed
**Handling:**
- Validate state format before use
- If invalid, clear state and log warning
- Prompt admin to restart upload process

**Scenario:** Multiple rapid uploads from same admin
**Handling:**
- Each upload clears previous state
- Only the most recent upload is processed
- Previous uploads are ignored

### Display Failure Scenarios

**Scenario:** Image file_id is invalid or expired
**Handling:**
- Catch Telegram API exception
- Fall back to text-only display
- Log warning with section and file_id
- Do not crash handler

**Scenario:** Database query fails when retrieving image settings
**Handling:**
- Catch exception in `get_setting()`
- Default to empty string (no image)
- Log error
- Continue with text-only display

## Testing Strategy

### Dual Testing Approach

This feature requires both unit tests and property-based tests for comprehensive coverage:

**Unit Tests** focus on:
- Specific examples of section image uploads (Welcome, Shop, Cart, etc.)
- Edge cases: auto-delete disabled (delay=0), invalid delay values
- Error conditions: missing state, invalid file types, database failures
- Integration points: handler registration, keyboard generation, state management
- Backward compatibility: existing welcome_image_id usage

**Property-Based Tests** focus on:
- Universal properties across all sections and inputs
- State management round-trips
- Session isolation between concurrent admins
- Auto-deletion timing with various delay values
- Status indicator accuracy across random database states

### Property-Based Testing Configuration

**Library:** `pytest` with `hypothesis` for Python

**Test Configuration:**
- Minimum 100 iterations per property test
- Each test tagged with feature name and property reference
- Tag format: `# Feature: admin-image-settings-enhancement, Property {N}: {property_text}`

**Example Property Test Structure:**

```python
from hypothesis import given, strategies as st
import pytest

@given(
    section=st.sampled_from([
        "welcome", "shop", "cart", "orders", 
        "wallet", "support", "admin_panel"
    ]),
    file_id=st.text(min_size=10, max_size=100)
)
@pytest.mark.asyncio
async def test_section_image_storage_isolation(section, file_id):
    """
    Feature: admin-image-settings-enhancement
    Property 4: Section Image Storage Isolation
    
    For any section image upload, updating that section's image 
    should not modify any other section's image settings.
    """
    # Setup: Get initial state of all sections
    initial_states = {}
    for s in ["welcome", "shop", "cart", "orders", "wallet", "support", "admin_panel"]:
        initial_states[s] = await get_setting(f"{s}_image_id", "")
    
    # Action: Update target section
    await set_setting(f"{section}_image_id", file_id)
    
    # Verify: Only target section changed
    for s in ["welcome", "shop", "cart", "orders", "wallet", "support", "admin_panel"]:
        current = await get_setting(f"{s}_image_id", "")
        if s == section:
            assert current == file_id, f"Target section {s} should be updated"
        else:
            assert current == initial_states[s], f"Other section {s} should be unchanged"
```

### Unit Test Coverage

**Test Categories:**

1. **Handler Tests**
   - `test_admin_image_settings_handler_displays_all_sections()`
   - `test_admin_section_image_handler_sets_correct_state()`
   - `test_admin_photo_router_routes_section_images()`
   - `test_admin_photo_router_ignores_invalid_state()`

2. **Auto-Delete Tests**
   - `test_auto_delete_with_zero_delay_skips_deletion()`
   - `test_auto_delete_with_invalid_delay_skips_deletion()`
   - `test_auto_delete_schedules_deletion_with_valid_delay()`
   - `test_auto_delete_handles_already_deleted_message()`

3. **State Management Tests**
   - `test_state_cleared_after_successful_upload()`
   - `test_state_preserved_after_failed_upload()`
   - `test_concurrent_admin_sessions_isolated()`

4. **Display Tests**
   - `test_welcome_section_displays_welcome_image()`
   - `test_shop_section_falls_back_to_welcome_image()`
   - `test_section_displays_text_only_when_no_image()`
   - `test_section_handles_invalid_file_id_gracefully()`

5. **Backward Compatibility Tests**
   - `test_existing_welcome_image_preserved()`
   - `test_shop_fallback_to_welcome_maintained()`
   - `test_new_fields_coexist_with_old_schema()`

### Test Execution

**Command:**
```bash
pytest tests/ --hypothesis-seed=random -v
```

**Coverage Target:** 90% code coverage for new handlers and modified functions

**CI Integration:** All tests must pass before merge to main branch

