---
description: "Use when planning Geopolio dataset expansion or rebalancing."
name: "Geopolio Dataset Expansion and Rebalance"
agent: "agent"
argument-hint: "Source dataset, target size, or balance issue"
---
Plan the next dataset step.

Use [README.md](README.md), [docs/DATASET_WORKFLOW.md](docs/DATASET_WORKFLOW.md), and [docs/FINETUNING_NOTES.md](docs/FINETUNING_NOTES.md).

Default source: `data/geopolio_dataset_2099s_global_multidecade.json`.
Default target: `data/geopolio_dataset_5000s_global_multidecade_balanced.json`.

Choose one: `expansion only`, `rebalance only`, `expansion then rebalance`, or `no action`.

Check whether the source is final or intermediate, whether normalized duplicates exist, whether labels need cleanup, and whether the notebook should point at the balanced file.

Return:
1. Recommendation: one of the four actions above
2. Why: short repo-based explanation
3. Next step: one concrete command or file change
4. Validation: one short check

Prefer new output files over overwriting source data.