# Observed simulation results

The default experiment executed 72 held-out traces × three trials × three strategies = 648 observations. Primary metrics below use the predeclared first trial; remaining trial metrics are in the saved output. No language model was evaluated.

| Strategy | Precision | Recall | F1 | Accuracy (Wilson 95% CI) |
|---|---:|---:|---:|---:|
| rule | 1.000 | 0.375 | 0.545 | 0.583 (0.468–0.690) |
| model | 1.000 | 0.667 | 0.800 | 0.778 (0.669–0.858) |
| hybrid | 1.000 | 0.729 | 0.843 | 0.819 (0.715–0.891) |

## Context/evidence ablation

Eight settings were executed with three trials each (5,184 total observation records, saved as experiment summaries). The table reports first-trial recall.

| Evidence | Event limit | Rule recall | Model fixture recall | Hybrid recall |
|---|---:|---:|---:|---:|
| full | 16 | 0.312 | 0.562 | 0.625 |
| full | 64 | 0.375 | 0.667 | 0.750 |
| full | 128 | 0.375 | 0.667 | 0.729 |
| full | 1024 | 0.500 | 0.917 | 0.979 |
| structured | 16 | 0.500 | 0.854 | 0.917 |
| structured | 64 | 0.500 | 0.854 | 0.917 |
| structured | 128 | 0.500 | 0.854 | 0.917 |
| structured | 1024 | 0.500 | 0.854 | 0.917 |

At 128 events, hybrid makes 162 fixture reviews across three trials versus 216 for the standalone model fixture, a 25% reduction in review opportunities. Both report zero API tokens and $0 inference cost; this does not establish monetary savings with an LLM.

Structured extraction preserves distributed classification evidence that full tail truncation loses. However, full 1024-event review performs better than structured review for the model/hybrid fixture in this experiment. This non-monotonic result is retained, not removed. Structured extraction scans all input events, so its end-to-end cost is not equal to truncation.

The held-out run records zero false positives (n=24 benign cases); the descriptive Wilson upper bound is 13.80%. Related resource/length variants are correlated and the fixture is synthetic. These findings do not establish real-world monitor accuracy. See [methodology](methodology.md).

Artifacts: [default run](../results/demo.json) · [ablation summaries](../results/context-sweep.json).
