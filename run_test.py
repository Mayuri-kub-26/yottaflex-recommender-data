#!/usr/bin/env python3
"""Test entry point with smaller volumes."""
import json
import sys
from datetime import datetime

# Configure safe UTF-8 output on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# Override settings
import config.settings_test as settings
sys.modules['config.settings'] = settings

from config.settings import *
from src.ids import gen
from src.utils import set_seed
from src.generate_masters import generate_customers, generate_categories, generate_products
from src.generate_sessions import generate_sessions, generate_pageviews
from src.generate_carts_orders import generate_carts_and_orders
from src.generate_relations_recommend import generate_product_relations, generate_recommendations
from src.inject_edges import inject_edge_cases
from src.split import chronological_split
from src.validate import Validator
from src.export import Exporter


def main():
    print("=" * 60)
    print("YottaFlex AI Candidate Project - TEST Run (Smaller Volumes)")
    print("=" * 60)
    print(f"Seed: {SEED}")
    print(f"Volumes: {N_CUSTOMERS} customers, {N_PRODUCTS} products, {N_SESSIONS} sessions, {N_ORDERS} orders")
    print("=" * 60)
    print()
    
    set_seed(SEED)
    gen.reset()
    
    print("[1/10] Generating master data...")
    customers = generate_customers(N_CUSTOMERS)
    print(f"  Generated {len(customers)} customers")
    categories = generate_categories()
    print(f"  Generated {len(categories)} categories")
    products = generate_products(N_PRODUCTS, categories)
    print(f"  Generated {len(products)} products")
    print()
    
    print("[2/10] Generating sessions and pageviews...")
    sessions = generate_sessions(customers, N_SESSIONS)
    print(f"  Generated {len(sessions)} sessions")
    pageviews = generate_pageviews(sessions, products)
    print(f"  Generated {len(pageviews)} pageviews")
    print()
    
    print("[3/10] Generating carts and orders...")
    carts, cart_lines, orders, order_lines = generate_carts_and_orders(
        sessions, customers, products, pageviews, N_ORDERS
    )
    print(f"  Generated {len(carts)} carts, {len(cart_lines)} cart lines")
    print(f"  Generated {len(orders)} orders, {len(order_lines)} order lines")
    print()
    
    print("[4/10] Generating product relations and recommendations...")
    relations = generate_product_relations(products, orders, order_lines)
    print(f"  Generated {len(relations)} product relations")
    recommendations = generate_recommendations(sessions, customers, products, orders, order_lines, relations)
    print(f"  Generated {len(recommendations)} recommendations")
    print()
    
    print("[5/10] Injecting required edge cases...")
    ground_truth = inject_edge_cases(customers, products, sessions, orders, order_lines, recommendations)
    print(f"  Injected {len(ground_truth)} edge cases")
    print()
    
    print("[6/10] Applying chronological train/test split...")
    train_sess, test_sess = chronological_split(sessions, recommendations)
    print(f"  Train: {len(train_sess)}, Test: {len(test_sess)}")
    print()
    
    print("[7/10] Exporting data...")
    exporter = Exporter()
    all_data = {
        "Customer": customers, "Category": categories, "Product": products,
        "Session": sessions, "PageView": pageviews, "Cart": carts,
        "CartLine": cart_lines, "Order": orders, "OrderLine": order_lines,
        "ProductRelation": relations, "Recommendation": recommendations
    }
    for name, data in all_data.items():
        exporter.to_csv(data, f"{name.lower()}.csv")
        exporter.to_json(data, f"{name.lower()}.json")
    exporter.to_csv(ground_truth, "ground_truth.csv", subdir="ground_truth")
    exporter.to_json(ground_truth, "ground_truth.json", subdir="ground_truth")
    exporter.to_sql(all_data)
    print()
    
    print("[8/10] Validating...")
    validator = Validator()
    validation_results = validator.validate_all(
        customers, categories, products, sessions, pageviews,
        carts, cart_lines, orders, order_lines, relations, recommendations, ground_truth
    )
    print(f"  Checks: {validation_results['checks_passed']}/{validation_results['checks_total']}, Errors: {len(validation_results['errors'])}")
    print()
    
    print("TEST COMPLETE!")
    print(f"Data in: {DATA_DIR}")
    print(f"Ground truth in: {GROUND_TRUTH_DIR}")


if __name__ == "__main__":
    main()
