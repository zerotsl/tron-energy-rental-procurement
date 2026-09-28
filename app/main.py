from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.models import RequirementInput
from app.services.cost_engine import build_comparison
from app.services.quote_sources import fetch_live_supplier_quotes

app = FastAPI(title="TRON Energy Procurement Assistant", version="0.1.0")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "tron-energy-procurement", "quote_mode": "demo"}


@app.get("/api/suppliers")
async def list_suppliers():
    return [quote.model_dump() for quote in fetch_live_supplier_quotes()]


@app.post("/api/compare")
async def compare(requirement: RequirementInput):
    result = build_comparison(requirement, fetch_live_supplier_quotes())
    return JSONResponse(content=result)
