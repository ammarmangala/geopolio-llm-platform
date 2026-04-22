# Finetuning Notes

This guide explains the notebook-based finetuning flow in plain language.

## Read this with the docs index

Start with [docs/README.md](../README.md) and [docs/guides/ARCHITECTURE.md](./ARCHITECTURE.md).

## What finetuning means here

You are training a base model on Geopolio examples.
Each sample becomes a text block like this:

```text
### Instruction:
...

### Input:
...

### Response:
...
```

The trainer learns the relationship between the instruction, the input, and the target response.

## Dataset used by the notebook

The notebook should use:

`data/geopolio_dataset_5000s_global_multidecade_balanced.json`

The notebook currently splits the dataset into:

- `train_dataset`
- `eval_dataset`

with a deterministic split:

```python
split = dataset.train_test_split(test_size = 0.1, seed = 42)
train_dataset = split["train"]
eval_dataset = split["test"]
```

That means:

- `90%` of the data is used for training
- `10%` is held out for evaluation

## Training settings

The current training configuration uses:

```python
SFTConfig(
    output_dir = "./output",
    num_train_epochs = 5,
    per_device_train_batch_size = 2,
    gradient_accumulation_steps = 4,
    learning_rate = 2e-4,
    warmup_steps = 80,
    lr_scheduler_type = "cosine",
    logging_steps = 50,
    eval_strategy = "steps",
    eval_steps = 200,
    save_strategy = "steps",
    save_steps = 200,
    save_total_limit = 2,
    load_best_model_at_end = True,
    metric_for_best_model = "eval_loss",
    greater_is_better = False,
    fp16 = False,
    optim = "adamw_8bit",
    seed = 42,
    packing = False,
    padding_free = False,
)
```

## What the main settings do

- `num_train_epochs = 5`: the model sees the training data five times
- `per_device_train_batch_size = 2`: small batch size for limited GPU memory
- `gradient_accumulation_steps = 4`: simulates a larger batch size
- `learning_rate = 2e-4`: controls how fast the model updates
- `warmup_steps = 80`: ramps up training gently at the start
- `lr_scheduler_type = "cosine"`: gradually lowers the learning rate
- `eval_steps = 200`: runs evaluation during training
- `save_steps = 200`: saves checkpoints during training
- `save_total_limit = 2`: keeps storage under control
- `load_best_model_at_end = True`: restores the best checkpoint at the end

## How to read loss

Do not focus on one number alone.
Look for these patterns instead:

- `train_loss` falling and `eval_loss` falling: good sign
- `train_loss` falling and `eval_loss` rising: possible overfitting
- both losses staying high: the model is probably underfitting

The best checkpoint is usually the one with the lowest `eval_loss`, not the last one.

## Why checkpoints matter

If Colab or another notebook runtime resets, anything not saved is lost.
That is why the notebook should keep checkpoints enabled and save a final model directory.

The final model should include both:

- model weights
- tokenizer files

## Hugging Face export

When the notebook pushes the model to Hugging Face, it should read the token from the `HF_TOKEN` environment variable.
Do not hardcode access tokens in the notebook.

If `HF_TOKEN` is missing, the login step should be skipped instead of failing the whole notebook.

## Basic notebook workflow

1. Load model and tokenizer.
2. Load the balanced dataset.
3. Split into train and eval sets.
4. Train with checkpoints enabled.
5. Keep the best checkpoint.
6. Save the final model and tokenizer.

## Common mistakes

- using the wrong dataset file
- training without a validation split
- saving only the last checkpoint
- reading only `train_loss`
- letting notebook paths depend on the notebook folder instead of the repo root

## If you are unsure

Use the balanced dataset, keep checkpoints on, and compare `train_loss` with `eval_loss` before choosing a final model.
