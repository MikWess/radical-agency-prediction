# Working on this experiment

The goal is predicting held-out judgments and decisions; style is secondary. Read README.md and experiments/001-decisions.md before changing scope.

Keep personal data, predictions, and weights local in ignored directories. Do not ingest accounts or send private evidence to hosted models without explicit authorization. Public repository content is methods, code, and synthetic examples only.

Never claim predictive accuracy from synthetic data or claim training happened unless it actually ran. Keep training, validation, and final test evidence separate; prevent leakage through profiles and retrieval too.

Check with `python3 -m unittest discover -s tests`. The scaffold has no model backend yet. Use standard-library tooling until an actual dependency is needed.
