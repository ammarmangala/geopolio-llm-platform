---
description: "Use when reviewing a Geopolio finetuning run or checkpoint."
name: "Geopolio Finetuning Review"
agent: "agent"
argument-hint: "Notebook cell, run logs, checkpoint, or model output"
---

Review a Geopolio finetuning run.

Use [README.md](README.md), [docs/DATASET_WORKFLOW.md](docs/DATASET_WORKFLOW.md), and [docs/FINETUNING_NOTES.md](docs/FINETUNING_NOTES.md).

Focus on [notebooks/geopolio_finetune.ipynb](notebooks/geopolio_finetune.ipynb) and check balanced dataset usage, repo-root paths, checkpoint saving, `load_best_model_at_end`, best checkpoint selection by `eval_loss`, final model/tokenizer saving, and train/eval loss behavior.

If logs, checkpoints, or outputs are provided, use them.

Return:

1. Verdict: `healthy`, `needs attention`, or `blocked`
2. What looks good: short bullets
3. Concerns: short bullets, or `none`
4. Next step: one concrete action
