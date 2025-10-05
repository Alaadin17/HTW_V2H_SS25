# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Alaa Alsleman
# E-Mail: alsleman.alaa@hotmail.com

"""
Project name: EV profile simulation with Emobpy
Description: Creates mobility and consumption profiles for electric vehicles.
"""

import os
import json


def get_rules_for_group(
    group: str, specifics_rules: dict, base_day_rules: dict
) -> dict:
    """
    Return rule definitions for a specific target group.

    Parameters
    ----------
    group : str
        Name of the group (e.g., 'commuter').
    specifics_rules : dict
        Dictionary containing group-specific rules.
    base_day_rules : dict
        Dictionary with base rules that apply to any day.

    Returns
    -------
    dict
        A dictionary with merged rules for:
        - 'weekday' : dict
            Rules for weekdays (base rules updated with group-specific rules).
        - 'weekend' : dict
            Rules for weekends (base rules updated with group-specific rules).
    """
    group_specs = specifics_rules.get(group, {})
    return {
        "weekday": {**base_day_rules, **group_specs.get("weekday", {})},
        "weekend": {**base_day_rules, **group_specs.get("weekend", {})},
    }


def create_emobpy_rules_yaml(
    path: str, groups: list, specifics_rules: dict, base_day_rules: dict
) -> str:
    """
    Create a YAML-compatible JSON file with rules for emobpy.

    Parameters
    ----------
    path : str
        Destination directory where the file will be created.
    groups : list of str
        List of group names (e.g., ['commuter', 'student']).
    specifics_rules : dict
        Dictionary with group-specific rule definitions.
    base_day_rules : dict
        Dictionary with baseline rules that apply to all groups.

    Returns
    -------
    str
        File path of the created rules file.

    Notes
    -----
    The file is written in JSON format but kept YAML-compatible.
    It will always be saved under the name ``rules.yml`` in the given path.
    """
    rules = {}
    for group in groups:
        rules[group] = get_rules_for_group(group, specifics_rules, base_day_rules)

    os.makedirs(path, exist_ok=True)
    filepath = os.path.join(path, "rules.yml")

    with open(filepath, "w") as file:
        file.write("# YAML-compatible file in JSON style\n")
        json.dump(rules, file, indent=10)

    print(f"Rules file saved at: {filepath} ✅")
