# YottaFlex AI Candidate Project
## Synthetic Data Generator for E-Commerce Recommendation Systems

> **Note on Dataset Generation:**  
> The raw generated dataset files (under `data/`, ~1.8 GB in total) are excluded from this Git repository via `.gitignore` to comply with GitHub's 100 MB file size restrictions.  
>  
> To generate the full dataset locally, run:
> ```bash
> python run.py
> ```
> This executes in ~2.5 minutes and produces all CSV, JSON, and SQL files in `data/`, matching the deterministic validation checksums in `docs/validation_summary.json` with fixed seed `20261022`. The ground truth anomalies (`ground_truth/`) and validation summaries remain committed.



## 1. Project Overview

This project focuses on building a synthetic data generator for an e-commerce recommendation system. It creates realistic, interconnected datasets that can be used to develop, test, and evaluate product recommendation algorithms.

In a real e-commerce platform, recommendation systems use customer activity, browsing history, shopping carts, purchase records, and product information to suggest relevant products. However, working with real customer data can introduce privacy concerns and make testing difficult.

To address this, this project generates entirely synthetic data that represents common e-commerce activities while preserving the relationships between customers, products, sessions, carts, orders, and recommendations.

The generator also includes data quality issues and edge cases to test how a recommendation system handles unusual situations. It applies business rules, prevents temporal data leakage, maintains traceability across datasets, and validates the generated data before exporting it.

**The main goal is to create a reliable, reproducible, and easy-to-understand dataset that can support the development and testing of recommendation systems.**

---

## 2. Project Objectives

The main objectives of this project are:

- Generate realistic synthetic e-commerce data without using real customer information.
- Create all required entities with consistent identifiers and relationships.
- Maintain referential integrity across the generated datasets.
- Apply recommendation rules to exclude unsuitable products.
- Prevent temporal data leakage through chronological train/test splitting.
- Introduce and label four specific edge cases for testing and validation.
- Ensure that the generated data can be reproduced using a fixed random seed.
- Validate data quality, relationships, business rules, and output consistency.
- Export the generated datasets in CSV, JSON, and SQL formats.
- Maintain separate ground-truth files for documenting intentionally introduced anomalies.

---

## 3. What Does This Project Generate?

The generator creates the main datasets required to represent an e-commerce recommendation environment.

These datasets cover the customer journey, from browsing products to adding items to carts, completing purchases, and receiving recommendations.

| Entity | Default Count | Description |
|---|---:|---|
| Customer | 20,000 | Customer profiles, demographics, loyalty tiers, and behavioral markers |
| Category | Approximately 14 | Product categories with hierarchy and seasonal information |
| Product | 10,000 | Product catalog containing prices, availability, status, and cold-start indicators |
| Session | 500,000 | Customer browsing sessions with device, channel, and bot information |
| PageView | 5 million or more | Product and page-view events recorded during sessions |
| Cart | Approximately 150,000 | Shopping carts with lifecycle and status information |
| CartLine | 400,000 or more | Individual products added to shopping carts |
| Order | 100,000 | Order records representing customer purchases and other order statuses |
| OrderLine | 250,000 or more | Individual products included in orders |
| ProductRelation | 50,000 or more | Relationships between products, including co-purchase and category-based relationships |
| Recommendation | 400,000 or more | Product recommendations generated under defined business rules |

These counts represent the default configuration. Actual volumes may vary depending on the generator's settings and the number of records created by dependent generation steps.

---

## 4. Technology Stack

The project is designed to be lightweight and easy to run.

- **Programming Language:** Python
- **Minimum Python Version:** Python 3.7
- **Dependencies:** Python standard library only
- **Output Formats:** CSV, JSON, and SQL
- **Configuration:** Centralized settings and a fixed random seed

No external Python packages are required for the default implementation.

---

## 5. Getting Started

Follow these steps to set up and run the project locally.

### Prerequisites

Make sure Python 3.7 or a compatible newer version is installed on your system.

To check your Python version, run:

```bash
python --version
```

### Step 1: Navigate to the Project Directory

Open a terminal and move to the project directory:

```bash
cd yottaflex-recommender-data
```

### Step 2: Run the Generator

Execute the main Python script:

```bash
python run.py
```

The generator uses the default configuration and random seed `20261022`.

### Step 3: Review the Generated Files

After execution, check the following directories:

- `data/` — Contains the generated datasets.
- `ground_truth/` — Contains labels and details for intentionally introduced edge cases.
- `docs/` — Contains the data dictionary, schema documentation, and validation reports.

The generator is intended to create the datasets, validate them, and export the results as part of a single workflow.

---

## 6. How the Generator Works

The generation process follows a structured sequence to maintain consistency between entities.

### Step 1: Generate Master Data

The generator creates the foundational entities first:

- Customers
- Categories
- Products

These entities provide the information needed to create the remaining datasets.

### Step 2: Generate Customer Sessions and Events

Customer sessions are created with relevant attributes such as device type, traffic channel, session timestamps, and bot indicators.

Page-view events are then associated with their respective sessions to represent customer browsing activity.

### Step 3: Generate Carts and Orders

The generator creates shopping carts, cart lines, orders, and order lines.

Relationships between these records are maintained using consistent identifiers. Derived values, such as order totals, are calculated from the associated line items rather than assigned independently.

### Step 4: Generate Product Relationships and Recommendations

Product relationships are generated to represent associations between products.

Recommendations are then created using the available customer, product, and purchase information. The recommendation logic applies the defined exclusion rules to avoid suggesting products that should not be recommended.

### Step 5: Inject the Required Edge Cases

Four specific edge cases are deliberately introduced to test data quality and recommendation-system behavior.

Each injected case is recorded in the separate ground-truth dataset.

### Step 6: Perform the Train/Test Split

The data is divided chronologically into training and testing sets using session start times.

The intended split is:

- **Training data:** 80%
- **Testing data:** 20%

The split is designed to ensure that training data does not contain events that occur after the training cutoff.

### Step 7: Validate and Export the Data

The generator checks data integrity and the defined business constraints before producing the final outputs.

The datasets are exported to CSV, JSON, and SQL formats, with validation results and checksums recorded in the documentation directory.

---

## 7. Entity ID Conventions

Consistent identifiers make it easier to connect records across datasets and trace data throughout the generation process.

The project follows the following ID conventions:

| Entity | ID Format | Example |
|---|---|---|
| Customer | `CUS-XXXXXX` | `CUS-000001` |
| Category | `CAT-XXXX` | `CAT-0001` |
| Product | `SKU-XXXXXX` | `SKU-000001` |
| Session | `SES-2026-XXXXXX` | `SES-2026-000001` |
| PageView | `EVT-<session-id>-XXX` | `EVT-SES-2026-000001-001` |
| Cart | `CART-2026-XXXXXX` | `CART-2026-000001` |
| CartLine | `CL-XXXXXXXXX` | `CL-000000001` |
| Order | `ORD-2026-XXXXXX` | `ORD-2026-000001` |
| OrderLine | `OL-XXXXXXXXX` | `OL-000000001` |
| ProductRelation | `PR-XXXXXXXXX` | `PR-000000001` |
| Recommendation | `REC-XXXXXXXXX` | `REC-000000001` |
| Ground Truth | `GT-XXXXXX` | `GT-000001` |

These conventions provide a consistent way to identify records and maintain relationships between entities.

---

## 8. Data Quality and Integrity

Data quality is an important part of this project because recommendation systems depend on accurate and consistent information.

The generator incorporates several checks and design principles to support reliable datasets.

### Referential Integrity

Relationships between entities are maintained using their identifiers.

For example:

- A session references the customer associated with it.
- A page-view event references its session.
- A cart line references its cart and product.
- An order line references its order and product.
- A recommendation references the relevant customer and recommended product.

Foreign-key relationships are validated, with any intentionally introduced exceptions documented in the ground-truth dataset.

### Derived Values

Values that depend on other records are calculated from their underlying data.

For example, order totals are calculated using the corresponding order lines instead of being generated independently.

This helps maintain consistency between transaction records and their details.

### History Preservation

Historical events are retained rather than overwritten.

Preserving event history makes it possible to analyze customer behavior over time and supports chronological dataset splitting.

### Lifecycle Tracking

Carts and orders include status information to represent different stages of the shopping process.

This makes the generated data more useful for testing workflows that depend on cart and order states.

### Validation Reports

The generator produces validation reports to summarize the results of data quality checks.

These reports are intended to help identify inconsistencies, review generated data volumes, and verify reproducibility.

---

## 9. Recommendation Business Rules

The recommendation generator follows defined exclusion rules to avoid suggesting products that are unsuitable for a customer.

### 9.1 Exclude Previously Purchased Products

Products already purchased by a customer are excluded from that customer's recommendations.

This rule helps prevent recommendations from including items that the customer has already bought.

The purchase history used for this decision should be limited to information available at the recommendation timestamp to avoid temporal leakage.

### 9.2 Exclude Discontinued Products

Products marked as discontinued must not appear in valid recommendations.

This ensures that recommendations do not include products that are no longer part of the active catalog.

### 9.3 Exclude Out-of-Stock Products

Products that are unavailable or out of stock must be excluded from valid recommendations.

This helps ensure that the recommendation output respects product availability.

### 9.4 Label Deliberate Violations

The project intentionally introduces a recommendation containing a discontinued product as one of its required edge cases.

This violation is documented in the ground-truth dataset so that it can be identified during testing.

**Important:** The deliberately injected violation is a test case, not an exception to the normal recommendation rules. Valid recommendations should continue to follow all exclusion rules.

---

## 10. Required Edge Cases

The project includes four deliberately introduced edge cases to evaluate how well the data pipeline handles unusual or invalid situations.

These cases are recorded in:

- `ground_truth/ground_truth.csv`
- `ground_truth/ground_truth.json`

The ground-truth files are maintained separately from the main datasets.

### Edge Case 1: Purchase Without a Prior Session

**Label:** `purchase_without_prior_session`

This case represents an order that exists without a valid preceding customer session or associated cart.

It tests whether the system can identify purchases that do not have the expected browsing or cart history.

The case also helps evaluate how the pipeline handles incomplete customer journeys without silently creating misleading relationships.

### Edge Case 2: Product Missing a Category

**Label:** `product_category_missing`

This case represents a product that does not have an assigned category.

It tests whether the system can handle missing product metadata without failing or incorrectly assigning a category.

The missing category is intentional and should be identifiable through the ground-truth record.

### Edge Case 3: Test Events Leaking Into Training Data

**Label:** `test_events_leak_into_training`

This case deliberately introduces test events into the training dataset.

It is designed to test whether the validation process can identify temporal data leakage.

The affected records should be labelled in the ground-truth dataset so that the issue can be detected and evaluated.

**Important:** This is an intentionally invalid test case. The normal train/test splitting process should prevent test events from entering the training dataset.

### Edge Case 4: Recommendation Includes a Discontinued Product

**Label:** `recommendation_includes_discontinued_product`

This case represents a recommendation that includes a discontinued product.

It tests whether the validation process can detect recommendations that violate product-status restrictions.

The invalid recommendation is intentionally introduced and labelled, while the normal recommendation-generation logic should continue to exclude discontinued products.

### Purpose of Edge-Case Injection

These cases help evaluate the generator's ability to represent and identify data quality problems.

Keeping them labelled and separate from normal input features makes it easier to test validation logic without confusing deliberate anomalies with valid records.

---

## 11. Train/Test Split and Data Leakage Prevention

A recommendation system should be evaluated using data that was not available when its training data was created.

To support this, the project uses a chronological split based on session start times.

### Split Configuration

| Dataset | Target Proportion | Purpose |
|---|---:|---|
| Training | 80% | Used to develop and train recommendation models |
| Testing | 20% | Used to evaluate model performance on later activity |

### Why Use a Chronological Split?

A random split can allow future events to influence training data, producing an unrealistic evaluation.

A chronological split better represents a real-world scenario in which a recommendation system learns from historical activity and predicts future behavior.

### Leakage Prevention

The intended split ensures that sessions assigned to the training period occur before sessions assigned to the testing period.

To maintain this separation:

- Use session timestamps to determine the chronological boundary.
- Ensure test-period events are not used as training features.
- Avoid using future purchases when generating recommendations for earlier timestamps.
- Keep ground-truth labels separate from model input features.
- Validate the temporal ordering of training and testing records.

The deliberately injected leakage case is retained only as a labelled test scenario for evaluating the validation process.

**Note:** A chronological session split alone does not guarantee complete leakage prevention. Feature construction, customer purchase history, product relationships, and recommendation generation must also respect the relevant cutoff timestamps.

---

## 12. Reproducibility

Reproducibility is important because it allows the generated data and validation results to be checked consistently across multiple runs.

The project uses a fixed random seed:

```python
SEED = 20261022
```

The seed is configured in the project's settings and is used to control random data generation.

### Reproducibility Features

- A fixed random seed.
- Deterministic ID generation.
- Consistent generation settings.
- Validation reports containing dataset information and checksums.
- A documented procedure for comparing outputs across runs.

When the same code, seed, configuration, and execution environment are used, the generator is intended to produce identical outputs.

For full reproducibility, all sources of randomness must use the configured seed, and record ordering, timestamps, serialization, and file generation must remain deterministic.

### How to Test Reproducibility

Run the generator for the first time:

```bash
python run.py
```

Save the checksums recorded in the validation report.

Next, remove the previously generated output files.

On Linux or macOS:

```bash
rm -rf data/* ground_truth/* docs/validation_summary.*
```

On Windows PowerShell:

```powershell
Remove-Item data/* -Force
Remove-Item ground_truth/* -Force
Remove-Item docs/validation_summary.* -Force
```

Run the generator again:

```bash
python run.py
```

Compare the checksums from both runs.

Matching checksums indicate that the compared files are identical. If the checksums differ, investigate the source of randomness, record ordering, timestamps, configuration, or serialization differences.

**Note:** The cleanup commands remove generated files from the specified directories. Back up any files you want to retain before running them.

---

## 13. Generated Output

The generator organizes its outputs into separate directories so that the datasets, validation results, and documentation remain easy to locate.

### `data/`

This directory contains the main generated datasets.

The data is exported in the supported formats:

- CSV
- JSON
- SQL

These files represent the normal synthetic e-commerce entities and their relationships, along with any intentionally injected test records required by the implementation.

### `ground_truth/`

This directory contains the ground-truth records for the four required edge cases.

Expected files:

```text
ground_truth/
├── ground_truth.csv
└── ground_truth.json
```

These records identify the injected anomalies and help evaluate whether the validation logic detects them correctly.

The ground-truth data must remain separate from model input features to avoid giving the model direct access to anomaly labels.

### `docs/`

This directory contains the project's documentation and validation reports.

Expected files include:

```text
docs/
├── data_dictionary.md
├── schema.md
├── validation_summary.json
└── validation_summary.md
```

The data dictionary explains the fields and constraints for each entity.

The schema document describes the relationships between entities.

The validation summaries report dataset volumes, validation results, and checksums.

### `source_manifest.md`

This file documents the origin of the generated data and confirms that the project uses synthetic data rather than real customer records or external datasets.

---

## 14. Project Structure

The project is organized into modules to keep data generation, validation, configuration, and export logic separate.

```text
yottaflex-recommender-data/
│
├── README.md
├── requirements.txt
├── run.py
├── source_manifest.md
│
├── config/
│   └── settings.py
│
├── src/
│   ├── ids.py
│   ├── utils.py
│   ├── generate_masters.py
│   ├── generate_sessions.py
│   ├── generate_carts_orders.py
│   ├── generate_relations_recommend.py
│   ├── inject_edges.py
│   ├── split.py
│   ├── validate.py
│   └── export.py
│
├── data/
│   └── Generated datasets
│
├── ground_truth/
│   └── Labelled edge cases
│
├── docs/
│   ├── data_dictionary.md
│   ├── schema.md
│   ├── validation_summary.json
│   └── validation_summary.md
│
└── prompts/
    └── AI prompt history
```

### Module Responsibilities

| File or Module | Responsibility |
|---|---|
| `run.py` | Coordinates the complete generation workflow |
| `config/settings.py` | Stores the random seed, entity volumes, and generation settings |
| `src/ids.py` | Generates identifiers according to the required ID conventions |
| `src/utils.py` | Provides shared helper functions |
| `src/generate_masters.py` | Generates customers, categories, and products |
| `src/generate_sessions.py` | Generates sessions and page-view events |
| `src/generate_carts_orders.py` | Generates carts, cart lines, orders, and order lines |
| `src/generate_relations_recommend.py` | Generates product relationships and recommendations |
| `src/inject_edges.py` | Introduces and labels the required edge cases |
| `src/split.py` | Performs the chronological train/test split |
| `src/validate.py` | Checks data integrity and business constraints |
| `src/export.py` | Exports datasets and validation artifacts |
| `data/` | Stores the generated datasets |
| `ground_truth/` | Stores labelled anomalies separately |
| `docs/` | Stores schema documentation and validation reports |
| `prompts/` | Maintains AI prompt history, as required by the project workflow |

The exact files produced by the implementation should match the actual contents of the repository.

---

## 15. Assumptions and Design Decisions

The generator follows these assumptions:

1. **Synthetic data only:** All customer, product, session, cart, order, and recommendation records are generated artificially.
2. **No external datasets:** No real customer records or external datasets are used.
3. **Currency:** All product prices and monetary values are expressed in USD.
4. **Session year:** Session, cart, and order identifiers use the year `2026`, following the specified ID conventions.
5. **Chronological split:** The intended training/testing proportions are 80% and 20%, based on session start times.
6. **Order statuses:** Most orders represent completed purchases, while other statuses may be included to represent different transaction states.
7. **Cold-start products:** Approximately 10% of products are marked as cold-start products.
8. **Sparse customers:** Approximately 15% of customers are marked as sparse users.
9. **Bot activity:** Approximately 1–2% of sessions are marked as bot or noisy sessions.
10. **Ground-truth separation:** Ground-truth labels are maintained separately and must not be used as model input features.
11. **Business-rule enforcement:** Valid recommendations exclude previously purchased, discontinued, and out-of-stock products.
12. **Intentional anomalies:** The four required edge cases are deliberately introduced and labelled for testing.

These assumptions provide a consistent foundation for generating and validating the synthetic datasets.

---

## 16. Validation Checklist

The following checklist summarizes the main conditions that should be verified after generation.

### Data Integrity

- [ ] All generated entities follow the required ID formats.
- [ ] IDs are unique within their respective entities.
- [ ] Foreign-key relationships are valid.
- [ ] Intentional missing relationships are documented in ground truth.
- [ ] Order totals match the corresponding order-line calculations.
- [ ] Cart and order statuses follow the defined lifecycle rules.
- [ ] Generated timestamps are valid and consistent.

### Recommendation Rules

- [ ] Previously purchased products are excluded from valid recommendations.
- [ ] Discontinued products are excluded from valid recommendations.
- [ ] Out-of-stock products are excluded from valid recommendations.
- [ ] Recommendation decisions use only information available at the relevant timestamp.
- [ ] The intentionally invalid recommendation is labelled in ground truth.

### Train/Test Split

- [ ] Training and testing data follow the configured chronological split.
- [ ] Test-period events do not appear in the normal training dataset.
- [ ] The deliberately injected leakage case is labelled.
- [ ] Ground-truth labels are not included as model input features.

### Edge Cases

- [ ] A purchase without a prior valid session or cart is represented.
- [ ] A product with a missing category is represented.
- [ ] A test event leaking into training is represented.
- [ ] A recommendation containing a discontinued product is represented.
- [ ] All four cases have corresponding ground-truth records.

### Reproducibility and Export

- [ ] The generator uses the configured random seed.
- [ ] CSV, JSON, and SQL exports are generated.
- [ ] Validation summaries are produced.
- [ ] Checksums are recorded.
- [ ] Repeated runs produce matching outputs under the same conditions.

This checklist describes the expected validation coverage. The validation report should confirm which checks actually passed during execution.

---

## 17. Documentation

The project includes supporting documentation to explain how the data is structured and how its quality is evaluated.

| File | Purpose |
|---|---|
| `README.md` | Project overview, setup instructions, workflow, and assumptions |
| `docs/data_dictionary.md` | Field definitions, data types, constraints, and validation rules |
| `docs/schema.md` | Entity relationships, cardinality, and bridge tables |
| `docs/validation_summary.json` | Machine-readable validation results, volumes, and checksums |
| `docs/validation_summary.md` | Human-readable validation summary |
| `source_manifest.md` | Data provenance and confirmation that the records are synthetic |
| `prompts/` | AI prompt history maintained for the project workflow |

These documents make the project easier to understand, review, test, and maintain.

---

## 18. Limitations

Although the generator is designed to represent realistic e-commerce activity, the generated data is synthetic and does not fully capture the complexity of a real production environment.

Some limitations include:

- Customer behavior is simulated rather than collected from actual shoppers.
- Product relationships may not reflect real market demand.
- Synthetic browsing and purchasing patterns may differ from real customer behavior.
- Generated data volumes and distributions depend on the configured generation rules.
- The usefulness of the datasets for recommendation models depends on the quality of the implemented generation logic.
- Passing structural validation does not automatically guarantee that the generated data is statistically representative of real e-commerce activity.

The dataset is primarily intended for development, testing, data-quality validation, and experimentation with recommendation systems.

---

## 19. Future Improvements

The project can be extended in several ways as the recommendation use case becomes more advanced.

Potential improvements include:

- Configurable dataset sizes through command-line arguments.
- More detailed customer behavior patterns.
- Additional product attributes and inventory changes over time.
- More sophisticated co-purchase and product-similarity relationships.
- Automated tests for every business rule and edge case.
- More detailed temporal leakage detection.
- Performance improvements for large data volumes.
- Statistical reports showing customer activity and product distributions.
- Additional validation for recommendation relevance and diversity.
- Automated comparison of output checksums across repeated runs.

These improvements can help make the generator more flexible and useful for different recommendation-system experiments.

---

## 20. Conclusion

The YottaFlex AI Candidate Project provides a structured way to generate synthetic e-commerce data for developing and testing product recommendation systems.

It brings together customer activity, product catalogs, sessions, carts, orders, product relationships, and recommendations while maintaining consistent identifiers and relationships.

The project also focuses on important practical concerns, including recommendation exclusions, chronological data splitting, reproducibility, data validation, and the handling of intentionally introduced edge cases.

By keeping the generated datasets, ground-truth labels, and documentation organized separately, the project provides a clear foundation for testing recommendation workflows and identifying data quality issues.

**The overall objective is to produce synthetic data that is consistent, traceable, reproducible, and useful for evaluating recommendation-system pipelines.**

---

## 21. License and Data Usage

This project generates synthetic data for development, testing, and evaluation purposes.

No real customer data or external datasets are used, according to the project's stated assumptions.

Any licensing requirements or restrictions should be documented separately if the project is distributed or used beyond the candidate evaluation.

---

**Project:** YottaFlex AI Candidate Project  
**Purpose:** Synthetic e-commerce data generation for recommendation systems  
**Default Random Seed:** `20261022`  
**Default Currency:** USD  
**Output Formats:** CSV, JSON, and SQL