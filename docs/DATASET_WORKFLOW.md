# Dataset Workflow

## Gebruik Dit Bestand Voor Training

Gebruik deze dataset voor training:

`data/geopolio_dataset_5000s_global_multidecade_balanced.json`

Waarom:
- `5000` samples
- `5000` unieke inputs
- `0` duplicates
- categories balanced
- regions balanced
- risk scores balanced

## Wat De Andere Bestanden Zijn

`data/geopolio_dataset_5000s_global_multidecade.json`
- eerste uitgebreide dataset tot 5000 samples
- niet volledig balanced op alle assen

`data/geopolio_dataset_5000s_global_multidecade.checkpoint.json`
- checkpoint/tussenbestand van generatie
- niet bedoeld als definitieve trainingsdataset

`data/geopolio_dataset_5000s_global_multidecade_balanced.json`
- definitieve balanced trainingsdataset
- dit bestand gebruiken voor finetuning of training

## Scripts

`scripts/generation/expand_dataset_to_target.py`
- breidt een bestaande dataset lokaal uit tot een target size
- gebruikt geen API key
- schrijft een nieuw bestand en checkpoint

`scripts/generation/rebalance_dataset.py`
- maakt van een bestaande dataset een balanced versie
- balanceert categories, regions en risk scores
- schrijft een nieuw balanced bestand

## Standaard Workflow

### 1. Dataset uitbreiden

```powershell
py scripts\generation\expand_dataset_to_target.py --target-size 5000
```

Output:
- `data/geopolio_dataset_5000s_global_multidecade.json`
- `data/geopolio_dataset_5000s_global_multidecade.checkpoint.json`

### 2. Dataset balancen

```powershell
py scripts\generation\rebalance_dataset.py
```

Output:
- `data/geopolio_dataset_5000s_global_multidecade_balanced.json`

## Belangrijk Over "Balanced"

Bij `5000` samples:
- `12` categories delen `5000` niet exact
- `18` regions delen `5000` niet exact
- `10` risk scores delen `5000` wel exact

Dus correct balanced betekent:
- categories: `416` of `417` per class
- regions: `277` of `278` per region
- risk scores: exact `500` per score

Als je ooit iets anders ziet, is de dataset niet volledig balanced.

## Snelle Checks

### Aantal samples

```powershell
py -c "import json; d=json.load(open(r'data\geopolio_dataset_5000s_global_multidecade_balanced.json', encoding='utf-8')); print(len(d))"
```

### Uniekheid controleren

```powershell
py -c "import json; d=json.load(open(r'data\geopolio_dataset_5000s_global_multidecade_balanced.json', encoding='utf-8')); s=[x['input'].strip().lower() for x in d]; print(len(d), len(set(s)), len(d)-len(set(s)))"
```

Verwachte output:

```text
5000 5000 0
```

### Volledige balance-check

```powershell
py -c "import json, collections; d=json.load(open(r'data\geopolio_dataset_5000s_global_multidecade_balanced.json', encoding='utf-8')); inputs=[x['input'].strip().lower() for x in d]; outputs=[json.loads(x['output']) for x in d]; print('total =', len(d)); print('unique =', len(set(inputs))); print('duplicates =', len(d)-len(set(inputs))); print('categories =', dict(collections.Counter(o['category'] for o in outputs).most_common())); print('regions =', dict(collections.Counter(o['region'] for o in outputs).most_common())); print('risk_scores =', dict(collections.Counter(o['risk_score'] for o in outputs).most_common()))"
```

## Hoe Zie Je Of Het Goed Is

Je wilt dit patroon zien:

- `total = 5000`
- `unique = 5000`
- `duplicates = 0`
- categories allemaal `416/417`
- regions allemaal `277/278`
- risk scores allemaal `500`

## Als Er Problemen Zijn

### Probleem: `python` werkt niet

Gebruik:

```powershell
py ...
```

in plaats van:

```powershell
python ...
```

### Probleem: Notebook vindt bestand niet

Je notebook draait waarschijnlijk vanuit `notebooks/` in plaats van repo-root.

Gebruik in notebooks:

```python
from pathlib import Path
repo = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
```

en bouw paden vanaf `repo`.

### Probleem: Dataset is niet balanced

Run opnieuw:

```powershell
py scripts\generation\rebalance_dataset.py
```

En controleer daarna opnieuw met de balance-check.

### Probleem: Duplicates

Controleer:

```powershell
py -c "import json; d=json.load(open(r'data\geopolio_dataset_5000s_global_multidecade_balanced.json', encoding='utf-8')); s=[x['input'].strip().lower() for x in d]; print(len(d), len(set(s)), len(d)-len(set(s)))"
```

Als het laatste getal niet `0` is, dan mag je die dataset niet gebruiken voor training.

## Aanbevolen Naamgeving In De Toekomst

Gebruik dit patroon:

- ruwe uitbreiding:
  `geopolio_dataset_<SIZE>_global_multidecade.json`
- checkpoint:
  `geopolio_dataset_<SIZE>_global_multidecade.checkpoint.json`
- definitieve trainingsdataset:
  `geopolio_dataset_<SIZE>_global_multidecade_balanced.json`

## Korte Samenvatting

Als je twijfelt, gebruik gewoon deze file:

`data/geopolio_dataset_5000s_global_multidecade_balanced.json`

## Wat Is Er In Deze Sessie Gedaan

Deze repository had als startpunt:

- `data/geopolio_dataset_2099s_global_multidecade.json`

Daarna zijn deze stappen uitgevoerd:

### 1. Uitbreidingsscript gemaakt

Bestand:

- `scripts/generation/expand_dataset_to_target.py`

Doel:

- de bestaande `2099`-sample dataset lokaal uitbreiden naar `5000`
- zonder API key
- zonder het bronbestand te overschrijven

Output:

- `data/geopolio_dataset_5000s_global_multidecade.json`
- `data/geopolio_dataset_5000s_global_multidecade.checkpoint.json`

### 2. Eerste 5000-sample dataset gecontroleerd

Resultaat:

- `5000` samples
- `5000` unieke inputs
- `0` duplicates

Maar:

- categories waren niet volledig schoon door extra labels uit de seed-dataset
- risk scores waren niet balanced

Dus die dataset was bruikbaar als tussenresultaat, maar niet als definitieve trainingsdataset.

### 3. Rebalance-script gemaakt

Bestand:

- `scripts/generation/rebalance_dataset.py`

Doel:

- category-labels normaliseren
- categories balancen
- regions balancen
- risk scores balancen
- opnieuw een nieuw bestand schrijven zonder het tussenbestand te overschrijven

Output:

- `data/geopolio_dataset_5000s_global_multidecade_balanced.json`

### 4. Definitieve balanced dataset gevalideerd

Definitieve check gaf:

- `5000` total
- `5000` unique
- `0` duplicates
- categories balanced op `416/417`
- regions balanced op `277/278`
- risk scores exact balanced op `500` per score

Conclusie:

- `data/geopolio_dataset_5000s_global_multidecade_balanced.json` is de definitieve trainingsdataset

### 5. Herbruikbare skill aangemaakt

Globale skill aangemaakt op:

- `C:\Users\ammar\.codex\skills\geopolio-dataset-balance`

Bestanden:

- `C:\Users\ammar\.codex\skills\geopolio-dataset-balance\SKILL.md`
- `C:\Users\ammar\.codex\skills\geopolio-dataset-balance\references\workflow.md`
- `C:\Users\ammar\.codex\skills\geopolio-dataset-balance\agents\openai.yaml`

Doel van de skill:

- later opnieuw dezelfde workflow kunnen gebruiken
- snel bepalen welk datasetbestand voor training bedoeld is
- expand/rebalance/validate stappen herhalen zonder alles opnieuw uit te leggen
