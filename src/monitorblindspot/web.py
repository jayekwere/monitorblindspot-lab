"""Local-only bounded simulation API. External models are CLI opt-in only."""

from __future__ import annotations

import csv
import hmac
import io
import os
import threading
import time
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .core import Experiment, RunRecord
from .dataset import load_dataset, public_case
from .engine import evaluate

STATIC = Path(__file__).parent / "static"


def create_app() -> FastAPI:
    app = FastAPI(title="Synthetic AI Safety Research", docs_url=None, redoc_url=None)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "[::1]", "testserver"])
    guard = threading.Lock()
    runs: dict[str, RunRecord] = {}
    timestamps: list[float] = []
    demo = STATIC / "demo.json"
    if demo.exists():
        runs["demo"] = RunRecord.model_validate_json(demo.read_text())

    @app.middleware("http")
    async def boundaries(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        if request.method not in {"GET", "HEAD", "POST"}:
            return Response("method denied", status_code=405)
        if request.method == "POST":
            origin = request.headers.get("origin")
            if origin and origin != f"{request.url.scheme}://{request.headers.get('host', '')}":
                return Response("origin denied", status_code=403)
            token = os.getenv("LAB_API_TOKEN", "")
            if token and not hmac.compare_digest(request.headers.get("authorization", ""), f"Bearer {token}"):
                return Response("authorization required", status_code=401)
            length = request.headers.get("content-length", "")
            if not length.isdigit() or int(length) > 16384:
                return Response("body length required; maximum 16 KiB", status_code=413)
            if len(await request.body()) > 16384:
                return Response("body too large", status_code=413)
            now = time.monotonic()
            timestamps[:] = [t for t in timestamps if now - t < 60]
            if len(timestamps) >= 6:
                return Response(
                    "rate limit: six writes per minute", status_code=429, headers={"Retry-After": "60"}
                )
            timestamps.append(now)
        response = await call_next(request)
        response.headers.update(
            {
                "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'",
                "X-Content-Type-Options": "nosniff",
                "Referrer-Policy": "no-referrer",
                "Cache-Control": "no-store",
            }
        )
        return response

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "mode": "synthetic-local"}

    @app.get("/api/scenarios")
    def scenarios() -> list[dict[str, Any]]:
        return [public_case(s) for s in load_dataset()]

    @app.get("/api/runs")
    def list_runs() -> list[str]:
        return list(runs)

    @app.get("/api/runs/{run_id}")
    def get_run(run_id: str) -> RunRecord:
        if run_id not in runs:
            raise HTTPException(404, "run not found")
        return runs[run_id]

    @app.post("/api/runs")
    def run(config: Experiment) -> dict[str, str]:
        if not guard.acquire(blocking=False):
            raise HTTPException(409, "an experiment is already running")
        try:
            result = evaluate(config)
            key = f"run-{time.time_ns()}"
            if len(runs) >= 4:
                del runs[next(iter(runs))]
            runs[key] = result
            return {"id": key}
        except ValueError:
            raise HTTPException(422, "configuration is unsupported for this dataset") from None
        finally:
            guard.release()

    @app.get("/api/runs/{run_id}/export")
    def export(run_id: str, format: str = "json") -> Response:
        result = get_run(run_id)
        if format == "json":
            return Response(
                result.model_dump_json(indent=2),
                media_type="application/json",
                headers={"Content-Disposition": "attachment; filename=experiment.json"},
            )
        if format != "csv":
            raise HTTPException(422, "format must be json or csv")
        stream = io.StringIO()
        fields = sorted({k for row in result.rows for k, v in row.items() if not isinstance(v, (dict, list))})
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in result.rows:
            # Neutralize spreadsheet formulas on all string fields.
            writer.writerow(
                {
                    k: (
                        "'" + str(v)
                        if isinstance(v, str) and v.startswith(("=", "+", "-", "@", "\t", "\r"))
                        else v
                    )
                    for k, v in row.items()
                    if k in fields
                }
            )
        return Response(
            stream.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=observations.csv"},
        )

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(STATIC / "index.html")

    app.mount("/assets", StaticFiles(directory=STATIC), name="assets")
    return app


app = create_app()
