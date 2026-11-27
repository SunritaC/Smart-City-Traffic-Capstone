"""Build and check a validated hourly dataset."""
from contextlib import closing
import logging
import sqlite3

import pandas as pd

from config import COLUMNS, DROP_OUTS, RANK

logger = logging.getLogger(__name__)


# Use WARNING when rows were affected and INFO when a check found no changes.
def change(n, action, reason):
    logger.log(logging.WARNING if n else logging.INFO, "%s %d rows | %s", action, n, reason)


def load_csv(path):
    try:
        # Read cells as text and preserve the literal holiday label None.
        raw = pd.read_csv(path, dtype="string", keep_default_na=False)
    except (FileNotFoundError, OSError, pd.errors.ParserError, pd.errors.EmptyDataError, UnicodeError) as exc:
        raise ValueError(f"Cannot read {path}: {exc}") from exc
    logger.info("Loaded %d rows and %d columns from %s", *raw.shape, path)
    # Validate the column names before doing any transformations.
    missing = set(COLUMNS) - set(raw)
    if missing or raw.empty:
        raise ValueError(f"Invalid schema or empty data. Missing columns: {sorted(missing)}")
    logger.info("Validated all nine required columns")
    return raw.loc[:, list(COLUMNS)].copy()


# Independently rank the same records in SQLite and compare with the Pandas result.
def reconcile(raw, hourly):
    cols = ["date_time", "weather_main", "temp", "traffic_volume"]
    rank = " ".join(f"WHEN '{name}' THEN {n}" for name, n in RANK.items())
    with closing(sqlite3.connect(":memory:")) as conn:
        raw[cols + ["weather_description", "source_row"]].to_sql("raw", conn, index=False)
        expected = pd.read_sql_query(f"""
            WITH ranked AS (
                SELECT *, ROW_NUMBER() OVER (
                    PARTITION BY date_time
                    ORDER BY CASE weather_main {rank} ELSE 0 END DESC,
                             weather_description, source_row
                ) AS rn FROM raw
            )
            SELECT date_time, weather_main, temp, traffic_volume
            FROM ranked WHERE rn = 1 ORDER BY date_time
        """, conn, parse_dates=["date_time"])
    pd.testing.assert_frame_equal(hourly[cols].reset_index(drop=True), expected, check_dtype=False)
    logger.info("SQLite reconciliation passed for %d hourly records", len(expected))


def impute(frame, field, invalid):
    invalid = invalid.fillna(True)
    # A year-month group keeps, for example, January 2014 separate from January 2015.
    months = frame["date_time"].dt.to_period("M")
    change(int(invalid.sum()), "Detected", f"invalid or missing {field}")
    for month in months[invalid].unique():
        group = months.eq(month)
        affected = group & invalid
        if affected.any():
            # Use only valid readings for the median, then replace just the flagged readings.
            median = frame.loc[group & ~invalid, field].median()
            if pd.isna(median):
                raise ValueError(f"No valid {field} in {month} for median imputation")
            frame.loc[affected, field] = median
            change(int(affected.sum()), "Imputed", f"{field} using the {month} median")
            logger.debug("%s median for %s = %.4f", field, month, median)


def build_hourly(path, baseline):
    raw = load_csv(path)
    # Remember the original CSV row position for the final tie-break.
    raw["source_row"] = range(len(raw))
    # Clean up spacing and capitalisation before comparing categories.
    for col in ("holiday", "weather_main", "weather_description"):
        cleaned = raw[col].str.strip().str.replace(r"\s+", " ", regex=True)
        cleaned = cleaned.str.lower() if col == "weather_description" else cleaned.str.title()
        fill = {"holiday": "None", "weather_main": "Unknown", "weather_description": ""}
        cleaned = cleaned.replace("", fill[col])
        change(int(raw[col].ne(cleaned).sum()), "Standardised", col)
        raw[col] = cleaned

    # Explicit formats preserve ambiguous day-first dates such as 02/10/2012.
    dates = pd.Series(pd.NaT, index=raw.index, dtype="datetime64[ns]")
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%d/%m/%Y %H:%M", "%d/%m/%Y %H:%M:%S"):
        pending = dates.isna()
        dates.loc[pending] = pd.to_datetime(raw.loc[pending, "date_time"].str.strip(), format=fmt, errors="coerce")
    valid = dates.notna() & dates.eq(dates.dt.floor("h"))
    change(int((~valid).sum()), "Dropped", "invalid or non-hourly timestamps")
    raw["date_time"] = dates
    raw = raw.loc[valid].copy()
    if raw.empty:
        raise ValueError("No valid hourly observations")
    logger.info("Parsed %d hourly timestamps", len(raw))

    for col in ("temp", "rain_1h", "snow_1h", "clouds_all", "traffic_volume"):
        values = pd.to_numeric(raw[col], errors="coerce").astype(float)
        change(int((values.isna() & raw[col].ne("")).sum()), "Marked missing", f"non-numeric {col}")
        raw[col] = values
    flags = raw.loc[raw["holiday"].ne("None")]
    holidays = flags.groupby(flags["date_time"].dt.normalize())["holiday"].max()
    # Remove identical records first. Rows with the same time can still differ in weather.
    exact = raw.duplicated(list(COLUMNS), keep="first")
    change(int(exact.sum()), "Dropped", "exact duplicates after standardisation")
    rows = raw.loc[~exact].copy()
    rows["weather_severity"] = rows["weather_main"].map(RANK).fillna(0).astype(int)
    # Put the highest weather score first within each timestamp. For tied scores, use
    # weather description and original row position.
    rows = rows.sort_values(["date_time", "weather_severity", "weather_description", "source_row"],
                            ascending=[True, False, True, True])
    # The first row in each timestamp group becomes the only observation for that hour.
    hourly = rows.drop_duplicates("date_time").copy()
    change(len(rows) - len(hourly), "Collapsed", "additional rows sharing a timestamp")
    assert hourly["date_time"].is_unique
    reconcile(raw, hourly)
    # Save a copy before imputation so Part 1 values can be reproduced.
    baseline.parent.mkdir(parents=True, exist_ok=True)
    hourly.drop(columns="source_row").to_csv(baseline, index=False)
    logger.info("Saved Part 1 baseline to %s", baseline)

    dropout = hourly["date_time"].isin(pd.to_datetime(list(DROP_OUTS)))
    for col, mask in (
        ("temp", hourly.temp.isna() | hourly.temp.le(0)),
        ("rain_1h", hourly.rain_1h.isna() | ~hourly.rain_1h.between(0, 9000)),
        ("snow_1h", hourly.snow_1h.isna() | hourly.snow_1h.lt(0)),
        ("clouds_all", hourly.clouds_all.isna() | ~hourly.clouds_all.between(0, 100)),
        ("traffic_volume", hourly.traffic_volume.isna() | hourly.traffic_volume.lt(0)
         | (dropout & hourly.traffic_volume.eq(0))),
    ):
        impute(hourly, col, mask)
    # Apply the holiday label to all recorded hours on that date.
    expanded = hourly.date_time.dt.normalize().map(holidays).fillna("None")
    change(int(hourly.holiday.ne(expanded).sum()), "Updated", "holiday labels across observed hours on flagged dates")
    hourly["holiday"] = expanded
    logger.info("Cleaned %d unique hours; %d flagged dates", len(hourly), len(holidays))
    return hourly.drop(columns="source_row")
