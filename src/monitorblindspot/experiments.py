"""Predeclared context/evidence ablation; never invokes a paid provider."""

from __future__ import annotations

from typing import Any

from .core import Experiment
from .engine import evaluate


def run_suite() -> dict[str, Any]:
    results = []
    for evidence in ("full", "structured"):
        for limit in (16, 64, 128, 1024):
            record = evaluate(Experiment(seed=17, trials=3, context_limit=limit, evidence_mode=evidence))
            results.append(
                {
                    "config": record.config,
                    "dataset_sha256": record.dataset_sha256,
                    "summary": record.summary,
                    "by_length": record.analysis["by_length"],
                    "errors": record.analysis["errors"],
                    "fixture_reviews": sum(r["fixture_review"] for r in record.rows),
                }
            )
    return {
        "mode": "deterministic-simulation",
        "protocol": "fixed seed 17; three trials; family-held-out evaluation; eight predeclared context/evidence settings",
        "experiments": results,
    }
