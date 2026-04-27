from typing import Dict, List

next_user_id: int = 3
next_product_id: int = 3
next_order_id: int = 2


DEFAULT_USER_ID: int = 1

users_db: Dict[int, dict] = {
    1: {"id": 1, "name": "Ahmed", "email": "ahmed@example.com"},
    2: {"id": 2, "name": "Fatima", "email": "fatima@example.com"},
}

products_db: Dict[int, dict] = {
    1: {"id": 1, "name": "Laptop", "price": 999.99, "category": "Electronics", "stock": 10},
    2: {"id": 2, "name": "Mouse", "price": 29.99, "category": "Accessories", "stock": 50},
}

cart_db: Dict[int, List[dict]] = {
    1: [
        {"product_id": 1, "product_name": "Laptop", "quantity": 2, "unit_price": 999.99, "total_price": 1999.98},
        {"product_id": 3, "product_name": "USB-C Cable", "quantity": 5, "unit_price": 15.99, "total_price": 79.95},
    ]
}


orders_db: Dict[int, List[dict]] = {
    1: [
        {
            "id": 1,
            "items": [...],
            "total_amount": 2079.93,
            "created_at": "2024-01-15T14:30:22"
        }
    ]
}

