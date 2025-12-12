import os
import sys
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

# Ensure project root is on sys.path for local runs
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from inflation_report.style import PAUL_TOL_PALETTES
from inflation_report.constants import EU_COUNTRY_CODES

API_URL_DEFAULT = os.getenv("INFLATION_API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Austria Inflation Dashboard", layout="wide")

st.title("Austria Inflation Dashboard")


def fetch_data(api_url: str, refresh: bool = False, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    endpoint = "/refresh" if (refresh or payload) else "/data"
    method = "POST" if (refresh or payload) else "GET"
    resp = requests.request(method, f"{api_url}{endpoint}", json=payload if payload else None, timeout=90)
    resp.raise_for_status()
    return resp.json()


# Sidebar controls
st.sidebar.header("Controls")
api_box = st.sidebar.expander("API Einstellungen", expanded=False)
api_url_input = api_box.text_input(
    "API Base URL",
    value=API_URL_DEFAULT,
    help="Leerlassen für Standard (http://127.0.0.1:8000) oder anpassen falls remote.",
)
api_url = api_url_input.strip() or API_URL_DEFAULT
refresh_btn = api_box.button("Daten neu laden")

# Allow country selection
selected_countries: List[str] = []

# Health check
health_ok = False
try:
    r = requests.get(f"{api_url}/health", timeout=5)
    health_ok = r.ok
    st.sidebar.success("Backend: healthy" if r.ok else "Backend: not healthy")
except Exception:
    st.sidebar.warning("Backend not reachable")

# Load data (cached per URL unless refresh)
@st.cache_data(show_spinner=False)
def load_cached(api: str, payload: Dict[str, Any] | None) -> Dict[str, Any]:
    return fetch_data(api, refresh=False, payload=payload)


data: Dict[str, Any] | None = None
payload = None
try:
    # Load config first to build multiselect
    cfg_only = fetch_data(api_url, refresh=False)
    cfg = cfg_only.get("config", {})
    base_countries = [c.upper() for c in cfg.get("countries", []) if c]

    options = sorted(set(base_countries + EU_COUNTRY_CODES))
    default_selection = base_countries or options
    selected_countries = st.sidebar.multiselect(
        "Länder", options=options, default=default_selection
    )
    payload_countries = sorted(set(selected_countries)) if selected_countries else base_countries or options
    payload = {"countries": payload_countries}

    if refresh_btn:
        with st.spinner("Lade Daten neu..."):
            data = fetch_data(api_url, refresh=True, payload=payload)
            load_cached.clear()
    else:
        with st.spinner("Lade Daten..."):
            data = load_cached(api_url, payload)
except Exception as exc:
    st.error(f"Fehler beim Laden der Daten: {exc}")

if not data:
    st.stop()

cfg = data.get("config", {})
inflation = pd.DataFrame(data.get("inflation", []))
interest = pd.DataFrame(data.get("interest_rates", []))
comparison = pd.DataFrame(data.get("comparison", []))

sel_start = None
sel_end = None

st.subheader("Inflation")

if not inflation.empty:
    hist = inflation[inflation["coicop"] == "CP00"].copy()
    hist["date"] = pd.to_datetime(hist["date"])

    # Zeitraum-Auswahl
    try:
        default_start = pd.to_datetime(cfg.get("analysis_start_date")).date() if cfg.get("analysis_start_date") else hist["date"].min().date()
    except Exception:
        default_start = hist["date"].min().date()
    default_end = hist["date"].max().date()

    date_range = st.sidebar.date_input(
        "Zeitraum",
        value=(default_start, default_end),
    )
    # Normalize selection to (start, end)
    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        sel_start, sel_end = date_range
    else:
        sel_start = default_start
        sel_end = default_end

    hist = hist[(hist["date"] >= pd.Timestamp(sel_start)) & (hist["date"] <= pd.Timestamp(sel_end))].copy()
    if hist.empty:
        st.info("Keine Daten im gewählten Zeitraum.")
    else:
        latest_points = hist.sort_values("date").groupby("country").tail(2)
        col_metrics = st.columns(len(latest_points["country"].unique()))
        for idx, (country, group) in enumerate(latest_points.groupby("country")):
            group_sorted = group.sort_values("date")
            latest_value = group_sorted["inflation_rate"].iloc[-1]
            prev_value = group_sorted["inflation_rate"].iloc[-2] if len(group_sorted) > 1 else None
            delta = latest_value - prev_value if prev_value is not None else None
            col_metrics[idx].metric(
                country,
                f"{latest_value:.2f} %",
                delta=None if delta is None else f"{delta:+.2f} %-Pkt",
                help="Monatliche Teuerungsrate (CP00) und Veränderung ggü. Vormonat",
            )

        tol_palette = PAUL_TOL_PALETTES["bright"]

        fig = px.line(
            hist,
            x="date",
            y="inflation_rate",
            color="country",
            color_discrete_sequence=tol_palette,
            labels={"inflation_rate": "Inflationsrate (%)", "date": "Jahr"},
            title="Inflationsrate",
        )
        fig.update_xaxes(tickformat="%b %Y", showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor="#B0B0B0", griddash="dot")
        st.plotly_chart(fig, width="stretch")
else:
    st.info("Keine Inflationsdaten verfügbar.")

st.divider()
st.subheader("Inflationskomponenten")
components_df = inflation.copy()
if not components_df.empty:
    components_df["date"] = pd.to_datetime(components_df["date"])
    component_options = sorted(components_df["country"].dropna().unique().tolist())
    if not component_options:
        st.info("Keine Komponenten-Daten verfügbar.")
    else:
        default_idx = 0
        if selected_countries and selected_countries[0] in component_options:
            default_idx = component_options.index(selected_countries[0])
        selected_component_country = st.selectbox(
            "Land für Komponenten-Analyse",
            options=component_options,
            index=default_idx,
        )
        comp_filtered = components_df[
            (components_df["country"] == selected_component_country)
            & (components_df["coicop"] != "CP00")
            & components_df["category"].notna()
        ].copy()
        if sel_start and sel_end:
            comp_filtered = comp_filtered[
                (comp_filtered["date"] >= pd.Timestamp(sel_start))
                & (comp_filtered["date"] <= pd.Timestamp(sel_end))
            ]

        if comp_filtered.empty:
            st.info("Keine Komponenten-Daten verfügbar.")
        else:
            fig_comp = px.area(
                comp_filtered,
                x="date",
                y="inflation_rate",
                color="category",
                category_orders={"category": sorted(comp_filtered["category"].unique())},
                color_discrete_sequence=PAUL_TOL_PALETTES["bright"] + PAUL_TOL_PALETTES["muted"],
                title=f"Inflationskomponenten – {selected_component_country}",
                labels={"inflation_rate": "Inflationsrate (%)", "date": "Jahr", "category": "Komponente"},
            )
            fig_comp.for_each_trace(lambda t: t.update(stackgroup=t.name, fill="tozeroy"))
            fig_comp.update_xaxes(tickformat="%b %Y", showgrid=False)
            fig_comp.update_yaxes(showgrid=True, gridcolor="#B0B0B0", griddash="dot")
            st.plotly_chart(fig_comp, width="stretch")
else:
    st.info("Keine Komponenten-Daten verfügbar.")

st.divider()
st.subheader("Differenz Österreich vs. Eurozone")
if not comparison.empty:
    if "Difference (AT - EA)" in comparison.columns:
        comparison["date"] = pd.to_datetime(comparison["date"])
        fig_diff = px.line(
            comparison,
            x="date",
            y="Difference (AT - EA)",
            labels={"Difference (AT - EA)": "Inflationsrate Differenz (AT - EA)", "date": "Jahr"},
            title="Inflationsdifferenz (AT - EA)",
        )
        fig_diff.update_xaxes(tickformat="%b %Y", showgrid=False)
        fig_diff.update_yaxes(showgrid=True, gridcolor="#B0B0B0", griddash="dot")
        st.plotly_chart(fig_diff, width="stretch")
    comp_display = comparison.copy()
    comp_display["date"] = pd.to_datetime(comp_display["date"]).dt.strftime("%b %Y")
    st.dataframe(comp_display.tail(12))
else:
    st.info("Keine Vergleichsdaten verfügbar.")

st.divider()
st.subheader("Leitzinsen (EZB & FED)")
if not interest.empty:
    interest["date"] = pd.to_datetime(interest["date"])
    if "source" not in interest.columns:
        interest["source"] = "ECB"

    interest["label"] = interest.apply(
        lambda row: f"{row['source']}: {row['rate_type']}", axis=1
    )

    fig_rates = px.line(
        interest,
        x="date",
        y="interest_rate",
        color="label",
        color_discrete_sequence=PAUL_TOL_PALETTES["bright"] + PAUL_TOL_PALETTES["muted"],
        labels={"interest_rate": "Zinssatz (%)", "date": "Jahr", "label": "Quelle/Typ"},
        title="Leitzinsen (EZB & FED)",
    )
    fig_rates.update_xaxes(tickformat="%b %Y", showgrid=False)
    fig_rates.update_yaxes(showgrid=True, gridcolor="#B0B0B0", griddash="dot")
    st.plotly_chart(fig_rates, width="stretch")
else:
    st.info("Keine Zinsdaten verfügbar.")

st.caption("Powered by FastAPI + Streamlit (keine Dateien, alles live aus der API)")
