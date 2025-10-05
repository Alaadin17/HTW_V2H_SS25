# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Alaa Alsleman
# E-Mail: alsleman.alaa@hotmail.com

"""
Project name: EV profile simulation with Emobpy
Description: Creates mobility and consumption profiles for electric vehicles.
"""

import os
from emobpy import DataBase


def define_path():

    # Don't change it. The structure is predefined.

    base_path = os.getcwd()
    # print((f"**base_path:** `{base_path}`"))
    relative_path = os.path.join("bev", "config_files")
    # print((f"**relative_path:** `{relative_path}`"))
    # 🔗 Combine
    config_path = os.path.join(base_path, relative_path)
    db_folder = "db"

    # print((f"**Config Files is under the following path:** `{config_path}`"))

    return base_path, config_path


def get_save_path(subfolder="bev_timeseries") -> str:
    """
    Returns the path where files should be saved.
    Optionally creates and returns a subfolder inside the current working directory.

    Args:
        subfolder (str, optional): Name of the subfolder to create/use.

    Returns:
        str: Absolute path to the (sub)folder.
    """
    file_path = os.getcwd()
    base_path = os.path.abspath(os.path.join(file_path, "..", ".."))
    results_path = os.path.join(base_path, "results")

    if subfolder:
        save_path = os.path.join(results_path, subfolder)
        print(type(save_path))
        if not os.path.exists(save_path):
            os.makedirs(save_path)
            print(f"📁 Folder created: {save_path}")
        else:
            print(f"✅ Folder already exists: {save_path}")
    else:
        pass

    return save_path


def get_consumption_profiles() -> dict:
    db = DataBase("db")
    db.loadfiles("db")
    consumption_profiles = {
        k: v
        for k, v in db.db.items()
        if isinstance(v, dict) and v.get("kind") == "consumption"
    }
    return consumption_profiles


def get_timeserie_from_consumption_profiles(consumption_profiles: dict) -> dict:
    """
    Extracts 'timeseries' data from a dictionary of consumption profiles.

    Args:
        consumption_profiles (dict):
            A dictionary where each key is a profile name (e.g., 'profile1'),
            and each value is another dictionary that may contain a 'timeseries' entry.

    Returns:
        dict:
            A new dictionary containing only those profiles that include a 'timeseries' entry.
            The keys are the profile names, and the values are the corresponding timeseries data.

    Notes:
        - Prints a warning for each profile missing the 'timeseries' key.
        - Prints an error message if no timeseries are found at all.
    """
    timeseries_data: dict = {}

    for key, profile in consumption_profiles.items():
        if "timeseries" in profile:
            timeseries_data[key] = profile["timeseries"]
        else:
            print(f"⚠️ 'timeseries' not found in profile '{key}'.")

    if not timeseries_data:
        print(
            "❌ No 'timeseries' found in any profile. Please ensure consumption was calculated."
        )

    return timeseries_data


def save_timeseries_to_csv(
    timeseries_data: dict, path: str, filename: str = "timeseries_output.csv"
) -> None:
    """
    Saves a dictionary of timeseries data to a CSV file.

    Args:
        timeseries_data (dict):
            A dictionary where keys are profile names (e.g., 'profile1') and
            values are lists or time series data (e.g., [10, 20, 30]).

        filename (str, optional):
            The name of the CSV file to create. Defaults to 'timeseries_output.csv'.


    Returns:
        None. Writes the CSV file to disk.

    """
    # Save each DataFrame
    for profile, df in timeseries_data.items():
        filename = os.path.join(path, f"{profile}.csv")
        df.to_csv(filename, index=True)
        print(f"✅ Saved: {filename}")
