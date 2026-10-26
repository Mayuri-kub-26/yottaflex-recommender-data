"""Configuration for YottaFlex synthetic data generator."""
import os
from pathlib import Path

# Project paths
ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
GROUND_TRUTH_DIR = ROOT / "ground_truth"
DOCS_DIR = ROOT / "docs"
PROMPTS_DIR = ROOT / "prompts"

# Ensure directories exist
for d in [DATA_DIR, GROUND_TRUTH_DIR, DOCS_DIR, PROMPTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Reproducibility
SEED = 20261022

# Volumes (as per requirements)
N_CUSTOMERS = 20000
N_PRODUCTS = 10000
N_SESSIONS = 500000
N_ORDERS = 100000

# Date ranges
SIGNUP_START = "2023-01-01"
SIGNUP_END = "2026-01-01"
DATA_START = "2025-01-01"
DATA_END = "2026-10-26"  # around now

# ID prefixes
PREFIX_CUS = "CUS"
PREFIX_CAT = "CAT"
PREFIX_SKU = "SKU"
PREFIX_SES = "SES"
PREFIX_EVT = "EVT"
PREFIX_CART = "CART"
PREFIX_CL = "CL"
PREFIX_ORD = "ORD"
PREFIX_OL = "OL"
PREFIX_PR = "PR"
PREFIX_REC = "REC"
PREFIX_GT = "GT"

# Enums
AGE_GROUPS = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
GENDERS = ["M", "F", "Other", "Unknown"]
REGIONS = ["North", "South", "East", "West", "Central"]
LOYALTY_TIERS = ["Bronze", "Silver", "Gold", "Platinum"]
DEVICE_TYPES = ["desktop", "mobile", "tablet"]
CHANNELS = ["organic", "paid", "direct", "email", "social"]
PAGE_TYPES = ["home", "category", "product", "search", "cart", "checkout"]
REFERRERS = ["none", "search", "ad", "email", "social", "internal"]
CART_STATUSES = ["open", "abandoned", "converted", "expired"]
ORDER_STATUSES = ["completed", "cancelled", "returned", "pending"]
PAYMENT_METHODS = ["card", "paypal", "applepay", "giftcard"]
PRODUCT_STATUSES = ["active", "discontinued", "out_of_stock"]
RELATION_TYPES = ["co_purchase", "same_category", "similar"]
REASON_TYPES = ["co_purchase", "same_category", "popular", "cold_start_fallback"]
EXCLUDED_REASONS = ["purchased", "discontinued", "out_of_stock", "unavailable", "test_leak_context"]
SPLITS = ["train", "test"]
ISSUE_TYPES = [
    "purchase_without_prior_session",
    "product_category_missing", 
    "test_events_leak_into_training",
    "recommendation_includes_discontinued_product"
]

# Export formats
EXPORT_CSV = True
EXPORT_JSON = True
EXPORT_SQL = True

# Feature flag for reproducibility runs
RUN_VALIDATION = True
GENERATE_CHECKSUMS = True
