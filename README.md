# Inflationsbericht Österreich

API und Dashboard zur Analyse von Inflationsdaten für Österreich im Vergleich zu Deutschland und dem Euroraum.

## Übersicht

Das Projekt lädt HICP-Daten von Eurostat, bereitet sie für Österreich/Deutschland/Euroraum auf und stellt sie über eine FastAPI-API bereit. Ein Streamlit-Dashboard greift live auf die API zu und zeigt Inflationsverläufe, Zinsdaten sowie die Differenz Österreich vs. Eurozone an. Daten werden bei jedem Abruf aktualisiert; bei fehlendem Eurostat-Zugriff nutzt die API fallback-Daten.

## Funktionen

- **Datenbeschaffung**: HICP (Eurostat `prc_hicp_manr`) für AT, DE, EA20 + EZB-Leitzinsen (`irt_st_m`).
- **Aufbereitung**: Long-Format mit Ländernamen, Kategorien und sauberen Datumswerten.
- **Analyse**: Vergleich Österreich vs. Eurozone (Differenz, Trendindikator).
- **API**: Vorberechnete Daten + Konfiguration als JSON (`/config`, `/data`, `/refresh`).
- **Dashboard**: Plotly-basierte Charts in Streamlit mit auswählbaren Ländern und Zeiträumen.

## Erste Schritte

### Voraussetzungen
- Python 3.8 oder höher

### Installation

1.  **Repository klonen**:
    ```bash
    git clone https://github.com/jstreitberger03/inflation-report-austria.git
    cd inflation-report-austria
    ```

2.  **Virtuelle Umgebung erstellen und aktivieren** (empfohlen):
    - Windows:
      ```bash
      python -m venv .venv
      .venv\Scripts\activate
      ```
    - macOS/Linux:
      ```bash
      python -m venv .venv
      source .venv/bin/activate
      ```

3.  **Abhängigkeiten installieren**:
    ```bash
    pip install -r requirements.txt
    ```

## Dashboard + API

Streamlit-Dashboard + FastAPI-Backend. Standardwerte (Länder/Zeiträume) sind im Code hinterlegt; optional kann eine eigene `config.yaml` bereitgestellt werden.

### Backend starten (FastAPI)

```bash
uvicorn backend.app:app --reload --port 8000
```

Endpoints:
- `GET /health` – Health Check
- `GET /config` – aktuelle Konfiguration
- `GET /data` – vorab berechnete Daten (Inflation, Vergleich, Zinsen)
- `POST /refresh` – Daten neu berechnen (optional mit Länder-/Zeitraum-Overrides)

### Dashboard starten (Streamlit)

```bash
streamlit run frontend/streamlit_app.py
```

Im Sidebar können Sie Länder hinzufügen/auswählen und den Zeitraum anpassen. Das Dashboard lädt die Daten live über die API.

## Projektstruktur

```
inflation-report-austria/
│
├── backend/                 # FastAPI Backend
├── frontend/                # Streamlit Dashboard
├── inflation_report/        # Kernmodule (Daten, Analyse, Config, Styles)
# optional: config.yaml      # eigene Defaults für API/Pipeline
├── pyproject.toml           # Projektmetadaten und Build-Konfiguration
├── requirements.txt         # Python-Paketabhängigkeiten
├── README.md                # Projektdokumentation
```

## Datenbasis
- **Anbieter**: Eurostat
- **Datensätze**: `prc_hicp_manr` (Inflation), `irt_st_m` (EZB-Leitzinsen)
- **Regionen**: Österreich (AT), Deutschland (DE), Euroraum (EA20)
- **Zeitraum**: ab 2002 (Inflation) bzw. 2000 (Zinsen)

## Technologie-Stack

| Komponente         | Technologie   |
|--------------------|---------------|
| **Kern**           | Python 3.8+   |
| **Daten**          | pandas, numpy, eurostat, pycountry |
| **Config**         | PyYAML        |
| **API**            | FastAPI, Pydantic, Uvicorn |
| **Dashboard**      | Streamlit, Plotly, Requests |

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert. Weitere Informationen finden Sie in der `LICENSE`-Datei.
