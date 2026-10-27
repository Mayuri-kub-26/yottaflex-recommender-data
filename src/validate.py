"""Validation checks for data quality."""
import json
import hashlib
from typing import List, Dict, Any
from datetime import datetime

from config.settings import DATA_DIR, GROUND_TRUTH_DIR


class Validator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.checks_passed = 0
        self.checks_total = 0
    
    def check(self, condition: bool, msg: str, is_warning: bool = False):
        self.checks_total += 1
        if condition:
            self.checks_passed += 1
        else:
            if is_warning:
                self.warnings.append(msg)
            else:
                self.errors.append(msg)
    
    def validate_all(self, customers, categories, products, sessions, pageviews, 
                     carts, cart_lines, orders, order_lines, relations, recommendations, ground_truth) -> Dict[str, Any]:
        """Run all validation checks."""
        # PK uniqueness
        self._check_pk_uniqueness(customers, "customer_id", "Customer")
        self._check_pk_uniqueness(categories, "category_id", "Category")
        self._check_pk_uniqueness(products, "product_id", "Product")
        self._check_pk_uniqueness(sessions, "session_id", "Session")
        self._check_pk_uniqueness(pageviews, "event_id", "PageView")
        self._check_pk_uniqueness(carts, "cart_id", "Cart")
        self._check_pk_uniqueness(cart_lines, "cart_line_id", "CartLine")
        self._check_pk_uniqueness(orders, "order_id", "Order")
        self._check_pk_uniqueness(order_lines, "order_line_id", "OrderLine")
        self._check_pk_uniqueness(relations, "relation_id", "ProductRelation")
        self._check_pk_uniqueness(recommendations, "recommendation_id", "Recommendation")
        self._check_pk_uniqueness(ground_truth, "gt_id", "GroundTruth")
        
        # FK integrity
        cust_ids = set(c["customer_id"] for c in customers)
        cat_ids = set(c["category_id"] for c in categories)
        prod_ids = set(p["product_id"] for p in products)
        sess_ids = set(s["session_id"] for s in sessions)
        cart_ids = set(c["cart_id"] for c in carts)
        order_ids = set(o["order_id"] for o in orders)
        
        for s in sessions:
            self.check(s["customer_id"] in cust_ids, f"Session {s['session_id']} has invalid customer FK")
        for p in products:
            if p["category_id"] is not None:
                self.check(p["category_id"] in cat_ids, f"Product {p['product_id']} has invalid category FK", True)
        for pv in pageviews:
            self.check(pv["session_id"] in sess_ids, f"PageView {pv['event_id']} has invalid session FK")
            self.check(pv["customer_id"] in cust_ids, f"PageView {pv['event_id']} has invalid customer FK")
        for c in carts:
            self.check(c["customer_id"] in cust_ids, f"Cart {c['cart_id']} has invalid customer FK")
            if c["session_id"]:
                self.check(c["session_id"] in sess_ids, f"Cart {c['cart_id']} has invalid session FK", True)
        for cl in cart_lines:
            self.check(cl["cart_id"] in cart_ids, f"CartLine {cl['cart_line_id']} has invalid cart FK")
            self.check(cl["product_id"] in prod_ids, f"CartLine {cl['cart_line_id']} has invalid product FK")
        for o in orders:
            self.check(o["customer_id"] in cust_ids, f"Order {o['order_id']} has invalid customer FK")
            if o["cart_id"]:
                self.check(o["cart_id"] in cart_ids, f"Order {o['order_id']} has invalid cart FK", True)
            if o["session_id"]:
                self.check(o["session_id"] in sess_ids, f"Order {o['order_id']} has invalid session FK", True)
        for ol in order_lines:
            self.check(ol["order_id"] in order_ids, f"OrderLine {ol['order_line_id']} has invalid order FK")
            self.check(ol["product_id"] in prod_ids, f"OrderLine {ol['order_line_id']} has invalid product FK")
        for r in relations:
            self.check(r["product_id_a"] in prod_ids and r["product_id_b"] in prod_ids, 
                      f"ProductRelation {r['relation_id']} has invalid product FK")
        for rec in recommendations:
            self.check(rec["customer_id"] in cust_ids, f"Recommendation {rec['recommendation_id']} has invalid customer FK")
            self.check(rec["product_id"] in prod_ids, f"Recommendation {rec['recommendation_id']} has invalid product FK")
            if rec["session_id"]:
                self.check(rec["session_id"] in sess_ids, f"Recommendation {rec['recommendation_id']} has invalid session FK", True)
        
        # Arithmetic reconciliation
        # Cart totals
        cart_line_sums = {}
        for cl in cart_lines:
            if cl["cart_id"] not in cart_line_sums:
                cart_line_sums[cl["cart_id"]] = 0
            cart_line_sums[cl["cart_id"]] += cl["line_amount"]
        for c in carts:
            expected = round(cart_line_sums.get(c["cart_id"], 0), 2)
            actual = round(c["cart_total"], 2)
            self.check(abs(expected - actual) < 0.01, f"Cart {c['cart_id']} total mismatch: {actual} vs {expected}", True)
        
        # Order totals
        order_line_sums = {}
        for ol in order_lines:
            if ol["order_id"] not in order_line_sums:
                order_line_sums[ol["order_id"]] = 0
            order_line_sums[ol["order_id"]] += ol["line_amount"]
        for o in orders:
            expected = round(order_line_sums.get(o["order_id"], 0), 2)
            actual = round(o["order_total"], 2)
            self.check(abs(expected - actual) < 0.01, f"Order {o['order_id']} total mismatch: {actual} vs {expected}", True)
        
        # Line amount calculations
        for cl in cart_lines:
            expected = round(cl["quantity"] * cl["unit_price"], 2)
            self.check(abs(cl["line_amount"] - expected) < 0.01, f"CartLine {cl['cart_line_id']} line_amount incorrect", True)
        for ol in order_lines:
            expected = round(ol["quantity"] * ol["unit_price"], 2)
            self.check(abs(ol["line_amount"] - expected) < 0.01, f"OrderLine {ol['order_line_id']} line_amount incorrect", True)
        
        # Date ordering
        for s in sessions:
            self.check(s["session_end"] >= s["session_start"], f"Session {s['session_id']} end before start")
        
        return {
            "checks_total": self.checks_total,
            "checks_passed": self.checks_passed,
            "errors": self.errors,
            "warnings": self.warnings,
            "success": len(self.errors) == 0
        }
    
    def _check_pk_uniqueness(self, items, key, name):
        ids = [item[key] for item in items]
        unique_ids = set(ids)
        self.check(len(ids) == len(unique_ids), f"{name} has duplicate primary keys")
    
    def compute_file_checksums(self) -> Dict[str, str]:
        """Compute checksums for all data files."""
        checksums = {}
        import os
        for fname in sorted(os.listdir(DATA_DIR)):
            if fname.endswith(('.csv', '.json', '.sql')):
                fpath = DATA_DIR / fname
                hasher = hashlib.sha256()
                with open(fpath, 'rb') as f:
                    while chunk := f.read(65536):
                        hasher.update(chunk)
                checksums[fname] = hasher.hexdigest()
        for fname in sorted(os.listdir(GROUND_TRUTH_DIR)):
            if fname.endswith(('.csv', '.json')):
                fpath = GROUND_TRUTH_DIR / fname
                hasher = hashlib.sha256()
                with open(fpath, 'rb') as f:
                    while chunk := f.read(65536):
                        hasher.update(chunk)
                checksums[f'ground_truth/{fname}'] = hasher.hexdigest()
        return checksums
