# Prior work and implications

Research checked November 15, 2026. These studies motivate the experiment; none establishes its accuracy for this particular person.

| Date | Primary source | Why it matters |
| --- | --- | --- |
| August 2016 | [A Persona-Based Neural Conversation Model](https://aclanthology.org/P16-1094/) | Early work on incorporating speaker identity into neural conversation models. Persona-conditioned language is an older research direction, not evidence of complete psychological replication. |
| June 2021 | [LoRA](https://arxiv.org/abs/2106.09685) | Adapts a pretrained model by learning low-rank updates while freezing original weights. A practical alternative to updating every weight. |
| May 2023 | [QLoRA](https://arxiv.org/abs/2305.14314) | Combines quantized frozen base weights with trainable adapters to reduce fine-tuning memory requirements. Hardware support and model choice still matter. |
| August 2024 | [LaMP](https://aclanthology.org/2024.acl-long.399/) | Seven personalized classification/generation tasks and retrieval-based personalization. Supports testing retrieval as a serious baseline. |
| November 2024 | [OPPU: personalized parameter-efficient fine-tuning](https://aclanthology.org/2024.emnlp-main.372/) | Direct precedent for per-user parameter-efficient adaptation; evaluated on personalization tasks. These tasks differ from predicting arbitrary real-life decisions. |
| November 15, 2024 | [Generative Agent Simulations of 1,000 People, v1](https://arxiv.org/abs/2411.10109v1) | Agents representing 1,052 real people from interview evidence. The original version reported survey predictions at 85% of participants' two-week self-consistency. This is a relative measure, not 85% raw accuracy on arbitrary behavior. |
| June 28, 2026 | [Revised study, v3](https://arxiv.org/abs/2411.10109v3) | Reports held-out survey accuracy at 83% (interview), 82% (survey), and 86% (combined) of test–retest consistency, versus 74% using demographics. Distinguish these updated results from the original 85% headline. |

The strongest implication is methodological: rich personal evidence can help without first changing weights. Predicting attitudes on structured questions is narrower than predicting exact messages, real actions, or responses under unseen circumstances. Measure those separately.

## Working recommendation

Start with a baseline and retrieval. Train an adapter only after a frozen benchmark exists. Avoid full-weight fine-tuning initially: it adds memory requirements and makes overfitting/forgetting harder to manage without proving that it adds value here. The main uncertainty is evidence quality and generalization, not whether a training job can run.
