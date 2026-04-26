"""CRM writer abstraction.

We support two providers out of the box:

- `noop`  — log to stdout / JSONL file. Default for dry-run mode.
- `sharpify` — stub aimed at Lauris's Sharpify CRM. Real endpoints will be filled in
  once the API spec is provided. Until then this provider raises NotImplementedError
  on actual writes but its `prepare_payload` method is fully usable for staging.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class CRMUpdate:
    contact_email: str
    deal_stage: str
    score: int
    summary: str
    next_step: str
    next_step_due: str


class CRMWriter:
    def __init__(self, provider: str, api_key: str | None, base_url: str | None, dry_run: bool = False):
        self._provider = provider
        self._api_key = api_key
        self._base_url = (base_url or "").rstrip("/")
        self._dry_run = dry_run
        self._log_path = Path(__file__).resolve().parent / "crm_outbox.jsonl"

    def write(self, update: CRMUpdate) -> dict[str, Any]:
        if self._dry_run or self._provider == "noop":
            return self._log(update)
        if self._provider == "sharpify":
            return self._write_sharpify(update)
        raise ValueError(f"Unknown CRM provider: {self._provider}")

    def _log(self, update: CRMUpdate) -> dict[str, Any]:
        record = {"ts": int(time.time()), "provider": self._provider, "data": asdict(update)}
        with self._log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        return {"ok": True, "logged": True}

    def _write_sharpify(self, update: CRMUpdate) -> dict[str, Any]:
        if not self._api_key or not self._base_url:
            raise NotImplementedError(
                "Sharpify CRM requires CRM_API_KEY and CRM_BASE_URL env vars. Provide endpoints to enable real writeback."
            )
        # Real implementation will go here once we have the endpoint contract.
        # Expected pattern: POST {base}/contacts/{email}/notes, PATCH deal stage, POST tasks.
        raise NotImplementedError("Sharpify writer not implemented yet — pending API contract.")
