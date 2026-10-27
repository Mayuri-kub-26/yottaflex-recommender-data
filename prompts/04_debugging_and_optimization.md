# Performance Problem & Fix

## What went wrong

Ran the generator for the first time at full scale (500k sessions, 100k orders) and it completely froze at step 3. Left it running for 10 minutes and nothing printed. Killed it.

Started profiling manually by adding print statements to find where it stalled - it was definitely inside generate_carts_and_orders.

## Root cause I found myself

Looking at the code I noticed this pattern repeated in two places:

```python
cart_total = sum([cl["line_amount"] for cl in cart_lines if cl["cart_id"] == cart["cart_id"]])
```

This loops over ALL cart_lines for EVERY single cart. With 150k carts and 375k lines that's 56 billion iterations. No wonder it hung.

Same problem for order total calculation:
```python
order_total = sum([ol["line_amount"] for ol in order_lines if ol["order_id"] == order["order_id"]])
```

And a nested loop in generate_recommendations where it searched through all orders to find a customer_id for each order_line.

## How I fixed it

**Cart lines**: Track a running total while generating lines, don't scan afterwards.

**Order lines from cart**: Build a lookup dict `cart_lines_by_cart[cart_id] = [list of lines]` once, then O(1) lookup per order.

**Customer purchase lookup**: Build `order_to_customer = {order_id: customer_id}` dict upfront, then O(1) lookup per order_line instead of nested loop.

Asked AI to double-check my refactor didn't change the random seed sequence (since each call to random.choice() needs to happen in the same order to keep reproducibility). It confirmed the approach was safe as long as I kept the same generation order.

## After fix

Full run:  app 2.5 minutes
Validation: 10,995,557 checks passed, 0 errors

Also fixed a Windows-specific crash at the very end - the emoji characters (✅, ⚠️) were crashing on Windows cp1252 console encoding. Swapped to [OK] and [!] text tags and added sys.stdout.reconfigure(encoding='utf-8') at startup.

