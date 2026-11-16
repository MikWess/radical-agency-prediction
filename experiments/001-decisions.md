# Experiment 001: predicting judgments and decisions

## Question

Does personal evidence improve predictions of held-out judgments beyond a generic language model, and does weight adaptation add anything beyond personal context?

## Pilot design (proposed, not a claimed sample-size requirement)

1. Collect 60 development scenarios with actual choices and brief explanations. Include tradeoffs about products, time, learning, and ordinary interpersonal situations. Use clear alternatives, including "depends / need more information" when appropriate. Prefer situations with a verifiable eventual action where possible.
2. Separately write 20 validation and 40 final test scenarios. Group paraphrases and scenarios about the same event together. Freeze the partition before fitting profiles, retrieval, or adapters. This is a feasibility pilot, not enough evidence for broad claims; choose a larger sample after seeing uncertainty.
3. Capture the person's actual answer before showing any predictions. Save the context available at that moment. Historical replies must be paired with the preceding situation; a pile of standalone thoughts is not equivalent training data.
4. Run A, B, and C on exactly the same items with fixed model/settings. Tune only on development/validation. Do not repeatedly inspect final-test results while changing the system.
5. Repeat a subset of judgments about two weeks later without showing the first answers. This estimates consistency, not a hard theoretical ceiling. For decisions, also compare stated intentions with later actions as a distinct outcome.
6. If there is a useful gap, collect more paired examples and try D using LoRA. Hundreds to low thousands of carefully selected pairs is a planning range, not a guarantee or universal minimum. Select checkpoints on validation only, and use a new untouched test set if earlier results influenced model choices.

## Measurements

- **Primary:** exact choice accuracy on a predefined set of options. Report per domain and overall, with sample count and uncertainty. Compare paired predictions on the same items; compare against chance and a development-set majority-choice baseline where labels have consistent meaning.
- **Probability quality:** multiclass Brier score (sum of squared differences from the one-hot outcome, averaged across cases; 0 is best). Do not equate a model's stated probability with calibrated confidence. Inspect reliability with enough observations.
- **Reasoning:** separately rate whether the predicted reason matches the real reason (0 = wrong, 1 = partial, 2 = same main tradeoff). Blind and randomize the condition labels. Self-ratings are informative but subjective, and should not replace choice accuracy.
- **Style:** optional, separately scored. Word overlap is not a proxy for agreeing on a decision.
- **Repeatability:** re-run on another set of fresh situations and track changes over time.

The initial script implements exact choice accuracy, a Wilson accuracy interval, and Brier score. The Wilson interval assumes independent cases; with related cases it is descriptive only and should be replaced by event-group uncertainty estimates. It is deliberately not an automated judge of reasoning. Bootstrap paired differences by event group for a larger evaluation; do not interpret small pilot deltas as established wins.

## Context and leakage

For every test item, give all conditions the same scenario context, stripped of the actual answer and subsequent events. Only personal evidence differs. Retrieval must use development examples only. Profiles, summaries, embeddings, adapter data, and synthetic augmentations must never be derived from the final test set. Near-duplicates and related conversations belong in one partition. Prefer chronological splits for historical data; prospective cases provide stronger evidence of prediction.

## First implementation choice

Use an instruction-tuned open-weight model that fits the local machine. Establish that it can understand the scenarios and produce valid structured probabilities before tuning it. Select the exact checkpoint after a small local inference test; no model purchase, download, cloud GPU, or private-data upload has been authorized or performed by this repository.

## Decision rule

Keep the simplest condition that shows a repeatable advantage on unseen cases. If retrieval performs as well as an adapter, keep retrieval. If an adapter helps, report where and how much. An inconclusive result is a valid outcome.
