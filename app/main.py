# TRON Energy Procurement Assistant

A multi-supplier TRON energy leasing procurement prototype for comparing single-vendor versus split-order sourcing options across multiple provider quote feeds.

## Project goals

- Integrate at least 2 supplier quote sources
- Normalize pricing across vendors into a single pricing model
- Filter options based on requested energy, rental duration, receiver address, budget, and latest delivery time
- Compare single-vendor and split-order procurement approaches
- Produce a complete cost breakdown with final recommendation and fallback options

## Tech stack

- Python 3.11+
- FastAPI
- Jinja2 templates
- Static HTML/CSS/JavaScript frontend

## Repository structure

- `app/` — FastAPI app and UI assets
- `app/services/` — quote source and comparison logic
- `app/static/` — frontend CSS and JavaScript
- `app/templates/` — HTML templates
- `requirements.txt` — dependencies

## Running locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then open:

- http://localhost:8000/
- API doc: http://localhost:8000/docs

## Example API request

```bash
curl -X POST http://localhost:8000/api/compare \
  -H "Content-Type: application/json" \
  -d '{
    "energy_units": 1200000,
    "rental_days": 30,
    "receiver_address": "TQjv4K2x4MVpVZQF1eYdqmYJd1hVGa6KZQ",
    "budget_usd": 5000,
    "latest_delivery_days": 7,
    "currency": "USD"
  }'
```

## Pricing model used by the prototype

The procurement engine standardizes each quote into the following comparable formula:

- Rental fee = rate_per_unit_per_day × energy_units × rental_days
- Service fee = rental_fee × service_fee_pct + fixed_service_fee
- Chain fee = chain_fee_per_unit × energy_units
- Other costs = estimated operational overhead
- Total = rental_fee + service_fee + chain_fee + other_costs

The split-order strategy uses the cheapest supplier first, with a second supplier filling the remainder while respecting min-order and capacity limits.

## Validation criteria status

The prototype includes:

- 2 integrated supplier quote feeds (demo real-time adapters)
- Unified pricing display and cost-normalization
- Single-vendor vs split-order comparison
- Cost breakdown and recommendation logic
- UI-based decision output

## Notes for production hardening

- Replace the mock supplier adapters with actual API integrations
- Add secure secret storage for provider tokens
- Add validation for receiver address and provider availability
- Add historical pricing snapshots to distinguish live and stale quotes
- Add audit logs and exports for procurement approval
