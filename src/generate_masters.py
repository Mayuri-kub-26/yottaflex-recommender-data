"""Generate master/parent data: Customer, Category, Product."""
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

from config.settings import *
from src.ids import gen
from src.utils import set_seed, random_date_between, iso_format, date_format, weighted_choice, round_money


def generate_customers(n: int) -> List[Dict[str, Any]]:
    """Generate customers with variety including sparse users."""
    customers = []
    set_seed(SEED)
    
    for i in range(n):
        signup_dt = random_date_between(SIGNUP_START, SIGNUP_END)
        # Some users are sparse (fewer sessions)
        is_sparse = random.random() < 0.15  # 15% sparse users
        is_bot_candidate = random.random() < 0.02  # 2% bot candidates
        
        customer = {
            "customer_id": gen.customer(),
            "signup_date": date_format(signup_dt),
            "age_group": weighted_choice(AGE_GROUPS, [0.12, 0.25, 0.25, 0.18, 0.12, 0.08]),
            "gender": weighted_choice(GENDERS, [0.48, 0.48, 0.03, 0.01]),
            "region": weighted_choice(REGIONS, [0.25, 0.25, 0.2, 0.2, 0.1]),
            "loyalty_tier": weighted_choice(LOYALTY_TIERS, [0.5, 0.3, 0.15, 0.05]),
            "is_sparse": is_sparse,
            "is_bot_flag_candidate": is_bot_candidate,
            "created_at": iso_format(signup_dt)
        }
        customers.append(customer)
    return customers


def generate_categories() -> List[Dict[str, Any]]:
    """Generate categories with hierarchy and seasonal categories."""
    categories = []
    set_seed(SEED + 1)
    
    # Top level categories
    top_level = [
        ("Electronics", False),
        ("Clothing", True),  # seasonal
        ("Home & Kitchen", False),
        ("Sports & Outdoors", True),  # seasonal
        ("Books", False),
        ("Toys & Games", True),  # seasonal
        ("Beauty & Personal Care", False),
        ("Automotive", False),
    ]
    
    cat_map = {}
    for name, seasonal in top_level:
        cat_id = gen.category()
        cat = {
            "category_id": cat_id,
            "parent_category_id": None,
            "category_name": name,
            "is_seasonal": seasonal,
            "is_active": True,
            "created_at": iso_format(datetime(2023, 1, 1))
        }
        categories.append(cat)
        cat_map[name] = cat_id
    
    # Add some subcategories
    subcats = [
        ("Electronics", "Phones", False),
        ("Electronics", "Laptops", False),
        ("Clothing", "Men's Wear", True),
        ("Clothing", "Women's Wear", True),
        ("Home & Kitchen", "Furniture", False),
        ("Sports & Outdoors", "Fitness", True),
    ]
    
    for parent_name, child_name, seasonal in subcats:
        cat_id = gen.category()
        cat = {
            "category_id": cat_id,
            "parent_category_id": cat_map[parent_name],
            "category_name": child_name,
            "is_seasonal": seasonal,
            "is_active": True,
            "created_at": iso_format(datetime(2023, 2, 1))
        }
        categories.append(cat)
    
    return categories


def generate_products(n: int, categories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate products with cold-start items and some without categories (edge case prep)."""
    products = []
    set_seed(SEED + 2)
    
    cat_ids = [c["category_id"] for c in categories if c["is_active"]]
    
    brands = ["BrandA", "BrandB", "BrandC", "BrandD", "BrandE", "GenericCo", "TechPro", "StyleMax"]
    adjectives = ["Premium", "Classic", "Deluxe", "Pro", "Basic", "Elite", "Smart"]
    nouns = ["Widget", "Device", "Item", "Product", "Gear", "Kit", "Set"]
    
    for i in range(n):
        is_cold_start = random.random() < 0.1  # 10% cold start
        status = weighted_choice(PRODUCT_STATUSES, [0.85, 0.08, 0.07])  # mostly active
        launch_dt = random_date_between("2023-01-01", "2026-06-01")
        
        # Occasionally product has no category (will be used for edge case)
        has_category = random.random() > 0.005  # 0.5% chance to have no category initially
        
        product = {
            "product_id": gen.product(),
            "category_id": random.choice(cat_ids) if has_category else None,
            "product_name": f"{random.choice(adjectives)} {random.choice(nouns)} {i+1}",
            "brand": random.choice(brands),
            "price": round_money(random.uniform(5.0, 500.0)),
            "currency": "USD",
            "status": status,
            "is_cold_start": is_cold_start,
            "launch_date": date_format(launch_dt),
            "created_at": iso_format(launch_dt)
        }
        products.append(product)
    
    return products
