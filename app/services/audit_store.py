from __future__ import annotations

import json
from pathlib import Path
from typing import Any


AUDIT_PATH = Path(__file__).resolve().parents[1] / "app" / "data" / "agent_audit.jsonl"


def _ensure_file() -> None:
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not AUDIT_PATH.exists():
        AUDIT_PATH.write_text("", encoding="utf-8")


def append_record(record: dict[str, Any]) -> dict[str, Any]:
    _ensure_file()
    with AUDIT_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
    return record


def read_recent_records(limit: int = 25) -> list[dict[str, Any]]:
    _ensure_file()
    entries: list[dict[str, Any]] = []
    if not AUDIT_PATH.exists():
        return entries
    with AUDIT_PATH.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
            if len(entries) >= limit:
                break
    return entries


def find_by_approval_id(approval_id: str) -> dict[str, Any] | None:
    for record in read_recent_records(limit=200):
        if record.get("approval_id") == approval_id:
            return record
    return None
