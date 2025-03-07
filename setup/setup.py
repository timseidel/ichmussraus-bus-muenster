import pandas as pd
import numpy as np

def load_data(bus_path, fussbus_path):
    """Lädt die CSV-Daten in Pandas DataFrames."""
    bus = pd.read_csv(bus_path)
    fussbus = pd.read_csv(fussbus_path)
    return bus, fussbus

def process_bus_data(bus):
    """Verarbeitet die Busdaten zu einem Graphen-Format."""
    bus["arrival_time"] = pd.to_timedelta(bus["arrival_time"])
    bus["departure_time"] = pd.to_timedelta(bus["departure_time"])
    
    edges = []
    for i in range(1, len(bus)):
        if bus.loc[i, "stop_sequence"] == 1:
            continue
        
        u = bus.loc[i - 1, "stop_id"]
        v = bus.loc[i, "stop_id"]
        t = round(bus.loc[i - 1, "departure_time"].total_seconds() / 60)
        tt = round((bus.loc[i, "arrival_time"] - bus.loc[i - 1, "departure_time"]).total_seconds() / 60)

        edges.append([u, v, t, tt])

    bus_edges = pd.DataFrame(edges, columns=["u", "v", "t", "tt"]).sort_values(by=["u"])

    rows_to_append = bus_edges.loc[bus_edges["t"] >= 1440]
    bus_edges.loc[bus_edges["t"] >= 1440, "t"] -= 1440

    bus_edges = pd.concat([bus_edges, rows_to_append], ignore_index=True)

    return bus_edges

def process_fussbus_data(fussbus):
    """Verarbeitet die Fußbusdaten zu einem Graphen-Format."""
    laufen_df = pd.DataFrame({
        "u": fussbus["from"], 
        "v": fussbus["to"], 
        "tt": np.round(fussbus["duration"], 0)
    })
    
    vector = np.arange(1666)
    vector_repeated = np.tile(vector, len(laufen_df))
    
    expanded_df = pd.DataFrame({
        "u": np.repeat(laufen_df["u"].values, len(vector)),
        "v": np.repeat(laufen_df["v"].values, len(vector)),
        "tt": np.repeat(laufen_df["tt"].values, len(vector)),
        "t": vector_repeated
    })

    expanded_df_rev = expanded_df.copy()
    expanded_df_rev[["u", "v"]] = expanded_df_rev[["v", "u"]].values
    
    fussbus_final = pd.concat([expanded_df, expanded_df_rev], ignore_index=True)
    
    # Neue Spaltenreihenfolge mit 't' vor 'tt'
    fussbus_final = fussbus_final[["u", "v", "t", "tt"]]
    
    return fussbus_final

def export_data(bus_edges, fussbus_edges, bus_output_path, combined_output_path):
    """Exportiert die verarbeiteten Daten in TG-Dateien."""
    combined_edges = pd.concat([bus_edges, fussbus_edges], ignore_index=True).sort_values(by=["u", "t"])
    combined_edges.to_csv(combined_output_path, sep=" ", header=False, index=False)
    bus_edges.to_csv(bus_output_path, sep=" ", header=False, index=False)

def main():
    print("TG wird generiert.")
    bus, fussbus = load_data("setup/bus.csv", "setup/fussbus_opti.csv")
    print("Quell-Dateien geladen.")
    
    print("Verarbeite Bus-Edges.")
    bus_edges = process_bus_data(bus)
    print("Bus-Edges verarbeitet.")

    print("Verarbeite Fußbus-Edges.")
    fussbus_edges = process_fussbus_data(fussbus)
    print("Fußbus-Edges verarbeitet.")
    
    print("Zusammenfügen von Bus-Edges und Fußbus-Edges + export.")
    export_data(bus_edges, fussbus_edges, "static/tg_bus.tg", "static/tg_busfussbus.tg")
    
    print("TG Dateien exportiert.")

if __name__ == "__main__":
    main()