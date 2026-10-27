# Schema Design Notes

## What I was thinking

Started by mapping out all the entities on paper first. The problem statement mentioned customer, product, session, cart, order and recommendation — but I knew I also needed category and the line-item bridge tables (CartLine, OrderLine) to keep things normalized.

The tricky part was figuring out where ProductRelation sits. It's a self-referential many-to-many on Product, so I needed a bridge table there too, not just a column on Product.

## Questions I asked AI

Asked Claude to help me decide:
- Should PageView be its own table or just embedded in Session?
- How should I handle the EVT id format — is `EVT-SES-2026-000001-001` readable enough?
- Is it better to store cart_total as a derived column or calculate it on the fly?

AI suggested keeping PageView as its own table (event sourcing pattern — never overwrite history), and deriving totals from line items rather than storing them independently so they don't drift out of sync.

## Decisions I made

- Kept PageView separate — each row is an immutable event
- IDs are zero-padded counters: CUS-000001, SKU-000001, SES-2026-000001
- cart_total and order_total are always computed from their child line amounts
- ProductRelation is a bridge table with relation_type enum

## Rough cardinality I sketched

Customer 1 → N Session
Session 1 → N PageView
Session 1 → 0/1 Cart
Cart 1 → N CartLine
Cart 1 → 0/1 Order
Order 1 → N OrderLine
Product N ↔ N Product (via ProductRelation)

