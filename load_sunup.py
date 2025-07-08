import pandas as pd
from pathlib import Path
import logging
logger = logging.getLogger(__name__)

import pandas as pd

def parse_sun_up_hours_from_file(file_path):
    """
    Parse the sun-up hours from a text file and return a Pandas Series
    representing the 8760 hours of the year.

    Args:
        file_path: Path to the text file containing sun-up hours, each row
                   representing the midpoint of the hour (e.g., 7.5 for the
                   hour from 7 to 8).

    Returns:
        Pandas Series of length 8760, with True for hours when the sun is up,
        and False for other hours.
    """
    logger.info(f"Processing sun-up hours from file: {file_path}")
    # Load sun-up hours from file, each line is a midpoint value (e.g., 7.5)
    with open(file_path, 'r') as file:
        sun_up_hours = [float(line.strip()) for line in file.readlines()]

    # Create a False schedule of length 8760 (representing hours in a year)
    schedule = pd.Series([False] * 8760, index=range(8760))

    # Loop through the sun-up hours and mark the corresponding hour as True
    for hour in sun_up_hours:
        # Convert midpoint hour to the full hour index, e.g., 7.5 -> 7
        hour_index = int(hour)  # The hour from 7 to 8 is represented as 7
        schedule[hour_index] = True

    average_sun_up_hours_per_day = schedule.sum() / 365

    logger.info(f"Total sun-up hours: {schedule.sum()}")
    logger.info(f"Average sun-up hours per day: {average_sun_up_hours_per_day:.2f}")
    return schedule

if __name__ == "__main__":
    # Example usage
    sun_hours_folder = r"C:\SIMULATION\240919 1401 z250 grid20\annual_daylight_enhanced\results"
    sun_hours_filename = r"sun-up-hours.txt"

    file_path = Path(sun_hours_folder) / sun_hours_filename
    df = process_sun_up_hours(file_path)
    print(df)
# # Example usage
# sun_hours_folder = r"C:\SIMULATION\240919 1401 z250 grid20\annual_daylight_enhanced\results"
# sun_hours_filename = r"sun-up-hours.txt"

# file_path = Path(sun_hours_folder) / sun_hours_filename
# df = process_sun_up_hours(file_path)
# print(df)
