# Geopolio Finetune Instructions

## Scope

These instructions apply to the full repository unless a more specific file-level instruction exists.

## Project Defaults

- Use `data/geopolio_dataset_5000s_global_multidecade_balanced.json` as the default training dataset.
- Treat `data/geopolio_dataset_5000s_global_multidecade.json` and checkpoint files as intermediate artifacts, not final training inputs.
- Prefer expanding and rebalancing data with the scripts in `scripts/generation/` instead of editing dataset files by hand.

## Dataset Quality Rules

- Before training or recommending a dataset, verify total sample count, uniqueness, and class balance.
- Do not train on a dataset that contains duplicate normalized inputs.
- Keep category labels canonical and consistent.
- Preserve the `instruction`, `input`, and JSON-encoded `output` schema for every sample.

## Notebook and Path Rules

- When writing notebook code, resolve paths from the repository root rather than assuming the notebook folder is the working directory.
- Keep notebook file paths portable across Windows and Colab-style environments.
- Use `py` in Windows command examples when a Python launcher is needed.

## Training Rules

- Keep checkpoint saving enabled during training.
- Prefer the best checkpoint by validation performance rather than the last step.
- Save both the final model and tokenizer after training.
- If validation loss rises while training loss falls, investigate overfitting before changing the model size or training duration.

## Editing Rules

- Keep changes minimal and focused.
- Do not overwrite source datasets when generating new variants; write new outputs.
- Keep intermediate files separate from final training artifacts.
