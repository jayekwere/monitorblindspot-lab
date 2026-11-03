"""Verify saved observations against a fresh deterministic run, excluding clock measurements."""

import json
from pathlib import Path

from monitorblindspot.core import Experiment, write_json
from monitorblindspot.engine import evaluate

saved = json.loads(Path("results/demo.json").read_text())
fresh = evaluate(Experiment.model_validate(saved["config"])).model_dump()


def observations(value: dict) -> list:
    return [
        {k: v for k, v in row.items() if k not in {"latency_ms", "extraction_ms"}} for row in value["rows"]
    ]


assert observations(saved) == observations(fresh), "deterministic observations drifted"
assert fresh["dataset_sha256"] == saved["dataset_sha256"], "dataset drifted"
write_json(Path("runs/reproduced.json"), fresh)
print(json.dumps({"reproduced": True, "rows": len(fresh["rows"]), "dataset_sha256": fresh["dataset_sha256"]}))
