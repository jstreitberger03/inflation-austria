"""Shared constants for the inflation report package."""

from __future__ import annotations

COICOP_CATEGORIES = ["CP00", "FOOD", "NRG", "IGD", "SERV"]

EU_COUNTRY_CODES = [
    "AT","BE","BG","HR","CY","CZ","DK","EE","FI","FR","DE","EL","GR","HU","IE","IT",
    "LT","LU","LV","MT","NL","PL","PT","RO","SE","SI","SK","ES"
]

COUNTRY_NAMES = {
    # Euro area and common aggregates
    "EA19": "Eurozone",
    "EA20": "Eurozone",
    "EA": "Eurozone",
    # EU members (German labels)
    "AT": "Österreich",
    "BE": "Belgien",
    "BG": "Bulgarien",
    "HR": "Kroatien",
    "CY": "Zypern",
    "CZ": "Tschechien",
    "DK": "Dänemark",
    "EE": "Estland",
    "FI": "Finnland",
    "FR": "Frankreich",
    "DE": "Deutschland",
    "EL": "Griechenland",
    "GR": "Griechenland",
    "HU": "Ungarn",
    "IE": "Irland",
    "IT": "Italien",
    "LT": "Litauen",
    "LU": "Luxemburg",
    "LV": "Lettland",
    "MT": "Malta",
    "NL": "Niederlande",
    "PL": "Polen",
    "PT": "Portugal",
    "RO": "Rumänien",
    "SE": "Schweden",
    "SI": "Slowenien",
    "SK": "Slowakei",
    "ES": "Spanien",
}

CATEGORY_NAMES = {
    "CP00": "Gesamtinflation",
    "FOOD": "Nahrungsmittel, Alkohol & Tabak",
    "NRG": "Energie",
    "IGD": "Industriegüter (ohne Energie)",
    "SERV": "Dienstleistungen",
}

MONTH_NAMES = {
    1: "Jan",
    2: "Feb",
    3: "Mär",
    4: "Apr",
    5: "Mai",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Okt",
    11: "Nov",
    12: "Dez",
}
