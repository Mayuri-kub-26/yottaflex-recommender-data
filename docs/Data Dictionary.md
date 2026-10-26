# Data Dictionary: E-commerce Dataset

This document lists every table in the dataset, what each field means, and the rules the data has to follow. The data is synthetic, so nothing here comes from real customers.

Generator seed: 20261022. Running the generator again with this seed gives the same row counts and checksums.

ID formats used across the dataset:

| Item | Format | Example |
| --- | --- | --- |
| Customer | CUS- plus 6 digits | CUS-000001 |
| Category | CAT- plus 4 digits | CAT-0001 |
| Product | SKU- plus 6 digits | SKU-000001 |
| Session | SES-2026- plus 6 digits | SES-2026-000001 |
| Page view event | EVT- plus the session ID, then a dash and 3 digits | EVT-SES-2026-000001-001 |
| Cart | CART-2026- plus 6 digits | CART-2026-000001 |
| Cart line | CL- plus 9 digits | CL-000000001 |
| Order | ORD-2026- plus 6 digits | ORD-2026-000001 |
| Order line | OL- plus 9 digits | OL-000000001 |
| Product relation | PR- plus 9 digits | PR-000000001 |
| Recommendation | REC- plus 9 digits | REC-000000001 |
| Ground truth entry | GT- plus 6 digits | GT-000001 |

All numbers are zero-padded so IDs line up the same way in every file.

---

## 1. Customer

A person who shops on the site. Customers are created first because almost everything else points back to them.

One customer can have many sessions, carts and orders.

| Field | Type | Required | What it holds and the rules |
| --- | --- | --- | --- |
| customer\_id | string, primary key | Yes | Format CUS-000001. Must be unique and never changes. |
| signup\_date | date | Yes | Between 2023-01-01 and 2026-01-01. |
| age\_group | enum | Yes | 18-24, 25-34, 35-44, 45-54, 55-64 or 65+ |
| gender | enum | Yes | M, F, Other or Unknown |
| region | enum | Yes | North, South, East, West or Central |
| loyalty\_tier | enum | Yes | Bronze, Silver, Gold or Platinum |
| is\_sparse | boolean | Yes | True for customers with very few sessions. |
| is\_bot\_flag\_candidate | boolean | Yes | True if the customer behaves like a bot or is otherwise noisy. These rows are flagged, not deleted. |
| created\_at | datetime | Yes | Cannot be earlier than the start of signup\_date. |

---

## 2. Category

Product categories. They can be nested, so a category may sit under a parent category.

One category can have many products.

| Field | Type | Required | What it holds and the rules |
| --- | --- | --- | --- |
| category\_id | string, primary key | Yes | Format CAT-0001. Unique. |
| parent\_category\_id | string, foreign key to Category | No | Empty for top-level categories. Otherwise it must point to a real category, and a category can never be its own parent or form a loop. |
| category\_name | string | Yes | Readable name, not blank, no extra spaces at the ends. |
| is\_seasonal | boolean | Yes | True for seasonal categories. |
| is\_active | boolean | Yes | False if the category is switched off. |
| created\_at | datetime | Yes | Must be a valid datetime. |

---

## 3. Product

The product catalog.

One product can show up in many cart lines, order lines and page views. Products also link to each other through the ProductRelation table.

| Field | Type | Required | What it holds and the rules |
| --- | --- | --- | --- |
| product\_id | string, primary key | Yes | Format SKU-000001. Unique and never changes. |
| category\_id | string, foreign key to Category | No | Normally a real category. A few products are deliberately left empty to test missing categories, and each one is recorded in the ground truth. |
| product\_name | string | Yes | Not blank. |
| brand | string | Yes | Not blank. |
| price | decimal | Yes | Above 0, two decimal places, roughly between 1.00 and 2000.00. |
| currency | enum | Yes | Always USD. |
| status | enum | Yes | active, discontinued or out\_of\_stock |
| is\_cold\_start | boolean | Yes | True for products with little or no history. |
| launch\_date | date | Yes | Must be a valid date. |
| created\_at | datetime | Yes | Must be a valid datetime. |

---

## 4. Session

One visit to the site by a customer. Page views belong to a session.

One session can have many page views, at most one cart, and at most one order.

| Field | Type | Required | What it holds and the rules |
| --- | --- | --- | --- |
| session\_id | string, primary key | Yes | Format SES-2026-000001. Unique. |
| customer\_id | string, foreign key to Customer | Yes | Must be an existing customer. |
| session\_start | datetime | Yes | Must be a valid datetime. |
| session\_end | datetime | Yes | Cannot be earlier than session\_start. |
| device\_type | enum | Yes | desktop, mobile or tablet |
| channel | enum | Yes | organic, paid, direct, email or social |
| is\_bot | boolean | Yes | True for bot or noisy sessions. |
| is\_test\_candidate | boolean | Yes | True for sessions used to create the deliberate test-leak cases. These are recorded in the ground truth. |
| created\_at | datetime | Yes | Must be a valid datetime. |

---

## 5. PageView

Each page a customer looks at during a session. The full history is kept and nothing is overwritten.

| Field | Type | Required | What it holds and the rules |
| --- | --- | --- | --- |
| event\_id | string, primary key | Yes | Format EVT-SES-2026-000001-001. The session part has to match the session\_id on the same row. |
| session\_id | string, foreign key to Session | Yes | Must be an existing session. |
| customer\_id | string, foreign key to Customer | Yes | Must be an existing customer. It repeats the session's customer so checks are easier. |
| product\_id | string, foreign key to Product | No | Empty for pages that are not about a product. Otherwise it must be a real product. |
| page\_type | enum | Yes | home, category, product, search, cart or checkout |
| view\_time | datetime | Yes | Should fall between session\_start and session\_end. |
| referrer | enum | Yes | none, search, ad, email, social or internal |
| created\_at | datetime | Yes | Must be a valid datetime. |

---

## 6. Cart

A shopping cart and where it currently stands.

One cart has many cart lines and can lead to at most one order.

| Field | Type | Required | What it holds and the rules |
| --- | --- | --- | --- |
| cart\_id | string, primary key | Yes | Format CART-2026-000001. Unique. |
| session\_id | string, foreign key to Session | No | Empty if the cart is not tied to a session. Otherwise it must be a real session. |
| customer\_id | string, foreign key to Customer | Yes | Must be an existing customer. |
| cart\_status | enum | Yes | open, abandoned, converted or expired |
| created\_at | datetime | Yes | Must be a valid datetime. |
| updated\_at | datetime | Yes | Cannot be earlier than created\_at. |
| cart\_total | decimal | Yes | 0.00 or more. Must equal the sum of line\_amount across the cart's lines. |

---

## 7. CartLine

One product inside a cart.

| Field | Type | Required | What it holds and the rules |
| --- | --- | --- | --- |
| cart\_line\_id | string, primary key | Yes | Format CL-000000001. Unique. |
| cart\_id | string, foreign key to Cart | Yes | Must be an existing cart. |
| product\_id | string, foreign key to Product | Yes | Must be an existing product. |
| quantity | integer | Yes | 1 or more. |
| unit\_price | decimal | Yes | Above 0. It is the product's price when the item was added, so it should stay consistent with that price. |
| line\_amount | decimal | Yes | Must equal quantity times unit\_price exactly. |
| added\_at | datetime | Yes | Should fall within the cart's or session's time range where possible. |
| created\_at | datetime | Yes | Must be a valid datetime. |

A product should appear only once per cart, so the pair (cart\_id, product\_id) should be unique unless there is a good reason for a repeat.

---

## 8. Order

A finished purchase. Order history is kept, never overwritten.

One order has many order lines.

| Field | Type | Required | What it holds and the rules |
| --- | --- | --- | --- |
| order\_id | string, primary key | Yes | Format ORD-2026-000001. Unique. |
| cart\_id | string, foreign key to Cart | No | Empty or real. Some orders are deliberately created with no valid earlier cart or session (edge case 1). Each is recorded in the ground truth. |
| session\_id | string, foreign key to Session | No | Empty or real. |
| customer\_id | string, foreign key to Customer | Yes | Must be an existing customer. |
| order\_status | enum | Yes | completed, cancelled, returned or pending |
| order\_date | datetime | Yes | Must be a valid datetime. In edge case 1 it can come before any session activity. |
| currency | enum | Yes | Always USD. |
| order\_total | decimal | Yes | 0.00 or more. Must equal the sum of line\_amount across the order's lines. |
| payment\_method | enum | Yes | card, paypal, applepay or giftcard |
| created\_at | datetime | Yes | Must be a valid datetime. |
| is\_anomalous\_edge1 | boolean | Yes | True when the purchase shows up before any session view and has no valid earlier session. Recorded in the ground truth. |

---

## 9. OrderLine

One product inside an order.

| Field | Type | Required | What it holds and the rules |
| --- | --- | --- | --- |
| order\_line\_id | string, primary key | Yes | Format OL-000000001. Unique. |
| order\_id | string, foreign key to Order | Yes | Must be an existing order. |
| product\_id | string, foreign key to Product | Yes | Must be an existing product. |
| quantity | integer | Yes | 1 or more. |
| unit\_price | decimal | Yes | Above 0. It is the price at the time of purchase. |
| line\_amount | decimal | Yes | Must equal quantity times unit\_price exactly. |
| created\_at | datetime | Yes | Must be a valid datetime. |

---

## 10. ProductRelation

Links two products that are connected in some way, such as bought together or in the same category. It works as a bridge table because many products can relate to many other products.

| Field | Type | Required | What it holds and the rules |
| --- | --- | --- | --- |
| relation\_id | string, primary key | Yes | Format PR-000000001. Unique. |
| product\_id\_a | string, foreign key to Product | Yes | Must be an existing product and cannot match product\_id\_b. |
| product\_id\_b | string, foreign key to Product | Yes | Must be an existing product and cannot match product\_id\_a. |
| relation\_type | enum | Yes | co\_purchase, same\_category or similar |
| score | float | Yes | Between 0 and 1. A higher number means a stronger link. |
| source | enum | Yes | Always generated. |
| created\_at | datetime | Yes | Must be a valid datetime. |

A product cannot be related to itself, and each combination of (product\_id\_a, product\_id\_b, relation\_type) should appear only once.

---

## 11. Recommendation

Products suggested to a customer, along with any reason a suggestion was excluded. This is kept separate from the ground truth.

Recommendations are linked to a customer, and optionally to a session and a product.

| Field | Type | Required | What it holds and the rules |
| --- | --- | --- | --- |
| recommendation\_id | string, primary key | Yes | Format REC-000000001. Unique. |
| session\_id | string, foreign key to Session | No | Empty or an existing session. |
| customer\_id | string, foreign key to Customer | Yes | Must be an existing customer. |
| product\_id | string, foreign key to Product | Yes | The product being recommended. Must exist. |
| recommended\_for\_product\_id | string, foreign key to Product | No | The product the customer was looking at, if there was one. |
| score | float | Yes | Between 0 and 1. |
| rank | integer | Yes | Position in the list, starting at 1. |
| reason | enum | Yes | co\_purchase, same\_category, popular or cold\_start\_fallback |
| excluded\_reason | enum | No | purchased, discontinued, out\_of\_stock, unavailable or test\_leak\_context. Filled in when the item was excluded or the reason matters. |
| is\_valid | boolean | Yes | True only if the recommendation passes every exclusion rule. It must be false in the deliberate case where a discontinued product is recommended, and that case is recorded in the ground truth. |
| split | enum | Yes | train or test, based on a split by time. |
| created\_at | datetime | Yes | Must be a valid datetime. |

Recommendations should leave out items the customer already bought, and items that are discontinued or unavailable.

---

## Ground Truth

Every known problem in the data is listed in the ground truth files, saved as `ground_truth/ground_truth.csv` and/or `ground_truth/ground_truth.json`. These files are only for checking results. They must never be used as input features.

| Field | Type | Required | What it holds and the rules |
| --- | --- | --- | --- |
| gt\_id | string, primary key | Yes | Format GT-000001. Unique. |
| issue\_type | enum | Yes | One of the four planned edge cases: purchase\_without\_prior\_session, product\_category\_missing, test\_events\_leak\_into\_training, recommendation\_includes\_discontinued\_product |
| entity\_type | enum | Yes | The table affected: Customer, Product, Session, PageView, Cart, CartLine, Order, OrderLine, ProductRelation or Recommendation |
| entity\_id | string | Yes | The ID of the affected row. It must exist in that table. |
| description | string | Yes | A short plain explanation of what is wrong. |
| expected\_decision | string | Yes | What should happen with this row, for example true, false, exclude or reject. |
| ground\_truth\_label | string | Yes | The label used when evaluating results. |
| is\_leakage\_candidate | boolean | Yes | True if the issue is related to data leakage. |
| created\_at | datetime | Yes | Must be a valid datetime. |

---

## Validation Checklist

These checks should pass on the generated data.

- Primary keys: every primary key is unique within its table.
- Foreign keys: every foreign key points to a row that exists. The only exceptions are the empty values allowed above, and those are labelled.
- Enums: every enum field uses one of its allowed values.
- Date order: session\_end is not before session\_start, updated\_at is not before created\_at, and view\_time sits inside the session. Only the edge case 1 orders may break the order\_date rule, and they are labelled.
- Math: line\_amount equals quantity times unit\_price in cart lines and order lines. cart\_total equals the sum of its cart lines. order\_total equals the sum of its order lines.
- Cart status: a cart moves through open, abandoned, converted and expired in a way that makes sense.
- Duplicates: no repeated IDs, no repeated product within a cart, and no repeated order lines.
- Time split: train and test are split by time. Test events should not leak into training, except in the deliberate leakage cases, which are labelled.
- Exclusions: recommendations leave out purchased, discontinued and unavailable items. The one deliberate violation is labelled.
- Reproducibility: the same seed (20261022) gives the same row counts and checksums every time.
- Traceability: IDs match across all files and use the same zero-padded format.
