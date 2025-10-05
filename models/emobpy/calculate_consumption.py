# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Alaa Alsleman
# E-Mail: alsleman.alaa@hotmail.com

"""
Project name: EV profile simulation with Emobpy
Description: Creates mobility and consumption profiles for electric vehicles.
"""

import pandas as pd
from typing import List, Tuple
from emobpy import DataBase, BEVspecs, HeatInsulation, Consumption


def get_all_profile_list() -> List[str]:
    """
    Loads the available mobility profiles from the local database.

    Returns:
        List[str]: A list of profile names found in the database.
    """
    db = DataBase("db")
    db.loadfiles("db")
    profiles_list = list(db.db.keys())

    return profiles_list


def get_driving_profiles():
    """
    Returns all driving profiles from the database.

    Parameters
    ----------

    Returns
    -------
    dict
        Dictionary of driving profiles, where:
        - keys are profile names (str)
        - values are profile entries (dict) with metadata and rules.

    Notes
    -----
    Only entries where ``kind == 'driving'`` are returned.
    """
    db = DataBase("db")
    db.loadfiles("db")
    driving_entries = {
        k: v
        for k, v in db.db.items()
        if isinstance(v, dict) and v.get("kind") == "driving"
    }
    return driving_entries


def get_consumption_profiles():
    """
    Returns all consumption profiles from the database.

    Parameters
    ----------

    Returns
    -------
    dict
        Dictionary of consumption profiles, where:
        - keys are profile names (str)
        - values are profile entries (dict) with metadata and rules.

    Notes
    -----
    Only entries where ``kind == 'consumption'`` are returned.
    """
    db = DataBase("db")
    db.loadfiles("db")
    consumption_entries = {
        k: v
        for k, v in db.db.items()
        if isinstance(v, dict) and v.get("kind") == "consumption"
    }
    return consumption_entries


def load_bev_database() -> Tuple[pd.DataFrame, BEVspecs]:
    """
    Loads the Battery Electric Vehicle (BEV) database with manufacturer,
    model, and production year information.

    Returns:
        pd.DataFrame: A DataFrame with columns ['Manufacturer', 'Model', 'Year'].
    """
    BEVs = BEVspecs()
    models = BEVs.data.copy()

    rows = []
    for manufacturer, model_dict in models.items():
        if manufacturer == "fallback_parameters":
            continue
        for model_name, years in model_dict.items():
            for year in years:
                rows.append((manufacturer, model_name, int(year)))

    bev_df = pd.DataFrame(rows, columns=["Manufacturer", "Model", "Year"])
    return bev_df, BEVs


def select_bev_models(indices: List[int], df_bev: pd.DataFrame) -> pd.DataFrame:
    """
    Selects specific BEV models from the DataFrame by row indices.

    Parameters:
        indices (List[int]): List of row indices to select.
        df_bev (pd.DataFrame): DataFrame containing BEV data.

    Returns:
        pd.DataFrame: A DataFrame with the selected models.
    """
    selected_models = df_bev.iloc[indices]
    return selected_models


def run(selected_models, profiles_list):
    """
    Run energy consumption simulations for selected BEV models and mobility profiles.

    Parameters
    ----------
    selected_models : pandas.DataFrame
        DataFrame containing at least the columns ``["Manufacturer", "Model", "Year"]``
        that specify the vehicle models to simulate.
    profiles_list : list of str
        List of mobility profile names to run the simulations with.

    Returns
    -------
    None
        The function runs the simulations and saves the resulting profiles in the database folder.

    Notes
    -----
    - For each selected BEV model, the function iterates over all provided mobility profiles.
    - A `Consumption` object is created and run with predefined parameters, including
      cabin heat transfer, airflow, passenger data, and driving cycle type.
    - The resulting consumption profiles are saved in the ``db`` folder.
    - After completing simulations, the database is updated.
    """
    BEVs = BEVspecs()
    db = DataBase("db")
    db.loadfiles("db")
    HI = HeatInsulation(True)  # Create heat insulation configuration by copying default

    models_tupeln = [
        tuple(x) for x in selected_models[["Manufacturer", "Model", "Year"]].values
    ]

    for element in models_tupeln:
        for profile in profiles_list:
            BEV = BEVs.model(element)  # Model instance containing vehicle parameters
            c = Consumption(profile, BEV)
            c.load_setting_mobility(db)

            c.run(
                heat_insulation=HI,
                weather_country="DE",
                weather_year=2016,
                passenger_mass=75,  # kg
                passenger_sensible_heat=70,  # W
                passenger_nr=1.5,  # number of passengers
                air_cabin_heat_transfer_coef=20,  # W/(m²K)
                air_flow=0.02,  # m³/s
                driving_cycle_type="WLTC",
                road_type=0,
                road_slope=0,
            )

            c.save_profile("db")
        # Update database after new profiles are created
        db.update()
