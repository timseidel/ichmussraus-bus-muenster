"""Ich muss hier raus - Flask App"""

import os
import sys
import subprocess
from typing import List, Dict, Tuple, Optional
from flask import Flask, render_template, request, jsonify, send_from_directory
import pandas as pd
import numpy as np
import pytglib as tgl

# Initialisierung der Flask-Anwendung
app = Flask(__name__)

# Definiere hier die benötigten Dateipfade
benoetigte_dateien: List[str] = ["static/tg_busfussbus.tg"]


def pruefe_dateien_existieren(dateien: List[str]) -> bool:
    """Überprüfe, ob die angegebenen Dateien existieren."""
    return all(os.path.exists(datei) for datei in dateien)


def generiere_dateien() -> None:
    """Führe ein externes Skript aus, um Dateien zu erzeugen."""
    try:
        subprocess.run(["python", "setup/setup.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Ein Fehler ist beim Erzeugen der Dateien aufgetreten: {e}")
        sys.exit()


def lade_daten():
    """Ladet die notwendigen Daten beim Start der Anwendung."""
    if not pruefe_dateien_existieren(benoetigte_dateien):
        print("Dateien fehlen, generiere Dateien...")
        generiere_dateien()
    else:
        print("Alle benötigten Dateien sind vorhanden.")

    # Laden der Haltestellen-Daten aus einer Feather-Datei
    try:
        haltestellen_data: pd.DataFrame = pd.read_feather(
            "static/haltestellen_data.feather"
        )
    except FileNotFoundError:
        print("Fehler: Die Haltestellen-Feather-Datei konnte nicht geladen werden.")
        sys.exit()

    # Laden des TG aus Datei in Static
    try:
        print("Lade Temporal Graph.")
        tg = tgl.load_ordered_edge_list("static/tg_busfussbus.tg")
    except FileNotFoundError:
        print("Fehler: Die .tg-Datei konnte nicht geladen werden.")
        sys.exit()

    # Nodemap Def und Calcs
    nodemap: Dict[int, int] = tg.getNodeMap()
    nodemap_reverse: Dict[int, int] = {v: k for k, v in nodemap.items()}

    return haltestellen_data, tg, nodemap, nodemap_reverse


@app.route("/load-stops", methods=["GET"])
def load_stops() -> "Flask.Response":
    """
    Gibt eine Liste aller Haltestellen mit ihren Details im JSON-Format zurück.
    """
    stops_data: List[Dict] = haltestellen_data[
        ["stop_id", "stop_name", "stop_lat", "stop_lon"]
    ].to_dict(orient="records")
    return jsonify(stops_data)


def find_nearest_stop(marker_lat: float, marker_lon: float, stops: pd.DataFrame) -> str:
    """
    Findet die nächstgelegene Haltestelle zu einem angegebenen geografischen Marker.
    """
    lat1, lon1 = np.radians(marker_lat), np.radians(marker_lon)
    lat2, lon2 = np.radians(stops["stop_lat"].values), np.radians(
        stops["stop_lon"].values
    )

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    earth_radius = 6371.0
    distances = earth_radius * c

    nearest_index = np.argmin(distances)
    nearest_stop_id = stops.iloc[nearest_index]["stop_id"]

    return str(int(nearest_stop_id))


def get_nearest_stop_details(
    marker_lat: float, marker_lon: float, stops: pd.DataFrame
) -> Tuple[Optional[str], Optional[str], Tuple[Optional[float], Optional[float]]]:
    """
    Findet die nächstgelegene Haltestelle und deren Details.
    """
    haltestelle_id = find_nearest_stop(marker_lat, marker_lon, stops)
    nearest_stop = stops.loc[stops["stop_id"] == int(haltestelle_id)].squeeze()

    if nearest_stop.empty:
        return None, None, (None, None)

    haltestelle_name: str = nearest_stop["stop_name"]
    nearest_lat: float = float(nearest_stop["stop_lat"])
    nearest_lon: float = float(nearest_stop["stop_lon"])

    return str(haltestelle_id), haltestelle_name, (nearest_lat, nearest_lon)


def format_and_convert_time_to_minutes(time_str: str) -> int:
    """
    Formatiert einen Zeit-String und konvertiert ihn in Minuten.
    """
    if len(time_str.split(":")) == 3:
        formatted_time = time_str
    elif len(time_str.split(":")) == 2:
        formatted_time = time_str + ":00"
    else:
        raise ValueError("Input time format not recognized")

    time_in_minutes = round(pd.to_timedelta(formatted_time).total_seconds() / 60)
    return time_in_minutes


def temporal_graph_solver(haltestelle: int, time_input: str) -> List[int]:
    """
    Berechnet die frühesten Ankunftszeiten basierend auf unserer .tg Datei.
    """
    time_input = format_and_convert_time_to_minutes(time_input)

    arrival_times = list(
        tgl.earliest_arrival_times(
            tg, nodemap[haltestelle], [time_input, time_input + 1440]
        )
    )

    arrival_times = [max(x - time_input, 0) for x in arrival_times]

    arrival_times = [
        arrival_times[index]
        for _, index in sorted((pos, idx) for idx, pos in nodemap_reverse.items())
    ]

    return arrival_times


@app.route("/")
def index() -> "Flask.Response":
    """
    Rendert und gibt die index.html-Vorlage zurück.
    """
    return render_template("index.html")


@app.route("/favicon.ico")
def favicon() -> "Flask.Response":
    """
    Sendet die Favicon-Icon-Datei vom statischen Ordner des Anwendungsservers zurück.
    """
    return send_from_directory(
        app.static_folder, "favicon.ico", mimetype="image/vnd.microsoft.icon"
    )


@app.route("/generate-data", methods=["POST"])
def generate_data() -> "Flask.Response":
    """
    Verarbeitet eine POST-Anfrage, um die nächstgelegene Haltestelle
    und entsprechende Zeitdaten zu ermitteln.
    """
    time_input: str = request.json.get("time_input")
    marker_position: Optional[Tuple[float, float]] = request.json.get("marker_position")

    if marker_position:
        lat, lon = marker_position

        haltestelle_id, haltestelle_name, (nearest_lat, nearest_lon) = (
            get_nearest_stop_details(lat, lon, haltestellen_data)
        )

        times = temporal_graph_solver(int(haltestelle_id), time_input)

        return jsonify(
            {
                "stop_name": haltestelle_name,
                "nearest_stop": {"lat": nearest_lat, "lon": nearest_lon},
                "times": times,
            }
        )

    else:
        return jsonify({"error": "Keine Marker-Position angegeben."}), 400


if __name__ == "__main__":
    haltestellen_data, tg, nodemap, nodemap_reverse = lade_daten()
    app.run(debug=False)
