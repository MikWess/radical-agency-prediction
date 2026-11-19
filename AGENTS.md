# Working on this experiment

This project is starting from ground zero. Do not treat previous experiment designs or recommendations in Git history as current decisions.

Keep personal data, credentials, private evidence, and model weights out of public commits. Review staged content before publishing. Do not upload private evidence to external services without explicit authorization.

Distinguish proposed work, observed evidence, and verified results. Do not invent findings or claim an experiment ran when it did not.

## Current implementation

`experiments/response-prediction/` contains the local MLX prediction/reveal loop. Start with `start.sh` (not a static file server). The pinned model is downloaded by `setup.sh`; inference must remain local/offline. A pending prediction must be persisted before accepting its answer and must not be returned by pending-state or export APIs. Completed answers are immutable; retries are idempotent. Preserve browser migration and the private SQLite database.

Run `python -m unittest discover -s tests -v` and `node --check experiments/response-prediction/app.js`. Real-model UI checks use a separate port and `--data-dir private/qa-response-prediction`, never the real notebook. The loop uses prompt examples, not trained weights. Do not claim accuracy improvement from different questions or from test fixtures.
