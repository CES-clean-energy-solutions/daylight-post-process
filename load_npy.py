from pathlib import Path
import numpy as np
import pandas as pd

folder_path = r"C:\SIMULATION\240919 1401 z250 grid20\annual_daylight_enhanced\results\__static_apertures__\default\direct"
file_name = r"M45.npy"

file_path = Path(folder_path) / file_name

# Ensure the file exists
if not file_path.exists():
    raise FileNotFoundError(f"The file {file_path} does not exist")

# Load the .npy file into a NumPy array
data_array = np.load(file_path)

# Convert the NumPy array to a Pandas DataFrame
df = pd.DataFrame(data_array)

# Summarize the data
summary = df.describe()  # Summary statistics like mean, std, min, max, etc.
total_sum = df.sum()  # Sum of all columns
mean_values = df.mean()  # Mean values of all columns

# Print or save the summary
print("Summary Statistics:\n", summary)
print("\nTotal Sum:\n", total_sum)
print("\nMean Values:\n", mean_values)