"""Inject the 4 required edge cases and generate ground truth."""
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

from config.settings import *
from src.ids import gen
from src.utils import set_seed, iso_format, random_datetime_in_range


def inject_edge_cases(customers: List[Dict[str, Any]], products: List[Dict[str, Any]],
                      sessions: List[Dict[str, Any]], orders: List[Dict[str, Any]],
                      order_lines: List[Dict[str, Any]], recommendations: List[Dict[str, Any]]) -> tuple:
    """Inject all 4 required edge cases and create ground truth."""
    ground_truth = []
    set_seed(SEED + 9)
    
    gt_count = 0
    
    # Edge case 1: Purchase appears before session view without a valid prior session
    if orders:
        # Modify an order to have no valid session/cart
        order = orders[0]
        original_session = order["session_id"]
        original_cart = order["cart_id"]
        order["session_id"] = None
        order["cart_id"] = None
        order["is_anomalous_edge1"] = True
        # Set order date before any session
        order["order_date"] = iso_format(datetime(2024, 12, 1, 10, 0, 0))
        order["created_at"] = order["order_date"]
        
        gt = {
            "gt_id": gen.ground_truth(),
            "issue_type": "purchase_without_prior_session",
            "entity_type": "Order",
            "entity_id": order["order_id"],
            "description": "Purchase appears before session view without a valid prior session",
            "expected_decision": "reject_or_flag",
            "ground_truth_label": "anomalous",
            "is_leakage_candidate": False,
            "created_at": iso_format(datetime.now())
        }
        ground_truth.append(gt)
        gt_count += 1
    
    # Edge case 2: Product category missing
    if products:
        # Find or create a product with missing category
        prod = None
        for p in products:
            if p["category_id"] is None:
                prod = p
                break
        if prod is None:
            prod = products[0]
            prod["category_id"] = None
        
        gt = {
            "gt_id": gen.ground_truth(),
            "issue_type": "product_category_missing",
            "entity_type": "Product",
            "entity_id": prod["product_id"],
            "description": "Product has no valid category assigned",
            "expected_decision": "exclude_or_require_category",
            "ground_truth_label": "missing_category",
            "is_leakage_candidate": False,
            "created_at": iso_format(datetime.now())
        }
        ground_truth.append(gt)
        gt_count += 1
    
    # Edge case 3: Test events leak into training
    if sessions:
        # Mark some test sessions as leaking into training
        session = sessions[10] if len(sessions) > 10 else sessions[0]
        session["is_test_candidate"] = True
        # Simulate leak by marking in context - we'll handle in split
        
        gt = {
            "gt_id": gen.ground_truth(),
            "issue_type": "test_events_leak_into_training",
            "entity_type": "Session",
            "entity_id": session["session_id"],
            "description": "Test events leak into training set (deliberate)",
            "expected_decision": "move_to_test_or_flag",
            "ground_truth_label": "leakage",
            "is_leakage_candidate": True,
            "created_at": iso_format(datetime.now())
        }
        ground_truth.append(gt)
        gt_count += 1
    
    # Edge case 4: Recommendation includes discontinued product
    if recommendations and products:
        # Find a discontinued product
        disc_prod = None
        for p in products:
            if p["status"] == "discontinued":
                disc_prod = p
                break
        if disc_prod is None:
            # Make one discontinued
            disc_prod = products[1]
            disc_prod["status"] = "discontinued"
        
        # Force a recommendation to include it as valid (violation)
        if recommendations:
            rec = recommendations[5] if len(recommendations) > 5 else recommendations[0]
            rec["product_id"] = disc_prod["product_id"]
            rec["is_valid"] = True  # Deliberate violation
            rec["excluded_reason"] = None
            rec["split"] = "train"  # put in train
            
            gt = {
                "gt_id": gen.ground_truth(),
                "issue_type": "recommendation_includes_discontinued_product",
                "entity_type": "Recommendation",
                "entity_id": rec["recommendation_id"],
                "description": "Recommendation includes discontinued product (violation of exclusion rule)",
                "expected_decision": "exclude",
                "ground_truth_label": "invalid_recommendation",
                "is_leakage_candidate": False,
                "created_at": iso_format(datetime.now())
            }
            ground_truth.append(gt)
            gt_count += 1
    
    return ground_truth
