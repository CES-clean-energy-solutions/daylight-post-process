import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from models import Level

def plot_illuminance(expanded_daylight_df, n_hours=24 * 5, n_sensors=10):
    fig, ax = plt.subplots()

    for i in range(n_sensors):
        ax.plot(expanded_daylight_df.iloc[:n_hours, i], label=f"Sensor {i}")

    ax.set_xlabel("Hour")
    ax.set_ylabel("Illuminance (lux)")
    ax.set_title(f"Illuminance values for the first {n_sensors} sensors")
    ax.legend()

    # Format the x-axis to show time in hours
    # ax.xaxis.set_major_formatter(mdates.DateFormatter("%H"))

    # Rotate the x-axis labels for better readability
    plt.xticks(rotation=45)

    # Display the plot
    plt.show()

def plot_statistic(df, statistic):
    # Get the summary statistics using describe()
    desc = df.describe()

    # Check if the chosen statistic exists in the describe output
    if statistic not in desc.index:
        raise ValueError(f"Statistic '{statistic}' is not available. Choose from {desc.index.tolist()}.")

    # Pull the selected statistic row (mean, max, min, etc.)
    stat_row = desc.loc[statistic]

    # Plot the selected statistic as a bar chart
    plt.figure(figsize=(8, 6))
    stat_row.plot(kind='bar')

    # Add labels and title
    plt.xlabel('Columns')
    plt.ylabel(statistic.capitalize())
    plt.title(f'{statistic.capitalize()} of Each Column')

    # Display the plot
    plt.show()

def plot_monthly_mean(df):
    """
    This function calculates the mean over all columns for each hour,
    resamples the data by month, and plots the monthly mean with month labels.

    Parameters:
    df (pd.DataFrame): DataFrame with a time series index (hours in a year) and multiple columns.
    """
    # Step 1: Calculate the mean over all columns for each hour
    hourly_mean = df.mean(axis=1)

    # Step 2: Resample by month and calculate the monthly mean
    monthly_mean = hourly_mean.resample('ME').mean()

    # Step 3: Plot the monthly mean with month labels
    plt.figure(figsize=(10, 6))
    monthly_mean.plot(kind='bar')

    # Customize the plot
    plt.xlabel('Month')
    plt.ylabel('Average Value')
    plt.title('Average Value per Month')

    # Format the x-axis to show the month names
    plt.xticks(ticks=range(len(monthly_mean.index)), labels=monthly_mean.index.strftime('%B'), rotation=45)

    # Show the plot
    plt.tight_layout()
    plt.show()


def plot_average_illuminance_sunup_hours(level: Level):
    """
    Plots the average illuminance over all sensors for each grid in the given Level object,
    only including the hours when the sun is up. The x-axis will display months in the center
    of each month, and the plot will start at the origin (0,0). Illuminance is averaged over days.

    Args:
        level: A Level object containing multiple grids with daylight DataFrames and sunup hours.
    """
    plt.figure(figsize=(10, 6))  # Set up the plot size

    # Loop through each grid in the level
    for grid in level.grids:
        # Filter the daylight DataFrame to only include sun-up hours
        daylight_sunup = grid.daylight_df.loc[level.sunup_hours]

        # Calculate the average illuminance over all sensors (columns) for each sun-up hour
        avg_illuminance = daylight_sunup.mean(axis=1)

        # Resample the data to daily average (smoothing over days)
        daily_avg_illuminance = avg_illuminance.resample('D').mean()

        # Plot the daily average illuminance over time (indexed by datetime)
        plt.plot(daily_avg_illuminance.index, daily_avg_illuminance, label=grid.name)

    # Format the x-axis to show months in the center of each month
    ax = plt.gca()  # Get current axis

    # Set major ticks for each month (we will hide them later)
    # ax.xaxis.set_major_locator(mdates.MonthLocator())  # One major tick for each month

    # Set the formatter to display abbreviated month names, centered in the middle of each month
    # ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))  # Format ticks as month names ('Jan', 'Feb', etc.)

    # Use DayLocator for the 15th of each month to center labels (acting as minor ticks for positioning)
    ax.xaxis.set_minor_locator(mdates.DayLocator(bymonthday=15))  # Set ticks on the 15th of each month
    ax.xaxis.set_minor_formatter(mdates.DateFormatter('%b'))  # Format the minor ticks to display month names

    # Hide the major ticks (so we don't have duplicate month labels)
    # ax.tick_params(axis='x', which='major', bottom=False)  # Hide major ticks
    ax.tick_params(axis='x', which='major', bottom=False, labelbottom=False)  # Hide major ticks and labels

    # Set the origin to 0,0 (both x and y axes)
    ax.set_ylim(bottom=0)  # Ensure the y-axis starts at 0
    ax.set_xlim(left=daily_avg_illuminance.index.min(), right=daily_avg_illuminance.index.max())  # Ensure full range for x-axis

    # Add labels and title
    plt.xlabel("Month")
    plt.ylabel("Average Daily Illuminance (lux)")
    plt.title(f"Average Daily Illuminance During Sun-up Hours for Level: {level.name}")
    plt.legend(title="Grid Name")
    plt.grid(True, which='major')  # Display grid lines on major ticks (months)

    # Rotate x-axis labels if needed for clarity
    plt.gcf().autofmt_xdate()

    # Show the plot
    plt.show()

def plot_average_illuminance(level: Level):
    """
    Plots the average illuminance over all sensors for each grid in the given Level object.
    Each grid will be represented as a separate line in the plot.

    Args:
        level: A Level object containing multiple grids with daylight DataFrames.
    """
    plt.figure(figsize=(10, 6))  # Set up the plot size

    # Loop through each grid in the level
    for grid in level.grids:
        # Calculate the average illuminance over all sensors (columns) for each hour
        avg_illuminance = grid.daylight_df.mean(axis=1)

        # Plot the average illuminance over time (indexed by datetime)
        plt.plot(avg_illuminance.index, avg_illuminance, label=grid.name)

    # Add labels and title
    plt.xlabel("Time")
    plt.ylabel("Average Illuminance (lux)")
    plt.title(f"Average Illuminance Over the Year for Level: {level.name}")
    plt.legend(title="Grid Name")
    plt.grid(True)

    # Show the plot
    plt.show()