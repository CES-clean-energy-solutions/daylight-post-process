from models import Level
from util_statistics import count_negative_values
from pathlib import Path
import os
import zipfile
import pandas as pd
import logging
import coloredlogs

from models import Level, Grid

import logging
logger = logging.getLogger(__name__)

def summarize_dataframe(df):
    """
    Summarizes the given DataFrame by printing key statistics.

    Args:
        df (pd.DataFrame): The DataFrame to summarize.

    Returns:
        None
    """
    print("DataFrame Summary:")
    print("------------------")

    # Basic statistics (count, mean, std, min, 25%, 50%, 75%, max)
    print("Summary statistics:\n", df.describe())

    # Total values per column
    if 0:
        print("\nTotal illuminance per sensor:")
        print(df.sum())

        # Mean values per column
        print("\nMean illuminance per sensor:")
        print(df.mean())

        # Count of non-zero values per column
        print("\nNumber of non-zero entries per sensor:")
        print((df > 0).sum())

    print("\nNumber of negative entries total:")
    print((df < 0).sum().sum())
    print("\nPercentage of negative entries total:")
    print((df < 0).sum().sum() / df.size * 100)
    print("\nNumber of columns with any negative entries:")
    print((df < 0).sum().astype(bool).sum())
    print("\nPercentage of columns with any negative entries:")
    print((df < 0).sum().astype(bool).sum() / len(df.columns) * 100)
    print("\nIf a column has any negative entries, what percentage of the entries are negative, averaged over all of these columns?")
    print((df[df < 0].count() / df.count()).mean() * 100)
    print("\nAverage negative entries over all sensors:")
    print(df[df < 0].mean().mean())

def print_dict_keys(d, level=0, max_level=3):
    if level > max_level:
        return
    for key, value in d.items():
        print('\t' * level + str(key))  # Use tab for indentation
        if isinstance(value, dict):
            print_dict_keys(value, level + 1, max_level)


def write_mesh_to_csv(grid, z_level, output_folder):
    grid_name = grid['identifier']
    vertices_file = output_folder / f"{z_level} {grid_name} vertices.csv"
    with open(vertices_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(grid['mesh']['vertices'])

    faces_file = output_folder / f"{z_level} {grid_name} faces.csv"
    with open(faces_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(grid['mesh']['faces'])

    print(f"Data written to {vertices_file} and {faces_file}")


def summarize_level(level: Level):
    """
    Summarize the data in a Level object, including sunup hours, grid information,
    and summary statistics from the daylight DataFrame.
    """
    # Summary of the Level
    print(f"Level Name: {level.name}")
    print(f"Level ID: {level.level}")
    print(f"Base Path: {level.base_path}")
    print(f"Output Path: {level.output_path}")
    print("Sunup Hours Summary:")
    print(f"  Total hours in the year: {len(level.sunup_hours)}")
    print(f"  Hours when sun is up: {level.sunup_hours.sum()}")
    print(f"  Percentage of sunup hours: {100 * level.sunup_hours.mean():.2f}%\n")

    # Summary of each grid within the level
    for grid in level.grids:
        count_neg = count_negative_values(grid.daylight_df)

        print(f"Grid Name: {grid.name}")
        print(f"  Number of Points: {len(grid.points)}")
        # print(f"  Number of Mesh Faces: {len(grid.mesh_faces)}")
        # print(f"  Number of Mesh Vertices: {len(grid.mesh_vertices)}")
        # print(f"  Number of Mesh Directions: {len(grid.mesh_directions)}")
        # print(f"  NPY File Path: {grid.npy_path}")

        # Summarizing the daylight DataFrame
        daylight_df = grid.daylight_df
        print(f"  Daylight DataFrame Summary for {grid.name}:")
        print(f"    Total hours of data: {len(daylight_df)}")
        print(f"    Number of sensors: {daylight_df.shape[1]}")
        print(f"    Overall average illuminance across all sensors: {daylight_df.mean().mean():.2f} lux")
        print(f"    Minimum illuminance across all sensors: {daylight_df.min().min():.2f} lux")
        print(f"    Maximum illuminance across all sensors: {daylight_df.max().max():.2f} lux")
        print(f"    Average illuminance by sensor:")
        # print(f"Negative values in {grid.name}:")
        print(f"    Total negative values: {count_neg['total_negative']}")
        print(f"    Columns with negative values: {count_neg['columns_with_negatives']}")

        # sensor_means = daylight_df.mean().head(5)  # Limiting to first 5 sensors for brevity
        # for sensor, mean_val in sensor_means.items():
        #     print(f"      {sensor}: {mean_val:.2f} lux")
        print()


def save_level_data_to_csv_OLD(level: Level, output_folder: Path, decimals: int = 1):
    """
    Collects sunup hours, grid vertices, grid mesh (with 4 vertices per face), mesh normals/directions,
    and monthly average illuminance per sensor for each grid in the level, and writes them to CSV files
    in a folder called 'output'. Truncates average illuminance to the specified number of decimals.

    Args:
        level: A Level object containing grids, sunup hours, and daylight data.
        decimals: Number of decimal places to round the average illuminance to (default is 1).
    """
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Write sunup hours to CSV
    sunup_hours_path = os.path.join(output_folder, f"{level.name}_sunup_hours.csv")
    level.sunup_hours.to_csv(sunup_hours_path, header=['Sunup Hours'])
    print(f"Sunup hours saved to {sunup_hours_path}")

    # Loop through each grid in the level
    for grid in level.grids:
        # Write grid vertices to CSV
        vertices_path = os.path.join(output_folder, f"{level.name}_{grid.name}_vertices.csv")
        pd.DataFrame(grid.mesh_vertices).to_csv(vertices_path, index=False, header=['X', 'Y', 'Z'])
        print(f"Grid vertices saved to {vertices_path}")

        # Write grid mesh (with 4 vertices per face) to CSV
        mesh_path = os.path.join(output_folder, f"{level.name}_{grid.name}_mesh.csv")
        pd.DataFrame(grid.mesh_faces).to_csv(mesh_path, index=False, header=['Vertex1', 'Vertex2', 'Vertex3', 'Vertex4'])
        print(f"Grid mesh (4 vertices per face) saved to {mesh_path}")

        # Write mesh normals/directions to CSV
        normals_path = os.path.join(output_folder, f"{level.name}_{grid.name}_normals.csv")
        pd.DataFrame(grid.mesh_directions).to_csv(normals_path, index=False, header=['Normal_X', 'Normal_Y', 'Normal_Z'])
        print(f"Grid normals/directions saved to {normals_path}")

        # Get monthly average illuminance per sensor for this grid
        monthly_avg_illuminance = grid.daylight_df.resample('ME').mean().round(decimals)

        # Write monthly average illuminance to CSV
        for month in monthly_avg_illuminance.index:
            # Format the month as YYYY-MM
            month_str = month.strftime('%Y-%m')
            illuminance_path = os.path.join(output_folder, f"{level.name}_{grid.name}_illuminance_{month_str}.csv")
            monthly_avg_illuminance.loc[month].to_csv(illuminance_path, header=['Average Illuminance'])
            print(f"Monthly average illuminance for {month_str} saved to {illuminance_path}")

def save_level_data_to_csv(level: Level, output_folder: Path, decimals: int = 1):
    """
    Collects sunup hours, grid vertices, grid mesh (with 4 vertices per face), mesh normals/directions,
    and monthly average illuminance per sensor for each grid in the level, and writes them to a .zip file.
    Truncates average illuminance to the specified number of decimals, and removes the temporary CSV files
    after adding them to the zip archive.

    Args:
        level: A Level object containing grids, sunup hours, and daylight data.
        decimals: Number of decimal places to round the average illuminance to (default is 1).
    """
    # Create a temporary output folder to store CSVs before zipping
    os.makedirs(output_folder, exist_ok=True)

    # Path for the zip file
    zip_file_path = os.path.join(output_folder, f"{level.name}_data.zip")

    # Create a zip file to write to
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:

        # Write sunup hours to CSV and add to zip
        sunup_hours_path = os.path.join(output_folder, f"{level.name}_sunup_hours.csv")
        level.sunup_hours.to_csv(sunup_hours_path, header=['Sunup Hours'])
        zipf.write(sunup_hours_path, arcname=f"{level.name}_sunup_hours.csv")
        os.remove(sunup_hours_path)  # Remove the temporary CSV file
        print(f"Sunup hours saved and added to zip, CSV removed.")

        # Loop through each grid in the level
        for grid in level.grids:
            # Write grid vertices to CSV and add to zip
            vertices_path = os.path.join(output_folder, f"{level.name}_{grid.name}_vertices.csv")
            pd.DataFrame(grid.mesh_vertices).to_csv(vertices_path, index=False, header=['X', 'Y', 'Z'])
            zipf.write(vertices_path, arcname=f"{level.name}_{grid.name}_vertices.csv")
            os.remove(vertices_path)  # Remove the temporary CSV file
            print(f"Grid vertices saved and added to zip, CSV removed.")

            # Write grid mesh (with 4 vertices per face) to CSV and add to zip
            mesh_path = os.path.join(output_folder, f"{level.name}_{grid.name}_mesh.csv")
            pd.DataFrame(grid.mesh_faces).to_csv(mesh_path, index=False, header=['Vertex1', 'Vertex2', 'Vertex3', 'Vertex4'])
            zipf.write(mesh_path, arcname=f"{level.name}_{grid.name}_mesh.csv")
            os.remove(mesh_path)  # Remove the temporary CSV file
            print(f"Grid mesh saved and added to zip, CSV removed.")

            # Write mesh normals/directions to CSV and add to zip
            normals_path = os.path.join(output_folder, f"{level.name}_{grid.name}_normals.csv")
            pd.DataFrame(grid.mesh_directions).to_csv(normals_path, index=False, header=['Normal_X', 'Normal_Y', 'Normal_Z'])
            zipf.write(normals_path, arcname=f"{level.name}_{grid.name}_normals.csv")
            os.remove(normals_path)  # Remove the temporary CSV file
            print(f"Grid normals saved and added to zip, CSV removed.")

            # Get monthly average illuminance per sensor for this grid
            monthly_avg_illuminance = grid.daylight_df.resample('ME').mean().round(decimals)

            # Write monthly average illuminance to CSV and add to zip
            for month in monthly_avg_illuminance.index:
                # Format the month as YYYY-MM
                month_str = month.strftime('%Y-%m')
                illuminance_path = os.path.join(output_folder, f"{level.name}_{grid.name}_illuminance_{month_str}.csv")
                monthly_avg_illuminance.loc[month].to_csv(illuminance_path, header=['Average Illuminance'])
                zipf.write(illuminance_path, arcname=f"{level.name}_{grid.name}_illuminance_{month_str}.csv")
                os.remove(illuminance_path)  # Remove the temporary CSV file
                print(f"Monthly average illuminance for {month_str} saved and added to zip, CSV removed.")

    print(f"All data compressed and saved to {zip_file_path}. Temporary CSV files removed.")
