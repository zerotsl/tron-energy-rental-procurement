from __future__ import annotations

from typing import Any

from app.models import CostBreakdown, QuoteSource, RequirementInput


def _calculate_breakdown(quote: QuoteSource, energy_units: int, rental_days: int) -> dict[str, float]:
    rental_fee = quote.rate_per_unit_per_day * energy_units * rental_days
    service_fee = (rental_fee * quote.service_fee_pct) + quote.fixed_service_fee
    chain_fee = quote.chain_fee_per_unit * energy_units
    other_costs = max(0.0, (energy_units / 1000000) * 8.5)
    subtotal = rental_fee + service_fee + chain_fee
    total = subtotal + other_costs

    return {
        "rental_fee": round(rental_fee, 2),
        "service_fee": round(service_fee, 2),
        "chain_fee": round(chain_fee, 2),
        "other_costs": round(other_costs, 2),
        "subtotal": round(subtotal, 2),
        "total": round(total, 2),
    }


def _rate_per_unit_cost(quote: QuoteSource, energy_units: int, rental_days: int) -> float:
    breakdown = _calculate_breakdown(quote, energy_units, rental_days)
    return breakdown["total"] / max(energy_units, 1)


def _supplier_is_feasible(quote: QuoteSource, requirement: RequirementInput) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    available = quote.available_energy_units >= requirement.energy_units
    if not available and quote.available_energy_units < requirement.energy_units:
        reasons.append(
            f"available capacity {quote.available_energy_units} is below required {requirement.energy_units}"
        )

    if quote.min_order_units > requirement.energy_units:
        reasons.append(
            f"min order {quote.min_order_units} exceeds requested energy {requirement.energy_units}"
        )

    if quote.rental_period_days < requirement.rental_days:
        reasons.append(
            f"rental window {quote.rental_period_days} days is shorter than requested {requirement.rental_days}"
        )

    if quote.estimated_delivery_days > requirement.latest_delivery_days:
        reasons.append(
            f"estimated delivery {quote.estimated_delivery_days} days exceeds latest acceptable {requirement.latest_delivery_days} days"
        )

    return len(reasons) == 0, reasons


def build_single_supplier_options(quotes: list[QuoteSource], requirement: RequirementInput) -> list[dict[str, Any]]:
    options: list[dict[str, Any]] = []
    for quote in quotes:
        feasible, reasons = _supplier_is_feasible(quote, requirement)
        if not feasible:
            continue

        breakdown = _calculate_breakdown(quote, requirement.energy_units, requirement.rental_days)
        per_unit = breakdown["total"] / requirement.energy_units
        options.append(
            {
                "type": "single_supplier",
                "supplier_id": quote.supplier_id,
                "supplier_name": quote.supplier_name,
                "source_name": quote.source_name,
                "source_url": quote.source_url,
                "required_energy_units": requirement.energy_units,
                "rental_period_days": requirement.rental_days,
                "cost_breakdown": breakdown,
                "total_cost_usd": breakdown["total"],
                "per_unit_cost_usd": round(per_unit, 6),
                "estimated_delivery_days": quote.estimated_delivery_days,
                "feasible": True,
                "reasons": [],
            }
        )

    options.sort(key=lambda item: item["total_cost_usd"])
    return options


def _build_split_pair(quote_a: QuoteSource, quote_b: QuoteSource, requirement: RequirementInput) -> dict[str, Any] | None:
    if quote_a.available_energy_units + quote_b.available_energy_units < requirement.energy_units:
        return None

    ordered = sorted([quote_a, quote_b], key=lambda q: q.rate_per_unit_per_day)
    cheaper, more_expensive = ordered

    cheaper_allocation = min(requirement.energy_units, cheaper.available_energy_units, cheaper.max_order_units)
    if cheaper_allocation < cheaper.min_order_units:
        cheaper_allocation = cheaper.min_order_units

    expensive_allocation = requirement.energy_units - cheaper_allocation
    if expensive_allocation < 0:
        return None

    if expensive_allocation > more_expensive.available_energy_units:
        return None
    if expensive_allocation > more_expensive.max_order_units:
        return None
    if expensive_allocation < more_expensive.min_order_units and requirement.energy_units > more_expensive.min_order_units:
        # try reverse split
        expensive_allocation = min(requirement.energy_units, more_expensive.available_energy_units, more_expensive.max_order_units)
        if expensive_allocation < more_expensive.min_order_units:
            return None
        cheaper_allocation = requirement.energy_units - expensive_allocation
        if cheaper_allocation < cheaper.min_order_units:
            return None

    if cheaper_allocation > cheaper.max_order_units or expensive_allocation > more_expensive.max_order_units:
        return None

    if cheaper_allocation < cheaper.min_order_units or expensive_allocation < more_expensive.min_order_units:
        return None

    if cheaper.estimated_delivery_days > requirement.latest_delivery_days or more_expensive.estimated_delivery_days > requirement.latest_delivery_days:
        return None

    if cheaper.rental_period_days < requirement.rental_days or more_expensive.rental_period_days < requirement.rental_days:
        return None

    cheaper_breakdown = _calculate_breakdown(cheaper, int(cheaper_allocation), requirement.rental_days)
    expensive_breakdown = _calculate_breakdown(more_expensive, int(expensive_allocation), requirement.rental_days)
    total_rental = cheaper_breakdown["total"] + expensive_breakdown["total"]
    total_service = cheaper_breakdown["service_fee"] + expensive_breakdown["service_fee"]
    total_chain = cheaper_breakdown["chain_fee"] + expensive_breakdown["chain_fee"]
    total_other = cheaper_breakdown["other_costs"] + expensive_breakdown["other_costs"]

    allocations = {
        cheaper.supplier_id: int(cheaper_allocation),
        more_expensive.supplier_id: int(expensive_allocation),
    }

    return {
        "type": "split_order",
        "suppliers": [
            {
                "supplier_id": cheaper.supplier_id,
                "supplier_name": cheaper.supplier_name,
                "allocated_energy_units": int(cheaper_allocation),
                "cost_breakdown": cheaper_breakdown,
            },
            {
                "supplier_id": more_expensive.supplier_id,
                "supplier_name": more_expensive.supplier_name,
                "allocated_energy_units": int(expensive_allocation),
                "cost_breakdown": expensive_breakdown,
            },
        ],
        "strategy": "cheapest-first split allocation",
        "allocations": allocations,
        "required_energy_units": requirement.energy_units,
        "rental_period_days": requirement.rental_days,
        "cost_breakdown": {
            "rental_fee": round(total_rental, 2),
            "service_fee": round(total_service, 2),
            "chain_fee": round(total_chain, 2),
            "other_costs": round(total_other, 2),
            "subtotal": round(total_rental + total_service + total_chain, 2),
            "total": round(total_rental + total_service + total_chain + total_other, 2),
        },
        "total_cost_usd": round(total_rental + total_service + total_chain + total_other, 2),
        "estimated_delivery_days": max(cheaper.estimated_delivery_days, more_expensive.estimated_delivery_days),
        "feasible": True,
        "reasons": [],
    }


def build_split_order_options(quotes: list[QuoteSource], requirement: RequirementInput) -> list[dict[str, Any]]:
    options: list[dict[str, Any]] = []
    for i, quote_a in enumerate(quotes):
        for quote_b in quotes[i + 1 :]:
            option = _build_split_pair(quote_a, quote_b, requirement)
            if option:
                options.append(option)
    options.sort(key=lambda item: item["total_cost_usd"])
    return options


def build_comparison(requirement: RequirementInput, quotes: list[QuoteSource]) -> dict[str, Any]:
    single_options = build_single_supplier_options(quotes, requirement)
    split_options = build_split_order_options(quotes, requirement)

    candidate_options = single_options + split_options
    if not candidate_options:
        return {
            "requirement_summary": {
                "energy_units": requirement.energy_units,
                "rental_days": requirement.rental_days,
                "receiver_address": requirement.receiver_address,
                "budget_usd": requirement.budget_usd,
                "latest_delivery_days": requirement.latest_delivery_days,
            },
            "selected_plan": {
                "status": "no_feasible_plan",
                "reason": "No supplier can satisfy the requested energy volume, delivery schedule, or minimum order constraints.",
            },
            "options": [],
            "supplier_catalog": [
                {
                    "supplier_id": q.supplier_id,
                    "supplier_name": q.supplier_name,
                    "source_name": q.source_name,
                    "source_url": q.source_url,
                    "currency": q.currency,
                    "quoted_unit": q.quoted_unit,
                    "rate_per_unit_per_day": q.rate_per_unit_per_day,
                    "min_order_units": q.min_order_units,
                    "available_energy_units": q.available_energy_units,
                    "max_order_units": q.max_order_units,
                    "rental_period_days": q.rental_period_days,
                    "estimated_delivery_days": q.estimated_delivery_days,
                }
                for q in quotes
            ],
            "notes": [
                "Current supplier quotes are below the request thresholds for a valid purchase plan.",
                "The comparison engine uses unified pricing and delivery constraints, then selects the cheapest feasible option.",
            ],
        }

    cheapest = min(candidate_options, key=lambda option: option["total_cost_usd"])
    selected = {
        "plan_type": cheapest["type"],
        "total_cost_usd": cheapest["total_cost_usd"],
        "supplier_names": (
            [q["supplier_name"] for q in cheapest["suppliers"]]
            if cheapest["type"] == "split_order"
            else [cheapest["supplier_name"]]
        ),
        "estimated_delivery_days": cheapest.get("estimated_delivery_days", None),
    }

    for option in candidate_options:
        if option["total_cost_usd"] <= requirement.budget_usd:
            selected = {
                "plan_type": option["type"],
                "total_cost_usd": option["total_cost_usd"],
                "supplier_names": (
                    [q["supplier_name"] for q in option["suppliers"]]
                    if option["type"] == "split_order"
                    else [option["supplier_name"]]
                ),
                "estimated_delivery_days": option.get("estimated_delivery_days", None),
            }
            break

    return {
        "requirement_summary": {
            "energy_units": requirement.energy_units,
            "rental_days": requirement.rental_days,
            "receiver_address": requirement.receiver_address,
            "budget_usd": requirement.budget_usd,
            "latest_delivery_days": requirement.latest_delivery_days,
        },
        "selected_plan": selected,
        "options": candidate_options,
        "supplier_catalog": [
            {
                "supplier_id": q.supplier_id,
                "supplier_name": q.supplier_name,
                "source_name": q.source_name,
                "source_url": q.source_url,
                "currency": q.currency,
                "quoted_unit": q.quoted_unit,
                "rate_per_unit_per_day": q.rate_per_unit_per_day,
                "min_order_units": q.min_order_units,
                "available_energy_units": q.available_energy_units,
                "max_order_units": q.max_order_units,
                "rental_period_days": q.rental_period_days,
                "estimated_delivery_days": q.estimated_delivery_days,
                "notes": q.notes,
            }
            for q in quotes
        ],
        "notes": [
            "Calculation basis: rental fee + service fee + chain fee + other related costs.",
            "Search range: all currently integrated suppliers that meet energy, budget, and delivery constraints.",
            "Recommendation is chosen based on the lowest feasible total cost while satisfying the request and contract conditions.",
        ],
    }
