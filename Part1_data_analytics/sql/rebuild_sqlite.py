"""Build the Part 1 SQLite database from the submitted CSV."""
import argparse
import csv
from datetime import datetime
import logging
from pathlib import Path
import sqlite3

logger = logging.getLogger(__name__)
root = Path(__file__).resolve().parent
columns = ("holiday", "temp", "rain_1h", "snow_1h", "clouds_all",
           "weather_main", "weather_description", "date_time", "traffic_volume")


def rows(reader):
    for row in reader:
        stamp = row["date_time"]
        try:
            date = datetime.fromisoformat(stamp)
        except ValueError:
            date = datetime.strptime(stamp, "%d/%m/%Y %H:%M")
        row["date_time"] = date.isoformat(sep=" ", timespec="seconds")
        yield tuple(row[column] for column in columns)


def build(csv_path, database_path):
    if not csv_path.is_file():
        raise FileNotFoundError(csv_path)
    with csv_path.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        if not set(columns).issubset(reader.fieldnames or ()):
            raise ValueError("The CSV is missing required columns.")
        # Exclusive creation protects an existing database.
        database_path.touch(exist_ok=False)
        connection = sqlite3.connect(database_path)
        try:
            with connection:
                connection.execute("BEGIN")
                connection.execute(SCHEMA)
                connection.executemany(
                    "INSERT INTO Traffic_Volume (" + ", ".join(columns) + ") VALUES (?,?,?,?,?,?,?,?,?)",
                    rows(reader),
                )
                connection.execute((root / "create_traffic_hourly.sql").read_text(encoding="utf-8"))
                counts = connection.execute(
                    "SELECT (SELECT COUNT(*) FROM Traffic_Volume), "
                    "(SELECT COUNT(*) FROM traffic_hourly)"
                ).fetchone()
        finally:
            connection.close()
    logger.info("Built %s with %d raw rows and %d observed hours", database_path, *counts)


SCHEMA = 'CREATE TABLE "Traffic_Volume" (\n\t"holiday"\tTEXT,\n\t"temp"\tREAL,\n\t"rain_1h"\tREAL,\n\t"snow_1h"\tREAL,\n\t"clouds_all"\tINTEGER,\n\t"weather_main"\tTEXT,\n\t"weather_description"\tTEXT,\n\t"date_time"\tTEXT,\n\t"traffic_volume"\tINTEGER\n)'


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=root / "Metro_Interstate_Traffic_Volume.csv")
    parser.add_argument("--output", type=Path, default=root / "trafficdata_rebuilt.db")
    args = parser.parse_args()
    try:
        build(args.csv, args.output)
    except (OSError, ValueError, sqlite3.Error) as exc:
        logger.error("Rebuild failed: %s", exc)
        raise SystemExit(1) from exc
