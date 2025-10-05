"""

        Bus_ele                      Bus_BEV
            |                            |
            |                            |------BEV-Storage
PV----------|                            |
            |<-------------------------->|
excess_bel--|
demand------|


"""

###########################################################################
# imports
###########################################################################
import logging
import os
import pandas as pd
from oemof.tools import logger

from oemof.solph import EnergySystem
from oemof.solph import Model
from oemof.solph import buses
from oemof.solph import components as cmp

from oemof.solph import flows
from oemof.solph import helpers
from oemof.solph import processing
from pyomo.opt import SolverStatus, TerminationCondition
import warnings

# Storage

# plot

import tkinter as tk
from tkinter import filedialog


def get_file_path():
    file_path = os.getcwd()
    start_dir = os.path.abspath(
        os.path.join(file_path, "..", "..")
    )  # main directory of the repo
    # Hauptfenster erstellen, aber verstecken
    root = tk.Tk()
    root.withdraw()

    # Dateiauswahldialog öffnen mit Startverzeichnis
    file_path = filedialog.askopenfilename(
        title="Wählen Sie eine Datei aus",
        initialdir=start_dir,  # Hier wird der Startordner gesetzt
        filetypes=[("Excel- und CSV-Dateien", "*.xlsx *.xls *.csv")],
    )

    if not file_path:
        print("Keine Datei wurde ausgewählt")
        return None

    return file_path


def get_timeseries():
    timeseries_path = (
        r"C:\git\github\V2G_HTW_SS25\input_timeseries\input_timeseries_with_BEV.csv"
    )
    df_timeseries = pd.read_csv(timeseries_path, delimiter=",")
    return df_timeseries


def get_BEV_timeserie():
    timeseries_path = get_file_path()
    BEV_timeseries = pd.read_csv(timeseries_path)
    return BEV_timeseries


class EnergySystemModel:
    # *************************************************************************
    # ********** PART 1 - Define and optimise the energy system ***************
    # *************************************************************************
    def __init__(self, dump_filename):
        super().__init__()
        # ****** Defining Variables ******
        self.dump_filename = dump_filename
        self.start_date = None
        self.periods = None
        self.freq = None
        self.time_index = None
        self.es = None
        self.model = None
        self.results = None
        self.bus_df = None
        self.data = None
        self.ev_params = None
        self.df_timeseries = None
        self.BEV_timeseries = None
        self.electricity_dataframe = None

        # initiate the logger (see the API docs for more information)
        logger.define_logging(
            logfile="oemof_example.log",
            screen_level=logging.INFO,
            file_level=logging.INFO,
        )

        # Output Info
        logging.info("Initialize the energy system")

        self.main()

    def main(self):
        self.should_dump_results = True  # oder False je nach Bedarf
        self.solver = "cbc"  # 'glpk', 'gurobi',....
        self.solver_verbose = False  # show/hide solver output
        self.solve_kwargs = None
        self.cmdline_options = None
        self.debug = False  # Set number_of_timesteps to 3 to get a readable lp-file.
        # can we get electricity from grid?
        self.grid_supply = 30  # kW
        self.wallbox_power = 11  # kW
        self.Model()

    def Model(self):
        logging.info("define_time_index")
        self.define_time_index()
        logging.info("define_timeseries")
        self.define_timeseries()
        logging.info("Create oemof objects")
        self.create_oemof_objects()
        logging.info("Optimise the energy system")
        self.optimise_energysystem()
        # if tee_switch is true solver messages will be displayed
        logging.info("Solve the optimization problem")
        self.solve_energysystem()
        logging.info("extract_results")
        self.extract_results()
        logging.info("Dump the energy system and the results.")
        self.dump_results()

    def define_time_index(self):
        # ****** Defining Time index ******
        self.start_date = "2022-01-01"
        self.periods = 672
        self.freq = "15min"
        self.time_index = pd.date_range(
            start=self.start_date, periods=self.periods, freq=self.freq
        )
        self.es = EnergySystem(timeindex=self.time_index, infer_last_interval=True)

    def define_timeseries(self):
        logging.info("Import general timeseries")
        self.df_timeseries = get_timeseries()
        logging.info("Import BEV-timeseries")
        # self.BEV_timeseries = get_BEV_timeserie()
        # Zeitreihen
        self.BEV_state = self.df_timeseries["BEV_at_home"]
        self.PV_load = self.df_timeseries["PV_kW"]
        self.demand = self.df_timeseries["Load_kW"]
        self.BEV_consumption = self.df_timeseries["consumption"]
        self.BEV_charging = self.df_timeseries["charging_power_kW"]

    def create_oemof_objects(self):

        ## variable_costs
        PV_variable_costs = 0
        Grid_variable_costs = 30
        Grid_feed_in_costs = -7.9
        Wallbox_variable_costs = 0

        ### BUS
        # create the first Bus = electricity bus
        b_el = buses.Bus(label="electricity")

        # define the connected bus = mobility bus
        b_bev = buses.Bus(label="mobility", balanced=True)

        self.es.add(b_el, b_bev)

        # create fixed source object representing pv power plants
        self.es.add(
            cmp.Source(
                label="pv",
                outputs={b_el: flows.Flow(fix=self.PV_load, nominal_value=1,variable_costs=PV_variable_costs)},
            )
        )


        # Grid als charger für das Auto, nur wenn es zu Hause ist
        wallbox = cmp.Source(
            label="wallbox",
            outputs={
                b_bev: flows.Flow(max=self.BEV_state, nominal_value=self.wallbox_power,variable_costs=Grid_variable_costs)
            },
        )
        self.es.add(wallbox)


        # Grid as Source
        grid = cmp.Source(
            label="grid-supply",
            outputs={
                b_el: flows.Flow(variable_costs=Grid_variable_costs, nominal_value=self.grid_supply)
            },
        )
        self.es.add(grid)

        # create excess component for the electricity bus to allow overproduction
        self.es.add(cmp.Sink(label="excess_bel", inputs={b_el: flows.Flow(variable_costs=Grid_feed_in_costs)}))

        # create simple sink object representing the electrical demand
        self.es.add(
            cmp.Sink(
                label="demand",
                inputs={b_el: flows.Flow(fix=self.demand, nominal_value=1)},
            )
        )

        # add BEV storage
        BEV = cmp.GenericStorage(
            label="BEV_Storage",
            inputs={b_bev: flows.Flow()},
            outputs={b_bev: flows.Flow()},
            nominal_storage_capacity=45,
            min_storage_level=0.4,
            max_storage_level=0.95,
            initial_storage_level=0.95,
            fixed_losses_absolute=self.BEV_consumption * 4,
        )
        self.es.add(BEV)

    def optimise_energysystem(self):
        ##########################################################################
        # Optimise the energy system and plot the results
        ##########################################################################

        # initialise the operational model
        self.model = Model(self.es)

        # model.receive_duals() #Schattenpreis

        if self.debug:
            file_path = os.path.join(
                helpers.extend_basic_path("lp_files"), "basic_example.lp"
            )
            logging.info(f"Store lp-file in {file_path}.")
            io_option = {"symbolic_solver_labels": True}
            self.model.write(file_path, io_options=io_option)

    def solve_energysystem(self):
        """
        Solves an oemof.solph model and checks if the solution is optimal.

        Raises RuntimeError if infeasible or failed.
        """
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)
            try:
                # if tee_switch is true solver messages will be displayed
                results = self.model.solve(
                    solver=self.solver, solve_kwargs={"tee": self.solver_verbose}
                )

                # Check solver status
                status = results.solver.status
                termination = results.solver.termination_condition

                if (status != SolverStatus.ok) or (
                    termination != TerminationCondition.optimal
                ):
                    msg = (
                        f"\n❌ The energy system could not find a solution.\n"
                        f"Solver status: {status}\n"
                        f"Termination condition: {termination}\n"
                        f"Message: {results.solver.message}\n"
                        f"⛔ Simulation aborted.\n"
                    )
                    raise RuntimeError(msg)

                print("✅ The model was solved successfully.")

            except RuntimeError as e:
                # Raise the warning or stop
                print(str(e))
                exit()

    def extract_results(self):
        # add results to the energy system to make it possible to store them.
        self.es.results["main"] = processing.results(self.model)
        self.es.results["meta"] = processing.meta_results(self.model)

    def dump_results(self):
        # The default path is the '.oemof' folder in your $HOME directory.
        # The default filename is 'es_dump.oemof'.
        # You can omit the attributes (as None is the default value) for testing
        # cases. You should use unique names/folders for valuable results to avoid
        # overwriting.

        file_path = os.getcwd()
        base_path = os.path.abspath(
            os.path.join(file_path, "..", "..")
        )  # main directory of the repo
        # 🔗 Combine to go to timeseries.csv
        dump_path = os.path.join(base_path, "dumps")

        if self.should_dump_results:
            self.es.dump(dpath=dump_path, filename=self.dump_filename)


if __name__ == "__main__":
    Energysystem = EnergySystemModel("case2_es_charger_limited_BEV_dumb")
