from dataclasses import dataclass
import numpy as np
import pandas as pd
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class DaylightResults:
    def __init__(self, name: str, base_path: Path, grids: list, sunup_hours: pd.Series):
        self.name = name
        self.base_path = base_path
        self.grids = grids
        self.sunup_hours = sunup_hours

class SensorMesh:
    def __init__(self, name: str, points: np.array, vertices: np.array, faces: np.array, directions: np.array):
        self.name = name
        self.points = points  # Nx3 array of xyz coordinates
        self.vertices = vertices  # Mx3 array of xyz coordinates
        self.faces = faces  # Nx4 array of vertex indices (4 per face)
        self.directions = directions  # Nx3 array of xyz normal vectors

        logger.info(f"Loaded sensor mesh {name} with {len(points)} sensors")

        # Infer grid shape based on unique x and y coordinates
        self.grid_shape = self._infer_grid_shape()
        logger.info(f"Inferring sensor grid shape for {name}: {self.grid_shape[0]} rows, {self.grid_shape[1]} columns")
        # logger.info(f"Inferred grid shape: {num_rows} rows, {num_cols} columns")

        self.grid_spacing = self.calculate_uniform_spacing()  # Calculate the uniform spacing for x, y, and z axes
        logger.info(f"Calculated sensor grid spacing: x {self.grid_spacing[0]}, y {self.grid_spacing[1]}, z {self.grid_spacing[2]}")

        self.direction = self.assert_unique_direction()  # Assert that all sensors have the same direction
        logger.info(f"Sensor direction: {self.direction}")

        # self.points_grid = self.rebuild_grid()  # MxNx3 array of xyz coordinates in 2D grid

    def _infer_grid_shape(self):
        """Infer the 2D grid shape by counting the unique x and y values."""
        unique_x = np.unique(self.points[:, 0])  # Unique x values
        unique_y = np.unique(self.points[:, 1])  # Unique y values

        num_cols = len(unique_x)  # Number of unique x values gives number of columns
        num_rows = len(unique_y)  # Number of unique y values gives number of rows

        return num_rows, num_cols

    def calculate_uniform_spacing(self):
        """
        Calculate the uniform spacing for x, y, and z axes. Ensure all spacing between successive values is equal.
        """
        axis_names = ['x', 'y', 'z']
        distances = []

        for i, axis_name in enumerate(axis_names):
            axis_values = self.points[:, i]  # Get the values for the axis (x, y, or z)
            sorted_values = np.sort(np.unique(axis_values))  # Sort unique values

            if sorted_values.size > 1:
                successive_distances = np.diff(sorted_values)  # Calculate successive distances
            else:
                successive_distances = np.array([0])  # No spacing if only one unique value

            assert np.unique(successive_distances).size == 1, f"All sensors in a grid should have the same {axis_name} spacing"

            distances.append(successive_distances[0])  # Add the calculated distance to the list

        # Return the tuple of (x_distance, y_distance, z_distance)
        return tuple(distances)

    def assert_unique_direction(self):
        """
        Assert that all sensors in the grid have the same direction, and return the unique direction.
        """
        unique_directions = np.unique(self.directions, axis=0)  # Find unique direction vectors

        # Assert that there is only one unique direction
        assert unique_directions.shape[0] == 1, "All sensors in a grid should have the same direction"

        unique_direction = unique_directions[0]  # Extract the unique direction

        return unique_direction

    def rebuild_grid(self):
        raise
        """Rebuild the 2D grid where each element contains the xyz coordinates of the sensor."""
        rows, cols = self.grid_shape

        # Reshape the flat points array into a 2D grid (rows x cols)
        reshaped_grid = self.points.reshape(rows, cols, 3)

        logger.info(f"Rebuilt sensor grid with shape: {reshaped_grid.shape}")
        return reshaped_grid

    def print_grid_info(self):
        """Print the 2D grid shape and grid point coordinates."""
        pass
        # logger.info(f"Rebuilt 2D Grid: {.shape}")
        # logger.info(f"Grid points: \n{grid}")

    def build_mesh_from_vertex_indices(self):
        """
        Build the mesh where each row contains the coordinates of the 4 vertices forming a face.

        Returns:
            np.array: A numpy array where each row contains the 4 vertices (with xyz coordinates) of a mesh face.
        """
        # Number of faces
        num_faces = self.faces.shape[0]

        # Initialize an empty array to store the mesh faces
        mesh_faces = np.zeros((num_faces, 4, 3))  # (num_faces, 4 vertices per face, 3 coordinates per vertex)

        # Loop over each face and gather the coordinates of its 4 vertices
        for i, face_indices in enumerate(self.faces):
            # Retrieve the vertex coordinates for this face
            vertices_for_face = self.vertices[face_indices]
            mesh_faces[i] = vertices_for_face

        return mesh_faces


    def draw_mesh(self):
        """
        Draw the mesh and the sensor points in a 3D plot using matplotlib.
        """
        mesh_faces = self.build_mesh_from_vertex_indices()

        fig = plt.figure(figsize=(12, 10))  # Make the plot larger
        ax = fig.add_subplot(111, projection='3d')

        # Plot the mesh faces
        for face in mesh_faces:
            # Create a 3D polygon for each face
            verts = [list(face)]
            ax.add_collection3d(Poly3DCollection(verts, facecolors='cyan', linewidths=1, edgecolors='r', alpha=.25))

        # Plot the sensor points
        ax.scatter(self.points[:, 0], self.points[:, 1], self.points[:, 2], c='black', marker='o', s=50, label="Sensors")

        # Set labels
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')

        # Set the plot limits
        ax.set_box_aspect([1, 1, 0.5])  # Aspect ratio is 1:1:0.5 for better visibility

        plt.legend()
        plt.show()


class GridResults:
    def __init__(self, name: str, sensormesh: SensorMesh, npy_path: Path, df: pd.DataFrame):
        self.name = name
        self.sensormesh = sensormesh
        self.npy_path = npy_path
        self.df = df

    def print_info(self):
        logger.info(f"Grid: {self.name}")

    def load_df(self):
        array = np.load(self.npy_path)
        daylight_df = pd.DataFrame(array)
        logger.info(f"Loaded {self.npy_path.name} with {daylight_df.shape[0]} sensors and {daylight_df.shape[1]} hours")

        self.df = daylight_df

    def align_illuminance_data(self, sun_up_series):
        """
        Aligns the illuminance data to the sun-up series, creating a new DataFrame
        indexed with DatetimeIndex and columns labeled sensor_1, sensor_2, ..., etc.
        Rows where the sun is not up (False in sun_up_series) will have zero values.

        Args:
            sun_up_series: Pandas Series indexed by DatetimeIndex with True for hours when the sun is up
                        and False otherwise.
            illuminance_df: DataFrame where rows are sensors and columns are the sun-up hours.

        Returns:
            A new DataFrame indexed by DatetimeIndex and columns labeled as sensor_1, sensor_2, etc.
            Rows where the sun is not up (False in sun_up_series) will be filled with zero.
        """
        assert isinstance(sun_up_series.index, pd.DatetimeIndex), "sun_up_series must have a DatetimeIndex."

        # Ensure that the number of True values in the sun-up series matches the number of columns in illuminance_df
        num_true_hours = sun_up_series.sum()
        assert num_true_hours == self.df.shape[1], "Number of sun-up hours does not match the number of columns in illuminance_df."

        # Transpose the illuminance data (so that sensors become columns and hours become rows)
        illuminance_transposed = self.df.T
        illuminance_transposed.columns = [f'sensor_{i+1}' for i in range(self.df.shape[0])]

        # Create an empty DataFrame indexed by the DatetimeIndex of sun_up_series
        aligned_df = pd.DataFrame(0, index=sun_up_series.index, columns=illuminance_transposed.columns, dtype=float)

        # Get the indices where the sun is up (True values in sun_up_series)
        sun_up_indices = sun_up_series[sun_up_series].index

        # Copy the illuminance data to the aligned DataFrame at the corresponding hours (sun_up_indices)
        aligned_df.loc[sun_up_indices] = illuminance_transposed.values
        logger.info(f"Aligned illuminance data for {self.name} grid to 8760 hours")
        self.df = aligned_df