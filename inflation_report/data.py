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

    df_long["country"] = df_long["geo"].map(COUNTRY_NAMES)
    df_long["category"] = df_long["coicop"].map(CATEGORY_NAMES)
    df_long["year"] = df_long["date"].dt.year
    df_long = df_long.sort_values("date")

    return df_long[["date", "year", "geo", "country", "coicop", "category", "inflation_rate"]]



def fetch_ecb_interest_rates(dataset: str = "irt_st_m") -> pd.DataFrame:
    """
    Fetch ECB main refinancing and deposit facility rates.

    Returns a tidy DataFrame with rate type and date columns.
    """
    print("Fetching ECB interest rates from Eurostat...")

    if eurostat is None:
        print("Eurostat library not available, creating synthetic interest rate data.")
        return _synthetic_interest_rates()

    try:
        df = eurostat.get_data_df(dataset, flags=False)
    except Exception as exc:  # pragma: no cover - network/service failures
        print(f"Error fetching ECB interest rates: {exc}")
        return _synthetic_interest_rates()

    if "geo\\TIME_PERIOD" in df.columns:
        df = df.rename(columns={"geo\\TIME_PERIOD": "geo"})

    df = df[((df["int_rt"] == "MRR_RT") | (df["int_rt"] == "DFR")) & (df["geo"] == "EA")]
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

    df_long["rate_type"] = df_long["int_rt"].map(
        {
            "MRR_RT": "main_refinancing",
            "DFR": "deposit_facility",
        }
    )
    return df_long[["date", "rate_type", "interest_rate"]]


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


def _synthetic_interest_rates() -> pd.DataFrame:
    """Create synthetic ECB rates when Eurostat is unavailable."""
    dates = pd.date_range("2000-01", "2025-10", freq="MS")
    main_rates: list[float] = []
    deposit_rates: list[float] = []

    for date in dates:
        if date < pd.Timestamp("2003-06-01"):
            main_rate = 4.5
        elif date < pd.Timestamp("2008-10-01"):
            main_rate = 2.0
        elif date < pd.Timestamp("2009-05-01"):
            main_rate = 1.25
        elif date < pd.Timestamp("2011-04-01"):
            main_rate = 1.0
        elif date < pd.Timestamp("2011-11-01"):
            main_rate = 1.5
        elif date < pd.Timestamp("2013-05-01"):
            main_rate = 1.0
        elif date < pd.Timestamp("2013-11-01"):
            main_rate = 0.5
        elif date < pd.Timestamp("2014-09-01"):
            main_rate = 0.25
        elif date < pd.Timestamp("2016-03-01"):
            main_rate = 0.05
        elif date < pd.Timestamp("2022-07-01"):
            main_rate = 0.0
        elif date < pd.Timestamp("2022-09-01"):
            main_rate = 0.5
        elif date < pd.Timestamp("2022-11-01"):
            main_rate = 1.25
        elif date < pd.Timestamp("2023-02-01"):
            main_rate = 2.0
        elif date < pd.Timestamp("2023-03-01"):
            main_rate = 2.5
        elif date < pd.Timestamp("2023-05-01"):
            main_rate = 3.0
        elif date < pd.Timestamp("2023-06-01"):
            main_rate = 3.5
        elif date < pd.Timestamp("2023-09-01"):
            main_rate = 4.0
        elif date < pd.Timestamp("2024-06-01"):
            main_rate = 4.5
        elif date < pd.Timestamp("2024-09-01"):
            main_rate = 4.25
        elif date < pd.Timestamp("2024-10-01"):
            main_rate = 3.65
        elif date < pd.Timestamp("2024-12-01"):
            main_rate = 3.40
        else:
            main_rate = 3.15

        if date < pd.Timestamp("2008-10-01"):
            deposit_rate = main_rate - 1.0
        elif date < pd.Timestamp("2009-05-01"):
            deposit_rate = main_rate - 0.75
        elif date < pd.Timestamp("2012-07-01"):
            deposit_rate = main_rate - 0.75
        elif date < pd.Timestamp("2014-06-01"):
            deposit_rate = 0.0
        elif date < pd.Timestamp("2014-09-01"):
            deposit_rate = -0.1
        elif date < pd.Timestamp("2015-12-01"):
            deposit_rate = -0.2
        elif date < pd.Timestamp("2016-03-01"):
            deposit_rate = -0.3
        elif date < pd.Timestamp("2019-09-01"):
            deposit_rate = -0.4
        elif date < pd.Timestamp("2022-07-01"):
            deposit_rate = -0.5
        elif date < pd.Timestamp("2022-09-01"):
            deposit_rate = 0.0
        elif date < pd.Timestamp("2022-11-01"):
            deposit_rate = 0.75
        elif date < pd.Timestamp("2023-02-01"):
            deposit_rate = 1.5
        elif date < pd.Timestamp("2023-03-01"):
            deposit_rate = 2.0
        elif date < pd.Timestamp("2023-05-01"):
            deposit_rate = 2.5
        elif date < pd.Timestamp("2023-06-01"):
            deposit_rate = 3.0
        elif date < pd.Timestamp("2023-09-01"):
            deposit_rate = 3.5
        elif date < pd.Timestamp("2024-06-01"):
            deposit_rate = 4.0
        elif date < pd.Timestamp("2024-09-01"):
            deposit_rate = 3.75
        elif date < pd.Timestamp("2024-10-01"):
            deposit_rate = 3.25
        elif date < pd.Timestamp("2024-12-01"):
            deposit_rate = 3.0
        else:
            deposit_rate = 2.75

        main_rates.append(main_rate)
        deposit_rates.append(deposit_rate)

    df_main = pd.DataFrame(
        {
            "date": dates,
            "rate_type": "main_refinancing",
            "interest_rate": main_rates,
        }
    )
    df_deposit = pd.DataFrame(
        {
            "date": dates,
            "rate_type": "deposit_facility",
            "interest_rate": deposit_rates,
        }
    )
    return pd.concat([df_main, df_deposit], ignore_index=True)
