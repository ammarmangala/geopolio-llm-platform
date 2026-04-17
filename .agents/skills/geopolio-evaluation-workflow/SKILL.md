---
name: geopolio-evaluation-workflow
description: "Use when comparing Geopolio models, running benchmark scripts, reviewing generated answers, or deciding whether a finetuned model is better than a previous checkpoint or base model."
---

# Geopolio Evaluation Workflow

Use this skill when validating model quality after finetuning or generation changes.

## When to Use

- Comparing a finetuned model with a base model.
- Reviewing benchmark outputs or test prompts.
- Checking whether a checkpoint is actually better.
- Creating a repeatable eval checklist for model runs.

## Evaluation Goals

Focus on practical quality, not just one metric.

- Correct geopolitical category.
- Correct region assignment.
- Sensible risk score and impact.
- Concise but informative analysis.
- Stable behavior across similar prompts.

## Workflow

1. Pick a fixed prompt set that covers easy, medium, and hard cases.
2. Run the same prompts against each candidate model.
3. Compare outputs side by side.
4. Check for category drift, region drift, and overconfident scores.
5. Note failures that are systematic rather than one-off.
6. Prefer the model that is most consistent on the prompt set, not just the most verbose.

## Decision Points

- If the model is numerically better but gives worse category or region labels, it is not the better model.
- If outputs are unstable across repeated prompts, treat the model as unreliable even if the summary metrics look acceptable.
- If the model is overfitting to the training style, add harder prompts to the eval set before approving it.

## What to Record

- Dataset used for evaluation.
- Base model and candidate model names.
- Prompt set or benchmark used.
- Common failure modes.
- Chosen winner and why.

## Useful Prompts

- Build a Geopolio evaluation checklist for model comparisons.
- Compare these two model outputs and identify the better one.
- Create a small benchmark set that covers the main geopolitical categories.
- Summarize the weakest failure modes in this finetuned model.
