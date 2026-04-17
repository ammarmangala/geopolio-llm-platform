# Finetuning Notes

Deze handleiding documenteert de finetune-aanpak in `notebooks/geopolio_finetune.ipynb`.

Doel:
- begrijpen wat elke stap doet
- snappen wanneer een model goed of slecht leert
- voorkomen dat Colab-onderbrekingen al je voortgang wissen

## 1. Wat Finetunen Hier Betekent

In deze repo finetune je een bestaand base model op Geopolio-voorbeelden.

Elke sample wordt omgezet naar een tekstblok zoals:

```text
### Instruction:
...

### Input:
...

### Response:
...
```

De trainer leert dan het patroon tussen instructie, input en gewenste response.

## 2. Dataset In De Notebook

De notebook laadt momenteel:

`data/geopolio_dataset_2099s_global_multidecade.json`

en bouwt daarna:
- `dataset`
- `train_dataset`
- `eval_dataset`

via:

```python
split = dataset.train_test_split(test_size = 0.1, seed = 42)
train_dataset = split["train"]
eval_dataset = split["test"]
```

Dat betekent:
- `90%` van de data wordt gebruikt om te trainen
- `10%` wordt apart gehouden om te evalueren

Waarom dit belangrijk is:
- `train_loss` laat zien hoe goed het model de trainingsdata leert
- `eval_loss` laat zien hoe goed het model generaliseert naar ongeziene voorbeelden

## 3. Training Config

De trainingscel gebruikt nu deze belangrijke instellingen:

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

## 4. Wat Deze Instellingen Praktisch Betekenen

`num_train_epochs = 5`
- het model gaat vijf keer door de trainingsset

`per_device_train_batch_size = 2`
- per stap ziet de GPU twee voorbeelden tegelijk

`gradient_accumulation_steps = 4`
- gradients worden vier mini-batches opgeteld voordat een optimizer-step gebeurt
- effectieve batch size wordt daardoor groter zonder extra VRAM te eisen

`learning_rate = 2e-4`
- bepaalt hoe agressief de gewichten worden aangepast

`warmup_steps = 80`
- start rustiger op om instabiliteit vroeg in training te beperken

`lr_scheduler_type = "cosine"`
- learning rate zakt geleidelijk volgens een cosine-curve

`logging_steps = 50`
- elke 50 stappen zie je trainingslogs

`eval_steps = 200`
- elke 200 stappen wordt validatie berekend

`save_steps = 200`
- elke 200 stappen wordt een checkpoint opgeslagen

`save_total_limit = 2`
- houdt alleen de laatste twee checkpoints om opslag te sparen

`load_best_model_at_end = True`
- na training wordt automatisch het checkpoint met de laagste `eval_loss` geladen

## 5. Hoe Je Loss Moet Lezen

Er is geen magische universele perfecte loss-waarde.

Belangrijker dan de absolute waarde:
- daalt `train_loss` duidelijk?
- daalt `eval_loss` ook?
- worden de outputs inhoudelijk beter?

In de praktijk:
- hoge `train_loss` en hoge `eval_loss`: model leert nog te weinig
- lage `train_loss` maar stijgende `eval_loss`: risico op overfitting
- dalende `train_loss` en dalende `eval_loss`: training gaat de goede kant op

De echte sweet spot is meestal:
- het checkpoint met de laagste `eval_loss`

Niet automatisch:
- het laatste checkpoint
- de laagste `train_loss`

## 6. Underfitting Vs Overfitting

`Underfitting`
- model leert de taak nog niet goed
- zowel training als validatie blijven relatief zwak

`Overfitting`
- model leert trainingsvoorbeelden te specifiek uit het hoofd
- `train_loss` blijft dalen terwijl `eval_loss` vlak blijft of stijgt

Conclusie:
- kijk nooit alleen naar `train_loss`
- gebruik altijd een validatieset als je serieus wilt beoordelen hoe goed de finetune is

## 7. Wat Er Gebeurt Als Colab Uitvalt

Als Colab compute op raakt of de runtime reset:
- RAM en GPU-geheugen verdwijnen
- niet-opgeslagen trainingsvoortgang is weg

Met `save_strategy = "no"` was dat gevaarlijk:
- training kon half klaar zijn
- maar zonder bruikbaar checkpoint

Met de huidige setup is dat beter:
- checkpoints komen in `./output`
- het eindmodel wordt extra opgeslagen in `./final_model`

De notebook doet nu ook:

```python
model.save_pretrained("./final_model")
tokenizer.save_pretrained("./final_model")
```

Dus:
- tussentijdse voortgang zit in `./output/checkpoint-*`
- het finale model zit in `./final_model`

## 8. Wat "Half Getraind" Betekent

Als training stopt op bijvoorbeeld:

```text
647/1315
Epoch 2.46/5
```

dan betekent dat:
- de training was ongeveer halverwege
- het model had wel geleerd
- maar zonder checkpoint was die voortgang meestal niet bruikbaar na een runtime reset

Met checkpoints kun je dat soort onderbrekingen veel beter opvangen.

## 9. Basisworkflow Voor De Notebook

1. Laad model en tokenizer.
2. Laad de dataset.
3. Maak `train_dataset` en `eval_dataset`.
4. Start training.
5. Bekijk `train_loss` en `eval_loss`.
6. Gebruik het beste checkpoint of het automatisch geladen beste model.
7. Sla model en tokenizer op.

## 10. Veelgemaakte Fouten

`NameError: dataset is not defined`
- de dataset-cel is niet uitgevoerd
- of de kernel is gereset

Training opnieuw starten zonder checkpoints
- dan verlies je makkelijk alles bij een Colab-reset

Alleen naar `train_loss` kijken
- daarmee kun je niet betrouwbaar zien of het model goed generaliseert

Een te kleine of scheve dataset gebruiken
- dan kan het model verkeerde patronen leren

## 11. Datasetkeuze In Deze Repo

In `DATASET_WORKFLOW.md` staat dat de aanbevolen trainingsdataset is:

`data/geopolio_dataset_5000s_global_multidecade_balanced.json`

De notebook verwijst nu nog naar:

`data/geopolio_dataset_2099s_global_multidecade.json`

Dat is niet per se fout, maar wel belangrijk om bewust te kiezen:
- `2099s`: kleiner, sneller trainen
- `5000s balanced`: waarschijnlijk beter als definitieve trainingsdataset

## 12. Praktische Vuistregels

- Gebruik een validation split.
- Sla checkpoints op tijdens training.
- Bewaar ook altijd een finale modelmap.
- Evalueer niet alleen numeriek, maar ook met echte voorbeeldprompts.
- Verander niet te veel hyperparameters tegelijk.

## 13. Handige Volgende Stap

Als je later serieuzer wilt vergelijken, documenteer dan per run:
- datasetnaam
- aantal samples
- modelnaam
- epochs
- learning rate
- batch size
- laagste `eval_loss`
- subjectieve kwaliteit van outputs

Dan kun je finetunes echt vergelijken in plaats van op gevoel te werken.
