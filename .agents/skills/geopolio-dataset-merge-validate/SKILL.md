---
name: geopolio-dataset-merge-validate
description: "Use when merging Geopolio datasets, removing duplicates, normalizing outputs, checking schema consistency, or deciding whether a combined dataset is ready for expansion or finetuning."
---

# Geopolio Dataset Merge and Validate

Use this skill when combining multiple Geopolio datasets or cleaning an intermediate file.

## When to Use

- Merging seed datasets into one file.
- Removing duplicate inputs before training.
- Checking that every row still matches the expected schema.
- Normalizing category labels or output JSON.
- Preparing a source file for expansion or rebalancing.

## Workflow

1. Load all candidate datasets.
2. Normalize the rows to one canonical schema.
3. Remove exact and near-exact duplicates.
4. Validate that every record still contains instruction, input, and output.
5. Check that the output JSON parses cleanly and includes all required fields.
6. Keep only the merged file that passes validation.

## Validation Checks

- `instruction` exists.
- `input` exists and is non-empty.
- `output` is valid JSON.
- `risk_score`, `region`, `category`, `impact`, and `analysis` are present.
- Category labels are canonical and consistent.
- Duplicate normalized inputs are removed.

## Decision Points

- If a row fails validation, drop it rather than silently preserving bad schema.
- If a category alias appears, map it to the canonical label before continuing.
- If duplicate content is found, deduplicate before any expansion or balancing step.

## Completion Criteria

The merged dataset is ready only when:

- the schema is consistent,
- the output parses cleanly,
- duplicates are removed,
- and the file is a clean source for later balancing or training.

## Useful Prompts

- Merge these Geopolio datasets and remove duplicates.
- Validate whether this dataset is safe to expand.
- Normalize the category labels in this combined file.
- Check whether the merged dataset still follows the expected schema.
