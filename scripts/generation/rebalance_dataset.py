"""
Build a fully balanced Geopolio dataset from an existing source dataset.

Balanced here means:
- categories match their target quotas exactly
- regions match their target quotas exactly
- risk scores match their target quotas exactly

Because 5000 is not divisible by 12 categories or 18 regions, the target quotas
use the mathematically closest possible split, with a maximum difference of 1.
For risk scores 1-10, 5000 is divisible by 10, so the default target is exactly
500 samples per score.
"""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from pathlib import Path

from expand_dataset_to_target import (
    CATEGORIES,
    REGION_DETAILS,
    build_analysis,
    impact_from_score,
    load_json,
    save_json,
    validate_sample,
)


CATEGORY_ALIASES = {
    "Trade War": "Trade Disruption",
    "Trade Policy": "Trade Disruption",
    "Currency and Trade": "Financial Contagion",
    "Political Instability": "Political Fragmentation",
    "Geopolitical Realignment": "Alliance Cohesion",
}

REGION_TEMPLATES = [
    "In {year}, {actor} triggered a {category_lower} shock in {region}, forcing European investors to reassess regional exposure {modifier}.",
    "During {year}, {actor} intensified a {category_lower} event across {region}, creating fresh market uncertainty for European portfolios {modifier}.",
    "In {year}, {actor} escalated a {category_lower} scenario in {region}, increasing risk for Europe-linked sectors and indices {modifier}.",
    "During {year}, {actor} pushed a {category_lower} dispute in {region}, causing European investors to revisit sector allocations {modifier}.",
]

YEAR_BUCKETS = [2003, 2006, 2008, 2011, 2014, 2016, 2019, 2021, 2023, 2024]
SCENARIO_MODIFIERS = [
    "after emergency cabinet talks",
    "after sanctions negotiations broke down",
    "after insurers repriced regional risk",
    "after trade officials failed to reach a compromise",
    "after security warnings disrupted investor sentiment",
    "after cross-border tensions hit logistics planning",
    "after commodity buyers started panic procurement",
    "after several European firms issued exposure warnings",
    "after transport operators cut guidance",
    "after policymakers warned of second-round market effects",
]

CATEGORY_CHANNELS = {
    "Energy Security": "higher fuel, power, and transport costs across Europe",
    "Regional Conflict": "sanctions risk, transport disruption, and a confidence shock",
    "Financial Contagion": "spread widening, bank exposure, and eurozone risk repricing",
    "Trade Disruption": "delays, freight inflation, and inventory shortages",
    "Resource Security": "scarcity in European industrial and energy supply chains",
    "Political Fragmentation": "policy uncertainty and weaker investor confidence",
    "Cyber Warfare": "operational outages, payment disruption, and digital trust erosion",
    "Nuclear Proliferation": "energy market stress, sanctions escalation, and defense repricing",
    "Alliance Cohesion": "higher security uncertainty and slower coordinated response",
    "Resource Nationalism": "margin compression and weaker legal certainty for multinationals",
    "Migration and Border Security": "political pressure, labor disruption, and fiscal strain",
    "Technology Governance": "costlier compliance and slower technology supply chains",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a fully balanced Geopolio dataset.")
    parser.add_argument(
        "--source",
        default="data/geopolio_dataset_5000s_global_multidecade.json",
        help="Source dataset used for normalization and sample reuse.",
    )
    parser.add_argument(
        "--output",
        default="data/geopolio_dataset_5000s_global_multidecade_balanced.json",
        help="Balanced output dataset.",
    )
    parser.add_argument(
        "--target-size",
        type=int,
        default=5000,
        help="Final dataset size.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for deterministic balancing.",
    )
    return parser.parse_args()


def quota_map(items: list, total: int) -> dict:
    base, remainder = divmod(total, len(items))
    return {
        item: base + (1 if index < remainder else 0)
        for index, item in enumerate(items)
    }


def canonical_category(category: str) -> str | None:
    if category in CATEGORIES:
        return category
    return CATEGORY_ALIASES.get(category)


def deduplicate_exact(samples: list[dict]) -> list[dict]:
    seen: set[str] = set()
    unique: list[dict] = []
    for sample in samples:
        key = sample["input"].strip().lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(sample)
    return unique


def normalize_sample(sample: dict) -> dict | None:
    if not validate_sample(sample):
        return None

    output = json.loads(sample["output"])
    category = canonical_category(output["category"])
    region = output["region"]
    risk_score = output["risk_score"]

    if category is None or region not in REGION_DETAILS or not 1 <= risk_score <= 10:
        return None

    output["category"] = category
    output["impact"] = impact_from_score(risk_score)

    normalized = dict(sample)
    normalized["output"] = json.dumps(output, ensure_ascii=False)
    return normalized


def score_targets(total: int) -> dict[int, int]:
    return quota_map(list(range(1, 11)), total)


def generate_assignment_plan(target_size: int) -> list[tuple[str, str, int]]:
    category_remaining = Counter(quota_map(CATEGORIES, target_size))
    region_remaining = Counter(quota_map(list(REGION_DETAILS), target_size))
    score_remaining = Counter(score_targets(target_size))

    assignments: list[tuple[str, str, int]] = []
    for _ in range(target_size):
        category = max(
            [item for item in CATEGORIES if category_remaining[item] > 0],
            key=lambda item: (category_remaining[item], random.random()),
        )
        region = max(
            [item for item in REGION_DETAILS if region_remaining[item] > 0],
            key=lambda item: (region_remaining[item], random.random()),
        )
        score = max(
            [item for item in range(1, 11) if score_remaining[item] > 0],
            key=lambda item: (score_remaining[item], random.random()),
        )

        assignments.append((category, region, score))
        category_remaining[category] -= 1
        region_remaining[region] -= 1
        score_remaining[score] -= 1

    return assignments


def sample_signature(sample: dict) -> tuple[str, str, int]:
    output = json.loads(sample["output"])
    return output["category"], output["region"], output["risk_score"]


def build_pool(samples: list[dict]) -> dict[tuple[str, str, int], list[dict]]:
    pool: dict[tuple[str, str, int], list[dict]] = {}
    for sample in samples:
        signature = sample_signature(sample)
        pool.setdefault(signature, []).append(sample)
    for items in pool.values():
        random.shuffle(items)
    return pool


def generate_new_sample(category: str, region: str, score: int, variant: int) -> dict:
    details = REGION_DETAILS[region]
    scenario = random.choice(REGION_TEMPLATES).format(
        year=random.choice(YEAR_BUCKETS),
        actor=random.choice(details["actors"]),
        category_lower=category.lower(),
        region=region,
        modifier=f"{random.choice(SCENARIO_MODIFIERS)}, case variant {variant}",
    )
    output = {
        "risk_score": score,
        "region": region,
        "category": category,
        "impact": impact_from_score(score),
        "analysis": build_analysis(region, category, score, CATEGORY_CHANNELS[category]),
    }
    return {
        "instruction": "Analyze the geopolitical risk of the following situation for European retail investors.",
        "input": scenario,
        "output": json.dumps(output, ensure_ascii=False),
    }


def build_balanced_dataset(source_samples: list[dict], target_size: int) -> list[dict]:
    plan = generate_assignment_plan(target_size)
    pool = build_pool(source_samples)
    result: list[dict] = []
    used_inputs: set[str] = set()
    variant = 1

    for category, region, score in plan:
        key = (category, region, score)
        chosen = None

        while pool.get(key):
            candidate = pool[key].pop()
            normalized_input = candidate["input"].strip().lower()
            if normalized_input in used_inputs:
                continue
            chosen = candidate
            break

        if chosen is None:
            for _ in range(50):
                candidate = generate_new_sample(category, region, score, variant)
                variant += 1
                normalized_input = candidate["input"].strip().lower()
                if normalized_input in used_inputs:
                    continue
                chosen = candidate
                break

        if chosen is None:
            raise RuntimeError(f"Could not generate unique sample for {(category, region, score)}")

        result.append(chosen)
        used_inputs.add(chosen["input"].strip().lower())

    balanced = deduplicate_exact(result)
    if len(balanced) == target_size:
        return balanced

    missing = target_size - len(balanced)
    variant = 100000
    while len(balanced) < target_size:
        category, region, score = plan[len(balanced)]
        chosen = None
        for _ in range(100):
            candidate = generate_new_sample(category, region, score, variant)
            variant += 1
            normalized_input = candidate["input"].strip().lower()
            if normalized_input in used_inputs:
                continue
            chosen = candidate
            break
        if chosen is None:
            raise RuntimeError(f"Could not restore missing unique samples: missing {missing}")
        balanced.append(chosen)
        used_inputs.add(chosen["input"].strip().lower())

    return balanced


def report(samples: list[dict]) -> dict[str, dict]:
    categories = Counter()
    regions = Counter()
    scores = Counter()
    for sample in samples:
        output = json.loads(sample["output"])
        categories[output["category"]] += 1
        regions[output["region"]] += 1
        scores[output["risk_score"]] += 1
    return {
        "categories": dict(categories),
        "regions": dict(regions),
        "risk_scores": dict(scores),
    }


def main() -> None:
    args = parse_args()
    random.seed(args.seed)

    source = Path(args.source)
    output = Path(args.output)

    raw_samples = load_json(source)
    normalized = []
    for sample in deduplicate_exact(raw_samples):
        fixed = normalize_sample(sample)
        if fixed is not None:
            normalized.append(fixed)

    balanced = build_balanced_dataset(normalized, args.target_size)
    save_json(output, balanced)
    print(f"Wrote {len(balanced)} balanced samples to {output}")
    print(json.dumps(report(balanced), indent=2))


if __name__ == "__main__":
    main()
