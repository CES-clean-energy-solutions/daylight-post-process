
import os
import copy
import zipfile
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import logging
from modelsRefactor import DaylightResults
logger = logging.getLogger(__name__)

class TransformedResults(DaylightResults):
    def __init__(self, results, tag: str):
        super().__init__(
            results.name + f" {tag}",
            results.base_path,
            copy.deepcopy(results.grids),
            results.sunup_hours,
        )
        logger.info(f"Copied results of DaylightResults: {self.name}")

    def save_results(self, output_folder: Path):
        # Ensure the output folder exists
        self._ensure_output_folder(output_folder)

        # Path for the zip file
        zip_file_path = os.path.join(output_folder, f"{self.name}.zip")

        # Create a zip file to write to
        with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            # Save sunup hours
            self._save_to_zip( self.sunup_hours, zipf, output_folder, f"{self.name}_sunup_hours.csv", header=["Sunup Hours"])

            # Process each grid
            for grid in self.grids:
                logger.info(f"Saving grid {grid.name}, {grid.df.shape[1]} sensors, {grid.df.shape[0]} rows to zip")

                # Save mesh vertices
                data = pd.DataFrame(grid.sensormesh.vertices)
                head = ["X", "Y", "Z"]
                fname = f"{self.name} {grid.name} vertices.csv"
                self._save_to_zip(data, zipf, output_folder, fname, header=head)

                # Save mesh faces (4 vertices per face)
                data = pd.DataFrame(grid.sensormesh.faces)
                head = ["Vertex1", "Vertex2", "Vertex3", "Vertex4"]
                fname = f"{self.name} {grid.name} mesh.csv"
                self._save_to_zip(data, zipf, output_folder, fname, header=head)

                # Save grid mesh normals
                data = pd.DataFrame(grid.sensormesh.directions)
                head = ["Normal_X", "Normal_Y", "Normal_Z"]
                fname = f"{self.name} {grid.name} normals.csv"
                self._save_to_zip(data, zipf, output_folder, fname, header=head)

                # Save grid DataFrame (df)
                self._save_to_zip( grid.df, zipf, output_folder, f"{self.name} {grid.name} data.csv")

            logger.info(f"Zip file saved to {zip_file_path}")

    def _ensure_output_folder(self, output_folder: Path):
        """Ensures the output folder exists."""
        logger.info(f"Ensuring output folder {output_folder}")
        os.makedirs(output_folder, exist_ok=True)

    def _save_to_zip(self, df: pd.DataFrame, zipf: zipfile.ZipFile, output_folder: Path, filename: str, header=None,):
        """
        Helper method to save a DataFrame to CSV, write it to the zip, and clean up the temporary CSV file.
        """
        csv_path = os.path.join(output_folder, filename)
        df.to_csv(csv_path, index=False, header=header)
        zipf.write(csv_path, arcname=filename)
        os.remove(csv_path)  # Remove the temporary CSV file
        logger.info(f"{filename} saved and added to zip, CSV removed.")

class AverageLuxMonthlySunup(TransformedResults):
    def __init__(self, results, time_filter, tag, resampling="ME", round=1):
        super().__init__(results, tag)
        self.time_filter = time_filter
        assert len(self.time_filter) == 8760, "Time filter must be 8760 hours long"
        assert (
            sum(self.time_filter) < 8760
        ), "Time filter must have some False values for sun up hours"
        self.resampling = resampling
        self.round = round
        logger.info(
            f"Created transformer for {self.name} with {sum(self.time_filter)} sunup hours, resampling {self.resampling}, rounding {self.round}"
        )

    def transform(self):
        for grid in self.grids:
            logger.info(f"Transforming grid {grid.name}")
            # Get monthly average illuminance per sensor for this grid
            # Copy over the original data
            grid.df = (
                grid.df[self.time_filter]
                .resample(self.resampling)
                .mean()
                # .round(self.round)
            )
            logger.info(
                f"Monthly average illuminance for {grid.name} over {self.time_filter.sum()} hours"
            )
            logger.info(f"Shape: {grid.df.shape}")
            # print(monthly_avg_illuminance)

    def plot_layout(self, paper_size_mm=(420, 297)):
        # Convert mm to inches (1 inch = 25.4 mm)
        paper_size_in = (paper_size_mm[0] / 25.4, paper_size_mm[1] / 25.4)

        # Sort grids by name
        sorted_grids = sorted(self.grids, key=lambda grid: grid.name)

        # Set up A3 landscape plot
        fig, ax = plt.subplots(figsize=paper_size_in)
        fig.suptitle("Monthly Total Average Illuminance per Grid", fontsize=14)

        # Plot each grid's monthly total illuminance
        for grid in sorted_grids:
            monthly_total = grid.df.sum(axis=1)

            # Plot the total monthly average illuminance for each grid
            ax.plot(
                monthly_total.index,
                monthly_total.values,
                marker="o",
                linestyle="-",
                label=f"Grid {grid.name}",
            )

        # Set x-axis labels to month names
        ax.set_xticks(monthly_total.index)
        ax.set_xticklabels([x.strftime("%b") for x in monthly_total.index])

        ax.set_xlabel("Month")
        ax.set_ylabel("Total Average Illuminance (Lux)")
        ax.grid(True)
        ax.legend()

        plt.tight_layout(
            rect=[0, 0, 1, 0.95]
        )  # Adjust layout to not overlap with the title
        plt.show()

class DaylightAutonomy(TransformedResults):
    def __init__(self, results, time_filter, resampling: str, threshold: int, tag="Daylight Autonomy"):
        super().__init__(results, tag)
        self.time_filter = time_filter
        self.resampling = resampling
        self.threshold = threshold

        assert len(self.time_filter) == 8760, "Time filter must be 8760 hours long"
        assert (sum(self.time_filter) < 8760), "Time filter must have some False values for sun up hours"

        logger.info(f"Created transformer for {self.name} with {sum(self.time_filter)} hours, resampling {self.resampling}")

    def transform(self):
        for grid in self.grids:
            logger.info(f"Transforming grid {grid.name}")
            # Get monthly average illuminance per sensor for this grid
            # Copy over the original data

            daylight_autonomy_sunup = grid.df[self.time_filter] > self.threshold
            grid.df = daylight_autonomy_sunup.resample(self.resampling).mean()
            logger.info(f"Monthly average illuminance for {grid.name} over {self.time_filter.sum()} hours")
            logger.info(f"Overall mean Daylight Autonomy at {self.threshold} lux: {'{:0.3f}'.format(grid.df.mean().mean())}")
            logger.info(f"Shape: {grid.df.shape}")
            # print(monthly_avg_illuminance)