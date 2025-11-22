"""Plain-text reporting utilities."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd


def generate_text_report(df, stats, comparison, trends, output_dir: str | Path = "output") -> str:
    """Create a comprehensive text report and return the file path."""
    output_path = Path(output_dir) / "inflation_report.txt"
    report_lines: list[str] = []

    report_lines.append("=" * 80)
    report_lines.append("INFLATIONSBERICHT: ÖSTERREICH IM EUROPÄISCHEN VERGLEICH")
    report_lines.append("=" * 80)
    report_lines.append(f"Erstellt am: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")

    report_lines.append("ZUSAMMENFASSUNG")
    report_lines.append("-" * 80)

    years = sorted(df["year"].unique())
    report_lines.append(f"Analysezeitraum: {years[0]} - {years[-1]}")
    report_lines.append("")

    for country, values in stats.items():
        latest_rate = values["latest"]
        latest_date = values["latest_date"]
        report_lines.append(
            f"{country} - Aktuelle Inflationsrate ({latest_date.strftime('%B %Y')}): {latest_rate:.2f}%"
        )
    report_lines.append("")

    report_lines.append("STATISTISCHE KENNZAHLEN (SEIT 2020)")
    report_lines.append("-" * 80)

    for country, values in stats.items():
        report_lines.append(f"\n{country}:")
        report_lines.append(f"  Durchschnittliche Inflation: {values['mean']:.2f}%")
        report_lines.append(f"  Median der Inflation:      {values['median']:.2f}%")
        report_lines.append(f"  Minimale Inflation:        {values['min']:.2f}%")
        report_lines.append(f"  Maximale Inflation:        {values['max']:.2f}%")
        report_lines.append(f"  Standardabweichung:        {values['std']:.2f}")

    report_lines.append("")
    report_lines.append("TRENDS UND EXTREMWERTE")
    report_lines.append("-" * 80)

    for country, values in trends.items():
        report_lines.append(f"\n{country}:")
        report_lines.append(
            f"  Höchste Inflation: {values['highest_rate']:.2f}% im {values['highest_date'].strftime('%B %Y')}"
        )
        report_lines.append(
            f"  Niedrigste Inflation: {values['lowest_rate']:.2f}% im {values['lowest_date'].strftime('%B %Y')}"
        )

    report_lines.append("")
    report_lines.append("MONATLICHER VERGLEICH")
    report_lines.append("-" * 80)
    report_lines.append(
        f"{'Monat':<12} {'Österreich':<15} {'Deutschland':<15} {'Eurozone':<15} {'Differenz (AT-EA)':<20}"
    )
    report_lines.append("-" * 80)

    for date in comparison.index[-12:]:
        austria_val = comparison.loc[date, "Österreich"]
        germany_val = comparison.loc[date, "Deutschland"]
        euro_val = comparison.loc[date, "Eurozone"]
        diff_val = comparison.loc[date, "Difference (AT - EA)"]

        report_lines.append(
            f"{date.strftime('%Y-%m'):<12} {austria_val:>8.2f}%      "
            f"{germany_val:>8.2f}%      {euro_val:>8.2f}%      "
            f"{diff_val:>8.2f} PP"
        )

    report_lines.append("")
    report_lines.append("ANALYSE-ZUSAMMENFASSUNG")
    report_lines.append("-" * 80)

    if "Difference (AT - EA)" in comparison.columns:
        avg_diff = comparison["Difference (AT - EA)"].mean()
        months_higher = (comparison["Difference (AT - EA)"] > 0).sum()
        total_months = len(comparison)

        report_lines.append(
            f"Durchschnittliche Differenz (Österreich - Eurozone): {avg_diff:.2f} Prozentpunkte."
        )
        report_lines.append(
            f"Österreich hatte in {months_higher} von {total_months} Monaten "
            f"({months_higher/total_months:.1%}) eine höhere Inflation als die Eurozone."
        )

        if avg_diff > 0.1:
            report_lines.append("Im Durchschnitt war die Inflation in Österreich tendenziell höher als im Euroraum.")
        elif avg_diff < -0.1:
            report_lines.append("Im Durchschnitt war die Inflation in Österreich tendenziell niedriger als im Euroraum.")
        else:
            report_lines.append("Im Durchschnitt entsprach die Inflation in Österreich weitgehend der des Euroraums.")

    report_lines.append("")
    report_lines.append("=" * 80)
    report_lines.append("ENDE DES BERICHTS")
    report_lines.append("=" * 80)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"Textbericht gespeichert unter: {output_path}")
    return str(output_path)


def print_summary(stats, trends) -> None:
    """Print a short summary to stdout."""
    print("\n" + "=" * 80)
    print("ZUSAMMENFASSUNG DER INFLATIONSANALYSE")
    print("=" * 80)

    for country, values in stats.items():
        print(f"\n{country}:")
        print(f"  Aktuell: {values['latest']:.2f}% ({values['latest_date'].strftime('%B %Y')})")
        print(f"  Durchschnitt (seit 2020): {values['mean']:.2f}%")
        print(f"  Spitzenwert: {trends[country]['highest_rate']:.2f}% ({trends[country]['highest_date'].strftime('%B %Y')})")

    print("\n" + "=" * 80)
