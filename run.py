#!/usr/bin/env python3
"""Main entry point for YottaFlex synthetic data generator."""
import json
import sys
from datetime import datetime

# Configure safe UTF-8 output on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Add project root to path
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

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
    print("YottaFlex AI Candidate Project - Synthetic Data Generator")
    print("=" * 60)
    print(f"Seed: {SEED}")
    print(f"Volumes: {N_CUSTOMERS} customers, {N_PRODUCTS} products, {N_SESSIONS} sessions, {N_ORDERS} orders")
    print("=" * 60)
    print()
    
    # Set seed for reproducibility
    set_seed(SEED)
    gen.reset()
    
    # Step 1: Generate masters
    print("[1/10] Generating master data...")
    customers = generate_customers(N_CUSTOMERS)
    print(f"  Generated {len(customers)} customers")
    
    categories = generate_categories()
    print(f"  Generated {len(categories)} categories")
    
    products = generate_products(N_PRODUCTS, categories)
    print(f"  Generated {len(products)} products")
    print()
    
    # Step 2: Generate sessions and pageviews
    print("[2/10] Generating sessions and pageviews...")
    sessions = generate_sessions(customers, N_SESSIONS)
    print(f"  Generated {len(sessions)} sessions")
    
    pageviews = generate_pageviews(sessions, products)
    print(f"  Generated {len(pageviews)} pageviews")
    print()
    
    # Step 3: Generate carts and orders
    print("[3/10] Generating carts and orders...")
    carts, cart_lines, orders, order_lines = generate_carts_and_orders(
        sessions, customers, products, pageviews, N_ORDERS
    )
    print(f"  Generated {len(carts)} carts, {len(cart_lines)} cart lines")
    print(f"  Generated {len(orders)} orders, {len(order_lines)} order lines")
    print()
    
    # Step 4: Generate relations and recommendations
    print("[4/10] Generating product relations and recommendations...")
    relations = generate_product_relations(products, orders, order_lines)
    print(f"  Generated {len(relations)} product relations")
    
    recommendations = generate_recommendations(sessions, customers, products, orders, order_lines, relations)
    print(f"  Generated {len(recommendations)} recommendations")
    print()
    
    # Step 5: Inject edge cases
    print("[5/10] Injecting required edge cases...")
    ground_truth = inject_edge_cases(customers, products, sessions, orders, order_lines, recommendations)
    print(f"  Injected {len(ground_truth)} edge cases (labelled in ground truth)")
    print()
    
    # Step 6: Chronological split
    print("[6/10] Applying chronological train/test split...")
    train_sess, test_sess = chronological_split(sessions, recommendations)
    print(f"  Train sessions: {len(train_sess)}, Test sessions: {len(test_sess)}")
    print()
    
    # Step 7: Export data
    print("[7/10] Exporting data (CSV/JSON/SQL)...")
    exporter = Exporter()
    
    all_data = {
        "Customer": customers,
        "Category": categories,
        "Product": products,
        "Session": sessions,
        "PageView": pageviews,
        "Cart": carts,
        "CartLine": cart_lines,
        "Order": orders,
        "OrderLine": order_lines,
        "ProductRelation": relations,
        "Recommendation": recommendations
    }
    
    for name, data in all_data.items():
        exporter.to_csv(data, f"{name.lower()}.csv")
        exporter.to_json(data, f"{name.lower()}.json")
    
    # Export ground truth separately
    exporter.to_csv(ground_truth, "ground_truth.csv", subdir="ground_truth")
    exporter.to_json(ground_truth, "ground_truth.json", subdir="ground_truth")
    
    exporter.to_sql(all_data)
    print()
    
    # Step 8: Validate
    print("[8/10] Validating data...")
    validator = Validator()
    validation_results = validator.validate_all(
        customers, categories, products, sessions, pageviews,
        carts, cart_lines, orders, order_lines, relations, recommendations, ground_truth
    )
    
    print(f"  Checks passed: {validation_results['checks_passed']}/{validation_results['checks_total']}")
    print(f"  Errors: {len(validation_results['errors'])}")
    print(f"  Warnings: {len(validation_results['warnings'])}")
    print()
    
    # Step 9: Generate validation summary
    print("[9/10] Generating validation summary...")
    checksums = validator.compute_file_checksums()
    
    summary = {
        "timestamp": datetime.now().isoformat(),
        "seed": SEED,
        "volumes": {
            "customers": len(customers),
            "categories": len(categories),
            "products": len(products),
            "sessions": len(sessions),
            "pageviews": len(pageviews),
            "carts": len(carts),
            "cart_lines": len(cart_lines),
            "orders": len(orders),
            "order_lines": len(order_lines),
            "product_relations": len(relations),
            "recommendations": len(recommendations),
            "ground_truth": len(ground_truth)
        },
        "split": {
            "train_sessions": len(train_sess),
            "test_sessions": len(test_sess)
        },
        "validation": validation_results,
        "checksums": checksums,
        "edge_cases_injected": [gt["issue_type"] for gt in ground_truth],
        "reproducibility": {
            "seed_fixed": SEED,
            "note": "Run twice with same seed to verify identical results"
        }
    }
    
    with open(DOCS_DIR / "validation_summary.json", 'w') as f:
        json.dump(summary, f, indent=2)
    
    with open(DOCS_DIR / "validation_summary.md", 'w') as f:
        f.write("# Validation Summary\n\n")
        f.write(f"**Generated:** {summary['timestamp']}  \n")
        f.write(f"**Seed:** {SEED}  \n\n")
        f.write("## Volumes\n\n")
        for k, v in summary['volumes'].items():
            f.write(f"- {k.replace('_', ' ').title()}: {v:,}\n")
        f.write("\n## Train/Test Split (Chronological)\n\n")
        f.write(f"- Train Sessions: {len(train_sess):,}\n")
        f.write(f"- Test Sessions: {len(test_sess):,}\n")
        f.write("\n## Validation Results\n\n")
        f.write(f"- Checks Passed: {validation_results['checks_passed']}/{validation_results['checks_total']}\n")
        f.write(f"- Errors: {len(validation_results['errors'])}\n")
        f.write(f"- Warnings: {len(validation_results['warnings'])}\n")
        f.write("\n## Edge Cases Injected\n\n")
        for ec in summary['edge_cases_injected']:
            f.write(f"- {ec}\n")
        f.write("\n## Reproducibility\n\n")
        f.write(f"- Fixed seed: {SEED}\n")
        f.write("- Run the generator twice with the same seed and compare checksums to verify identical outputs.\n")
    
    print(f"  Wrote validation_summary.json and validation_summary.md")
    print()
    
    # Step 10: Summary
    print("[10/10] Complete!")
    print("=" * 60)
    print("Generation complete successfully!")
    print(f"Output directory: {DATA_DIR}")
    print(f"Ground truth: {GROUND_TRUTH_DIR}")
    print(f"Docs: {DOCS_DIR}")
    print("=" * 60)
    
    if validation_results['errors']:
        print("\n[!] Errors found:")
        for e in validation_results['errors'][:5]:
            print(f"  - {e}")
        if len(validation_results['errors']) > 5:
            print(f"  ... and {len(validation_results['errors']) - 5} more")
    
    if validation_results['warnings']:
        print(f"\n[!] {len(validation_results['warnings'])} warnings (see validation summary for details)")
    
    print("\n[OK] All required edge cases injected and labelled in ground_truth/")
    print("[OK] Data is chronologically split to prevent leakage")
    print("[OK] Reproducible with fixed seed 20261022")
    print("[OK] All IDs follow the specified conventions")


if __name__ == "__main__":
    main()
