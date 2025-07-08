# %%
from pathlib import Path
import csv
import datetime as datetime
import os
import re
import zipfile
import shutil
import copy

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from load_sunup import parse_sun_up_hours_from_file
from load_ill import read_ill, align_illuminance_data
from util_output import summarize_dataframe, summarize_level, save_level_data_to_csv
from parse_hbjson import parse_hbjson
from util_plotting import plot_average_illuminance_sunup_hours
from util_statistics import generate_sunup_summary_dataframe
from modelsRefactor import DaylightResults, GridResults, SensorMesh
from transformers import AverageLuxMonthlySunup, DaylightAutonomy

pd.set_option("display.max_columns", None)
pd.set_option("display.max_colwidth", None)

import logging
import coloredlogs

# Create a logger
logger = logging.getLogger(__name__)

# Setup coloredlogs with a basic configuration
coloredlogs.install(
    level="INFO",  # Set the log level
    fmt="%(asctime)s - %(levelname)s - %(message)s",  # Format of the logs
    datefmt="%Y-%m-%d %H:%M:%S",  # Date format
)

simulation_folder = Path(r"F:\SIMULATION")

run_folders = list()

pattern = r"z\d+(\.)*\d* grid\d+"
for folder in simulation_folder.iterdir():
    if folder.is_dir() and re.match(pattern, folder.name):
        run_folders.append(folder)
logger.info(f"Found {len(run_folders)} runs to process")
run_folders.sort(key=lambda x: float(re.search(r"z(\d+(\.)*\d*)", x.name).group(1)))

for i, folder in enumerate(run_folders):
    print(i, folder.name)

# levels = list()

# run_folders = run_folders[0:1]
run_folders = run_folders[0:1]
print(run_folders)
# %%

for i, folder in enumerate(run_folders):
    run_folder = folder

    logger.info(f"Processing run folder {i} {run_folder}")
    this_level = DaylightResults(
        name=run_folder.name, base_path=run_folder, grids=[], sunup_hours=None
    )

    # Get the sunup hours
    sun_hours_folder = this_level.base_path / "annual_daylight_enhanced" / "results"
    sunup_hours = parse_sun_up_hours_from_file(sun_hours_folder / "sun-up-hours.txt")
    sun_up_series = pd.Series(sunup_hours)
    sun_up_series.index = pd.to_datetime(
        sun_up_series.index, unit="h", origin="2024-01-01"
    )
    this_level.sunup_hours = sun_up_series

    # Get the model hbjson file
    model_file = list(this_level.base_path.glob("*.hbjson"))
    assert len(model_file) == 1
    model_file = model_file[0]
    hb_model = parse_hbjson(model_file)
    logger.info(f"Loaded hbjson file {hb_model['identifier']}")

    logger.info( f"{len(hb_model['properties']['radiance']['sensor_grids'])} sensor grids found:")
    for grid in hb_model["properties"]["radiance"]["sensor_grids"]:
        logger.info( f"\tsensor_grid {grid['type']} ID '{grid['identifier']}' name {grid['display_name']} with {len(grid['sensors'])} sensors")

        # Get the sensor positions and mesh data
        points = np.array([tuple(sensor["pos"]) for sensor in grid["sensors"]])
        mesh_faces = np.array(grid["mesh"]["faces"])
        mesh_vertices = np.array(grid["mesh"]["vertices"])
        mesh_directions = np.array([tuple(sensor["dir"]) for sensor in grid["sensors"]])
        this_sensormesh = SensorMesh( name=grid["identifier"], points=points, vertices=mesh_vertices, faces=mesh_faces, directions=mesh_directions,)

        this_grid = GridResults( name=grid["identifier"], sensormesh=this_sensormesh, npy_path=None, df=None)
        # this_sensormesh.draw_mesh()
        this_level.grids.append(this_grid)

    del hb_model  # Free up memory

    # The results are stored in the annual_daylight_enhanced/results folder, each grid has a separate file matching the name of the grid
    annual_simulation_folder = ( this_level.base_path / "annual_daylight_enhanced" / "results" / "__static_apertures__" / "default" / "total")
    for results_file in annual_simulation_folder.glob("*.npy"):
        result_name = results_file.stem
        assert result_name in [
            g.name for g in this_level.grids
        ], f"Grid {result_name} not found in {this_level.name}"

        grid_index = [g.name for g in this_level.grids].index(
            result_name
        )  # Could store the grids as a dictionary instead
        this_level.grids[grid_index].npy_path = results_file

    # Load the illuminance values and expand the sunup hours to 8760 hours
    for grid in this_level.grids:
        logger.info(f"Processing file {grid.npy_path.name} for grid {grid.name}")
        grid.load_df()
        grid.align_illuminance_data(this_level.sunup_hours)  # Expand the df to 8760 hours
#%% Details

    for grid in this_level.grids:
        logger.info(f"Processing grid {grid.name}")
        summarize_dataframe(grid.df)

    # %% OUTPUT
    # Monthly average illuminance
    this_level_average_monthly = AverageLuxMonthlySunup(this_level, this_level.sunup_hours, tag="Average Monthly Lux", )
    this_level_average_monthly.transform()
    this_level_average_monthly.save_results(simulation_folder / "output")

    #%%

    # this_level_daylight_autonomy_yearly = DaylightAutonomy(this_level, this_level.sunup_hours, resampling="YE", threshold=100)
    # this_level_daylight_autonomy_yearly.transform()
    # this_level_daylight_autonomy_yearly.name
    # this_level_daylight_autonomy_yearly.save_results(simulation_folder / "output")
    for threshold in [100, 300, 5000]:
        this_level_daylight_autonomy = DaylightAutonomy(this_level, this_level.sunup_hours, resampling="YE", threshold=threshold, tag=f"Annual Daylight Autonomy {threshold}")
        this_level_daylight_autonomy.transform()
        this_level_daylight_autonomy.save_results(simulation_folder / "output")
