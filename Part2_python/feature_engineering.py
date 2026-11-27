"""Create reproducible time, weather and congestion features."""
import logging

import numpy as np
import pandas as pd

from config import CONGESTION, LOW_VISIBILITY, SEVERE

logger = logging.getLogger(__name__)


def engineer(frame):
    logger.info("Before features: %d rows, %d columns", *frame.shape)
    out = frame.copy()
    # Pull the clock hour and day of week from the timestamp. Monday is 0 and Sunday is 6.
    out["hour"] = out.date_time.dt.hour
    out["day_of_week"] = out.date_time.dt.dayofweek
    out["is_weekend"] = out.day_of_week.ge(5).astype(int)
    out["is_holiday"] = out.holiday.ne("None").astype(int)
    # Sine and cosine make the ends of a cycle meet, so 23:00 is close to midnight.
    for col, period in (("hour", 24), ("day_of_week", 7)):
        angle = 2 * np.pi * out[col] / period
        out[f"{col}_sin"] = np.sin(angle)
        out[f"{col}_cos"] = np.cos(angle)
    out["temp_c"] = out.temp - 273.15
    out["is_low_visibility"] = out.weather_main.isin(LOW_VISIBILITY).astype(int)
    out["is_severe_weather"] = out.weather_main.isin(SEVERE).astype(int)
    # Standardise both fields by subtracting the mean and dividing by the population SD.
    for col in ("temp_c", "clouds_all"):
        mean, sd = out[col].mean(), out[col].std(ddof=0)
        out[f"{col}_z"] = (out[col] - mean) / sd if sd > 0 else 0.0
        logger.debug("%s scaling mean %.4f and SD %.4f", col, mean, sd)
    # Keep the fixed Part 1 threshold and Power BI bands alongside the Part 2 categories.
    volume = out.traffic_volume
    out["is_congested_fixed"] = volume.gt(CONGESTION).astype(int)
    out["traffic_category_bi"] = np.select([volume.lt(4500), volume.le(CONGESTION)],
                                           ["Low", "Medium"], default="High")
    # Use the 25th, 50th and 75th percentiles as cutoffs for the four congestion classes.
    q1, q2, q3 = volume.quantile([.25, .5, .75])
    logger.debug("Congestion quartiles Q1/Q2/Q3 = %.2f / %.2f / %.2f", q1, q2, q3)
    out["congestion_category"] = np.select([volume.le(q1), volume.le(q2), volume.le(q3)],
                                            ["Low", "Medium", "High"], default="Severe")
    # One-hot encoding creates a separate 0/1 column for each weather label.
    out = pd.concat([out, pd.get_dummies(out.weather_main, prefix="weather", dtype=int)], axis=1)
    logger.info("After features: %d rows, %d columns", *out.shape)
    return out
