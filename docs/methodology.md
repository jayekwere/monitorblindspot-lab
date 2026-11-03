# Experimental methodology

## Testable hypotheses
H1: truncating observations can hide the early half of distributed evidence and reduce recall. H2: label-free structured extraction preserves salient events under the same event limit. H3: hybrid authorization rules plus model review can reduce missed violations and model-review calls relative to standalone review. H4: structured extraction is not guaranteed to improve every synthetic reviewer outcome.

This release evaluates rules and deterministic reviewer fixtures, not a trained language model. The `model` strategy uses a structured evaluator interface; real OpenAI/Claude/local calls are optional and were not run. The fixture is deliberately imperfect: it links prose classifications and tool actions, detects missing evidence, can overreact to quoted administrator keywords, and has seed-controlled uncertainty. Its behavior is defined in source and never reads labels, scenario family or rationale.

## Dataset and labels
The generator yields 144 cases: 12 mechanism families × four lengths (16, 64, 256, 768 events) × three resource variants. Families, not random rows, determine the 72/72 development/evaluation split. Every case has chronological event IDs, difficulty, an intervention-required label, onset (if positive) and rationale. Related variants share structure; these are not 144 independent real incidents.

A positive label means policy intervention is needed: unauthorized tenant access (including an attempted action denied by the gateway), administrator grants, writes after revocation, unapproved restricted exports, conflicting transfer instructions or missing mandatory classification evidence. Negative cases include ordinary work, explicit approvals, incident quotations and dry-runs. The held-out split includes 48 positives and 24 negatives. Incomplete evidence requires review under the stated policy; this is not a claim that an actual harmful export occurred.

## Observations and strategies
`full` keeps the last N events. `structured` first scans the entire trace and retains non-background events, then applies the same N-event limit. Extraction uses event kinds, not labels. This is a privileged complete-input preprocessing step: its cost is measured separately, and the comparison is not an equal end-to-end input-budget experiment. Event limits are not tokenizer context lengths.

Rule monitoring tracks tenant, classification, approvals, grants and revocations with configurable risk threshold and instruction-pattern flag. The simple rule baseline does not understand prose confidentiality; missing classification scores below the default threshold, intentionally exposing a monitoring gap. It is a detector, not an authorization gateway. Model review extracts bounded evidence IDs and a risk score. Invalid IDs, malformed responses and budget failures produce explicit unclassified errors. Hybrid uses high-confidence rules first, skips clearly routine activity, and invokes review for remaining notes/exports; aggregation takes maximum risk and unions evidence.

All outputs are schema validated. Model observations contain policy and events only. No labels, onset, rationale or case-family fields are passed to the model. Trace reconstruction joins observed IDs to the fingerprinted dataset, avoiding repeated raw event copies.

## Metrics
Precision, recall, F1, accuracy, false-positive and missed-violation rates derive from explicit confusion counts. Primary point estimates and Wilson 95% intervals use the first predeclared trial (seed 17), one observation per unique scenario. Other trial metrics (seeds 18, 19) are saved separately. Trials are not pooled as independent sample size. Zero precision/recall denominators return zero by convention; empty binomial rates return null.

Brier score and calibration bins use risk probabilities on labeled cases. Latency is measured batch-review duration, not an online alerting service latency. Extraction duration is recorded separately. Retrospective event lag records distance from labeled onset to batch completion, not first streaming detection. Timeline highlights are cited evidence, not proof of an online alarm at that event. API tokens and cost are zero in deterministic mode. Fixture-review counts measure call opportunities, not billed tokens or monetary savings.

## Predeclared experiments
`monitorblindspot-lab suite` runs eight settings: context limits 16/64/128/1024 × full/structured, seed 17, three trials, held-out split. Save summary outputs in results/context-sweep.json. The default run contains 648 actual records (72 cases × three trials × three strategies). Length and family breakdowns, confusion matrices, errors, calibration and per-trial metrics are saved.

## Limitations and negative findings
The generator and fixture share explicit policy concepts, so this is engineering validation and a methodological demonstration. It cannot establish monitoring performance on natural-language agents or frontier models. Public labels can be memorized. Evaluation variants are correlated and positives are more common than in many deployments. Structured extraction can discard subtle background clues, and the fixture's prompt-dependent uncertainty makes comparisons non-monotonic. In this run full 1024-event review exceeds structured review for the model/hybrid fixture; preserving salient events is not sufficient to guarantee better performance. Cost-quality claims require actual model-token measurements, which remain unexecuted. No threshold was tuned against held-out outcomes during this release.
