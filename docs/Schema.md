# Schema Overview

This is a quick look at how the tables in the dataset fit together: what each one is, how they connect, and the rules they follow. For field-level details, see the Data Dictionary.

## The tables at a glance

| Table | What it is | Primary key | Notes |
| --- | --- | --- | --- |
| Customer | Shoppers | customer\_id (CUS-XXXXXX) | 20,000 customers. Includes some with very few sessions and some that look like bots. |
| Category | Product categories | category\_id (CAT-XXXX) | Can be nested under a parent category. Some are seasonal. |
| Product | The catalog | product\_id (SKU-XXXXXX) | 10,000 products. Includes new products with no history, plus discontinued and out-of-stock items. A few have no category on purpose, and those are labelled. |
| Session | A visit to the site | session\_id (SES-2026-XXXXXX) | 500,000 sessions. Includes some bot or noisy visits. |
| PageView | A page seen during a session | event\_id (EVT-session-XXX) | Full view history is kept for every session. |
| Cart | A shopping cart | cart\_id (CART-2026-XXXXXX) | Tied to a customer and usually a session. Status is open, abandoned, converted or expired. |
| CartLine | One product in a cart | cart\_line\_id (CL-XXXXXXXXX) | line\_amount is quantity times unit\_price. |
| Order | A finished purchase | order\_id (ORD-2026-XXXXXX) | 100,000 orders. A few have no earlier session or cart on purpose (edge case 1), and those are labelled. |
| OrderLine | One product in an order | order\_line\_id (OL-XXXXXXXXX) | Same math as CartLine. |
| ProductRelation | Two products linked together | relation\_id (PR-XXXXXXXXX) | The link can be bought together, same category, or similar. |
| Recommendation | Suggested products | recommendation\_id (REC-XXXXXXXXX) | Built with exclusion rules. Any rule that gets broken on purpose is labelled in the ground truth. |
| GroundTruth | The answer key | gt\_id (GT-XXXXXX) | Lists the four planned edge cases. It is never used as input. |

## How the tables connect

| Link | Type | In plain words |
| --- | --- | --- |
| Customer to Session | one to many | A customer can have many sessions. |
| Customer to Cart | one to many | A customer can have many carts. |
| Customer to Order | one to many | A customer can place many orders. |
| Session to PageView | one to many | A session is made up of many page views. |
| Session to Cart | one to zero or one | A session can have a cart, but doesn't have to. |
| Session to Order | one to zero or one | A session can end in an order, but doesn't have to. |
| Cart to CartLine | one to many | A cart holds many line items. |
| Cart to Order | one to zero or one | A cart can turn into one order. |
| Order to OrderLine | one to many | An order holds many line items. |
| Product to CartLine, OrderLine, PageView | one to many | A product can appear in many carts, orders and page views. |
| Product to Product (through ProductRelation) | many to many | Products can be related to many other products. |
| Customer, Session, Product to Recommendation | many to one | Many recommendations can point back to the same customer, session or product. |

## Bridge tables

- CartLine connects carts and products.
- OrderLine connects orders and products.
- ProductRelation connects products to other products.

## History is kept

- Page views, carts, orders and similar records are never overwritten. Changes show up through status fields and timestamps.
- Once an ID is assigned, it never changes.
- Ground truth stays in its own files and is never mixed into the input features.

## Main rules

- Every primary key is unique.
- Every foreign key points to a real row. The only exceptions are the deliberate empty values, and those are labelled in the ground truth.
- Totals are calculated from their parts, so a total always equals the sum of its line amounts.
- The train and test split follows time order, to avoid leakage. Any deliberate leakage is labelled.
- Recommendations should leave out items that were already purchased, discontinued or unavailable. Any deliberate violations are labelled.
- The same seed, 20261022, always gives the same data.
