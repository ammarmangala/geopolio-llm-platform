---
description: "Use when auditing Geopolio notebook paths or dataset references."
name: "Geopolio Notebook Path Audit"
agent: "agent"
argument-hint: "Notebook path, cell, or path issue"
---
Audit notebook paths and dataset references.

Use [README.md](README.md), [docs/DATASET_WORKFLOW.md](docs/DATASET_WORKFLOW.md), and [docs/FINETUNING_NOTES.md](docs/FINETUNING_NOTES.md).

Focus on [notebooks/geopolio_finetune.ipynb](notebooks/geopolio_finetune.ipynb) and check repo-root path handling, Windows/Colab portability, balanced-dataset defaulting, accidental use of intermediate or checkpoint files, and clean source/output separation.

If a cell or path is provided, inspect that first.

Return:
1. Verdict: `portable`, `needs changes`, or `blocked`
2. Path issues found: short bullets
3. Recommended fixes: short bullets
4. Next step: one concrete file or cell to update

Stay focused on path safety and dataset selection.