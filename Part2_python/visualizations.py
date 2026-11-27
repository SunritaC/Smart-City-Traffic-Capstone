"""Plot the cleaned hourly data."""
import logging

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


def save_figures(frame, folder):
    folder.mkdir(parents=True, exist_ok=True)

    # Use the same layout, save and log steps for each figure.
    def save(fig, name):
        path = folder / name
        fig.tight_layout()
        fig.savefig(path, dpi=150, facecolor="white")
        plt.close(fig)
        logger.info("Saved figure: %s", path)

    fig, ax = plt.subplots(figsize=(8, 3.8))
    # Average all observations at each clock hour to find the daily traffic profile.
    hourly = frame.groupby("hour").traffic_volume.mean()
    ax.bar(hourly.index, hourly, color="#147C83")
    ax.set(title="Average traffic by hour", xlabel="Local hour", ylabel="Vehicles per hour", xticks=range(0,24,2))
    save(fig, "01_hourly_demand.png")

    fig, ax = plt.subplots(figsize=(8, 3.8))
    # Plot weekday and weekend averages separately so their peak hours can be compared.
    for day, label, color in [(0, "Weekday", "#155B77"), (1, "Weekend", "#D68041")]:
        group = frame.loc[frame.is_weekend.eq(day)].groupby("hour").traffic_volume.mean()
        ax.plot(group.index, group, label=label, color=color, linewidth=2)
    ax.set(title="Weekday and weekend traffic", xlabel="Local hour", ylabel="Vehicles per hour", xticks=range(0,24,2))
    ax.legend(frameon=False)
    save(fig, "02_weekday_weekend.png")

    fig, ax = plt.subplots(figsize=(8, 4))
    # Each point pairs Celsius temperature with the volume recorded in that hour.
    ax.scatter(frame.temp_c, frame.traffic_volume, s=5, alpha=.12, color="#155B77", edgecolors="none")
    ax.set(title="Temperature and traffic", xlabel="Temperature (°C)", ylabel="Vehicles per hour")
    save(fig, "03_temperature_traffic.png")

    fig, ax = plt.subplots(figsize=(8, 4.3))
    # Add counts to the weather labels so rare conditions are visible beside their averages.
    groups = frame.groupby("weather_main").traffic_volume.agg(["mean", "size"]).sort_values("mean")
    labels = [f"{name} (n={count:,})" for name, count in groups["size"].items()]
    ax.barh(labels, groups["mean"], color="#147C83")
    ax.set(title="Average traffic by retained weather condition", xlabel="Vehicles per observed hour")
    save(fig, "04_weather_traffic.png")
