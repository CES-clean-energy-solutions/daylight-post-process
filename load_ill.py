from pathlib import Path
import struct
import pandas as pd

def read_ill(file_path, binary=True):
    """
    Reads the .ill file and returns a Pandas DataFrame with the data.
    """
    if binary:
        # Read the header info
        header_info, header_line_count = read_ill_header(file_path)

        # Define the columns for the data
        data_columns = [f'Hour {i+1}' for i in range(header_info['NCOLS'])]  # Modify this based on actual NCOLS

        # Load the data into a Pandas DataFrame
        data_df = load_ill_data_into_pandas(file_path, header_info, header_line_count, data_columns)
    else:
        # Read the .ill file as a text file
        with open(file_path, 'r') as f:
            # Read each line and split it into values
            data = [list(map(float, line.split())) for line in f.readlines()]
            # Convert the data into a DataFrame
            data_df = pd.DataFrame(data)
            # Rename the columns to sensor_1, sensor_2, ..., etc.
            data_df.columns = [f'sensor_{i+1}' for i in range(data_df.shape[1])]

    return data_df

def read_ill_header(file_path, header_line_count=8):
    """
    Reads a fixed number of header lines from the .ill file and returns a dictionary of header info.
    Assumes 8 header lines by default.
    """
    file_path = Path(file_path)

    # Ensure the file exists
    if not file_path.exists():
        raise FileNotFoundError(f"The file {file_path} does not exist")

    header_info = {}

    with file_path.open('rb') as file:
        for _ in range(header_line_count):
            line = file.readline().decode('utf-8', errors='ignore').strip()
            if '=' in line:
                key, value = line.split('=')
                header_info[key] = int(value) if value.isdigit() else value

    return header_info, header_line_count

def load_ill_data_into_pandas(file_path, header_info, header_line_count, data_columns):
    """
    Loads the binary data into a Pandas DataFrame based on header info.
    """
    file_path = Path(file_path)

    # Read the file again, skip the header lines, and load the binary data
    with file_path.open('rb') as file:
        # Skip the header lines
        for _ in range(header_line_count):
            file.readline()

        # Extract header values
        nrows = int(header_info.get('NROWS', 0))
        ncols = int(header_info.get('NCOLS', 0))
        endian_format = '>' if int(header_info.get('BigEndian', 0)) else '<'

        # Read the binary data and store it into a Pandas DataFrame
        data = []
        for _ in range(nrows):
            row = []
            for _ in range(ncols):
                chunk = file.read(4)  # Assuming 4-byte floats
                value = struct.unpack(f'{endian_format}f', chunk)[0]
                row.append(value)
            data.append(row)

        # Create a DataFrame
        data_df = pd.DataFrame(data, columns=data_columns[:ncols])

    return data_df

def align_illuminance_data_old(sun_up_series, illuminance_df):
    """
    Aligns the illuminance data to the sun-up series, creating a new DataFrame
    with 8760 rows (hours in a year) and columns labeled sensor_1, sensor_2, ..., etc.
    Hours where the sun is not up (False in sun_up_series) will have zero values.

    Args:
        sun_up_series: Pandas Series of length 8760 with True for hours when the sun is up
                       and False otherwise.
        illuminance_df: DataFrame where rows are sensors and columns are the sun-up hours.

    Returns:
        A new DataFrame with 8760 rows (one for each hour of the year) and
        columns labeled as sensor_1, sensor_2, etc. Rows where the sun is not up
        (False in sun_up_series) will be filled with zero.
    """
    # Ensure the sun-up series has 8760 rows
    assert len(sun_up_series) == 8760, "Sun-up series must have 8760 values."

    # Ensure that the number of True values in the sun-up series matches the number of columns in illuminance_df
    num_true_hours = sun_up_series.sum()
    assert num_true_hours == illuminance_df.shape[1], "Number of sun-up hours does not match the number of columns in illuminance_df."

    # Transpose the illuminance data (so that sensors become columns and hours become rows)
    illuminance_transposed = illuminance_df.T
    illuminance_transposed.columns = [f'sensor_{i+1}' for i in range(illuminance_df.shape[0])]

    # Create an empty DataFrame with 8760 rows and columns labeled sensor_1, sensor_2, ...
    aligned_df = pd.DataFrame(0, index=range(8760), columns=illuminance_transposed.columns, dtype=float)

    # Get the indices where the sun is up (True values in sun_up_series)
    sun_up_indices = sun_up_series[sun_up_series].index

    # Copy the illuminance data to the aligned DataFrame at the corresponding hours (sun_up_indices)
    aligned_df.loc[sun_up_indices] = illuminance_transposed.values

    return aligned_df

def align_illuminance_data(sun_up_series, illuminance_df):
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
    assert num_true_hours == illuminance_df.shape[1], "Number of sun-up hours does not match the number of columns in illuminance_df."

    # Transpose the illuminance data (so that sensors become columns and hours become rows)
    illuminance_transposed = illuminance_df.T
    illuminance_transposed.columns = [f'sensor_{i+1}' for i in range(illuminance_df.shape[0])]

    # Create an empty DataFrame indexed by the DatetimeIndex of sun_up_series
    aligned_df = pd.DataFrame(0, index=sun_up_series.index, columns=illuminance_transposed.columns, dtype=float)

    # Get the indices where the sun is up (True values in sun_up_series)
    sun_up_indices = sun_up_series[sun_up_series].index

    # Copy the illuminance data to the aligned DataFrame at the corresponding hours (sun_up_indices)
    aligned_df.loc[sun_up_indices] = illuminance_transposed.values

    return aligned_df