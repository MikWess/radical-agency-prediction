# Data design

Use paired examples: **situation and available context → actual judgment/decision + optional explanation**. An essay or diary entry can supply background; it does not necessarily label the response to a new situation.

Keep raw sources private. Start with deliberately recorded scenarios and answers instead of bulk-importing accounts. Include only the other person's context needed for the prediction; remove names and irrelevant details. Keep source provenance, timestamps, and whether text was written by the person or drafted by an assistant. Assistant-generated text must not silently become ground truth for the person.

Suggested private development record:

```json
{
  "id": "unique-example-id",
  "event_group": "same-event-or-conversation",
  "observed_at": "ISO-8601 timestamp",
  "source": "self_recorded",
  "authorship": "human",
  "domain": "product",
  "context": "Only facts available before answering",
  "scenario": "A concrete tradeoff",
  "options": ["A", "B", "C"],
  "choice": "B",
  "explanation": "Actual explanation, not an invented rationale",
  "split": "development"
}
```

Store explanatory option text with each scenario, not just letters. Letters are item-local labels, not stable preferences. Keep outcome/action records distinct from stated intentions. Empty or unknown reasons are allowed; never fabricate them.

For supervised fine-tuning, the input contains context + scenario + options; the target contains the actual response. Do not train on a generated explanation and call it the person's thinking. A memory index should be easy to update when preferences change; weight updates are less transparent.

## Local scorer format

Answer records contain `id`, `options` (list of unique option labels), and `choice` (one of those labels). Prediction records contain `id` and `probabilities` (exactly one finite probability per option, totaling 1). IDs must match exactly, with no duplicates or missing cases. For tied highest probabilities, include an explicit `choice` among the tied options using a policy fixed before seeing the answer. The scorer retains the probability distribution for Brier scoring; never alter it just to break a tie. For other predictions, `choice` is optional and must agree with the highest-probability option if supplied.

The public starter scenarios have no personal answers. Local initialization creates blank answer and prediction templates. This scaffold does not enforce blinding or partition isolation; those remain operator responsibilities until a collection interface is built.
