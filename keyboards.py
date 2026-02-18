from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def back_btn(target="main_menu"):
    return InlineKeyboardButton("\u2b05\ufe0f Back", callback_data=target)


def back_kb(target="main_menu"):
    return InlineKeyboardMarkup([[back_btn(target)]])


# ==================== USER KEYBOARDS ====================

def main_menu_kb(is_admin=False):
    buttons = [
        [InlineKeyboardButton("\ud83d\udecd\ufe0f Shop", callback_data="shop"),
         InlineKeyboardButton("\ud83d\udd0d Search", callback_data="search")],
        [InlineKeyboardButton("\ud83d\uded2 My Cart", callback_data="cart"),
         InlineKeyboardButton("\ud83d\udce6 My Orders", callback_data="my_orders")],
        [InlineKeyboardButton("\u2753 Help", callback_data="help")],
    ]
    if is_admin:
        buttons.append([InlineKeyboardButton("\ud83d\udc64 Admin Panel", callback_data="admin")])
    return InlineKeyboardMarkup(buttons)


def categories_kb(categories, back="main_menu"):
    buttons = []
    for cat in categories:
        buttons.append([InlineKeyboardButton(
            f"{cat['emoji']} {cat['name']}", callback_data=f"cat_{cat['id']}"
        )])
    buttons.append([back_btn(back)])
    return InlineKeyboardMarkup(buttons)


def products_kb(products_list, category_id):
    buttons = []
    for p in products_list:
        buttons.append([InlineKeyboardButton(
            f"{p['name']} \u2014 ${p['price']:.2f}", callback_data=f"prod_{p['id']}"
        )])
    buttons.append([back_btn("shop")])
    return InlineKeyboardMarkup(buttons)


def product_detail_kb(product_id, category_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("\ud83d\uded2 Add to Cart", callback_data=f"addcart_{product_id}")],
        [back_btn(f"cat_{category_id}")],
    ])


def cart_kb(cart_items, total):
    buttons = []
    for item in cart_items:
        buttons.append([
            InlineKeyboardButton("\u2796", callback_data=f"cartdec_{item['id']}"),
            InlineKeyboardButton(f"{item['name']} x{item['quantity']}", callback_data="noop"),
            InlineKeyboardButton("\u2795", callback_data=f"cartinc_{item['id']}"),
            InlineKeyboardButton("\ud83d\uddd1\ufe0f", callback_data=f"cartdel_{item['id']}"),
        ])
    buttons.append([InlineKeyboardButton("\ud83c\udff7\ufe0f Apply Coupon", callback_data="apply_coupon")])
    buttons.append([InlineKeyboardButton(f"\ud83d\udcb3 Checkout (${total:.2f})", callback_data="checkout")])
    buttons.append([InlineKeyboardButton("\ud83d\uddd1\ufe0f Clear All", callback_data="clear_cart")])
    buttons.append([back_btn("main_menu")])
    return InlineKeyboardMarkup(buttons)


def empty_cart_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("\ud83d\udecd\ufe0f Browse Shop", callback_data="shop")],
        [back_btn("main_menu")],
    ])


def checkout_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("\u2705 Confirm Order", callback_data="confirm_order")],
        [back_btn("cart")],
    ])


def order_detail_kb(back="my_orders"):
    return InlineKeyboardMarkup([[back_btn(back)]])


def confirm_kb(yes_data, no_data="main_menu"):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("\u2705 Yes", callback_data=yes_data),
         InlineKeyboardButton("\u274c No", callback_data=no_data)],
    ])


# ==================== ADMIN KEYBOARDS ====================

def admin_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("\ud83d\udcca Dashboard", callback_data="adm_dash")],
        [InlineKeyboardButton("\ud83d\udcc2 Categories", callback_data="adm_cats"),
         InlineKeyboardButton("\ud83d\udce6 Products", callback_data="adm_prods")],
        [InlineKeyboardButton("\ud83d\uded2 Orders", callback_data="adm_orders"),
         InlineKeyboardButton("\ud83d\udc65 Users", callback_data="adm_users")],
        [InlineKeyboardButton("\ud83d\udce3 Broadcast", callback_data="adm_broadcast"),
         InlineKeyboardButton("\ud83c\udff7\ufe0f Coupons", callback_data="adm_coupons")],
        [InlineKeyboardButton("\u2699\ufe0f Settings", callback_data="adm_settings")],
        [back_btn("main_menu")],
    ])


def admin_cats_kb(categories):
    buttons = []
    for cat in categories:
        buttons.append([InlineKeyboardButton(
            f"{cat['emoji']} {cat['name']}", callback_data=f"adm_cat_{cat['id']}"
        )])
    buttons.append([InlineKeyboardButton("\u2795 Add Category", callback_data="adm_addcat")])
    buttons.append([back_btn("admin")])
    return InlineKeyboardMarkup(buttons)


def admin_cat_detail_kb(cat_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("\u270f\ufe0f Edit", callback_data=f"adm_editcat_{cat_id}"),
         InlineKeyboardButton("\ud83d\uddd1\ufe0f Delete", callback_data=f"adm_delcat_{cat_id}")],
        [back_btn("adm_cats")],
    ])


def admin_prods_kb(products_list):
    buttons = []
    for p in products_list:
        buttons.append([InlineKeyboardButton(
            f"{p['name']} \u2014 ${p['price']:.2f}", callback_data=f"adm_prod_{p['id']}"
        )])
    buttons.append([InlineKeyboardButton("\u2795 Add Product", callback_data="adm_addprod")])
    buttons.append([back_btn("admin")])
    return InlineKeyboardMarkup(buttons)


def admin_prod_detail_kb(prod_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("\u270f\ufe0f Name", callback_data=f"adm_editprod_name_{prod_id}"),
         InlineKeyboardButton("\ud83d\udcb0 Price", callback_data=f"adm_editprod_price_{prod_id}")],
        [InlineKeyboardButton("\ud83d\udcdd Desc", callback_data=f"adm_editprod_desc_{prod_id}"),
         InlineKeyboardButton("\ud83d\uddbc\ufe0f Image", callback_data=f"adm_editprod_img_{prod_id}")],
        [InlineKeyboardButton("\ud83d\uddd1\ufe0f Delete", callback_data=f"adm_delprod_{prod_id}")],
        [back_btn("adm_prods")],
    ])


def admin_orders_kb(orders):
    status_emoji = {"pending": "\ud83d\udfe1", "confirmed": "\ud83d\udfe2", "processing": "\ud83d\udd35",
                    "shipped": "\ud83d\udce6", "delivered": "\u2705", "cancelled": "\ud83d\udd34"}
    buttons = []
    for o in orders:
        emoji = status_emoji.get(o["status"], "\u26aa")
        buttons.append([InlineKeyboardButton(
            f"{emoji} #{o['id']} \u2014 ${o['total']:.2f}", callback_data=f"adm_order_{o['id']}"
        )])
    buttons.append([back_btn("admin")])
    return InlineKeyboardMarkup(buttons)


def admin_order_detail_kb(order_id):
    statuses = ["confirmed", "processing", "shipped", "delivered", "cancelled"]
    buttons = []
    row = []
    for s in statuses:
        row.append(InlineKeyboardButton(s.title(), callback_data=f"adm_setstatus_{order_id}_{s}"))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([back_btn("adm_orders")])
    return InlineKeyboardMarkup(buttons)


def admin_users_kb(users):
    buttons = []
    for u in users[:20]:
        banned = "\ud83d\udd34" if u["banned"] else "\ud83d\udfe2"
        name = u["full_name"] or u["username"] or str(u["user_id"])
        buttons.append([InlineKeyboardButton(
            f"{banned} {name}", callback_data=f"adm_user_{u['user_id']}"
        )])
    buttons.append([back_btn("admin")])
    return InlineKeyboardMarkup(buttons)


def admin_user_detail_kb(user_id, is_banned):
    action = "unban" if is_banned else "ban"
    label = "\u2705 Unban" if is_banned else "\ud83d\udeab Ban"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(label, callback_data=f"adm_{action}_{user_id}")],
        [back_btn("adm_users")],
    ])


def admin_coupons_kb(coupons):
    buttons = []
    for c in coupons:
        active = "\ud83d\udfe2" if c["active"] else "\ud83d\udd34"
        buttons.append([InlineKeyboardButton(
            f"{active} {c['code']} \u2014 {c['discount_percent']}% off",
            callback_data=f"adm_coupon_{c['code']}"
        )])
    buttons.append([InlineKeyboardButton("\u2795 Add Coupon", callback_data="adm_addcoupon")])
    buttons.append([back_btn("admin")])
    return InlineKeyboardMarkup(buttons)


def admin_coupon_detail_kb(code):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("\ud83d\uddd1\ufe0f Delete", callback_data=f"adm_delcoupon_{code}")],
        [back_btn("adm_coupons")],
    ])
