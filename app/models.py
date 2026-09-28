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
