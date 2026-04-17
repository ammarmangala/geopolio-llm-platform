# Dataset Workflow

This page explains which dataset to train on and how to keep the dataset pipeline safe as the project grows.

## Read this with the docs index

Start with [docs/README.md](../README.md) and [docs/guides/ARCHITECTURE.md](./ARCHITECTURE.md).

## Recommended training dataset

Use this file for training:

`data/geopolio_dataset_5000s_global_multidecade_balanced.json`

Why this file is the default:

- `5000` samples
- `5000` unique inputs
- `0` duplicates
- balanced categories
- balanced regions
- balanced risk scores

## Other dataset files

`data/geopolio_dataset_5000s_global_multidecade.json`

- first expanded dataset
- useful as an intermediate artifact
- not fully balanced

`data/geopolio_dataset_5000s_global_multidecade.checkpoint.json`

- generation checkpoint
- not a final training file

`data/geopolio_dataset_5000s_global_multidecade_balanced.json`

- final balanced training dataset
- use this for finetuning

## Scripts

`scripts/generation/expand_dataset_to_target.py`

- expands a source dataset locally to a target size
- does not require an API key
- writes a new output dataset and checkpoint

`scripts/generation/rebalance_dataset.py`

- normalizes category labels
- balances categories, regions, and risk scores
- writes a new balanced dataset

## Standard workflow

### 1. Expand the dataset

```powershell
py scripts\generation\expand_dataset_to_target.py --target-size 5000
```

Outputs:

- `data/geopolio_dataset_5000s_global_multidecade.json`
- `data/geopolio_dataset_5000s_global_multidecade.checkpoint.json`

### 2. Rebalance the dataset

```powershell
py scripts\generation\rebalance_dataset.py
```

Output:

- `data/geopolio_dataset_5000s_global_multidecade_balanced.json`

## What balanced means here

For `5000` samples:

- `12` categories cannot divide evenly, so each category should appear `416` or `417` times
- `18` regions cannot divide evenly, so each region should appear `277` or `278` times
- `10` risk scores divide evenly, so each score should appear exactly `500` times

If the final counts do not match that pattern, the dataset is not ready.

## Quick checks

### Count samples

```powershell
py -c "import json; d=json.load(open(r'data\geopolio_dataset_5000s_global_multidecade_balanced.json', encoding='utf-8')); print(len(d))"
```

### Check uniqueness

```powershell
py -c "import json; d=json.load(open(r'data\geopolio_dataset_5000s_global_multidecade_balanced.json', encoding='utf-8')); s=[x['input'].strip().lower() for x in d]; print(len(d), len(set(s)), len(d)-len(set(s)))"
```

Expected output:

```text
5000 5000 0
```

### Check balance

```powershell
py -c "import json, collections; d=json.load(open(r'data\geopolio_dataset_5000s_global_multidecade_balanced.json', encoding='utf-8')); inputs=[x['input'].strip().lower() for x in d]; outputs=[json.loads(x['output']) for x in d]; print('total =', len(d)); print('unique =', len(set(inputs))); print('duplicates =', len(d)-len(set(inputs))); print('categories =', dict(collections.Counter(o['category'] for o in outputs).most_common())); print('regions =', dict(collections.Counter(o['region'] for o in outputs).most_common())); print('risk_scores =', dict(collections.Counter(o['risk_score'] for o in outputs).most_common()))"
```

## If something looks wrong

- If `python` does not work, use `py`.
- If a notebook cannot find a file, resolve paths from the repository root.
- If the dataset is unbalanced, rerun `py scripts\generation\rebalance_dataset.py`.
- If duplicates exist, do not train on that file.

## Naming convention

Use this pattern for future files:

- expanded dataset: `geopolio_dataset_<SIZE>_global_multidecade.json`
- checkpoint: `geopolio_dataset_<SIZE>_global_multidecade.checkpoint.json`
- final training dataset: `geopolio_dataset_<SIZE>_global_multidecade_balanced.json`

## If the workflow grows

If this logic keeps expanding, split it by concern instead of adding more to one large file.

Good split points are:

- dataset constants and catalogs
- sample generation
- validation and normalization
- balancing and quotas
- CLI or script entrypoints
- tests for each rule set

That keeps the code easier to read, easier to test, and easier to change without breaking unrelated parts.

## Naming convention for future docs and features

Use names that describe the topic, not vague placeholders.

Good names:

- `DATASET_SPLITTING.md`
- `DATASET_GENERATION.md`
- `DATASET_BALANCING.md`
- `MODEL_EVALUATION.md`
- `FEATURE_NAME.md` only when the feature has a specific, stable name

Avoid names like:

- `future_feature.md`
- `notes.md`
- `misc.md`

If a topic gets bigger, put it in its own file or folder rather than making one generic document do everything.

## Summary

If you are unsure, use `data/geopolio_dataset_5000s_global_multidecade_balanced.json`.
