"""
Order History Service for Blind Date Book
Handles order tracking, delivery history, and duplicate exclusion
"""

import uuid
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, Optional, List, Tuple

ORDER_HISTORY_VERSION = "1.0"


@dataclass
class OrderHistory:
    """Order history data model"""
    order_history_id: str
    order_id: str
    user_id: str
    books_received: List[str]
    delivery_date: Optional[str]
    delivery_status: str
    created_at: str


def parse_order_for_history(order: dict, user_id: str) -> Dict:
    """Convert order to history entry"""
    # Extract book IDs from cart items
    books_received = []
    if isinstance(order.get('cart_items'), list):
        books_received = [item.get('book_id', '') for item in order['cart_items']]
    
    return {
        'order_history_id': str(uuid.uuid4()),
        'order_id': order.get('order_id'),
        'user_id': user_id,
        'books_received': books_received,
        'delivery_date': None,
        'delivery_status': 'pending',
        'created_at': datetime.utcnow().isoformat() + 'Z',
        'updated_at': datetime.utcnow().isoformat() + 'Z'
    }


def get_unified_exclude_list(
    user_avoid_list: List[str],
    delivered_books: List[str]
) -> List[str]:
    """
    Create unified exclude list from multiple sources
    Deduplicates and returns set of book IDs to exclude
    """
    exclude_set = set(user_avoid_list or []) | set(delivered_books or [])
    return list(exclude_set)


def mark_order_delivered(
    order_history: dict,
    delivery_date: str,
    tracking_number: Optional[str] = None
) -> Dict:
    """Mark order as delivered"""
    order_history['delivery_status'] = 'delivered'
    order_history['delivery_date'] = delivery_date
    if tracking_number:
        order_history['tracking_number'] = tracking_number
    order_history['updated_at'] = datetime.utcnow().isoformat() + 'Z'
    return order_history


def get_books_from_delivered_orders(order_histories: List[Dict]) -> List[str]:
    """Extract all book IDs from delivered orders"""
    books = []
    for history in order_histories:
        if history.get('delivery_status') == 'delivered':
            books.extend(history.get('books_received', []))
    return list(set(books))  # Deduplicate


def validate_order_filter(filters: dict) -> Tuple[bool, Optional[str]]:
    """Validate order history filter parameters"""
    if 'status' in filters and filters['status'] not in ['pending', 'in-transit', 'delivered', 'returned', 'all']:
        return False, "Invalid status filter"
    
    if 'sort' in filters and filters['sort'] not in ['date', 'status', 'amount']:
        return False, "Invalid sort field"
    
    if 'order' in filters and filters['order'] not in ['asc', 'desc']:
        return False, "Invalid sort order"
    
    return True, None


def apply_order_filters(orders: List[Dict], filters: dict) -> List[Dict]:
    """Apply filters to orders"""
    result = orders
    
    # Filter by status
    if filters.get('status') and filters['status'] != 'all':
        result = [o for o in result if o.get('delivery_status') == filters['status']]
    
    # Filter by date range
    if filters.get('from_date'):
        result = [o for o in result if o.get('delivery_date', '') >= filters['from_date']]
    if filters.get('to_date'):
        result = [o for o in result if o.get('delivery_date', '') <= filters['to_date']]
    
    # Sort
    sort_field = filters.get('sort', 'date')
    sort_order = filters.get('order', 'desc')
    
    if sort_field == 'date':
        sort_key = lambda o: o.get('delivery_date', '') or o.get('created_at', '')
    elif sort_field == 'status':
        sort_key = lambda o: o.get('delivery_status', '')
    elif sort_field == 'amount':
        sort_key = lambda o: o.get('total_amount', 0)
    else:
        sort_key = lambda o: o.get('created_at', '')
    
    result = sorted(result, key=sort_key, reverse=(sort_order == 'desc'))
    
    return result


def paginate_orders(orders: List[Dict], limit: int = 10, offset: int = 0) -> Dict:
    """Paginate orders"""
    total = len(orders)
    paginated = orders[offset:offset + limit]
    
    return {
        'total': total,
        'count': len(paginated),
        'offset': offset,
        'limit': limit,
        'orders': paginated
    }
