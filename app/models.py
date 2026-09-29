from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class QuoteSource(BaseModel):
    model_config = ConfigDict(extra="ignore")

    supplier_id: str
    supplier_name: str
    source_name: str
    source_url: str
    currency: str = "USD"
    quoted_unit: str = "energy_unit"
    rate_per_unit_per_day: float
    min_order_units: int
    available_energy_units: int
    max_order_units: int
    rental_period_days: int
    estimated_delivery_days: int
    service_fee_pct: float = 0.0
    fixed_service_fee: float = 0.0
    chain_fee_per_unit: float = 0.0
    notes: str = ""


class RequirementInput(BaseModel):
    energy_units: int = Field(..., gt=0)
    rental_days: int = Field(..., gt=0)
    receiver_address: str = Field(..., min_length=10)
    budget_usd: float = Field(..., gt=0)
    latest_delivery_days: int = Field(..., gt=0)
    currency: str = "USD"

    @field_validator("receiver_address")
    @classmethod
    def validate_address(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("receiver_address is required")
        if len(cleaned) < 10:
            raise ValueError("receiver_address is too short")
        return cleaned


class CostBreakdown(BaseModel):
    rental_fee: float
    service_fee: float
    chain_fee: float
    other_costs: float
    subtotal: float
    total: float


class SupplierOption(BaseModel):
    supplier_id: str
    supplier_name: str
    source_name: str
    source_url: str
    required_energy_units: int
    rental_period_days: int
    cost_breakdown: CostBreakdown
    total_cost_usd: float
    per_unit_cost_usd: float
    estimated_delivery_days: int
    feasible: bool
    reasons: list[str] = []


class ComparisonResult(BaseModel):
    requirement_summary: dict
    selected_plan: dict
    options: list[dict]
    supplier_catalog: list[dict]
    notes: list[str]


class AgentPolicy(BaseModel):
    agent_name: str = "procurement-agent"
    max_total_spend_usd: float = 5000.0
    max_per_unit_cost_usd: float = 0.0
    allowed_supplier_ids: list[str] = Field(default_factory=lambda: ["energybridge-nodes"])
    blocked_supplier_ids: list[str] = Field(default_factory=list)
    max_delivery_days: int = 7
    require_human_approval: bool = True
    allowed_receiver_prefixes: list[str] = Field(default_factory=lambda: ["TQjv4K2x4MVpVZQF1eYdqmYJd1hVGa6KZQ"])
    notes: str = "Agent pays only approved suppliers within cap; any violation halts execution."


class AgentDecisionRequest(BaseModel):
    requirement: RequirementInput
    policy: AgentPolicy | None = None
    scenario: str | None = None


class AgentDecision(BaseModel):
    session_id: str
    status: str
    selected_supplier: str | None = None
    total_cost_usd: float | None = None
    budget_limit_usd: float | None = None
    reason: str
    approval_id: str | None = None
    kiln_model: str | None = None
    kiln_tokens_used: int | None = None
    kiln_energy_kwh: float | None = None
    tx_hash: str | None = None
    trace: list[str] = Field(default_factory=list)
