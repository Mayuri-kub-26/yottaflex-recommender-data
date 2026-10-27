"""Generate product relations and recommendations."""
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

from config.settings import *
from src.ids import gen
from src.utils import set_seed, iso_format, weighted_choice, round_money


def generate_product_relations(products: List[Dict[str, Any]], orders: List[Dict[str, Any]], 
                                order_lines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate co-purchase and category relationships."""
    relations = []
    set_seed(SEED + 7)
    
    # Group order lines by order
    order_to_products = {}
    for ol in order_lines:
        if ol["order_id"] not in order_to_products:
            order_to_products[ol["order_id"]] = []
        order_to_products[ol["order_id"]].append(ol["product_id"])
    
    # Generate co-purchase relations
    pairs_seen = set()
    for order_id, prod_list in order_to_products.items():
        if len(prod_list) >= 2:
            # Create pairs
            for i in range(len(prod_list)):
                for j in range(i+1, min(i+3, len(prod_list))):  # limit pairs
                    p_a = prod_list[i]
                    p_b = prod_list[j]
                    key = tuple(sorted([p_a, p_b]) + ["co_purchase"])
                    if key in pairs_seen:
                        continue
                    pairs_seen.add(key)
                    rel = {
                        "relation_id": gen.product_relation(),
                        "product_id_a": min(p_a, p_b) if False else p_a,
                        "product_id_b": p_b if p_a != p_b else prod_list[i+1],
                        "relation_type": "co_purchase",
                        "score": round(random.uniform(0.3, 0.9), 3),
                        "source": "generated",
                        "created_at": iso_format(datetime.now())
                    }
                    if rel["product_id_a"] == rel["product_id_b"]:
                        continue
                    relations.append(rel)
                    if len(relations) > 50000:
                        break
                if len(relations) > 50000:
                    break
            if len(relations) > 50000:
                break
    
    # Add same category relations
    prod_by_cat = {}
    for p in products:
        if p["category_id"]:
            if p["category_id"] not in prod_by_cat:
                prod_by_cat[p["category_id"]] = []
            prod_by_cat[p["category_id"]].append(p["product_id"])
    
    for cat_id, prod_list in prod_by_cat.items():
        if len(prod_list) >= 2:
            for i in range(min(10, len(prod_list))):
                for j in range(i+1, min(i+3, len(prod_list))):
                    p_a, p_b = prod_list[i], prod_list[j]
                    key = tuple(sorted([p_a, p_b]) + ["same_category"])
                    if key in pairs_seen:
                        continue
                    pairs_seen.add(key)
                    rel = {
                        "relation_id": gen.product_relation(),
                        "product_id_a": p_a,
                        "product_id_b": p_b,
                        "relation_type": "same_category",
                        "score": round(random.uniform(0.2, 0.6), 3),
                        "source": "generated",
                        "created_at": iso_format(datetime.now())
                    }
                    relations.append(rel)
    
    return relations


def generate_recommendations(sessions: List[Dict[str, Any]], customers: List[Dict[str, Any]],
                            products: List[Dict[str, Any]], orders: List[Dict[str, Any]],
                            order_lines: List[Dict[str, Any]], relations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate recommendations with exclusions."""
    recommendations = []
    set_seed(SEED + 8)
    
    # Get purchased products per customer
    order_to_customer = {o["order_id"]: o["customer_id"] for o in orders}
    customer_purchased = {}
    for ol in order_lines:
        cust = order_to_customer.get(ol["order_id"])
        if cust:
            if cust not in customer_purchased:
                customer_purchased[cust] = set()
            customer_purchased[cust].add(ol["product_id"])
    
    prod_map = {p["product_id"]: p for p in products}
    all_prod_keys = list(prod_map.keys())
    active_prods = [p["product_id"] for p in products if p["status"] == "active"]
    discontinued_prods = [p["product_id"] for p in products if p["status"] == "discontinued"]
    
    # Generate recommendations for some sessions
    rec_count = 0
    for session in sessions[:100000]:  # limit for size
        if rec_count > 80000:
            break
        cust = session["customer_id"]
        purchased = customer_purchased.get(cust, set())
        
        # Generate 2-5 recommendations per session
        num_recs = random.randint(2, 5)
        for rank in range(1, num_recs + 1):
            # Pick a candidate
            candidate = random.choice(active_prods) if active_prods else random.choice(all_prod_keys)
            prod = prod_map[candidate]
            
            is_valid = True
            excluded_reason = None
            
            # Apply exclusions
            if candidate in purchased:
                is_valid = False
                excluded_reason = "purchased"
            elif prod["status"] == "discontinued":
                is_valid = False
                excluded_reason = "discontinued"
            elif prod["status"] == "out_of_stock":
                is_valid = False
                excluded_reason = "out_of_stock"
            
            rec = {
                "recommendation_id": gen.recommendation(),
                "session_id": session["session_id"],
                "customer_id": cust,
                "product_id": candidate,
                "recommended_for_product_id": random.choice(all_prod_keys) if all_prod_keys else None,
                "score": round(random.uniform(0.1, 0.95), 3),
                "rank": rank,
                "reason": weighted_choice(REASON_TYPES, [0.4, 0.3, 0.2, 0.1]),
                "excluded_reason": excluded_reason,
                "is_valid": is_valid,
                "split": random.choice(SPLITS),  # will be fixed by chronological split
                "created_at": session["session_start"]
            }
            recommendations.append(rec)
            rec_count += 1
    
    return recommendations
