"""
Module for generating HTML reports from inflation analysis.
"""
from datetime import datetime
import os


def generate_html_report(df, stats, comparison, trends, forecast_df, output_dir='output'):
    """
    Erstellt einen umfassenden HTML-Bericht der Inflationsanalyse.
    
    Args:
        df (pd.DataFrame): Verarbeitete Inflationsdaten.
        stats (dict): Wörterbuch mit Statistiken.
        comparison (pd.DataFrame): Monatlicher Vergleich.
        trends (dict): Daten zu Trends und Extremwerten.
        forecast_df (pd.DataFrame): Prognosedaten.
        output_dir (str): Verzeichnis zum Speichern des Berichts.
        
    Returns:
        str: Pfad zum gespeicherten Bericht.
    """
    
    # Metadaten für den Bericht abrufen
    years = sorted(df['year'].unique())
    latest_date = df['date'].max()
    report_date = datetime.now()
    
    # Prognosemethode ermitteln
    forecast_method = "Holt-Winters Exponentielle Glättung mit Trend"
    if forecast_df is not None and not forecast_df.empty and 'method' in forecast_df.columns:
        forecast_method = forecast_df['method'].iloc[0]
    
    html_content = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="author" content="Julian Streitberger">
    <meta name="description" content="Analyse der Inflationsentwicklung in Österreich, Deutschland und der Eurozone.">
    <title>Inflationsbericht {years[-1]}: Österreich im europäischen Vergleich</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: #ffffff;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }}
        header {{
            background-color: #343a40;
            color: #ffffff;
            padding: 30px 40px;
            border-bottom: 4px solid #007bff;
        }}
        header h1 {{
            font-size: 2em;
            margin-bottom: 10px;
            font-weight: 600;
        }}
        header .subtitle {{
            font-size: 1.1em;
            color: #e9ecef;
        }}
        .metadata {{
            display: flex;
            gap: 25px;
            font-size: 0.85em;
            margin-top: 20px;
            padding-top: 15px;
            border-top: 1px solid #495057;
        }}
        .metadata-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .metadata-label {{
            color: #adb5bd;
        }}
        .content {{
            padding: 40px;
        }}
        .section {{
            margin-bottom: 40px;
        }}
        .section-title {{
            font-size: 1.5em;
            color: #343a40;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #dee2e6;
            font-weight: 600;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        .card {{
            background-color: #ffffff;
            padding: 25px;
            border: 1px solid #e9ecef;
            border-radius: 4px;
        }}
        .card h3 {{
            font-size: 1.2em;
            margin-bottom: 15px;
            font-weight: 600;
            color: #007bff;
        }}
        .stat {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #f1f3f5;
            font-size: 0.95em;
        }}
        .stat:last-child {{ border-bottom: none; }}
        .stat-label {{ color: #6c757d; }}
        .stat-value {{ font-weight: 600; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            font-size: 0.9em;
        }}
        th, td {{
            padding: 10px 12px;
            border: 1px solid #dee2e6;
            text-align: left;
        }}
        th {{
            background-color: #f8f9fa;
            font-weight: 600;
        }}
        .positive {{ color: #dc3545; }}
        .negative {{ color: #28a745; }}
        .image-container {{
            border: 1px solid #dee2e6;
            padding: 20px;
            margin-top: 20px;
        }}
        .image-container h3 {{
            font-size: 1.2em;
            margin-bottom: 15px;
        }}
        object {{
            width: 100%;
            height: auto;
        }}
        footer {{
            background-color: #f8f9fa;
            color: #6c757d;
            text-align: center;
            padding: 20px;
            font-size: 0.85em;
            border-top: 1px solid #dee2e6;
        }}
        .disclaimer {{
            background-color: #fcf8e3;
            border: 1px solid #faebcc;
            color: #8a6d3b;
            padding: 20px;
            margin-top: 20px;
            border-radius: 4px;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Inflationsbericht Österreich</h1>
            <p class="subtitle">Vergleichende Analyse der Inflationsentwicklung in Österreich, Deutschland und der Eurozone</p>
            <div class="metadata">
                <div class="metadata-item">
                    <span class="metadata-label">Berichtszeitraum:</span>
                    <span class="metadata-value">{years[0]} - {years[-1]}</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">Datenstand:</span>
                    <span class="metadata-value">{latest_date.strftime('%B %Y')}</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">Erstellt am:</span>
                    <span class="metadata-value">{report_date.strftime('%d.%m.%Y, %H:%M Uhr')}</span>
                </div>
            </div>
        </header>
        
        <div class="content">
            <!-- Executive Summary -->
            <div class="section">
                <h2 class="section-title">Zusammenfassung</h2>
                <p>Diese Analyse untersucht die Inflationsentwicklung in Österreich im Vergleich zu Deutschland und der Eurozone auf Basis des Harmonisierten Verbraucherpreisindex (HVPI) von Eurostat. Der Bericht umfasst deskriptive Statistiken, Zeitreihenprognosen und Visualisierungen der wichtigsten Trends.</p>
                <p><strong>Aktuelle Entwicklung ({stats['Österreich']['latest_date'].strftime('%B %Y')}):</strong> Die Inflationsrate in Österreich liegt bei {stats['Österreich']['latest']:.2f}%. Im Vergleich dazu beträgt sie in Deutschland {stats['Deutschland']['latest']:.2f}% und in der Eurozone {stats['Eurozone']['latest']:.2f}%. Die Differenz zur Eurozone beträgt {abs(stats['Österreich']['latest'] - stats['Eurozone']['latest']):.2f} Prozentpunkte.</p>
                <p><strong>Prognose:</strong> Basierend auf einem {forecast_method}-Modell wird eine {'Senkung' if forecast_df is not None and not forecast_df.empty and forecast_df[forecast_df['country']=='Österreich']['inflation_rate'].iloc[-1] < stats['Österreich']['latest'] else 'gleichbleibende Tendenz'} der Inflation in den kommenden Monaten erwartet.</p>
            </div>
            
            <!-- Methodik -->
            <div class="section">
                <h2 class="section-title">Methodik und Datenbasis</h2>
                <div class="card">
                    <h3>Überblick</h3>
                    <div class="stat">
                        <span class="stat-label">Datenquelle:</span>
                        <span class="stat-value">Eurostat (Datensatz: prc_hicp_manr)</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Indikator:</span>
                        <span class="stat-value">Harmonisierter Verbraucherpreisindex (HVPI), jährliche Veränderungsrate</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Prognosemodell:</span>
                        <span class="stat-value">{forecast_method}</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Trainingsdaten (Prognose):</span>
                        <span class="stat-value">Letzte 24 Monate</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Konfidenzintervall:</span>
                        <span class="stat-value">95%</span>
                    </div>
                </div>
            </div>

            <!-- Statistische Kennzahlen -->
            <div class="section">
                <h2 class="section-title">Statistische Kennzahlen (seit 2020)</h2>
                <div class="grid">
"""
    
    # Add statistics cards
    for country in ['Österreich', 'Deutschland', 'Eurozone']:
        if country in stats:
            html_content += f"""                    <div class="card">
                        <h3>{country}</h3>
                        <div class="stat">
                            <span class="stat-label">Durchschnitt:</span>
                            <span class="stat-value">{stats[country]['mean']:.2f}%</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Median:</span>
                            <span class="stat-value">{stats[country]['median']:.2f}%</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Maximum:</span>
                            <span class="stat-value positive">{stats[country]['max']:.2f}%</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Minimum:</span>
                            <span class="stat-value negative">{stats[country]['min']:.2f}%</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Standardabweichung:</span>
                            <span class="stat-value">{stats[country]['std']:.2f}</span>
                        </div>
                    </div>
"""
    
    html_content += """                </div>
            </div>
"""
    
    # Add forecast section
    if forecast_df is not None and not forecast_df.empty:
        forecast_df_filtered = forecast_df[forecast_df['date'] <= '2026-03-31'].copy()
        
        html_content += """            <div class="section">
                <h2 class="section-title">Inflationsprognose bis März 2026</h2>
                <div class="grid">
"""
        
        for country in ['Österreich', 'Deutschland', 'Eurozone']:
            country_forecast = forecast_df_filtered[forecast_df_filtered['country'] == country].sort_values('date')
            if not country_forecast.empty:
                html_content += f"""                    <div>
                        <h4>{country}</h4>
                        <table>
                            <thead>
                                <tr>
                                    <th>Monat</th>
                                    <th>Prognose</th>
                                    <th>95% Konfidenzintervall</th>
                                </tr>
                            </thead>
                            <tbody>
"""
                
                month_names = {
                    1: 'Jan', 2: 'Feb', 3: 'Mär', 4: 'Apr', 5: 'Mai', 6: 'Jun',
                    7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Okt', 11: 'Nov', 12: 'Dez'
                }
                for _, row in country_forecast.iterrows():
                    month_str = f"{month_names[row['date'].month]} {row['date'].year}"
                    html_content += f"""                                <tr>
                                    <td>{month_str}</td>
                                    <td>{row['inflation_rate']:.2f}%</td>
                                    <td>{row['lower_bound']:.2f}% - {row['upper_bound']:.2f}%</td>
                                </tr>
"""
                
                html_content += """                            </tbody>
                        </table>
                    </div>
"""
        
        html_content += """                </div>
            </div>
"""
    
    # Add visualizations
    html_content += """            <div class="section">
                <h2 class="section-title">Visualisierungen</h2>
                <div class="image-container">
                    <h3>Vergleich der Inflationsraten mit Prognose</h3>
                    <object data="inflation_comparison.svg" type="image/svg+xml">
                        <p>SVG wird nicht unterstützt.</p>
                    </object>
                </div>
                <div class="image-container">
                    <h3>EZB-Leitzinsen</h3>
                    <object data="ecb_interest_rates.svg" type="image/svg+xml">
                        <p>SVG wird nicht unterstützt.</p>
                    </object>
                </div>
                <div class="image-container">
                    <h3>Inflationsdifferenz (Österreich - Eurozone)</h3>
                    <object data="inflation_difference.svg" type="image/svg+xml">
                        <p>SVG wird nicht unterstützt.</p>
                    </object>
                </div>
                <div class="image-container">
                    <h3>Statistischer Vergleich</h3>
                    <object data="statistics_comparison.svg" type="image/svg+xml">
                        <p>SVG wird nicht unterstützt.</p>
                    </object>
                </div>
                <div class="image-container">
                    <h3>Langfristige Entwicklung seit 2002</h3>
                    <object data="historical_comparison.svg" type="image/svg+xml">
                        <p>SVG wird nicht unterstützt.</p>
                    </object>
                </div>
                <div class="image-container">
                    <h3>Bestandteile der Inflation in Österreich</h3>
                    <object data="inflation_components_at.svg" type="image/svg+xml">
                        <p>SVG wird nicht unterstützt.</p>
                    </object>
                </div>
                <div class="image-container">
                    <h3>EU-weiter Inflationsvergleich (Heatmap)</h3>
                    <object data="eu_inflation_heatmap.svg" type="image/svg+xml">
                        <p>SVG wird nicht unterstützt.</p>
                    </object>
                </div>
            </div>
        </div>
        
        <footer>
        </footer>
    </div>
</body>
</html>"""
    
    # Save HTML file
    output_path = os.path.join(output_dir, 'inflation_report.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"HTML-Bericht gespeichert unter: {output_path}")
    return output_path
