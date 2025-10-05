import matplotlib.pyplot as plt
import pandas as pd
from oemof.solph import EnergySystem
import logging
from oemof.tools import logger
from oemof.solph import views
import os
import matplotlib

matplotlib.use("TkAgg")  # sicherstellen, dass ein GUI-fähiges Backend genutzt wird

# initiate the logger (see the API docs for more information)
logger.define_logging(
    logfile="oemof_example.log",
    screen_level=logging.INFO,
    file_level=logging.INFO,
)


def get_dump_path():
    file_path = os.getcwd()
    base_path = os.path.abspath(
        os.path.join(file_path, "..", "..")
    )  # main directory of the repo
    # 🔗 Combine to go to timeseries.csv
    dump_path = os.path.join(base_path, "dumps")
    return dump_path


def get_save_path(subfolder="esys") -> str:
    """
    Returns the path where files should be saved.
    Optionally creates and returns a subfolder inside the current working directory.

    Args:
        subfolder (str, optional): Name of the subfolder to create/use.

    Returns:
        str: Absolute path to the (sub)folder.
    """
    file_path = os.getcwd()
    base_path = os.path.abspath(
        os.path.join(file_path, "..", "..", "results")
    )  # main directory of the repo
    # 🔗 Combine to go to results - esys path

    if subfolder:
        save_path = os.path.join(base_path, subfolder)

        if not os.path.exists(save_path):
            os.makedirs(save_path)
            print(f"📁 Folder created: {save_path}")
        else:
            print(f"✅ Folder already exists: {save_path}")
    else:
        pass

    return save_path


def restore_results(dump_path, filename) -> tuple[any, any]:
    restore_results = True
    if restore_results:
        logging.info("Restore the energy system and the results.")
        energysystem = EnergySystem()
        energysystem.restore(dpath=dump_path, filename=filename)
        results_main_df = energysystem.results["main"]
        results_meta_df = energysystem.results["meta"]
        return results_main_df, results_meta_df

    else:
        logging.warning("Results restoration skipped.")
        return None


def get_electricity_flows(results_df) -> pd.DataFrame:
    Dictionary_flows_electricity = {}
    results = results_df
    for k, v in results.items():
        # Demand
        if str(k[0]) == "electricity" and str(k[1]) == "demand":
            label = str("demand")  # label sicher als String
            flow = v["sequences"]["flow"]
            Dictionary_flows_electricity[label] = flow
        # grid-feed-in
        elif str(k[0]) == "electricity" and str(k[1]) == "excess_bel":
            label = str("grid-feed-in")  # label sicher als String
            flow = v["sequences"]["flow"]
            Dictionary_flows_electricity[label] = flow
        # grid-supply
        elif str(k[0]) == "grid-supply" and str(k[1]) == "electricity":
            label = str("grid-supply")  # label sicher als String
            flow = v["sequences"]["flow"]
            Dictionary_flows_electricity[label] = flow
        # PV
        elif str(k[0]) == "pv" and str(k[1]) == "electricity":
            label = str("pv")  # label sicher als String
            flow = v["sequences"]["flow"]
            Dictionary_flows_electricity[label] = flow
        elif str(k[0]) == "wallbox" and str(k[1]) == "mobility":
            label = str(f"from {k[0]} to {k[1]}")  # label sicher als String
            flow = v["sequences"]["flow"]
            Dictionary_flows_electricity[label] = flow
        elif str(k[0]) == "wallbox_to_BEV" and str(k[1]) == "mobility":
            label = str(f"from Wallbox to {k[1]}")  # label sicher als String
            flow = v["sequences"]["flow"]
            Dictionary_flows_electricity[label] = flow
        elif str(k[0]) == "mobility" and str(k[1]) == "wallbox_from_BEV":
            label = str(f"from {k[0]} to Wallbox")  # label sicher als String
            flow = v["sequences"]["flow"]
            Dictionary_flows_electricity[label] = flow

    Data_electricity = pd.DataFrame(Dictionary_flows_electricity)
    return Data_electricity


def extract_battery_data(results, storage_label):
    """
    Extrahiert Ladefluss, Entladefluss und Speicherinhalt eines oemof-Speichers.

    Parameter:
    -----------
    results : dict
        Ergebnisse aus dem oemof.solve().
    storage_label : str
        Label des Speichers, z. B. 'BEV_Storage'.

    Rückgabe:
    ---------
    df : pd.DataFrame
        DataFrame mit Zeitreihen (SOC, charge, discharge).
    """

    # Knoten extrahieren
    node_data = views.node(results, storage_label)
    sequences = node_data["sequences"]
    # Spaltennamen umbenennen für Lesbarkeit
    renamed_cols = {}
    for col in sequences.columns:
        if col[1] == "storage_content":
            renamed_cols[col] = "State_of_Charge"
    df = sequences.rename(columns=renamed_cols)
    return df

def save_dataframe_to_csv(
    df: pd.DataFrame,
    filepath: str,
    filename: str,
    sep=",",
    encoding="utf-8",
    index=True,
):
    """
    Speichert ein pandas DataFrame als CSV-Datei unter einem bestimmten Pfad.

    Parameter:
    - df: pandas.DataFrame
    - filepath: str, z. B. "C:/Users/Name/Projekte/daten.csv"
    - sep: Spaltentrenner, Standard: ","
    - encoding: Zeichensatz, Standard: "utf-8"
    - index: Ob der Index gespeichert werden soll, Standard: False
    """

    # Vollständiger Pfad zur Datei
    full_path = os.path.join(filepath, f"{filename}.csv")

    try:
        df.to_csv(full_path, sep=sep, encoding=encoding, index=index)
        print(f"✅ DataFrame erfolgreich gespeichert unter: {filepath}")
    except Exception as e:
        print(f"❌ Fehler beim Speichern der CSV-Datei: {e}")


def plot(
    df, columns_to_plot=None, color_map=None, title="Energy Flows"
):
    """
    Plots energy flow time series from a DataFrame.
    """
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("DataFrame must have DatetimeIndex.")

    if columns_to_plot is None:
        columns_to_plot = df.columns.tolist()

    # Fallback-Farben automatisch generieren, falls nicht angegeben
    default_colors = plt.cm.get_cmap("tab10", len(columns_to_plot))

    if color_map is None:
        color_map = {}

    fig, ax = plt.subplots(figsize=(14, 6))

    for i, col in enumerate(columns_to_plot):
        if col not in df.columns:
            print(f"⚠️ Column {col} not in DataFrame — skipping")
            continue

        # Farbe finden oder fallback verwenden
        color = color_map.get(col, default_colors(i))
        ax.plot(df.index, df[col].fillna(0), label=col, linewidth=2, color=color)

    ax.set_title(title)
    ax.set_xlabel("Time")
    ax.set_ylabel("Energy Flow (kW)")
    ax.grid(True)
    ax.legend(loc="upper left", fontsize=9)
    plt.tight_layout()
    plt.show()



if __name__ == "__main__":
    case_1 = "case2_es_charger_limited_BEV_dumb"
    case_2 = "case3_es_charger_limited_BEV_transformer_uni_directional"
    case_3 = "case4_es_charger_limited_BEV_transformer_bi_directional"
    case_to_study = case_3

    ### restore and get results ####
    path = get_dump_path()
    main_results = restore_results(path, filename=case_to_study)[0]
    elec_flows_df = get_electricity_flows(main_results)
    battery_flows_df = extract_battery_data(main_results, "BEV_Storage")
    save_dataframe_to_csv(elec_flows_df, get_save_path(), case_to_study, ",")
    plot(elec_flows_df)
    plot(battery_flows_df)