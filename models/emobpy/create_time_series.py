# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Alaa Alsleman
# E-Mail: alsleman.alaa@hotmail.com

"""
Project name: EV profile simulation with Emobpy
Description: Creates mobility and consumption profiles for electric vehicles.
"""

import os
import yaml

from emobpy import Mobility


# ----------------------------------------
# Einzelne Regelgruppe aus der Datei laden
# ----------------------------------------
def get_user_group_rule(filepath: str, group: str) -> dict:
    """
    Load and return the rule definitions for a specific user group from a YAML file.

    Parameters
    ----------
    filepath : str
        Path to the YAML file containing group rules.
    group : str
        Name of the group whose rules should be retrieved.

    Returns
    -------
    dict
        Dictionary with the rules for the specified group.

    Raises
    ------
    FileNotFoundError
        If the specified file does not exist.
    KeyError
        If the given group is not found in the rules file.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        rules = yaml.safe_load(f)
        print(rules)
    return rules[group]


# Zeitreihen für Gruppen erstellen
def create_time_series_for_usergroups(
    total_hours: int,
    time_step_in_hrs: float,
    reference_date: str,
    user_group: str,
    config_path: str,
    db_folder: str = "db",
) -> Mobility:
    """
    Create mobility time series for a defined user group.

    Parameters
    ----------
    total_hours : int
        Total number of hours for the simulation (e.g., 168 for one week).
    time_step_in_hrs : float
        Time resolution of the time series in hours (e.g., 0.25 for 15 minutes).
    reference_date : str
        Reference date for the start of the time series (format: 'YYYY-MM-DD').
    user_group : str
        Name of the user group (e.g., 'commuter', 'retiree', 'student').
    config_path : str
        Path to the configuration folder containing the statistical input files.
    db_folder : str, optional
        Folder where the generated `.pkl` profiles are saved (default is 'db').

    Returns
    -------
    Mobility
        A `Mobility` object containing the generated time series for the given user group.

    Notes
    -----
    - The function automatically loads statistical input files:
      - ``TripsPerDay.csv``
      - ``DepartureDestinationTrip.csv``
      - ``DistanceDurationTrip.csv``
    - The generated profile is saved in the specified ``db_folder``.
    """
    print(f"🔄 Erstelle Mobilitätsprofil für: {user_group}")

    mobility_object = Mobility(config_folder=config_path)
    mobility_object.set_params(
        name_prefix=f"BEV_{user_group}",
        total_hours=total_hours,  # e.g. 1 week
        time_step_in_hrs=time_step_in_hrs,  # e.g. 0.25 = 15 minutes
        category=user_group,
        reference_date=reference_date,
    )
    mobility_object.set_stats(
        stat_ntrip_path=os.path.join(config_path, "TripsPerDay.csv"),
        stat_dest_path=os.path.join(config_path, "DepartureDestinationTrip.csv"),
        stat_km_duration_path=os.path.join(config_path, "DistanceDurationTrip.csv"),
    )
    mobility_object.set_rules(rule_key=user_group)
    mobility_object.run()
    mobility_object.save_profile(
        folder=db_folder, description=f"Mobilitätsprofil für {user_group}"
    )
    print(f"✅ Profil gespeichert: {user_group}\n")

    return mobility_object
