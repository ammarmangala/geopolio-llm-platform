---
name: geopolio-dataset-workflow
description: "Use when generating, expanding, rebalancing, validating, or selecting Geopolio finetuning datasets; checking duplicates, category balance, region balance, risk-score balance, or choosing the correct training file."
---

# Geopolio Dataset Workflow

Use this skill when working on the Geopolio fine-tuning pipeline in this repository.

## When to Use

- Expanding an existing dataset to a larger target size.
- Rebalancing a dataset before finetuning.
- Checking whether a dataset is safe to train on.
- Deciding which dataset file the notebook should load.
- Comparing a raw expanded dataset against the final balanced dataset.

## Core Rule

For finetuning, prefer the balanced dataset:

- `data/geopolio_dataset_5000s_global_multidecade_balanced.json`

Use the smaller or intermediate datasets only for experiments or debugging.

## Workflow

1. Expand the current dataset locally if a larger target is needed.
2. Rebalance the expanded dataset so categories, regions, and risk scores follow the target quotas.
3. Validate the final file for total size, uniqueness, and distribution.
4. Update notebook inputs only after the balanced dataset passes checks.
5. Keep checkpoint or intermediate files separate from the final training dataset.

## Validation Checks

Always verify all of the following before training:

- Total sample count matches the target size.
- Unique normalized inputs equal total samples.
- Duplicate count is zero.
- Categories are as evenly distributed as possible.
- Regions are as evenly distributed as possible.
- Risk scores are balanced exactly when the target size allows it.

For the current 5000-sample target, the expected pattern is:

- categories: 416 or 417 each
- regions: 277 or 278 each
- risk scores: exactly 500 each

## Decision Points

- If duplicates exist, do not train on the dataset.
- If category or region counts drift, rerun the rebalance script.
- If the notebook points at `2099s`, switch it to the balanced 5000-sample dataset for the final run.
- If a file is a checkpoint or intermediate output, keep it out of the training path.

## Useful Commands

Expand the dataset:

```powershell
py scripts\generation\expand_dataset_to_target.py --target-size 5000
```

Rebalance the dataset:

```powershell
py scripts\generation\rebalance_dataset.py
```

Check total sample count:

```powershell
py -c "import json; d=json.load(open(r'data\geopolio_dataset_5000s_global_multidecade_balanced.json', encoding='utf-8')); print(len(d))"
```

Check uniqueness:

```powershell
py -c "import json; d=json.load(open(r'data\geopolio_dataset_5000s_global_multidecade_balanced.json', encoding='utf-8')); s=[x['input'].strip().lower() for x in d]; print(len(d), len(set(s)), len(d)-len(set(s)))"
```

Run a full balance check:

```powershell
py -c "import json, collections; d=json.load(open(r'data\geopolio_dataset_5000s_global_multidecade_balanced.json', encoding='utf-8')); outputs=[json.loads(x['output']) for x in d]; print('total =', len(d)); print('unique =', len({x['input'].strip().lower() for x in d})); print('duplicates =', len(d)-len({x['input'].strip().lower() for x in d})); print('categories =', dict(collections.Counter(o['category'] for o in outputs).most_common())); print('regions =', dict(collections.Counter(o['region'] for o in outputs).most_common())); print('risk_scores =', dict(collections.Counter(o['risk_score'] for o in outputs).most_common()))"
```

## Completion Criteria

Consider the workflow complete only when:

- the target file exists,
- the dataset is unique,
- the distributions are acceptable,
- and the notebook or training script points at the balanced file.

## Example Prompts

- Create a Geopolio dataset skill for the expand, rebalance, and validation workflow.
- Check whether the current Geopolio training dataset is safe to finetune on.
- Update the notebook to use the balanced dataset and explain why.
- Validate the 5000-sample Geopolio dataset before training.
