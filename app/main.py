from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


LEDGER_PATH = Path(__file__).resolve().parents[1] / "data" / "testnet_settlements.jsonl"


def create_testnet_settlement(purchase_id: str, amount_usd: float, recipient_address: str, supplier_name: str, approval_id: str) -> dict[str, Any]:
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "purchase_id": purchase_id,
        "approval_id": approval_id,
        "network": "Tron Nile testnet (simulated)",
        "amount_usd": round(float(amount_usd), 2),
        "recipient_address": recipient_address,
        "supplier_name": supplier_name,
        "status": "settled",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    tx_input = json.dumps(payload, sort_keys=True) + f"|{time.time_ns()}"
    tx_hash = "0x" + hashlib.sha256(tx_input.encode("utf-8")).hexdigest()

    settlement = {
        **payload,
        "tx_hash": tx_hash,
    }
    with LEDGER_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(settlement, sort_keys=True) + "\n")
    return settlement


def read_recent_settlements(limit: int = 20) -> list[dict[str, Any]]:
    if not LEDGER_PATH.exists():
        return []
    entries: list[dict[str, Any]] = []
    with LEDGER_PATH.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            entries.append(json.loads(line))
            if len(entries) >= limit:
                break
    return entries
