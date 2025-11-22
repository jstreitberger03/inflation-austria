"""Visualization helpers powered by plotnine."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from plotnine import (
    aes,
    element_blank,
    element_rect,
    element_line,
    element_text,
    facet_wrap,
    geom_area,
    geom_col,
    geom_line,
    geom_hline,
    geom_point,
    geom_ribbon,
    geom_text,
    geom_tile,
    geom_vline,
    ggplot,
    labs,
    position_dodge,
    scale_color_brewer,
    scale_color_manual,
    scale_fill_gradient2,
    scale_fill_identity,
    scale_fill_manual,
    scale_linetype_manual,
    scale_size_manual,
    scale_x_datetime,
    scale_y_continuous,
    theme,
    theme_minimal,
)

from .config import ReportConfig, ensure_config
from .constants import CATEGORY_NAMES, COUNTRY_NAMES

try:
    import locale
except ImportError:  # pragma: no cover - locale unavailable
    locale = None


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

    df_filtered = df[(df["date"] >= config.analysis_start_date) & (df["coicop"] == "CP00")].copy()
    if df_filtered.empty:
        print("No overall inflation data found for comparison plot after filtering.")
        return None

    if forecast_df is None:
        forecast_df = forecast_inflation(df_filtered, config)
    forecast_df = forecast_df[forecast_df["date"] <= config.forecast_display_limit].copy()

    connection_points = []
    for country in df["country"].dropna().unique():
        last_hist = df[df["country"] == country].sort_values("date").iloc[-1]
        connection_points.append(
            {
                "date": last_hist["date"],
                "geo": last_hist["geo"],
                "country": last_hist["country"],
                "inflation_rate": last_hist["inflation_rate"],
                "lower_bound": last_hist["inflation_rate"],
                "upper_bound": last_hist["inflation_rate"],
                "type": "Prognose",
                "is_forecast": False,
            }
        )

    connection_df = pd.DataFrame(connection_points)
    df_hist = df_filtered.copy()
    df_hist["type"] = "Historisch"
    df_hist["lower_bound"] = df_hist["inflation_rate"]
    df_hist["upper_bound"] = df_hist["inflation_rate"]

    forecast_df = forecast_df.copy()
    forecast_df["type"] = "Prognose"
    if "country" not in forecast_df.columns and "geo" in forecast_df.columns:
        forecast_df["country"] = forecast_df["geo"].map(COUNTRY_NAMES)

    df_combined = pd.concat([df_hist, connection_df, forecast_df], ignore_index=True)
    df_combined = df_combined.dropna(subset=["country"])

    events = pd.DataFrame(
        {
            "date": pd.to_datetime(["2020-03-11", "2022-02-24", "2025-01-20"]),
            "label": ["COVID-19", "Ukraine-Krieg", "Liberation Day"],
            "y_pos": [2, 9, 5],
        }
    )

    y_min = np.floor(df_combined["lower_bound"].min())
    y_max = np.ceil(df_combined["upper_bound"].max())
    y_breaks = np.arange(y_min, y_max + 1, 1.0)

    plot = (
        ggplot(df_combined, aes(x="date", y="inflation_rate", color="country"))
        + geom_line(aes(linetype="type"), size=1.3, alpha=0.9)
        + geom_point(size=1.8, alpha=0.6, data=df_combined[df_combined["type"] == "Historisch"])
        + geom_ribbon(
            aes(ymin="lower_bound", ymax="upper_bound", fill="country"),
            data=df_combined[df_combined["type"] == "Prognose"],
            alpha=0.12,
            show_legend=False,
        )
        + geom_vline(data=events, mapping=aes(xintercept="date"), linetype="dashed", alpha=0.4, color="#333333")
        + geom_text(
            data=events,
            mapping=aes(x="date", y="y_pos", label="label"),
            angle=90,
            va="bottom",
            ha="right",
            size=9,
            color="#333333",
            nudge_y=0.3,
        )
        + scale_color_manual(values=["#2E86AB", "#A23B72", "#F18F01"], labels=["Österreich", "Deutschland", "Eurozone"])
        + scale_fill_manual(values=["#2E86AB", "#A23B72", "#F18F01"])
        + scale_linetype_manual(values=["solid", "dashed"], labels=["Historisch", "Prognose"])
        + scale_x_datetime(date_labels="%b %Y", date_breaks="3 months")
        + scale_y_continuous(limits=[y_min, y_max], breaks=y_breaks)
        + theme_minimal()
        + labs(
            title="Inflationsrate im Vergleich (mit Prognose bis März 2026)",
            x="",
            y="Inflationsrate (%)",
            color="Region",
            linetype="",
            caption="Quelle: Eurostat (2025). HICP - Harmonisierter Verbraucherpreisindex. Schattierung: 95%-Konfidenzintervall. Kritische Ereignisse markiert.",
        )
        + theme(
            plot_title=element_text(size=14, face="bold", margin={"b": 15}),
            plot_caption=element_text(size=9, hjust=0, margin={"t": 12}, color="#666666"),
            axis_title=element_text(size=12),
            axis_title_x=element_blank(),
            axis_text=element_text(size=10),
            axis_text_x=element_text(angle=45, hjust=1),
            legend_position="top",
            legend_title=element_blank(),
            legend_text=element_text(size=11),
            legend_box_margin=5,
            panel_grid_minor_x=element_blank(),
            panel_grid_major_x=element_blank(),
            panel_grid_minor_y=element_line(alpha=0.25, linetype="dotted", size=0.5, color="#CCCCCC"),
            panel_grid_major_y=element_line(alpha=0.5, linetype="dotted", size=0.8, color="#999999"),
            figure_size=(15, 7),
            panel_background=element_rect(fill="white"),
            plot_background=element_rect(fill="#FAFAFA"),
        )
    )

    output_path = Path(output_dir) / "inflation_comparison.svg"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plot.save(output_path, dpi=300, format="svg")
    print(f"Saved plot to {output_path}")
    return str(output_path)


def plot_difference(comparison_df, config: ReportConfig, output_dir: str | Path = "output"):
    """Create a bar plot showing the difference in inflation rates."""
    config = ensure_config(config)
    if "Difference (AT - EA)" not in comparison_df.columns:
        print("No difference column found in comparison data")
        return None

    if hasattr(comparison_df.index, "year"):
        comparison_df = comparison_df[comparison_df.index >= config.analysis_start_date].copy()
    else:
        comparison_df = comparison_df[comparison_df.index >= pd.to_datetime(config.analysis_start_date)].copy()

    plot_df = comparison_df.reset_index()
    plot_df["color"] = ["#2ecc71" if x < 0 else "#e74c3c" for x in plot_df["Difference (AT - EA)"]]

    plot = (
        ggplot(plot_df, aes(x="date", y="Difference (AT - EA)"))
        + geom_col(aes(fill="color"), show_legend=False)
        + geom_hline(yintercept=0, color="black", size=0.5)
        + scale_fill_identity()
        + scale_x_datetime(date_labels="%B %Y", date_breaks="6 months")
        + theme_minimal()
        + labs(
            title="Inflationsdifferenz: Österreich zur Eurozone (seit 2020)",
            subtitle="Positive Werte = Höhere Inflation in Österreich",
            x="",
            y="Differenz (Prozentpunkte)",
            caption="Quelle: Eurostat (2025). HICP - Harmonisierter Verbraucherpreisindex.",
        )
        + theme(
            plot_title=element_text(size=13, face="bold", margin={"b": 5}),
            plot_subtitle=element_text(size=10, margin={"b": 10}),
            plot_caption=element_text(size=8, hjust=0, margin={"t": 10}),
            axis_title=element_text(size=11),
            axis_title_x=element_blank(),
            axis_text=element_text(size=9),
            axis_text_x=element_text(angle=45, hjust=1),
            panel_grid_minor_x=element_blank(),
            panel_grid_major_x=element_blank(),
            panel_grid_minor_y=element_line(alpha=0.25, linetype="dotted", size=0.5, color="#CCCCCC"),
            panel_grid_major_y=element_line(alpha=0.5, linetype="dotted", size=0.8, color="#999999"),
            figure_size=(12, 6),
            panel_background=element_rect(fill="white"),
            plot_background=element_rect(fill="white"),
        )
    )

    output_path = Path(output_dir) / "inflation_difference.svg"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plot.save(output_path, dpi=300, format="svg")
    print(f"Saved plot to {output_path}")
    return str(output_path)


def plot_inflation_components(df, output_dir: str | Path = "output"):
    """Create a line plot showing the components of inflation for Austria."""
    _set_locale()
    df_austria = df[(df["geo"] == "AT") & (df["date"] >= "2020-01-01")].copy()
    if df_austria.empty or "category" not in df_austria.columns:
        print("No component data found for Austria to plot.")
        return None

    y_min = np.floor(df_austria["inflation_rate"].min())
    y_max = np.ceil(df_austria["inflation_rate"].max())
    y_breaks = np.arange(y_min, y_max + 2, 2.0)

    plot = (
        ggplot(df_austria, aes(x="date", y="inflation_rate", color="category"))
        + geom_line(aes(size="category"), alpha=0.9)
        + geom_point(aes(shape="category"), size=2.5, alpha=0.7)
        + scale_size_manual(
            values={
                CATEGORY_NAMES["CP00"]: 1.5,
                CATEGORY_NAMES["NRG"]: 1.0,
                CATEGORY_NAMES["FOOD"]: 1.0,
                CATEGORY_NAMES["SERV"]: 1.0,
                CATEGORY_NAMES["IGD"]: 1.0,
            }
        )
        + scale_color_brewer(type="qual", palette="Set1")
        + scale_x_datetime(date_labels="%b %Y", date_breaks="4 months")
        + scale_y_continuous(limits=[y_min, y_max], breaks=y_breaks)
        + theme_minimal()
        + labs(
            title="Bestandteile der Inflation in Österreich (seit 2020)",
            x="",
            y="Inflationsrate (%)",
            color="Inflationskomponente",
            size="Inflationskomponente",
            shape="Inflationskomponente",
            caption="Quelle: Eurostat (2025). HICP - Harmonisierter Verbraucherpreisindex.",
        )
        + theme(
            plot_title=element_text(size=14, face="bold", margin={"b": 15}),
            plot_caption=element_text(size=9, hjust=0, margin={"t": 12}, color="#666666"),
            axis_title=element_text(size=12),
            axis_title_x=element_blank(),
            axis_text=element_text(size=10),
            axis_text_x=element_text(angle=45, hjust=1),
            legend_position="top",
            legend_title=element_text(size=11, face="bold"),
            legend_text=element_text(size=10),
            panel_grid_major_y=element_line(alpha=0.5, linetype="dotted", size=0.8, color="#999999"),
            figure_size=(15, 7),
            plot_background=element_rect(fill="#FAFAFA"),
        )
    )

    output_path = Path(output_dir) / "inflation_components_at.svg"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plot.save(output_path, dpi=300, format="svg")
    print(f"Saved component plot to {output_path}")
    return str(output_path)


def plot_statistics_comparison(stats, config: ReportConfig, output_dir: str | Path = "output"):
    """Create a bar plot comparing key statistics between regions."""
    config = ensure_config(config)
    metrics = ["mean", "median", "min", "max"]
    metric_names = {
        "mean": "Durchschnittliche Inflationsrate (%)",
        "median": "Median Inflationsrate (%)",
        "min": "Minimale Inflationsrate (%)",
        "max": "Maximale Inflationsrate (%)",
    }

    plot_data = []
    for country, values in stats.items():
        for metric in metrics:
            plot_data.append({"country": country, "metric": metric_names[metric], "value": values[metric]})

    plot_df = pd.DataFrame(plot_data)
    plot_df["label"] = plot_df["value"].apply(lambda x: f"{x:.1f}%")

    plot = (
        ggplot(plot_df, aes(x="country", y="value", fill="country"))
        + geom_col(alpha=0.7, show_legend=False)
        + scale_fill_manual(values=["#1f77b4", "#2ca02c", "#ff7f0e"])
        + geom_text(aes(label="label"), va="bottom", position=position_dodge(width=0.9), size=8)
        + facet_wrap("~metric", ncol=2, scales="free_y")
        + theme_minimal()
        + labs(
            title=f"Deskriptive Statistik der Inflationsraten (seit {pd.to_datetime(config.analysis_start_date).year})",
            x="",
            y="Inflationsrate (%)",
            caption="Quelle: Eurostat (2025). HICP - Harmonisierter Verbraucherpreisindex.",
        )
        + theme(
            plot_title=element_text(size=13, face="bold", margin={"b": 10}),
            plot_caption=element_text(size=8, hjust=0, margin={"t": 10}),
            strip_text=element_text(size=11, face="bold"),
            axis_title=element_text(size=11),
            axis_text=element_text(size=9),
            panel_grid_minor_x=element_blank(),
            panel_grid_major_x=element_blank(),
            panel_grid_minor_y=element_line(alpha=0.25, linetype="dotted", size=0.5, color="#CCCCCC"),
            panel_grid_major_y=element_line(alpha=0.5, linetype="dotted", size=0.8, color="#999999"),
            figure_size=(12, 9),
            panel_background=element_rect(fill="white"),
            plot_background=element_rect(fill="white"),
        )
    )

    output_path = Path(output_dir) / "statistics_comparison.svg"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plot.save(output_path, dpi=300, format="svg")
    print(f"Saved plot to {output_path}")
    return str(output_path)


def plot_ecb_interest_rates(interest_df, output_dir: str | Path = "output"):
    """Create a plot showing ECB interest rates over time."""
    _set_locale()

    if interest_df is None or interest_df.empty:
        print("No interest rate data available; skipping interest rate plot.")
        return None

    interest_df = interest_df.dropna(subset=["interest_rate", "date"])
    if interest_df.empty:
        print("Interest rate data empty after cleaning; skipping interest rate plot.")
        return None

    if "rate_type" in interest_df.columns:
        y_min = np.floor(interest_df["interest_rate"].min())
        y_max = np.ceil(interest_df["interest_rate"].max())
        if y_max < y_min:
            y_min, y_max = y_max, y_min
        y_breaks = np.arange(y_min, y_max + 1, 1.0)

        plot = (
            ggplot(interest_df, aes(x="date", y="interest_rate", color="rate_type"))
            + geom_line(size=1.5, alpha=0.9)
            + geom_point(size=1.2, alpha=0.4)
            + scale_color_manual(
                values=["#2C3E50", "#E74C3C"], labels=["Hauptrefinanzierungssatz", "Einlagenfazilität"]
            )
            + scale_x_datetime(date_labels="%Y", date_breaks="3 years")
            + scale_y_continuous(limits=[y_min, y_max], breaks=y_breaks)
            + theme_minimal()
            + labs(
                title="EZB-Leitzinsen seit 2000",
                x="",
                y="Zinssatz (%)",
                color="",
                caption="Quelle: Europäische Zentralbank (2025).",
            )
            + theme(
                plot_title=element_text(size=14, face="bold", margin={"b": 15}),
                plot_caption=element_text(size=9, hjust=0, margin={"t": 12}, color="#666666"),
                axis_title=element_text(size=12),
                axis_title_x=element_blank(),
                axis_text=element_text(size=10),
                axis_text_x=element_text(angle=0, hjust=0.5),
                legend_position="top",
                legend_title=element_blank(),
                legend_text=element_text(size=11),
                legend_box_margin=5,
                panel_grid_minor_x=element_blank(),
                panel_grid_major_x=element_blank(),
                panel_grid_minor_y=element_line(alpha=0.25, linetype="dotted", size=0.5, color="#CCCCCC"),
                panel_grid_major_y=element_line(alpha=0.5, linetype="dotted", size=0.8, color="#999999"),
                figure_size=(15, 7),
                panel_background=element_rect(fill="white"),
                plot_background=element_rect(fill="#FAFAFA"),
            )
        )
    else:
        y_min = np.floor(interest_df["interest_rate"].min())
        y_max = np.ceil(interest_df["interest_rate"].max())
        if y_max < y_min:
            y_min, y_max = y_max, y_min
        y_breaks = np.arange(y_min, y_max + 1, 1.0)

        plot = (
            ggplot(interest_df, aes(x="date", y="interest_rate"))
            + geom_line(color="#2C3E50", size=1.5, alpha=0.9)
            + geom_point(color="#2C3E50", size=1.2, alpha=0.4)
            + geom_area(fill="#34495E", alpha=0.12)
            + scale_x_datetime(date_labels="%Y", date_breaks="3 years")
            + scale_y_continuous(breaks=y_breaks)
            + theme_minimal()
            + labs(
                title="EZB-Hauptrefinanzierungssatz seit 2000",
                x="",
                y="Leitzins (%)",
                caption="Quelle: Europäische Zentralbank (2025).",
            )
            + theme(
                plot_title=element_text(size=14, face="bold", margin={"b": 15}),
                plot_caption=element_text(size=9, hjust=0, margin={"t": 12}, color="#666666"),
                axis_title=element_text(size=12),
                axis_title_x=element_blank(),
                axis_text=element_text(size=10),
                axis_text_x=element_text(angle=0, hjust=0.5),
                legend_position="none",
                panel_grid_minor_x=element_blank(),
                panel_grid_major_x=element_blank(),
                panel_grid_minor_y=element_line(alpha=0.25, linetype="dotted", size=0.5, color="#CCCCCC"),
                panel_grid_major_y=element_line(alpha=0.5, linetype="dotted", size=0.8, color="#999999"),
                figure_size=(15, 7),
                panel_background=element_rect(fill="white"),
                plot_background=element_rect(fill="#FAFAFA"),
            )
        )

    output_path = Path(output_dir) / "ecb_interest_rates.svg"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plot.save(output_path, dpi=300, format="svg")
    print(f"Saved interest rate plot to {output_path}")
    return str(output_path)


def plot_eu_heatmap(output_dir: str | Path = "output"):
    """Create a heatmap showing inflation rates for EU countries since 2020."""
    _set_locale()
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

        df_long["country_name"] = df_long["geo"].map(COUNTRY_NAMES).fillna(df_long["geo"])
        df_long["year_month"] = df_long["date"].dt.to_period("M").astype(str)
        df_long["quarter"] = df_long["date"].dt.to_period("Q")

        df_quarterly = df_long.groupby(["country_name", "quarter"])["inflation_rate"].mean().reset_index()
        df_quarterly["quarter_str"] = df_quarterly["quarter"].astype(str)

        avg_inflation = df_quarterly.groupby("country_name")["inflation_rate"].mean().sort_values()
        df_quarterly["country_name"] = pd.Categorical(df_quarterly["country_name"], categories=avg_inflation.index, ordered=True)

        plot = (
            ggplot(df_quarterly, aes(x="quarter_str", y="country_name", fill="inflation_rate"))
            + geom_tile(color="white", size=0.5)
            + scale_fill_gradient2(
                low="#3498db",
                mid="#f1c40f",
                high="#e74c3c",
                midpoint=4,
                limits=[df_quarterly["inflation_rate"].min(), df_quarterly["inflation_rate"].max()],
            )
            + theme_minimal()
            + labs(
                title="Inflationsrate EU-Länder im Vergleich (Quartalsdurchschnitt seit 2020)",
                x="Quartal",
                y="Land",
                fill="Inflation (%)",
                caption="Quelle: Eurostat (2025). HICP - Harmonisierter Verbraucherpreisindex.",
            )
            + theme(
                plot_title=element_text(size=12, face="bold", margin={"b": 10}),
                plot_caption=element_text(size=8, hjust=0, margin={"t": 10}),
                axis_title=element_text(size=10),
                axis_text=element_text(size=8),
                axis_text_x=element_text(angle=90, hjust=1, vjust=0.5),
                legend_position="right",
                legend_title=element_text(size=9),
                legend_text=element_text(size=8),
                figure_size=(16, 10),
                panel_background=element_rect(fill="white"),
                plot_background=element_rect(fill="white"),
            )
        )

        output_path = Path(output_dir) / "eu_inflation_heatmap.svg"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plot.save(output_path, dpi=300, format="svg")
        print(f"Saved heatmap to {output_path}")
        return str(output_path)

    except Exception as exc:  # pragma: no cover - runtime issues
        print(f"Error creating heatmap: {exc}")
        return None


def plot_historical_comparison(config: ReportConfig, output_dir: str | Path = "output"):
    """Create a historical comparison plot since Euro introduction with markers."""
    _set_locale()
    config = ensure_config(config)
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

        events = pd.DataFrame(
            {
                "date": pd.to_datetime(["2008-09-15", "2020-03-11", "2022-02-24"]),
                "label": ["Finanzkrise", "COVID-19", "Ukraine-Krieg"],
                "y_pos": [8, 2, 9],
            }
        )

        y_min = np.floor(df_long["inflation_rate"].min())
        y_max = np.ceil(df_long["inflation_rate"].max())
        y_breaks = np.arange(y_min, y_max + 1, 1.0)

        plot = (
            ggplot(df_long, aes(x="date", y="inflation_rate", color="country"))
            + geom_line(size=1.3, alpha=0.9)
            + geom_point(size=1.8, alpha=0.6)
            + geom_vline(data=events, mapping=aes(xintercept="date"), linetype="dashed", alpha=0.4, color="#333333")
            + geom_text(
                data=events,
                mapping=aes(x="date", y="y_pos", label="label"),
                angle=90,
                va="bottom",
                ha="right",
                size=9,
                color="#333333",
                nudge_y=0.3,
            )
            + scale_color_manual(values=["#2E86AB", "#A23B72", "#F18F01"], labels=["Österreich", "Deutschland", "Eurozone"])
            + scale_x_datetime(date_labels="%Y", date_breaks="2 years")
            + scale_y_continuous(limits=[y_min, y_max], breaks=y_breaks)
            + theme_minimal()
            + labs(
                title=f"Langfristige Inflationsentwicklung (seit {pd.to_datetime(config.historical_start_date).year})",
                x="",
                y="Inflationsrate (%)",
                color="Region",
                caption="Quelle: Eurostat (2025). HICP - Harmonisierter Verbraucherpreisindex. Kritische Ereignisse: Finanzkrise 2008, COVID-19, Ukraine-Krieg.",
            )
            + theme(
                plot_title=element_text(size=14, face="bold", margin={"b": 15}),
                plot_caption=element_text(size=9, hjust=0, margin={"t": 12}, color="#666666"),
                axis_title=element_text(size=12),
                axis_title_x=element_blank(),
                axis_text=element_text(size=10),
                axis_text_x=element_text(angle=0, hjust=0.5),
                legend_position="top",
                legend_title=element_blank(),
                legend_text=element_text(size=11),
                legend_box_margin=5,
                panel_grid_minor_x=element_blank(),
                panel_grid_major_x=element_blank(),
                panel_grid_minor_y=element_line(alpha=0.25, linetype="dotted", size=0.5, color="#CCCCCC"),
                panel_grid_major_y=element_line(alpha=0.5, linetype="dotted", size=0.8, color="#999999"),
                figure_size=(15, 7),
                panel_background=element_rect(fill="white"),
                plot_background=element_rect(fill="#FAFAFA"),
            )
        )

        output_path = Path(output_dir) / "historical_comparison.svg"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plot.save(output_path, dpi=300, format="svg")
        print(f"Saved plot to {output_path}")
        return str(output_path)

    except Exception as exc:  # pragma: no cover - runtime issues
        print(f"Error creating historical plot: {exc}")
        return None
