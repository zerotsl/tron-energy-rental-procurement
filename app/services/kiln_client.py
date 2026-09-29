from __future__ import annotations

import json
import os
import time
import uuid
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any

from app.models import AgentPolicy, RequirementInput
from app.services.audit_store import append_record, read_recent_records
from app.services.cost_engine import build_comparison
from app.services.kiln_client import call_kiln_model
from app.services.quote_sources import fetch_live_supplier_quotes


def default_agent_policy() -> dict[str, Any]:
    return {
        "agent_name": "procurement-agent",
        "max_total_spend_usd": 1800.0,
        "max_per_unit_cost_usd": 0.0021,
        "allowed_supplier_ids": ["energybridge-nodes"],
        "blocked_supplier_ids": ["tronlease-pro"],
        "max_delivery_days": 3,
        "require_human_approval": True,
        "allowed_receiver_prefixes": ["TQjv4K2x4MVpVZQF1eYdqmYJd1hVGa6KZQ"],
        "notes": "The agent may only spend within its whitelist and capped budget. Any violation results in immediate stop.",
    }


def _decision_context(requirement: RequirementInput, policy: dict[str, Any], quotes: list[Any]) -> dict[str, Any]:
    comparison = build_comparison(requirement, quotes)
    selected = comparison.get("selected_plan") or {}
    selected_supplier_names = selected.get("supplier_names") or []
    total_cost_usd = float(selected.get("total_cost_usd") or 0.0)
    estimated_delivery_days = selected.get("estimated_delivery_days")
    return {
        "comparison": comparison,
        "selected": selected,
        "selected_supplier_names": selected_supplier_names,
        "total_cost_usd": total_cost_usd,
        "estimated_delivery_days": estimated_delivery_days,
    }


def _kiln_prompt(requirement: RequirementInput, policy: dict[str, Any], context: dict[str, Any]) -> str:
    return (
        "You are a budgeting policy engine for a procurement agent. "
        "Check whether this purchase is allowed under the following constraints: "
        f"budget_cap={policy['max_total_spend_usd']} USD, "
        f"allowed_suppliers={policy['allowed_supplier_ids']}, "
        f"max_delivery_days={policy['max_delivery_days']}, "
        f"required_energy={requirement.energy_units}, rental_days={requirement.rental_days}, "
        f"latest_delivery_days={requirement.latest_delivery_days}, "
        f"selected_plan={context['selected']}. "
        "Return JSON with keys: status, reason, approved. "
        "status must be either 'approved' or 'stopped'."
    )


def _allowed_receiver(requirement: RequirementInput, policy: dict[str, Any]) -> bool:
    prefix = policy.get("allowed_receiver_prefixes", [])
    if not prefix:
        return True
    return any(requirement.receiver_address.startswith(item) for item in prefix)


def evaluate_purchase_decision(requirement: RequirementInput | dict[str, Any], policy: dict[str, Any] | None = None, quotes: list[Any] | None = None, scenario: str | None = None) -> dict[str, Any]:
    req = requirement if isinstance(requirement, RequirementInput) else RequirementInput(**requirement)
    active_policy = default_agent_policy() if policy is None else {**default_agent_policy(), **policy}
    supplier_quotes = quotes or fetch_live_supplier_quotes()
    context = _decision_context(req, active_policy, supplier_quotes)
    selected = context["selected"]
    total_cost = float(context["total_cost_usd"])
    allowed_suppliers = set(active_policy.get("allowed_supplier_ids", []))
    supplier_names = context["selected_supplier_names"]
    budget_ok = total_cost <= float(active_policy.get("max_total_spend_usd", req.budget_usd))
    supplier_ok = not supplier_names or all(name in allowed_suppliers for name in supplier_names)
    delivery_ok = context["estimated_delivery_days"] is None or context["estimated_delivery_days"] <= int(active_policy.get("max_delivery_days", req.latest_delivery_days))
    receiver_ok = _allowed_receiver(req, active_policy)

    kiln_result = call_kiln_model(
        system_prompt="You enforce purchase policy. Approve only when all conditions are satisfied.",
        user_prompt=_kiln_prompt(req, active_policy, context),
        session_id=scenario or "default-agent-session",
    )

    if not budget_ok:
        reason = f"Budget violation: total_cost_usd={total_cost} exceeds max_total_spend_usd={active_policy['max_total_spend_usd']}"
        return _stop_decision(req, active_policy, context, kiln_result, reason, scenario)
    if not supplier_ok:
        reason = f"Unauthorized supplier selection: {supplier_names} is not in allowed supplier list {sorted(allowed_suppliers)}"
        return _stop_decision(req, active_policy, context, kiln_result, reason, scenario)
    if not delivery_ok:
        reason = f"Delivery deadline violation: estimated_delivery_days={context['estimated_delivery_days']} exceeds max_delivery_days={active_policy['max_delivery_days']}"
        return _stop_decision(req, active_policy, context, kiln_result, reason, scenario)
    if not receiver_ok:
        reason = f"Receiver address {req.receiver_address} is outside the approved receiving list"
        return _stop_decision(req, active_policy, context, kiln_result, reason, scenario)

    approved = kiln_result.get("status") == "approved" or kiln_result.get("approved") is True
    output = {
        "session_id": scenario or "default-agent-session",
        "status": "approved" if approved else "stopped",
        "selected_supplier": supplier_names[0] if supplier_names else "none",
        "total_cost_usd": total_cost,
        "budget_limit_usd": float(active_policy.get("max_total_spend_usd", req.budget_usd)),
        "reason": kiln_result.get("reason") or "Approved by policy engine and human rules.",
        "approval_id": str(uuid.uuid4()),
        "kiln_model": kiln_result.get("model", "gpt-oss-120b"),
        "kiln_tokens_used": kiln_result.get("usage", {}).get("total_tokens"),
        "kiln_energy_kwh": kiln_result.get("energy_kwh"),
        "trace": [
            "supplier policy checked",
            "budget checked",
            "delivery window checked",
            "Kiln policy review completed",
        ],
        "scenario": scenario,
    }

    if output["status"] == "approved":
        settlement = create_testnet_settlement(
            purchase_id=output["approval_id"],
            amount_usd=total_cost,
            recipient_address=req.receiver_address,
            supplier_name=output["selected_supplier"],
            approval_id=output["approval_id"],
        )
        output["tx_hash"] = settlement["tx_hash"]
        output["chain_network"] = settlement["network"]
        append_record({
            "kind": "agent_approval",
            "status": "approved",
            "scenario": scenario,
            **output,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        return output

    return _stop_decision(req, active_policy, context, kiln_result, "Kiln rejected the spend request after policy checks", scenario)


def _stop_decision(requirement: RequirementInput, policy: dict[str, Any], context: dict[str, Any], kiln_result: dict[str, Any], reason: str, scenario: str | None) -> dict[str, Any]:
    decision = {
        "session_id": scenario or "default-agent-session",
        "status": "stopped",
        "selected_supplier": (context.get("selected_supplier_names") or [None])[0],
        "total_cost_usd": float(context.get("total_cost_usd") or 0.0),
        "budget_limit_usd": float(policy.get("max_total_spend_usd", requirement.budget_usd)),
        "reason": reason,
        "approval_id": str(uuid.uuid4()),
        "kiln_model": kiln_result.get("model", "gpt-oss-120b"),
        "kiln_tokens_used": kiln_result.get("usage", {}).get("total_tokens"),
        "kiln_energy_kwh": kiln_result.get("energy_kwh"),
        "trace": [
            "budget_policy_failed_or_supplier_not_allowed",
            "Kiln review captured high-risk route",
            "agent execution halted automatically",
        ],
        "scenario": scenario,
    }
    append_record({
        "kind": "agent_stop",
        "status": "stopped",
        "scenario": scenario,
        **decision,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    return decision


def generate_demo_scenario(name: str) -> dict[str, Any]:
    catalogue = fetch_live_supplier_quotes()
    policies = {
        "budget_overrun": {
            "max_total_spend_usd": 1800.0,
            "allowed_supplier_ids": ["energybridge-nodes"],
            "blocked_supplier_ids": ["tronlease-pro"],
            "max_delivery_days": 3,
            "require_human_approval": True,
        },
        "blocked_supplier": {
            "max_total_spend_usd": 5000.0,
            "allowed_supplier_ids": ["energybridge-nodes"],
            "blocked_supplier_ids": ["tronlease-pro"],
            "max_delivery_days": 7,
            "require_human_approval": True,
        },
        "deadline_violation": {
            "max_total_spend_usd": 5000.0,
            "allowed_supplier_ids": ["energybridge-nodes", "tronlease-pro"],
            "blocked_supplier_ids": [],
            "max_delivery_days": 2,
            "require_human_approval": True,
        },
    }

    scenarios = {
        "budget_overrun": {
            "energy_units": 1200000,
            "rental_days": 30,
            "receiver_address": "TQjv4K2x4MVpVZQF1eYdqmYJd1hVGa6KZQ",
            "budget_usd": 2500,
            "latest_delivery_days": 7,
            "currency": "USD",
        },
        "blocked_supplier": {
            "energy_units": 1200000,
            "rental_days": 30,
            "receiver_address": "TQjv4K2x4MVpVZQF1eYdqmYJd1hVGa6KZQ",
            "budget_usd": 5000,
            "latest_delivery_days": 7,
            "currency": "USD",
        },
        "deadline_violation": {
            "energy_units": 1200000,
            "rental_days": 30,
            "receiver_address": "TQjv4K2x4MVpVZQF1eYdqmYJd1hVGa6KZQ",
            "budget_usd": 5000,
            "latest_delivery_days": 1,
            "currency": "USD",
        },
    }

    policy = policies.get(name, policies["budget_overrun"])
    requirement = scenarios.get(name, scenarios["budget_overrun"])
    return evaluate_purchase_decision(requirement, policy=policy, quotes=catalogue, scenario=name)


def approve_pending_purchase(approval_id: str) -> dict[str, Any]:
    record = None
    for entry in read_recent_records(limit=200):
        if entry.get("approval_id") == approval_id:
            record = entry
            break
    if not record:
        return {"status": "not_found", "approval_id": approval_id}
    if record.get("status") != "stopped":
        return {"status": "already_resolved", "approval_id": approval_id, "record": record}
    return {
        "status": "approval_rejected",
        "approval_id": approval_id,
        "message": "This purchase was stopped because it violated a hard spend boundary; a human cannot override the policy by accident.",
        "record": record,
    }
