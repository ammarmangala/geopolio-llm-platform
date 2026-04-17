"""
Geopolio Dataset Generator
Generates a balanced geopolitical risk dataset via OpenAI API.
Target: 5000 samples across all categories, regions, and decades.
"""

import json
import time
import random
import os
from openai import OpenAI

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
API_KEY = os.environ.get("OPENAI_API_KEY", "sk-jouw-key-hier")
TARGET = 5000
BATCH_SIZE = 50
OUTPUT_FILE = "geopolio_dataset_5000s_multidecade.json"
CHECKPOINT_FILE = "checkpoint.json"
MODEL = "gpt-5.4-mini"  # goedkoop en snel, vervang door gpt-4o voor hogere kwaliteit

client = OpenAI(api_key=API_KEY)

# ─────────────────────────────────────────
# DISTRIBUTION TABLES
# ─────────────────────────────────────────
CATEGORIES = [
    "Energy Security",
    "Regional Conflict",
    "Financial Contagion",
    "Trade Disruption",
    "Resource Security",
    "Political Fragmentation",
    "Cyber Warfare",
    "Nuclear Proliferation",
    "Alliance Cohesion",
    "Resource Nationalism",
    "Migration and Border Security",
    "Technology Governance",
]

REGIONS = [
    "Europe", "Middle East", "East Asia", "Southeast Asia",
    "Central Asia", "Latin America", "Sub-Saharan Africa",
    "North Africa", "West Africa", "Transatlantic", "Arctic",
    "Eastern Europe", "Northern Europe", "South Asia",
    "Western Balkans", "Central Africa", "East Africa", "Space",
]

DECADES = [
    ("2000-2010", [
        "9/11 economic aftermath and War on Terror impact on markets",
        "2003 Iraq War and oil price shock",
        "2004-2007 EU enlargement with Poland and Baltic states",
        "2006 Russia-Ukraine gas dispute",
        "2007 Estonia cyberattack by Russia",
        "2007-2008 Global financial crisis and Lehman Brothers",
        "2008 Russia-Georgia war over South Ossetia",
        "2005 Hurricane Katrina oil supply disruption",
        "2004 Madrid bombings economic impact",
        "2009 Dubai World debt crisis",
        "2001 Argentina sovereign default",
        "2003 SARS outbreak supply chain disruption",
        "2006 Israel-Lebanon war shipping disruption",
        "2008 Zimbabwe hyperinflation contagion fears",
        "2009 Greek debt crisis early signs",
    ]),
    ("2010-2020", [
        "2010 Greek sovereign debt crisis and eurozone contagion",
        "2011 Arab Spring and North African instability",
        "2011 Fukushima nuclear disaster supply chain impact",
        "2012 Iran nuclear sanctions and oil embargo",
        "2013 Cyprus banking crisis and bail-in",
        "2014 Russia annexation of Crimea and Ukraine crisis",
        "2015 Greek debt referendum and Grexit fears",
        "2016 Brexit referendum shock",
        "2016 Turkey coup attempt and lira crisis",
        "2017 Qatar diplomatic blockade by Gulf states",
        "2018 US-China trade war tariffs",
        "2019 Hong Kong protests and Chinese market impact",
        "2019 Saudi Aramco drone attack",
        "2015 Refugee crisis and European border tensions",
        "2018 Italian populist government bond crisis",
    ]),
    ("2020-2024", [
        "2020 COVID-19 pandemic supply chain collapse",
        "2021 Suez Canal Ever Given blockage",
        "2021 Belarus migrant crisis at Polish border",
        "2022 Russia invasion of Ukraine energy crisis",
        "2022 Nord Stream pipeline sabotage",
        "2022 Taiwan Strait military exercises",
        "2023 Houthi Red Sea shipping attacks",
        "2023 Wagner Group mutiny in Russia",
        "2023 Israel-Hamas war regional escalation",
        "2024 Chinese rare earth export restrictions",
        "2024 US chip export controls on ASML",
        "2023 Niger coup and Sahel instability",
        "2022 Sri Lanka sovereign default",
        "2023 Silicon Valley Bank collapse contagion",
        "2024 EU Carbon Border Adjustment Mechanism",
    ]),
]

EXAMPLE = {
    "instruction": "Analyze the geopolitical risk of the following situation for European retail investors.",
    "input": "Russia has completely cut off natural gas supplies to Poland and Bulgaria, citing non-payment in rubles.",
    "output": "{\"risk_score\": 8, \"region\": \"Eastern Europe\", \"category\": \"Energy Security\", \"impact\": \"High\", \"analysis\": \"The supply cutoff directly destabilizes energy markets across Central and Eastern Europe. Investors with exposure to European utilities and energy-intensive industrials face elevated downside risk. ETFs tracking the DAX and WIG20 are particularly vulnerable given Germany and Poland's historical dependency on Russian pipeline gas. Consider reducing exposure to MSCI Europe energy-heavy constituents until alternative supply routes are confirmed.\"}"
}

# ─────────────────────────────────────────
# PROMPT BUILDER
# ─────────────────────────────────────────
def build_prompt(batch_size, categories, regions, decade_info, existing_inputs):
    decade_label, decade_examples = decade_info
    existing_sample = random.sample(existing_inputs, min(5, len(existing_inputs))) if existing_inputs else []

    avoid_section = ""
    if existing_sample:
        avoid_section = f"""
AVOID DUPLICATES - Do NOT generate scenarios similar to these already existing ones:
{chr(10).join(f'- {s}' for s in existing_sample)}
"""

    return f"""You are a data generation system for training an AI geopolitical risk model.

TASK: Generate exactly {batch_size} unique training samples.

STRICT OUTPUT RULES:
- Return ONLY a valid JSON array. No preamble, no explanation, no markdown, no code blocks.
- Every output field must be a properly escaped JSON string.
- Complete all {batch_size} items. Do not truncate.

EACH ITEM MUST FOLLOW THIS EXACT STRUCTURE:
{{"instruction": "Analyze the geopolitical risk of the following situation for European retail investors.", "input": "<scenario>", "output": "{{\\\"risk_score\\\": <1-10>, \\\"region\\\": \\\"<region>\\\", \\\"category\\\": \\\"<category>\\\", \\\"impact\\\": \\\"<Low|Moderate|High|Critical>\\\", \\\"analysis\\\": \\\"<analysis>\\\"}}"}}

DECADE FOCUS FOR THIS BATCH: {decade_label}
Draw inspiration from events like:
{chr(10).join(f'- {e}' for e in decade_examples)}

CATEGORY DISTRIBUTION FOR THIS BATCH (spread evenly):
{', '.join(categories)}

REGION DISTRIBUTION FOR THIS BATCH (vary widely):
{', '.join(regions)}

RISK SCORE DISTRIBUTION:
- Scores 2-4: 20% of samples
- Scores 5-7: 50% of samples
- Scores 8-10: 30% of samples

{avoid_section}

QUALITY RULES:
- Every scenario must be realistic and historically plausible for {decade_label}
- Analysis must reference specific European indices, ETFs, companies, or sectors by name
- No two scenarios can be identical or near-identical
- Vary severity, geography, and investor impact per item
- Keep analysis concise but expert-level, 3-5 sentences

STYLE REFERENCE - Match this example exactly:
{json.dumps(EXAMPLE, ensure_ascii=False)}

Generate all {batch_size} items now."""

# ─────────────────────────────────────────
# VALIDATOR
# ─────────────────────────────────────────
def validate_sample(sample):
    required_keys = ["instruction", "input", "output"]
    for key in required_keys:
        if key not in sample:
            return False
    try:
        output = json.loads(sample["output"])
        required_output_keys = ["risk_score", "region", "category", "impact", "analysis"]
        for key in required_output_keys:
            if key not in output:
                return False
        if not isinstance(output["risk_score"], (int, float)):
            return False
        if output["impact"] not in ["Low", "Moderate", "High", "Critical"]:
            return False
        if len(output["analysis"]) < 50:
            return False
    except:
        return False
    return True

def deduplicate(samples):
    seen = set()
    unique = []
    for s in samples:
        key = s["input"].strip().lower()[:100]
        if key not in seen:
            seen.add(key)
            unique.append(s)
    return unique

# ─────────────────────────────────────────
# CHECKPOINT
# ─────────────────────────────────────────
def save_checkpoint(samples):
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(samples, f, ensure_ascii=False)

def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE) as f:
            data = json.load(f)
        print(f"Checkpoint gevonden: {len(data)} samples hersteld.")
        return data
    return []

# ─────────────────────────────────────────
# MAIN GENERATOR
# ─────────────────────────────────────────
def generate_batch(batch_size, decade_info, existing_inputs):
    categories_sample = random.sample(CATEGORIES, min(6, len(CATEGORIES)))
    regions_sample = random.sample(REGIONS, min(8, len(REGIONS)))
    prompt = build_prompt(batch_size, categories_sample, regions_sample, decade_info, existing_inputs)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
        max_tokens=16000,
    )

    content = response.choices[0].message.content.strip()

    # Strip markdown code blocks if present
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    content = content.strip()

    samples = json.loads(content)
    return samples

def main():
    print("Geopolio Dataset Generator gestart")
    print(f"Target: {TARGET} samples | Batch size: {BATCH_SIZE} | Model: {MODEL}")
    print("─" * 60)

    all_samples = load_checkpoint()
    existing_inputs = [s["input"] for s in all_samples]

    # Decade rotation: 20% 2000s, 30% 2010s, 50% 2020s
    decade_weights = [0.2, 0.3, 0.5]

    batch_num = 0
    errors = 0
    max_errors = 10

    while len(all_samples) < TARGET:
        remaining = TARGET - len(all_samples)
        batch_size = min(BATCH_SIZE, remaining)
        batch_num += 1

        # Pick decade based on weights
        decade_info = random.choices(DECADES, weights=decade_weights, k=1)[0]

        print(f"Batch {batch_num} | Decade: {decade_info[0]} | Generating {batch_size} samples...", end=" ")

        try:
            raw_samples = generate_batch(batch_size, decade_info, existing_inputs[-50:])

            # Validate
            valid = [s for s in raw_samples if validate_sample(s)]
            invalid_count = len(raw_samples) - len(valid)

            # Add to pool
            all_samples.extend(valid)
            all_samples = deduplicate(all_samples)
            existing_inputs = [s["input"] for s in all_samples]

            print(f"Got {len(raw_samples)} | Valid: {len(valid)} | Invalid: {invalid_count} | Total: {len(all_samples)}/{TARGET}")

            # Save checkpoint every batch
            save_checkpoint(all_samples)
            errors = 0

        except Exception as e:
            errors += 1
            print(f"ERROR ({errors}/{max_errors}): {e}")
            if errors >= max_errors:
                print("Te veel fouten. Gestopt.")
                break
            time.sleep(10)
            continue

        # Rate limit buffer
        time.sleep(2)

    # Final save
    final = all_samples[:TARGET]
    with open(OUTPUT_FILE, "w") as f:
        json.dump(final, f, indent=2, ensure_ascii=False)

    print("─" * 60)
    print(f"Klaar! {len(final)} samples opgeslagen in {OUTPUT_FILE}")

    # Stats
    from collections import Counter
    categories = [json.loads(s["output"])["category"] for s in final]
    decades_dist = []
    print(f"\nCategory verdeling:")
    for cat, count in sorted(Counter(categories).items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")

if __name__ == "__main__":
    main()
