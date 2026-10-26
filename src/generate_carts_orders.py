"""Generate carts, cart lines, orders, order lines."""
import random
from datetime import timedelta, datetime
from typing import List, Dict, Any

from config.settings import *
from src.ids import gen
from src.utils import set_seed, random_datetime_in_range, iso_format, weighted_choice, round_money


def generate_carts_and_orders(sessions: List[Dict[str, Any]], customers: List[Dict[str, Any]], 
                               products: List[Dict[str, Any]], pageviews: List[Dict[str, Any]],
                               n_orders: int) -> tuple:
    """Generate carts, cart lines, orders, order lines."""
    carts = []
    cart_lines = []
    orders = []
    order_lines = []
    
    set_seed(SEED + 5)
    
    # Build lookup
    session_map = {s["session_id"]: s for s in sessions}
    cust_map = {c["customer_id"]: c for c in customers}
    prod_map = {p["product_id"]: p for p in products}
    
    # Only active products for normal cart additions
    active_products = [p for p in products if p["status"] == "active"]
    
    cart_count = 0
    order_count = 0
    
    # Generate carts from sessions (most sessions might add to cart)
    for session in sessions:
        if cart_count >= 150000:  # reasonable number
            break
        if random.random() < 0.3:  # 30% of sessions create cart
            session_start = datetime.strptime(session["session_start"].replace('Z', ''), "%Y-%m-%dT%H:%M:%S")
            cart_created = session_start + timedelta(minutes=random.randint(5, 30))
            cart_status = weighted_choice(CART_STATUSES, [0.2, 0.5, 0.3, 0.0])  # some converted
            
            cart = {
                "cart_id": gen.cart("2026"),
                "session_id": session["session_id"],
                "customer_id": session["customer_id"],
                "cart_status": cart_status,
                "created_at": iso_format(cart_created),
                "updated_at": iso_format(cart_created + timedelta(minutes=random.randint(1, 10))),
                "cart_total": 0.0
            }
            carts.append(cart)
            cart_count += 1
            
            # Add cart lines
            num_items = random.randint(1, 4)
            for _ in range(num_items):
                prod = random.choice(active_products) if active_products else random.choice(products)
                qty = random.randint(1, 3)
                unit_price = prod["price"]
                line_amt = round_money(qty * unit_price)
                
                cl = {
                    "cart_line_id": gen.cart_line(),
                    "cart_id": cart["cart_id"],
                    "product_id": prod["product_id"],
                    "quantity": qty,
                    "unit_price": unit_price,
                    "line_amount": line_amt,
                    "added_at": iso_format(cart_created + timedelta(minutes=random.randint(1, 5))),
                    "created_at": iso_format(cart_created)
                }
                cart_lines.append(cl)
            
            # Update cart total
            cart_total = sum([cl["line_amount"] for cl in cart_lines if cl["cart_id"] == cart["cart_id"]])
            cart["cart_total"] = round_money(cart_total)
    
    # Generate orders
    set_seed(SEED + 6)
    # Create orders from converted carts mostly
    converted_carts = [c for c in carts if c["cart_status"] == "converted"]
    
    for i in range(n_orders):
        if order_count >= n_orders:
            break
        # Most orders come from converted carts
        if converted_carts and random.random() < 0.8:
            cart = random.choice(converted_carts)
            converted_carts.remove(cart)  # use once
            session = session_map.get(cart["session_id"])
            order_date = datetime.strptime(cart["updated_at"].replace('Z', ''), "%Y-%m-%dT%H:%M:%S") + timedelta(minutes=random.randint(1, 15))
            order_status = "completed"  # mostly completed
        else:
            # Some orders without cart/session (will create edge case 1 later, but create normal ones too)
            customer = random.choice(customers)
            order_date = random_datetime_in_range(datetime(2025, 6, 1), datetime(2026, 10, 1))
            session = None
            cart = None
            order_status = weighted_choice(ORDER_STATUSES, [0.9, 0.05, 0.03, 0.02])
        
        order = {
            "order_id": gen.order("2026"),
            "cart_id": cart["cart_id"] if cart else None,
            "session_id": session["session_id"] if session else None,
            "customer_id": cart["customer_id"] if cart else random.choice(customers)["customer_id"],
            "order_status": order_status,
            "order_date": iso_format(order_date),
            "currency": "USD",
            "order_total": 0.0,
            "payment_method": weighted_choice(PAYMENT_METHODS, [0.6, 0.2, 0.15, 0.05]),
            "created_at": iso_format(order_date),
            "is_anomalous_edge1": False
        }
        orders.append(order)
        order_count += 1
        
        # Add order lines
        if cart:
            # Copy from cart lines
            for cl in cart_lines:
                if cl["cart_id"] == cart["cart_id"]:
                    ol = {
                        "order_line_id": gen.order_line(),
                        "order_id": order["order_id"],
                        "product_id": cl["product_id"],
                        "quantity": cl["quantity"],
                        "unit_price": cl["unit_price"],
                        "line_amount": cl["line_amount"],
                        "created_at": iso_format(order_date)
                    }
                    order_lines.append(ol)
        else:
            # Create random order lines
            num_items = random.randint(1, 3)
            for _ in range(num_items):
                prod = random.choice([p for p in products if p["status"] == "active"] or products)
                qty = random.randint(1, 2)
                unit_price = prod["price"]
                line_amt = round_money(qty * unit_price)
                ol = {
                    "order_line_id": gen.order_line(),
                    "order_id": order["order_id"],
                    "product_id": prod["product_id"],
                    "quantity": qty,
                    "unit_price": unit_price,
                    "line_amount": line_amt,
                    "created_at": iso_format(order_date)
                }
                order_lines.append(ol)
        
        # Update order total
        order_total = sum([ol["line_amount"] for ol in order_lines if ol["order_id"] == order["order_id"]])
        order["order_total"] = round_money(order_total)
    
    return carts, cart_lines, orders, order_lines
