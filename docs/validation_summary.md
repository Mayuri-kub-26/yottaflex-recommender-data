# Validation Summary

**Generated:** 2026-10-27T21:26:43.401510  
**Seed:** 20261022  

## Volumes

- Customers: 20,000
- Categories: 14
- Products: 10,000
- Sessions: 449,382
- Pageviews: 3,718,472
- Carts: 134,934
- Cart Lines: 337,303
- Orders: 100,000
- Order Lines: 220,517
- Product Relations: 50,281
- Recommendations: 80,001
- Ground Truth: 4

## Train/Test Split (Chronological)

- Train Sessions: 359,505
- Test Sessions: 89,877

## Validation Results

- Checks Passed: 10995557/10995557
- Errors: 0
- Warnings: 0

## Edge Cases Injected

- purchase_without_prior_session
- product_category_missing
- test_events_leak_into_training
- recommendation_includes_discontinued_product

## Reproducibility

- Fixed seed: 20261022
- Run the generator twice with the same seed and compare checksums to verify identical outputs.
