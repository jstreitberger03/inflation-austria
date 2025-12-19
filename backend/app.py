from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

import pandas as pd
from fastapi import Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from inflation_report.analysis import compare_regions
from inflation_report.config import ReportConfig, load_config
from inflation_report.data import fetch_interest_rates, fetch_inflation_data, process_inflation_data


DATA_CACHE: Dict[str, DataResponse] = {}


def _cache_key(override: Optional[DataRequest]) -> str:
    if override is None:
        return "default"
    # Always include countries, analysis_start_date, and historical_start_date in the cache key
    payload = {
        "countries": getattr(override, "countries", None),
        "analysis_start_date": getattr(override, "analysis_start_date", None),
        "historical_start_date": getattr(override, "historical_start_date", None),
    }
    return json.dumps(payload, sort_keys=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Warm the cache on startup and clear it on shutdown.
    FastAPI recommends lifespan handlers over on_event.
    """
    try:
        DATA_CACHE[_cache_key(None)] = compute_data()
    except Exception as exc:  # pragma: no cover - best-effort warmup
        print(f"Cache warmup failed: {exc}")
    yield
    DATA_CACHE.clear()


app = FastAPI(title="Inflation Report Austria API", version="0.2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _df_records(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Convert DataFrame to JSON-serializable records, memoizing datetime formatting per column.
    """
    if df.empty:
        return []

    records = df.copy()
    # Precompute string conversion map per datetime column to avoid repeated dtype checks downstream.
    for col, dtype in records.dtypes.items():
        if pd.api.types.is_datetime64_any_dtype(dtype):
            records[col] = records[col].dt.strftime("%Y-%m-%d")
    return records.to_dict(orient="records")


class ConfigResponse(BaseModel):
    countries: List[str]
    analysis_start_date: str
    historical_start_date: str
    forecast_months: int
    forecast_training_window: int
    forecast_display_limit: str


class DataResponse(BaseModel):
    config: ConfigResponse
    inflation: List[Dict[str, Any]]
    interest_rates: List[Dict[str, Any]]
    comparison: List[Dict[str, Any]]


class DataRequest(BaseModel):
    countries: Optional[List[str]] = None
    analysis_start_date: Optional[str] = None
    historical_start_date: Optional[str] = None


def compute_data(config_path: Optional[str] = None, override: Optional[DataRequest] = None) -> DataResponse:
    cache_key = _cache_key(override)
    if cache_key in DATA_CACHE:
        return DATA_CACHE[cache_key]

    cfg: ReportConfig = load_config(config_path)
    if override:
        if override.countries:
            cfg = ReportConfig(
                countries=override.countries,
                analysis_start_date=cfg.analysis_start_date,
                historical_start_date=cfg.historical_start_date,
                forecast_months=cfg.forecast_months,
                forecast_training_window=cfg.forecast_training_window,
                forecast_display_limit=cfg.forecast_display_limit,
            )
        if override.analysis_start_date:
            cfg = ReportConfig(
                countries=cfg.countries,
                analysis_start_date=pd.to_datetime(override.analysis_start_date),
                historical_start_date=cfg.historical_start_date,
                forecast_months=cfg.forecast_months,
                forecast_training_window=cfg.forecast_training_window,
                forecast_display_limit=cfg.forecast_display_limit,
            )
        if override.historical_start_date:
            cfg = ReportConfig(
                countries=cfg.countries,
                analysis_start_date=cfg.analysis_start_date,
                historical_start_date=pd.to_datetime(override.historical_start_date),
                forecast_months=cfg.forecast_months,
                forecast_training_window=cfg.forecast_training_window,
                forecast_display_limit=cfg.forecast_display_limit,
            )

    raw = fetch_inflation_data(cfg)
    df = process_inflation_data(raw, cfg)
    df = df.dropna(subset=["date"])

    interest_df = fetch_interest_rates()
    comparison_df = compare_regions(df)

    data_response = DataResponse(
        config=ConfigResponse(
            countries=cfg.countries,
            analysis_start_date=str(cfg.analysis_start_date.date()),
            historical_start_date=str(cfg.historical_start_date.date()),
            forecast_months=cfg.forecast_months,
            forecast_training_window=cfg.forecast_training_window,
            forecast_display_limit=str(cfg.forecast_display_limit.date()),
        ),
        inflation=_df_records(df),
        interest_rates=_df_records(interest_df) if not interest_df.empty else [],
        comparison=_df_records(comparison_df.reset_index()) if not comparison_df.empty else [],
    )
    DATA_CACHE[cache_key] = data_response
    return data_response


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/config", response_model=ConfigResponse)
def get_config() -> ConfigResponse:
    data: DataResponse = compute_data()
    return data.config


@app.get("/data", response_model=DataResponse)
def get_data() -> DataResponse:
    return compute_data()


@app.post("/refresh", response_model=DataResponse)
def refresh_data(payload: DataRequest = Body(default=None)) -> DataResponse:
    try:
        return compute_data(override=payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
