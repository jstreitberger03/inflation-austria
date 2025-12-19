"""Visualization helpers using Matplotlib and python-plot-template."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from python_plot_template import (
    add_hline,
    add_vline,
    apply_template,
    palette_colors,
    save_plot,
    set_labels,
    set_limits,
)

from .config import ReportConfig, ensure_config
from .constants import COUNTRY_NAMES

try:
    import locale
except ImportError:  # pragma: no cover - locale unavailable
    locale = None


PALETTE_REGIONS = ["#4477AA", "#EE6677", "#228833"]
GRID_LIGHT = "#D5DBE5"


def _set_locale(preferences: tuple[str, ...] = ("de_DE.UTF-8", "German_Germany.1252", "deu_deu")) -> None:
    """Set locale for consistent month names."""
    if locale is None:
        return
    for loc in preferences:
        try:
            locale.setlocale(locale.LC_TIME, loc)
            return
        except Exception:
            continue


def _country_palette(countries: Iterable[str]) -> dict[str, str]:
    """Map names to consistent Tol colors."""
    colors = list(PALETTE_REGIONS) + list(palette_colors("muted"))
    mapping: dict[str, str] = {}
    for idx, country in enumerate(countries):
        mapping[country] = colors[idx % len(colors)]
    return mapping


def _style_time_axis(ax: plt.Axes, interval: int = 3, fmt: str = "%b %Y", rotation: int = 35) -> None:
    """Apply consistent monthly ticks and label rotation."""
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=interval))
    ax.xaxis.set_major_formatter(mdates.DateFormatter(fmt))
    for label in ax.get_xticklabels():
        label.set_rotation(rotation)
        label.set_horizontalalignment("right")
    ax.margins(x=0.01)


def _add_caption(fig: plt.Figure, text: str) -> None:
    """Place a subtle caption in the lower-left corner."""
    fig.text(0.01, 0.01, text, fontsize=9, color="#5f6368", ha="left", va="bottom")


def _code_to_country(code: str) -> str:
    """Convert ISO-2 code to country name with graceful fallback."""
    if code in COUNTRY_NAMES:
        return COUNTRY_NAMES[code]
    if len(code) == 2:
        try:
            import pycountry

            match = pycountry.countries.get(alpha_2=code)
            if match:
                return match.name
        except Exception:
            pass
    return code


def create_output_directory(output_dir: str | Path = "output") -> str:
    """Create output directory for reports if it doesn't exist."""
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    return str(path)


def plot_inflation_comparison(df, config: ReportConfig, forecast_df=None, output_dir: str | Path = "output"):
    """Create a line plot comparing inflation rates with forecast."""
    config = ensure_config(config)
    from .forecasting import forecast_inflation

    _set_locale()
    apply_template(palette="bright", font_size=12)

    df_hist = df[(df["date"] >= config.analysis_start_date) & (df["coicop"] == "CP00")].copy()
    if df_hist.empty:
        print("No overall inflation data found for comparison plot after filtering.")
        return None

    if forecast_df is None:
        forecast_df = forecast_inflation(df_hist, config)
    forecast_df = forecast_df.copy()
    forecast_df = forecast_df[forecast_df["date"] <= pd.to_datetime(config.forecast_display_limit)]
    if "country" not in forecast_df.columns and "geo" in forecast_df.columns:
        forecast_df["country"] = forecast_df["geo"].map(COUNTRY_NAMES)

    countries = [c for c in ["Österreich", "Deutschland", "Eurozone"] if c in df_hist["country"].unique()]
    if not countries:
        countries = sorted(df_hist["country"].dropna().unique())
    color_map = _country_palette(countries)

    fig, ax = plt.subplots(figsize=(14, 6.5))

    y_min, y_max = np.inf, -np.inf
    for country in countries:
        hist = df_hist[df_hist["country"] == country].sort_values("date")
        if hist.empty:
            continue
        ax.plot(hist["date"], hist["inflation_rate"], color=color_map[country], linewidth=2.2, label=f"{country} Historisch")
        ax.scatter(hist["date"], hist["inflation_rate"], color=color_map[country], s=18, alpha=0.8, zorder=3)

        y_min = min(y_min, hist["inflation_rate"].min())
        y_max = max(y_max, hist["inflation_rate"].max())

        fc = forecast_df[forecast_df["country"] == country].sort_values("date")
        if fc.empty:
            continue

        ax.plot(fc["date"], fc["inflation_rate"], color=color_map[country], linewidth=2.0, linestyle="--", label=f"{country} Prognose")
        if {"lower_bound", "upper_bound"}.issubset(fc.columns):
            ax.fill_between(fc["date"], fc["lower_bound"], fc["upper_bound"], color=color_map[country], alpha=0.14, linewidth=0)
            y_min = min(y_min, fc["lower_bound"].min())
            y_max = max(y_max, fc["upper_bound"].max())
        else:
            y_min = min(y_min, fc["inflation_rate"].min())
            y_max = max(y_max, fc["inflation_rate"].max())

        # Connect last historical point to forecast start for smoother handoff
        last_hist = hist.iloc[-1]
        first_fc = fc.iloc[0]
        ax.plot([last_hist["date"], first_fc["date"]], [last_hist["inflation_rate"], first_fc["inflation_rate"]], color=color_map[country], linewidth=1.6, linestyle=":")

    events = [
        (pd.Timestamp("2020-03-11"), "COVID-19", 2),
        (pd.Timestamp("2022-02-24"), "Ukraine-Krieg", 8.5),
    ]
    for date, label, ypos in events:
        add_vline(date, ax=ax, color="#555555", linestyle="--", linewidth=0.9, alpha=0.7)
        ax.text(date, ypos, label, rotation=90, va="bottom", ha="right", fontsize=8.5, color="#555555")

    set_labels("Inflationsrate im Vergleich (mit Prognose)", "", "Inflationsrate (%)", ax=ax)
    _style_time_axis(ax, interval=3, fmt="%b %Y", rotation=30)
    margin = max(0.5, (y_max - y_min) * 0.08)
    set_limits(ylim=(np.floor(y_min - margin), np.ceil(y_max + margin)), ax=ax)
    ax.yaxis.set_major_locator(mticker.MultipleLocator(1))
    ax.legend(loc="upper right", ncol=2)
    _add_caption(fig, "Quelle: Eurostat (2025) — Schattierung: 95%-Konfidenzintervall")

    output_path = Path(output_dir) / "inflation_comparison.svg"
    save_plot(output_path, dpi=300, fig=fig)
    plt.close(fig)
    print(f"Saved plot to {output_path}")
    return str(output_path)


def plot_difference(comparison_df, config: ReportConfig, output_dir: str | Path = "output"):
    """Create a bar plot showing the difference in inflation rates."""
    config = ensure_config(config)
    apply_template(palette="muted", font_size=11)

    if "Difference (AT - EA)" not in comparison_df.columns:
        print("No difference column found in comparison data")
        return None

    if hasattr(comparison_df.index, "year"):
        comparison_df = comparison_df[comparison_df.index >= config.analysis_start_date].copy()
    else:
        comparison_df = comparison_df[comparison_df.index >= pd.to_datetime(config.analysis_start_date)].copy()

    plot_df = comparison_df.reset_index()
    plot_df["color"] = np.where(plot_df["Difference (AT - EA)"] < 0, "#228833", "#EE6677")

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(plot_df["date"], plot_df["Difference (AT - EA)"], color=plot_df["color"], width=22)
    add_hline(0, ax=ax, color="#2d2d2d", linestyle="--", linewidth=0.9)

    set_labels("Inflationsdifferenz: Österreich vs. Eurozone", "", "Differenz (Prozentpunkte)", ax=ax)
    _style_time_axis(ax, interval=4, fmt="%b %Y", rotation=35)
    ax.yaxis.set_major_locator(mticker.MultipleLocator(0.5))
    _add_caption(fig, "Quelle: Eurostat (2025). Positive Werte = höhere Inflation in Österreich.")

    output_path = Path(output_dir) / "inflation_difference.svg"
    save_plot(output_path, dpi=300, fig=fig)
    plt.close(fig)
    print(f"Saved plot to {output_path}")
    return str(output_path)


def plot_inflation_components(df, output_dir: str | Path = "output"):
    """Create a line plot showing the components of inflation for Austria."""
    _set_locale()
    apply_template(palette="bright", font_size=11)

    df_austria = df[(df["geo"] == "AT") & (df["date"] >= "2020-01-01")].copy()
    if df_austria.empty or "category" not in df_austria.columns:
        print("No component data found for Austria to plot.")
        return None

    categories = df_austria["category"].unique().tolist()
    colors = _country_palette(categories)

    fig, ax = plt.subplots(figsize=(14, 6.5))
    for cat in categories:
        subset = df_austria[df_austria["category"] == cat].sort_values("date")
        ax.plot(subset["date"], subset["inflation_rate"], label=cat, color=colors[cat], linewidth=2.0)
        ax.scatter(subset["date"], subset["inflation_rate"], color=colors[cat], s=18, alpha=0.8)

    set_labels("Bestandteile der Inflation in Österreich (seit 2020)", "", "Inflationsrate (%)", ax=ax)
    _style_time_axis(ax, interval=3, fmt="%b %Y", rotation=30)
    y_min, y_max = df_austria["inflation_rate"].min(), df_austria["inflation_rate"].max()
    margin = max(0.5, (y_max - y_min) * 0.08)
    set_limits(ylim=(np.floor(y_min - margin), np.ceil(y_max + margin)), ax=ax)
    ax.yaxis.set_major_locator(mticker.MultipleLocator(5))
    ax.legend(loc="upper left", ncol=2, title="Inflationskomponente")
    _add_caption(fig, "Quelle: Eurostat (2025). HICP - Harmonisierter Verbraucherpreisindex.")

    output_path = Path(output_dir) / "inflation_components_at.svg"
    save_plot(output_path, dpi=300, fig=fig)
    plt.close(fig)
    print(f"Saved component plot to {output_path}")
    return str(output_path)


def plot_statistics_comparison(stats, config: ReportConfig, output_dir: str | Path = "output"):
    """Create a bar plot comparing key statistics between regions."""
    config = ensure_config(config)
    apply_template(palette="bright", font_size=11)

    metrics = [
        ("mean", "Durchschnittliche Inflationsrate (%)"),
        ("median", "Median Inflationsrate (%)"),
        ("min", "Minimale Inflationsrate (%)"),
        ("max", "Maximale Inflationsrate (%)"),
    ]

    countries = list(stats.keys())
    colors = _country_palette(countries)

    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    axes = axes.flatten()

    for ax, (metric_key, metric_label) in zip(axes, metrics, strict=False):
        values = [stats[c][metric_key] for c in countries]
        bars = ax.bar(countries, values, color=[colors[c] for c in countries], alpha=0.9)
        ax.set_title(metric_label, fontsize=12, pad=8)
        ax.yaxis.set_major_locator(mticker.MultipleLocator(1))
        for bar, value in zip(bars, values, strict=False):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{value:.1f}", ha="center", va="bottom", fontsize=10)
        ax.tick_params(axis="x", rotation=0)
        ax.grid(axis="y", linestyle=":", linewidth=0.8, color=GRID_LIGHT)

    fig.suptitle(f"Deskriptive Statistik der Inflationsraten (seit {pd.to_datetime(config.analysis_start_date).year})", fontsize=14, y=0.98)
    fig.tight_layout(rect=[0, 0.02, 1, 0.95])
    _add_caption(fig, "Quelle: Eurostat (2025). HICP - Harmonisierter Verbraucherpreisindex.")

    output_path = Path(output_dir) / "statistics_comparison.svg"
    save_plot(output_path, dpi=300, fig=fig)
    plt.close(fig)
    print(f"Saved plot to {output_path}")
    return str(output_path)


def plot_ecb_interest_rates(interest_df, output_dir: str | Path = "output"):
    """Create a plot showing ECB interest rates over time."""
    _set_locale()
    apply_template(palette="muted", font_size=11)

    if interest_df is None or interest_df.empty:
        print("No interest rate data available; skipping interest rate plot.")
        return None

    interest_df = interest_df.dropna(subset=["interest_rate", "date"])
    if interest_df.empty:
        print("Interest rate data empty after cleaning; skipping interest rate plot.")
        return None

    fig, ax = plt.subplots(figsize=(14, 6.5))

    y_min = np.floor(interest_df["interest_rate"].min())
    y_max = np.ceil(interest_df["interest_rate"].max())

    if "rate_type" in interest_df.columns:
        for rate_type, color in zip(sorted(interest_df["rate_type"].unique()), palette_colors("bright"), strict=False):
            subset = interest_df[interest_df["rate_type"] == rate_type].sort_values("date")
            ax.plot(subset["date"], subset["interest_rate"], label=rate_type, color=color, linewidth=2.0)
            ax.scatter(subset["date"], subset["interest_rate"], color=color, s=16, alpha=0.7)
    else:
        subset = interest_df.sort_values("date")
        color = "#4477AA"
        ax.plot(subset["date"], subset["interest_rate"], color=color, linewidth=2.2, label="Hauptrefinanzierungssatz")
        ax.fill_between(subset["date"], subset["interest_rate"], color=color, alpha=0.15)

    set_labels("EZB-Leitzinsen seit 2000", "", "Zinssatz (%)", ax=ax)
    _style_time_axis(ax, interval=6, fmt="%Y", rotation=0)
    set_limits(ylim=(y_min - 0.5, y_max + 0.5), ax=ax)
    ax.yaxis.set_major_locator(mticker.MultipleLocator(1))
    ax.legend(loc="upper left", title="")
    _add_caption(fig, "Quelle: Europäische Zentralbank (2025).")

    output_path = Path(output_dir) / "ecb_interest_rates.svg"
    save_plot(output_path, dpi=300, fig=fig)
    plt.close(fig)
    print(f"Saved interest rate plot to {output_path}")
    return str(output_path)


def plot_eu_heatmap(output_dir: str | Path = "output"):
    """Create a heatmap showing inflation rates for EU countries since 2020."""
    _set_locale()
    apply_template(palette="bright", font_size=11)
    print("Fetching EU-wide inflation data for heatmap...")

    try:
        import eurostat
    except ImportError as exc:  # pragma: no cover - optional dependency missing
        print(f"Eurostat not available: {exc}")
        return None

    try:
        df = eurostat.get_data_df("prc_hicp_manr", flags=False)
        if "geo\\TIME_PERIOD" in df.columns:
            df = df.rename(columns={"geo\\TIME_PERIOD": "geo"})

        df_filtered = df[df["coicop"].str.startswith("CP00")].copy()
        time_columns = [col for col in df_filtered.columns if isinstance(col, str) and "-" in str(col)]

        df_long = df_filtered.melt(id_vars=["geo"], value_vars=time_columns, var_name="period", value_name="inflation_rate")
        df_long["date"] = pd.to_datetime(df_long["period"], format="%Y-%m", errors="coerce")
        df_long["inflation_rate"] = pd.to_numeric(df_long["inflation_rate"], errors="coerce")
        df_long = df_long.dropna(subset=["inflation_rate", "date"])
        df_long = df_long[df_long["date"] >= "2020-01-01"]

        country_counts = df_long.groupby("geo").size().sort_values(ascending=False)
        top_countries = country_counts.head(15).index.tolist()
        df_long = df_long[df_long["geo"].isin(top_countries)]

        df_long["country_name"] = df_long["geo"].apply(_code_to_country)
        df_long["quarter"] = df_long["date"].dt.to_period("Q")

        df_quarterly = df_long.groupby(["country_name", "quarter"])["inflation_rate"].mean().reset_index()
        df_quarterly["quarter_str"] = df_quarterly["quarter"].astype(str)

        avg_inflation = df_quarterly.groupby("country_name")["inflation_rate"].mean().sort_values()
        df_quarterly["country_name"] = pd.Categorical(df_quarterly["country_name"], categories=avg_inflation.index, ordered=True)

        pivot = df_quarterly.pivot(index="country_name", columns="quarter_str", values="inflation_rate").sort_index()
        pivot = pivot.loc[:, sorted(pivot.columns)]

        fig, ax = plt.subplots(figsize=(15, 9))
        cax = ax.imshow(pivot.values, aspect="auto", cmap="coolwarm", interpolation="nearest")
        ax.set_xticks(range(pivot.shape[1]))
        ax.set_xticklabels(pivot.columns, rotation=60, ha="right")
        ax.set_yticks(range(pivot.shape[0]))
        ax.set_yticklabels(pivot.index)
        set_labels("Inflationsrate EU-Länder (Quartalsdurchschnitt seit 2020)", "Quartal", "Land", ax=ax)

        cbar = fig.colorbar(cax, ax=ax, fraction=0.025, pad=0.02)
        cbar.set_label("Inflation (%)")

        fig.tight_layout()
        _add_caption(fig, "Quelle: Eurostat (2025).")

        output_path = Path(output_dir) / "eu_inflation_heatmap.svg"
        save_plot(output_path, dpi=300, fig=fig)
        plt.close(fig)
        print(f"Saved heatmap to {output_path}")
        return str(output_path)

    except Exception as exc:  # pragma: no cover - runtime issues
        print(f"Error creating heatmap: {exc}")
        return None


def plot_historical_comparison(config: ReportConfig, output_dir: str | Path = "output"):
    """Create a historical comparison plot since Euro introduction with markers."""
    _set_locale()
    config = ensure_config(config)
    apply_template(palette="bright", font_size=12)
    print("Fetching historical data since Euro introduction...")

    try:
        import eurostat
    except ImportError as exc:  # pragma: no cover - optional dependency missing
        print(f"Eurostat not available: {exc}")
        return None

    try:
        df = eurostat.get_data_df("prc_hicp_manr", flags=False)
        if "geo\\TIME_PERIOD" in df.columns:
            df = df.rename(columns={"geo\\TIME_PERIOD": "geo"})

        df_filtered = df[(df["coicop"].str.startswith("CP00")) & (df["geo"].isin(config.countries + ["EA19"]))].copy()

        if "EA20" in df_filtered["geo"].values and "EA19" in df_filtered["geo"].values:
            df_filtered = df_filtered[df_filtered["geo"] != "EA19"]

        time_columns = [col for col in df_filtered.columns if isinstance(col, str) and "-" in str(col)]
        df_long = df_filtered.melt(id_vars=["geo"], value_vars=time_columns, var_name="period", value_name="inflation_rate")
        df_long["date"] = pd.to_datetime(df_long["period"], format="%Y-%m", errors="coerce")
        df_long["inflation_rate"] = pd.to_numeric(df_long["inflation_rate"], errors="coerce")
        df_long = df_long.dropna(subset=["inflation_rate", "date"])
        df_long = df_long[df_long["date"] >= config.historical_start_date]

        df_long["country"] = df_long["geo"].map(COUNTRY_NAMES)
        df_long = df_long.dropna(subset=["country"])

        countries = [c for c in ["Österreich", "Deutschland", "Eurozone"] if c in df_long["country"].unique()]
        color_map = _country_palette(countries)

        fig, ax = plt.subplots(figsize=(14, 6.5))
        for country in countries:
            subset = df_long[df_long["country"] == country].sort_values("date")
            ax.plot(subset["date"], subset["inflation_rate"], label=country, color=color_map[country], linewidth=2.0)
            ax.scatter(subset["date"], subset["inflation_rate"], color=color_map[country], s=16, alpha=0.7)

        events = [
            (pd.Timestamp("2008-09-15"), "Finanzkrise"),
            (pd.Timestamp("2020-03-11"), "COVID-19"),
            (pd.Timestamp("2022-02-24"), "Ukraine-Krieg"),
        ]
        for date, label in events:
            add_vline(date, ax=ax, color="#555555", linestyle="--", linewidth=0.9, alpha=0.7)
            ax.text(date, ax.get_ylim()[1], label, rotation=90, va="bottom", ha="right", fontsize=8.5, color="#555555")

        set_labels(f"Langfristige Inflationsentwicklung (seit {pd.to_datetime(config.historical_start_date).year})", "", "Inflationsrate (%)", ax=ax)
        ax.legend(loc="upper right")
        _style_time_axis(ax, interval=60, fmt="%Y", rotation=0)
        y_min, y_max = df_long["inflation_rate"].min(), df_long["inflation_rate"].max()
        margin = max(0.5, (y_max - y_min) * 0.08)
        set_limits(ylim=(np.floor(y_min - margin), np.ceil(y_max + margin)), ax=ax)
        ax.yaxis.set_major_locator(mticker.MultipleLocator(1))
        _add_caption(fig, "Quelle: Eurostat (2025). Kritische Ereignisse markiert.")

        output_path = Path(output_dir) / "historical_comparison.svg"
        save_plot(output_path, dpi=300, fig=fig)
        plt.close(fig)
        print(f"Saved plot to {output_path}")
        return str(output_path)

    except Exception as exc:  # pragma: no cover - runtime issues
        print(f"Error creating historical plot: {exc}")
        return None
