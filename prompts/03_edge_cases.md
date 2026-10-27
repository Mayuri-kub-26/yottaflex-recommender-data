# Edge Cases & Ground Truth

## The 4 required edge cases

The spec was explicit — inject these four and label them:

1. Purchase without prior session
2. Product with missing category
3. Test event leaking into training
4. Recommendation includes discontinued product

My first thought was to just randomly corrupt some rows. AI pointed out that's the wrong approach — better to inject them deliberately and surgically into specific rows so they're traceable.

## How I structured inject_edges.py

Each edge case modifies one specific row and creates a corresponding entry in ground_truth with:
- issue_type (the enum from the spec)
- entity_type + entity_id (so evaluators can look it up)
- expected_decision (what a good pipeline should do with it)
- ground_truth_label

## Key design question

I asked AI: "Should the ground truth be a separate table or a flag column on the existing tables?"

Answer was a separate file, always. Mixing it into the main tables risks it being used as a feature. Ground truth is the answer key — it should never touch the training data pipeline.

## What ground_truth/ contains

- ground_truth.csv / ground_truth.json
- 4 rows, one per edge case
- GT-000001 through GT-000004

## Note on edge case 1 (purchase without session)

I set the order date to 2024-12-01 — before any session in the dataset (which starts 2025-01-01). That makes it clearly anomalous by timestamp comparison alone.

## Note on edge case 4 (discontinued recommendation)

Injected by finding a discontinued product and forcing rec index 5 to point at it with `is_valid=True`. The violation is the is_valid=True flag — a correct pipeline should catch that.

