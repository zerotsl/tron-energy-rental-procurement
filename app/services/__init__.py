from __future__ import annotations

from typing import Any

from app.models import QuoteSource, RequirementInput


def get_demo_sources() -> list[QuoteSource]:
    return [
        QuoteSource(
            supplier_id="tronlease-pro",
            supplier_name="TronLease Pro",
            source_name="TronLease Pro Live Quote API",
            source_url="https://api.tronleasepro.example/quotes/live",
            currency="USD",
            quoted_unit="energy_unit",
            rate_per_unit_per_day=0.0000036,
            min_order_units=150000,
            available_energy_units=4200000,
            max_order_units=2400000,
            rental_period_days=30,
            estimated_delivery_days=2,
            service_fee_pct=0.045,
            fixed_service_fee=45.0,
            chain_fee_per_unit=0.00012,
            notes="Fastest delivery and strong availability; suited for urgent energy replenishment.",
        ),
        QuoteSource(
            supplier_id="energybridge-nodes",
            supplier_name="EnergyBridge Nodes",
            source_name="EnergyBridge Nodes Quote Feed",
            source_url="https://quotes.energybridge.example/v1/energy",
            currency="USD",
            quoted_unit="energy_unit",
            rate_per_unit_per_day=0.0000032,
            min_order_units=180000,
            available_energy_units=3600000,
            max_order_units=2200000,
            rental_period_days=45,
            estimated_delivery_days=3,
            service_fee_pct=0.035,
            fixed_service_fee=65.0,
            chain_fee_per_unit=0.00011,
            notes="Best cost-per-unit for medium and long-term rental windows.",
        ),
    ]


def fetch_live_supplier_quotes() -> list[QuoteSource]:
    """Placeholder for real vendor integrations.

    Real implementations would hit each vendor API, normalize response payloads,
    and return QuoteSource instances. This demo version intentionally returns
    standard mock quotes so the engine behaves as a real procurement comparator.
    """
    return get_demo_sources()


def normalize_requirement(requirement: RequirementInput | dict[str, Any]) -> RequirementInput:
    if isinstance(requirement, RequirementInput):
        return requirement
    return RequirementInput(**requirement)
