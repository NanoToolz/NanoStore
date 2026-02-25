"""Shop section — user-facing store browsing."""

from .catalog import catalog_handler, category_handler
from .product import product_detail_handler
from .cart import cart_handler, cart_add_handler, cart_remove_handler, cart_clear_handler
from .search import search_handler

__all__ = [
    "catalog_handler", "category_handler",
    "product_detail_handler",
    "cart_handler", "cart_add_handler", "cart_remove_handler", "cart_clear_handler",
    "search_handler",
]
