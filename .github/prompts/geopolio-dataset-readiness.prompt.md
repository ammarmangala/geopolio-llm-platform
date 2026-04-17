---
description: "Use when validating a Geopolio dataset before training."
name: "Geopolio Dataset Readiness"
agent: "agent"
argument-hint: "Dataset path or description"
---
Validate the dataset for finetuning readiness.

Default target: `data/geopolio_dataset_5000s_global_multidecade_balanced.json`.

Use [README.md](README.md), [docs/DATASET_WORKFLOW.md](docs/DATASET_WORKFLOW.md), and [docs/FINETUNING_NOTES.md](docs/FINETUNING_NOTES.md).

Check sample count, normalized input uniqueness, schema validity, canonical categories, balance, and whether the file is final or intermediate.

If a path is provided, inspect that file. Otherwise inspect the default target.

Return:
1. Verdict: `ready` or `not ready`
2. Key findings: short bullets
3. Failed checks: short bullets, or `none`
4. Next step: one concrete action

If not ready, name the failed rule and the next script or file to use.