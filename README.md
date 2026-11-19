# Radical Agency: personal response prediction

Given earlier examples, how well can a foundation model predict Mikey’s response to a new short question?

## Run the live loop on an Apple silicon Mac

Requires `uv`. First-time setup installs an isolated Python environment and downloads the pinned, 4-bit [Qwen3 4B MLX model](https://huggingface.co/mlx-community/Qwen3-4B-4bit) into ignored `models/` (approximately 2.3 GB):

```sh
./experiments/response-prediction/setup.sh
./experiments/response-prediction/start.sh
```

Open http://127.0.0.1:8765/experiments/response-prediction/ and click **Start a prediction**. Keep the server running while using the page. The old `python -m http.server` command only serves static files and cannot run this loop.

1. The model predicts an answer using earlier examples. The server saves the prediction, prompt, model revision, settings, example IDs, and timestamps before presenting the question.
2. Type or use your device’s keyboard dictation to give a spontaneous answer. The prediction remains on the server, absent from the pending-run API response.
3. **Save my answer & reveal** saves the answer and reveals the existing prediction. Answers cannot be edited after reveal; repeated requests do not duplicate answers.
4. Optionally score the prediction’s main point from 0–2. Try the next question: the previous answer becomes another example.
5. Review history to compare example counts and scores. Export the experiment as JSON for private backup and analysis.

The first prediction loads the model and takes longer. Generation is local with MLX; inference runs with Hugging Face offline mode. The setup download is the only required model-provider network access. No hosted API key is needed.

## What “learning” means here

This version uses in-context examples, not weight updates or fine-tuning. It selects up to 40 recent answers within an 18,000-character evidence budget. It excludes answers sharing the current question’s ID or exact text. Optional context is saved but not included in the prediction prompt. No personal profile, outside messages, or biographical knowledge is supplied to the model.

There are 40 questions. Unanswered questions come first; after the deck is exhausted, the least-answered question repeats with a visible label, and its prior answers remain excluded. Near-duplicate semantic questions are **not** automatically detected. This is an exploratory loop, not a clean held-out benchmark. Scores on different questions cannot establish that more examples caused improvement.

Next research step: use fresh questions to compare the same model with no personal examples against a frozen set of examples, score predictions with condition labels hidden, then test whether fine-tuning adds value. Main point, details, and voice should remain separate judgments. No improvement is claimed just because the loop runs.

## Private persistence

- `private/response-prediction/lab.sqlite3` stores real answers, predictions, prompts, and ratings. It is ignored by Git, created with owner-only file permissions, and **not encrypted**.
- Existing answers under the original browser localStorage key are imported automatically on connection, with deterministic deduplication. The old browser copy is untouched. Use the same browser and `127.0.0.1:8765` origin for migration.
- Pending predictions survive reloads and server restarts. Draft answers stay in browser localStorage until submitted. Saved answers are independent of browser storage.
- Export includes examples and completed runs (including prompts); it omits unanswered predictions. Exports contain personal information and belong in ignored `private/`, never public commits.
- The server binds only to `127.0.0.1`, serves only the page and JS, validates Host/Origin, and requires a per-process token for mutations and exports. It does not expose repo files or private directories. Do not expose it through a public tunnel.
- Browser history, training files, private examples, model weights, and credentials must not be published. Public code contains no real participant answers.

## Verification

```sh
.venv/bin/python -m unittest discover -s tests -v
node --check experiments/response-prediction/app.js
```

The tests cover hidden prediction state, pre-answer timestamps, retry idempotency, immutable answers, reuse of prior examples, import deduplication, repeated-question exclusion, inference failure recovery, scoring validation, private-file protection, and request-origin/token enforcement. Tests use synthetic evidence and a deterministic predictor; real-model browser QA is separate.

For an isolated manual test with the real model:

```sh
./experiments/response-prediction/start.sh --port 8766 --data-dir private/qa-response-prediction
```

Use that separate origin and database for synthetic test answers. Do not put test answers into the participant notebook.
