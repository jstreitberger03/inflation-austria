"""Data loading and preparation utilities."""

from __future__ import annotations

import numpy as np
import pandas as pd

from typing import Mapping

from .config import ReportConfig, ensure_config
from .constants import CATEGORY_NAMES, COICOP_CATEGORIES, COUNTRY_NAMES

try:  # Optional import to allow offline work
    import eurostat
except ImportError:  # pragma: no cover - fallback for environments without eurostat
    eurostat = None

try:  # Optional Fed data fetcher
    import pandas_datareader as pdr
except ImportError:  # pragma: no cover - optional
    pdr = None

try:  # Optional country name mapping
    import pycountry
except ImportError:  # pragma: no cover - pycountry not available
    pycountry = None


def fetch_inflation_data(
    config: ReportConfig | Mapping[str, object],
    dataset: str = "prc_hicp_manr",
) -> pd.DataFrame:
    """
    Fetch HICP inflation data from Eurostat for the configured countries.

    Returns a wide DataFrame with one column per period.
    """
    config = ensure_config(config)
    print("Fetching inflation data from Eurostat...")
    countries = list(config.countries) + ["EA19"]

    if eurostat is None:
        print("Eurostat library not available, using sample data.")
        return _get_sample_data()

    try:
        df = eurostat.get_data_df(dataset, flags=False)
    except Exception as exc:  # pragma: no cover - network/service failures
        print(f"Error fetching data from Eurostat: {exc}")
        print("Falling back to sample data for demonstration purposes...")
        return _get_sample_data()

    if "geo\\TIME_PERIOD" in df.columns:
        df = df.rename(columns={"geo\\TIME_PERIOD": "geo"})

    df_filtered = df[(df["coicop"].isin(COICOP_CATEGORIES)) & (df["geo"].isin(countries))].copy()

    # Prefer EA20 when both Euro area codes are present
    if "EA20" in df_filtered["geo"].values and "EA19" in df_filtered["geo"].values:
        df_filtered = df_filtered[df_filtered["geo"] != "EA19"]

    print(f"Fetched {len(df_filtered)} records for selected regions")
    return df_filtered


def _country_label(code: str) -> str:
    """Return human-friendly country name for a code, with fallbacks."""
    if not code:
        return code
    # Overrides for German labels
    overrides = {
        "FR": "Frankreich",
    }
    if code in overrides:
        return overrides[code]
    if code in COUNTRY_NAMES:
        return COUNTRY_NAMES[code]
    if pycountry:
        try:
            c = pycountry.countries.get(alpha_2=code)
            if c and hasattr(c, "name"):
                return c.name
        except Exception:
            pass
    return code


def process_inflation_data(df: pd.DataFrame, config: ReportConfig | Mapping[str, object]) -> pd.DataFrame:
    """Clean and reshape raw inflation data into a tidy DataFrame."""
    config = ensure_config(config)
    time_columns = [col for col in df.columns if isinstance(col, str) and "-" in str(col)]

    df_long = df.melt(
        id_vars=["geo", "coicop"],
        value_vars=time_columns,
        var_name="period",
        value_name="inflation_rate",
    )
    df_long["date"] = pd.to_datetime(df_long["period"], format="%Y-%m", errors="coerce")
    df_long["inflation_rate"] = pd.to_numeric(df_long["inflation_rate"], errors="coerce")
    df_long = df_long.dropna(subset=["inflation_rate", "date"])
    df_long = df_long[df_long["date"] >= config.historical_start_date]

    df_long["country"] = df_long["geo"].apply(_country_label)
    df_long["category"] = df_long["coicop"].map(CATEGORY_NAMES)
    df_long["year"] = df_long["date"].dt.year
    df_long = df_long.sort_values("date")

    return df_long[["date", "year", "geo", "country", "coicop", "category", "inflation_rate"]]


def fetch_ecb_interest_rates(dataset: str = "irt_st_m") -> pd.DataFrame:
    """
    Fetch ECB main refinancing and deposit facility rates.
    Returns empty DataFrame on failure (no synthetic fallback).
    """
    print("Fetching ECB interest rates from Eurostat...")

    if eurostat is None:
        print("Eurostat library not available; ECB rates unavailable.")
        return pd.DataFrame(columns=["date", "rate_type", "interest_rate", "source"])

    try:
        df = eurostat.get_data_df(dataset, flags=False)
    except Exception as exc:  # pragma: no cover - network/service failures
        print(f"Error fetching ECB interest rates: {exc}")
        return pd.DataFrame(columns=["date", "rate_type", "interest_rate", "source"])

    if "geo\\TIME_PERIOD" in df.columns:
        df = df.rename(columns={"geo\\TIME_PERIOD": "geo"})

    df = df[((df["int_rt"] == "MRR_RT") | (df["int_rt"] == "DFR")) & (df["geo"].isin(["EA", "EA19", "EA20"]))]
    time_columns = [col for col in df.columns if isinstance(col, str) and "-" in str(col)]

    df_long = df.melt(
        id_vars=["geo", "int_rt"],
        value_vars=time_columns,
        var_name="period",
        value_name="interest_rate",
    )
    df_long["date"] = pd.to_datetime(df_long["period"], format="%Y-%m", errors="coerce")
    df_long["interest_rate"] = pd.to_numeric(df_long["interest_rate"], errors="coerce")
    df_long = df_long.dropna(subset=["interest_rate", "date"])
    df_long = df_long[df_long["date"] >= "2000-01-01"].sort_values("date")

    if df_long.empty:
        print("ECB interest rates empty after filtering.")
        return pd.DataFrame(columns=["date", "rate_type", "interest_rate", "source"])

    df_long["rate_type"] = df_long["int_rt"].map(
        {
            "MRR_RT": "main_refinancing",
            "DFR": "deposit_facility",
        }
    )
    df_long["source"] = "ECB"
    return df_long[["date", "rate_type", "interest_rate", "source"]]


def fetch_fed_interest_rates() -> pd.DataFrame:
    """
    Fetch effective Fed Funds rate (monthly) from FRED.
    Returns empty DataFrame on failure (no synthetic fallback).
    """
    print("Fetching Federal Reserve interest rates...")

    if pdr is None:
        print("pandas-datareader not available; Fed rates unavailable.")
        return pd.DataFrame(columns=["date", "rate_type", "interest_rate", "source"])

    try:
        # DFF = Effective Federal Funds Rate (daily). Aggregate to monthly mean.
        df = pdr.DataReader("DFF", "fred")
    except Exception as exc:  # pragma: no cover - network/service failures
        print(f"Error fetching Fed rates: {exc}")
        return pd.DataFrame(columns=["date", "rate_type", "interest_rate", "source"])

    if df.empty:
        print("Fed rates empty after fetch.")
        return pd.DataFrame(columns=["date", "rate_type", "interest_rate", "source"])

    df = df.reset_index().rename(columns={"DATE": "date", "DFF": "interest_rate"})
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["interest_rate"] = pd.to_numeric(df["interest_rate"], errors="coerce")
    df = df.dropna(subset=["date", "interest_rate"])
    df = df[df["date"] >= "2000-01-01"]

    # Monthly average
    df = (
        df.set_index("date")
        .resample("MS")
        .mean()
        .reset_index()
    )
    df["rate_type"] = "fed_funds_effective"
    df["source"] = "FED"
    return df[["date", "rate_type", "interest_rate", "source"]]


def fetch_interest_rates() -> pd.DataFrame:
    """Return combined ECB and FED interest rates."""
    ecb = fetch_ecb_interest_rates()
    fed = fetch_fed_interest_rates()
    frames = [df for df in (ecb, fed) if df is not None and not df.empty]
    if not frames:
        return pd.DataFrame(columns=["date", "rate_type", "interest_rate", "source"])
    return pd.concat(frames, ignore_index=True).sort_values("date")


def _get_sample_data() -> pd.DataFrame:
    """Provide sample inflation data for offline demonstration."""
    dates = pd.date_range("2023-01-01", "2025-10-31", freq="ME")
    periods = [f"{d.year}-{d.month:02d}" for d in dates]

    data = pd.DataFrame()
    data["geo"] = ["AT", "DE", "EA20"]

    rng = np.random.default_rng(seed=42)
    for period in periods:
        if period.startswith("2023"):
            base = [6.8, 6.1, 6.1]
        elif period.startswith("2024"):
            base = [4.2, 3.8, 3.8]
        else:
            base = [2.8, 2.3, 2.5]
        data[period] = base + rng.normal(0, 0.35, size=3)

    # Include required identifier columns for downstream steps
    data["coicop"] = "CP00"
    return data

