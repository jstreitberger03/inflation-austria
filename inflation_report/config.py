"""Configuration helpers for the inflation report backend/dashboard."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

import pandas as pd
import yaml

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[1] / "config.yaml"
DEFAULT_CONFIG: dict[str, object] = {
    "countries": ["AT", "DE", "EA20"],
    "analysis_start_date": "2020-01-01",
    "historical_start_date": "2002-01-01",
    "forecast_months": 12,
    "forecast_training_window": 24,
    "forecast_display_limit": "2026-03-31",
}


@dataclass(frozen=True)
class ReportConfig:
    """Parsed configuration with typed fields for the report."""

    countries: list[str]
    analysis_start_date: pd.Timestamp
    historical_start_date: pd.Timestamp
    forecast_months: int
    forecast_training_window: int
    forecast_display_limit: pd.Timestamp

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "ReportConfig":
        """Create a configuration object from a raw mapping."""
        return cls(
            countries=list(_ensure_list(data.get("countries", []))),
            analysis_start_date=pd.to_datetime(data.get("analysis_start_date")),
            historical_start_date=pd.to_datetime(data.get("historical_start_date")),
            forecast_months=int(data.get("forecast_months", 12)),
            forecast_training_window=int(data.get("forecast_training_window", 24)),
            forecast_display_limit=pd.to_datetime(data.get("forecast_display_limit")),
        )


def load_config(path: str | Path | None = None) -> ReportConfig:
    """Load the YAML config file into a typed config object."""
    cfg_path = Path(path) if path else DEFAULT_CONFIG_PATH
    raw: dict[str, object]
    if cfg_path.exists():
        with open(cfg_path, "r", encoding="utf-8") as handle:
            raw = yaml.safe_load(handle) or {}
    else:
        raw = DEFAULT_CONFIG
    return ReportConfig.from_mapping(raw)


def ensure_config(config: ReportConfig | Mapping[str, Any]) -> ReportConfig:
    """Coerce a dict-like config into a ReportConfig instance."""
    if isinstance(config, ReportConfig):
        return config
    return ReportConfig.from_mapping(dict(config))


def _ensure_list(value: Any) -> Iterable[Any]:
    if isinstance(value, (list, tuple)):
        return value
    return [value]
