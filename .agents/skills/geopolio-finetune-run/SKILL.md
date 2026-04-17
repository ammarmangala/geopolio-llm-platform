---
name: geopolio-finetune-run
description: "Use when running or adjusting the Geopolio finetuning notebook; loading the dataset, creating train/eval splits, interpreting loss, resuming from checkpoints, or saving the final model and tokenizer."
---

# Geopolio Finetune Run

Use this skill when you are training or updating the notebook-based finetuning flow.

## When to Use

- Running the finetuning notebook end to end.
- Changing the training dataset used by the notebook.
- Adjusting hyperparameters for a new run.
- Recovering from a runtime reset or interrupted session.
- Deciding which checkpoint or final model to keep.

## Core Rule

Treat the balanced dataset as the default training source:

- `data/geopolio_dataset_5000s_global_multidecade_balanced.json`

Use the smaller dataset only when you want a faster diagnostic run.

## Workflow

1. Load the model and tokenizer.
2. Load the chosen dataset from the repository root or a notebook-safe relative path.
3. Create a deterministic train/eval split.
4. Train with checkpoints enabled.
5. Compare `train_loss` and `eval_loss` during training.
6. Keep the best checkpoint, not just the last one.
7. Save both the model and tokenizer to the final output directory.

## Decision Points

- If the notebook kernel reset, restore from the latest checkpoint before starting over.
- If `eval_loss` improves while `train_loss` falls, continue and keep the best checkpoint.
- If `train_loss` falls but `eval_loss` rises, stop changing the data first; overfitting is more likely than a trainer bug.
- If the notebook still points at `2099s`, switch it to the balanced 5000-sample dataset for the final run.

## Checks Before Calling a Run Complete

- The dataset path is correct.
- The split is reproducible.
- Checkpoints were written during training.
- The best model was loaded or selected.
- The final model directory contains both weights and tokenizer files.

## Useful Prompts

- Update the finetuning notebook to use the balanced 5000-sample dataset.
- Explain whether this training curve suggests overfitting or underfitting.
- Recover the notebook workflow after a Colab reset.
- Reduce the training run to a faster diagnostic configuration.
