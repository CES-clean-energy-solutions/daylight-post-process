import pandas as pd

def count_negative_values(df: pd.DataFrame):
    """
    Counts the number of negative values in the given DataFrame and provides
    additional information about columns containing negative values.

    Args:
        df: A Pandas DataFrame containing numerical data.

    Returns:
        A dictionary containing:
        - total_negative: Total number of negative values in the entire DataFrame.
        - negative_per_column: A Series with the number of negative values per column (sensor).
        - columns_with_negatives: Number of columns that contain at least one negative value.
    """
    # Count total number of negative values in the entire DataFrame
    total_negative = (df < 0).sum().sum()

    # Count number of negative values per column
    negative_per_column = (df < 0).sum()

    # Count columns with at least one negative value
    columns_with_negatives = (negative_per_column > 0).sum()

    return {
        "total_negative": total_negative,
        "negative_per_column": negative_per_column,
        "columns_with_negatives": columns_with_negatives
    }

def generate_sunup_summary_dataframe(df: pd.DataFrame, sunup_hours: pd.Series, resample_window: str) -> pd.DataFrame:
    """
    Generates a summary DataFrame by averaging the original data over the specified time period,
    only including rows where the sun is up (sunup_hours is True).

    Args:
        df: A Pandas DataFrame where rows are time-indexed (e.g., datetime) and columns are sensors.
        sunup_hours: A Pandas Series indexed the same as df, with True indicating sun-up hours.
        resample_window: A string representing the resample frequency (e.g., 'D' for daily, 'M' for monthly, etc.).

    Returns:
        A new DataFrame where the rows are averaged values over the specified time period (sunup hours only),
        and the columns remain the same.
    """
    # Ensure the DataFrame is indexed by a DatetimeIndex
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("The DataFrame must be indexed by a DatetimeIndex.")

    # Ensure the sunup_hours series has the same index as the DataFrame
    if not df.index.equals(sunup_hours.index):
        raise ValueError("The sunup_hours Series must have the same index as the DataFrame.")

    # Filter the DataFrame to only include sunup hours
    sunup_df = df.loc[sunup_hours]

    # Resample the filtered data using the provided window and calculate the mean
    resampled_sunup_df = sunup_df.resample(resample_window).mean()

    return resampled_sunup_df
