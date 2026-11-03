"""Trace-level experiments with scenario-clustered uncertainty and observation provenance."""

from __future__ import annotations

import time
from typing import Any

from .adapters import Model, ProviderError
from .core import Experiment, RunRecord, classification, digest
from .dataset import load_dataset
from .monitors import RuleConfig, SyntheticReviewer, observe, review

STRATEGIES = ("rule", "model", "hybrid")


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    metrics = classification([r for r in rows if r["trial"] == 0])
    metrics["repeated_trial_metrics"] = [
        {"trial": trial, **classification([r for r in rows if r["trial"] == trial])}
        for trial in sorted({r["trial"] for r in rows})
    ]
    for key in ("cost_usd", "input_tokens", "output_tokens"):
        metrics[key] = sum(r.get(key, 0) for r in rows)
    metrics["latency_ms"] = sum(r["latency_ms"] for r in rows) / len(rows) if rows else 0.0
    return metrics


def evaluate(config: Experiment, model: Model | None = None) -> RunRecord:
    cases = load_dataset()
    selected = [s for s in cases if config.split == "all" or s.split == config.split]
    if not selected:
        raise ValueError("split has no monitoring traces")
    rows = []
    for trial in range(config.trials):
        reviewer = model or SyntheticReviewer(config.seed + trial)
        for scenario in selected:
            extraction_start = time.perf_counter()
            events = observe(scenario.events, config.context_limit, config.evidence_mode)
            extraction_ms = (time.perf_counter() - extraction_start) * 1000
            for strategy in STRATEGIES:
                start = time.perf_counter()
                before = reviewer.usage.model_copy()
                error = None
                try:
                    decision, used_model = review(
                        strategy, events, reviewer, RuleConfig(threshold=config.threshold)
                    )
                    prediction = decision.risk >= config.threshold
                    risk = decision.risk
                    evidence = decision.evidence
                    reason = decision.reason
                except (ValueError, ProviderError):
                    prediction = None
                    risk = 0.5
                    evidence = []
                    reason = "review failed"
                    used_model = True
                    error = "provider limit or invalid structured evidence"
                after = reviewer.usage
                rows.append(
                    {
                        "id": scenario.id,
                        "family": scenario.family,
                        "difficulty": scenario.difficulty,
                        "trial": trial,
                        "strategy": strategy,
                        "label": scenario.label,
                        "prediction": prediction,
                        "risk": risk,
                        "evidence": evidence,
                        "reason": reason,
                        "error": error,
                        "trace_length": len(scenario.events),
                        "observed_event_ids": [e.id for e in events],
                        "extraction_ms": extraction_ms,
                        "detection_lag_events": len(scenario.events) - 1 - scenario.onset
                        if prediction and scenario.onset is not None
                        else None,
                        "latency_ms": (time.perf_counter() - start) * 1000,
                        "fixture_review": used_model and model is None,
                        "input_tokens": after.input_tokens - before.input_tokens,
                        "output_tokens": after.output_tokens - before.output_tokens,
                        "cost_usd": after.estimated_cost_usd - before.estimated_cost_usd,
                    }
                )
    summary = [
        {"strategy": strategy, **summarize([r for r in rows if r["strategy"] == strategy])}
        for strategy in STRATEGIES
    ]
    by_length = [
        {
            "length": length,
            "strategy": strategy,
            **classification(
                [
                    r
                    for r in rows
                    if r["strategy"] == strategy and r["trace_length"] == length and r["trial"] == 0
                ]
            ),
        }
        for length in (16, 64, 256, 768)
        for strategy in STRATEGIES
    ]
    by_category = [
        {
            "family": family,
            "strategy": strategy,
            **classification(
                [r for r in rows if r["strategy"] == strategy and r["family"] == family and r["trial"] == 0]
            ),
        }
        for family in sorted({s.family for s in selected})
        for strategy in STRATEGIES
    ]
    return RunRecord(
        project="MonitorBlindspot Lab",
        mode="external-model" if model else "deterministic-simulation",
        dataset_sha256=digest([s.model_dump() for s in cases]),
        config_sha256=digest(config.model_dump()),
        config=config.model_dump(),
        providers=[model.name if model else "synthetic-context-reviewer-v1"],
        rows=rows,
        summary=summary,
        analysis={
            "unique_cases": len(selected),
            "interval_unit": "first predeclared trial; Wilson intervals over unique scenarios; repeated trials reported separately",
            "by_length": by_length,
            "by_category": by_category,
            "errors": sum(r["error"] is not None for r in rows),
            "evidence_reconstruction": "join observed_event_ids to the fingerprinted dataset; no labels enter reviewer prompts",
        },
    )
