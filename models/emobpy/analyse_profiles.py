# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Alaa Alsleman
# E-Mail: alsleman.alaa@hotmail.com

"""
Project name: EV profile simulation with Emobpy
Description: Creates mobility and consumption profiles for electric vehicles.
"""


from emobpy import DataBase
from emobpy.plot import NBplot
from IPython.display import display, Markdown, clear_output
import ipywidgets as widgets


def load_profiles(db_path):
    """
    Load all mobility profiles from the Database.

    Parameters
    ----------
    db_path : str or Path
        Path to the directory containing the mobility Database.

    Returns
    -------
    DataBase
        A DataBase object with the loaded mobility profiles.
    """
    db = DataBase(db_path)
    db.loadfiles()
    return db


def list_profiles(db):
    """
    Return a list of profile names stored in the database.

    Parameters
    ----------
    db : DataBase
        A DataBase object containing mobility profiles.

    Returns
    -------
    list of str
        List of profile names available in the database.
    """
    return list(db.db.keys())


def show_profile_info(db, profile_name):
    """
    Show the rules and type of the given profile.

    Parameters
    ----------
    db : DataBase
        A DataBase object containing mobility profiles.
    profile_name : str
        Name of the profile to retrieve information for.

    Returns
    -------
    dict
        Dictionary with profile information containing:
        - 'name' (str): The profile name.
        - 'kind' (str): The profile type.
        - 'rules' (dict): The user-defined rules of the profile.

    Raises
    ------
    ValueError
        If the specified profile is not found in the database.
    """
    if profile_name not in db.db:
        raise ValueError(f"Profil {profile_name} nicht in der Datenbank gefunden.")

    data = db.db[profile_name]
    return {"name": profile_name, "kind": data["kind"], "rules": data["user_rules"]}


def plot_profile(db, profile_name, save_path=None):
    """
    Visualize a driving profile as a Plotly figure.

    Parameters
    ----------
    db : DataBase
        A DataBase object containing mobility profiles.
    profile_name : str
        Name of the profile to visualize.
    save_path : str or Path, optional
        File path to save the plot as an interactive HTML file.
        If None (default), the plot is not saved.

    Returns
    -------
    plotly.graph_objects.Figure
        The Plotly figure object representing the driving profile.
    """
    plot = NBplot(db)
    fig = plot.sgplot_dp(profile_name)

    if save_path:
        fig.write_html(save_path)
    return fig


def run_profile_viewer(profile_name, db):
    """
    Display an interactive viewer for a given mobility profile inside a Jupyter notebook.

    Parameters
    ----------
    profile_name : str or None
        Name of the profile to visualize. If None, a warning message is shown instead.
    db : DataBase
        A DataBase object containing mobility profiles.

    Returns
    -------
    None
        This function displays the profile information and plot inline in the notebook
        using IPython widgets and Plotly.
    """
    output = widgets.Output()
    with output:
        clear_output(wait=True)
        if profile_name is not None:
            display(Markdown(f"## 🔍 Profilansicht: `{profile_name}`"))
            fig = plot_profile(db, profile_name)
            fig.update_layout(title=f"🔍 Profil: {profile_name}")
            fig.show()
        else:
            display(Markdown("⚠️ **Du musst zuerst ein Profil erstellen.**"))
    display(output)
