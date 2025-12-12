# Inflationsbericht Österreich ![CI](https://github.com/jstreitberger03/inflation-report-austria/actions/workflows/ci.yml/badge.svg)

API und Dashboard zur Analyse von Inflationsdaten für Österreich im Vergleich zu Deutschland und dem Euroraum.

## Übersicht

Das Projekt lädt HICP-Daten von Eurostat, bereitet sie für Österreich/Deutschland/Euroraum auf und stellt sie über eine FastAPI-API bereit. Ein Streamlit-Dashboard greift live auf die API zu, zeigt Inflationsverläufe, Komponenten je Land, Zinsdaten (EZB + FED) sowie die Differenz Österreich vs. Eurozone. Daten werden gecached, um wiederholte Abrufe schnell zu bedienen; bei fehlendem Eurostat/FRED-Zugriff bleiben die entsprechenden Serien leer.

## Funktionen

- **Datenbeschaffung**: HICP (Eurostat `prc_hicp_manr`) für AT, DE, EA20 + EZB-Leitzinsen (`irt_st_m`) + Fed Funds (FRED `DFF`).
- **Aufbereitung**: Long-Format mit Ländernamen, Kategorien, sauberen Datumswerten.
- **Analyse**: Vergleich Österreich vs. Eurozone (Differenz, Trendindikator).
- **API**: Vorberechnete Daten + Konfiguration als JSON (`/config`, `/data`, `/refresh`), inklusive Cache pro Request-Payload.
- **Dashboard**: Plotly-basierte Charts in Streamlit mit wählbaren Ländern/Zeiträumen, Komponenten-Chart pro Land (nicht aufaddiert), KPI-Kacheln je Land, Zinschart für EZB & FED.

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

Im Sidebar können Sie Länder auswählen und den Zeitraum setzen. Die API-URL ist standardmäßig `http://127.0.0.1:8000` (anpassbar im Sidebar-Expander).

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
- **Datensätze**: `prc_hicp_manr` (Inflation), `irt_st_m` (EZB-Leitzinsen), `DFF` (Fed Funds, FRED)
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

## Changelog
Für kleinere interne Anpassungen ist kein separates Changelog nötig. Falls Versionen veröffentlicht oder verteilt werden, sollte ein kurzes `CHANGELOG.md` mit Datum und Stichpunkten gepflegt werden.

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert. Weitere Informationen finden Sie in der `LICENSE`-Datei.
