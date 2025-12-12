from __future__ import annotations

from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

import pandas as pd
from fastapi import Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from inflation_report.analysis import compare_regions
from inflation_report.config import ReportConfig, load_config
from inflation_report.data import fetch_interest_rates, fetch_inflation_data, process_inflation_data


DATA_CACHE: Dict[str, Any] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Warm the cache on startup and clear it on shutdown.
    FastAPI recommends lifespan handlers over on_event.
    """
    try:
        DATA_CACHE["data"] = compute_data()
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
    records = df.copy()
    for col in records.columns:
        if pd.api.types.is_datetime64_any_dtype(records[col]):
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

    return DataResponse(
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


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/config", response_model=ConfigResponse)
def get_config() -> ConfigResponse:
    data: DataResponse = DATA_CACHE.get("data") or compute_data()
    DATA_CACHE["data"] = data
    return data.config


@app.get("/data", response_model=DataResponse)
def get_data() -> DataResponse:
    data: DataResponse = DATA_CACHE.get("data") or compute_data()
    DATA_CACHE["data"] = data
    return data


@app.post("/refresh", response_model=DataResponse)
def refresh_data(payload: DataRequest = Body(default=None)) -> DataResponse:
    try:
        data = compute_data(override=payload)
        DATA_CACHE["data"] = data
        return data
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
Weitere Ländercodes (ISO, kommagetrennt)

fr
