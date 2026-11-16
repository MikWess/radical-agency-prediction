# Radical Agency: personal prediction

Can an existing language model predict one person's judgments and decisions on situations it has never seen?

An early experiment within [Radical Agency](https://mikeywessman.com/project.html?id=m-brain). The primary target is judgments and decisions. Wording is a separate, secondary outcome.

**Status:** research plan and local benchmark scaffolding. No personal dataset has been imported, no model has been trained, and no predictive performance has been measured.

## The experiment

Compare the same base model under four conditions:

| Condition | What changes |
| --- | --- |
| A: generic | Scenario only; no personal history |
| B: profile | A short profile derived only from development data |
| C: retrieval | Profile plus relevant past situations and actual responses |
| D: adapter | A LoRA adapter trained on development examples; initially no retrieval |

Add adapter + retrieval only after measuring these separately. Keep scenario context, model version, generation settings, and evaluation items fixed. Start with A–C; D is conditional on enough useful examples and a demonstrated gap.

Fine-tuning starts from pretrained weights and adapts them; it can also cause forgetting. LoRA freezes the base model and trains small additional matrices. Resetting the pretrained weights would discard the reason to start with an existing model.

## Start locally

Python 3.9+; standard library only. Nothing here makes network requests.

```sh
python3 scripts/benchmark.py init
python3 -m unittest discover -s tests
```

This copies six **synthetic workflow examples** into ignored `private/`; they are not a valid benchmark of anyone. Replace them with fresh, privately written scenarios. Freeze the scenarios before collecting answers. The fixed public examples are suitable only for learning the workflow.

Record an actual answer in `private/answers.jsonl` without viewing model predictions. Have each condition produce a separate JSONL prediction file following the template. Then score:

```sh
python3 scripts/benchmark.py score private/answers.jsonl private/predictions-template.jsonl
```

An unfilled template intentionally fails scoring. Scores are local; model execution and training are not implemented yet. Do not paste private inputs into a hosted model without separately deciding to authorize that data transfer.

Read [the first experiment](experiments/001-decisions.md), [data design](docs/data.md), and [prior research](docs/research.md).

## Public methods, private evidence

Personal examples, interviews, responses, model predictions, and model weights belong under ignored directories. Public commits contain code, synthetic examples, and methodology only. Git ignore is a convenience, not a privacy boundary: review staged files before every push. Trained weights can retain personal information and are private too.

## What a result would mean

Success means better predictions on untouched cases than the generic baseline, with uncertainty reported. Sounding convincing or sounding like the person is insufficient. A failure could mean poor context, a weak base model, inadequate data, unstable preferences, or a limitation of the approach. This experiment does not measure consciousness or establish a complete model of a person.
