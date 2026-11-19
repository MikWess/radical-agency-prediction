# Radical Agency: personal response prediction

An exploratory experiment: given earlier examples, how well can a foundation model predict Mikey’s response to a new short question?

## Open the planning page

From this repository, run:

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

Open http://127.0.0.1:8765/experiments/response-prediction/ in a browser.

The buildless HTML page explains the proposed experiment and includes 20 starter questions, browser-local answer collection, dated history, and JSON export. Use device keyboard dictation for spoken input. There is no model connection, audio recording, training, or measured result yet.

Answers stay in browser localStorage for the page’s origin. Use a consistent browser and address, and export backups. Exported JSON contains personal data: move it into `private/`, which is ignored by Git. Do not commit exports. Browser storage is not encrypted or a durable backup.

## Proposed first comparison

Collect 30–50 answers over several sessions. Compare the same base model with no personal examples against that model given a fixed selection of earlier answers. Use 15–20 fresh questions; keep near-duplicate questions out of both training and evaluation sets. These are exploratory sample targets, not a power calculation or training-data sufficiency claim.

Record predictions before revealing the real answer to the model; hide predictions from the participant until their answer is saved. Score shuffled, unlabeled predictions for main point and details (0–2 each), with voice rated separately. Report individual failures as well as averages. Later, evaluate fine-tuning against the examples baseline. Test answers used for training must be retired from held-out evaluation.

Next implementation: a local model runner, immutable run records (model, settings, prompt, example IDs, timestamps), hidden prediction/reveal flow, and comparison scoring. The current question deck is for examples only.

Personal data, credentials, private evidence, and model weights stay local and out of this public repository. No external scripts or network requests are used by the page.
