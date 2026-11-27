"""Query the processed traffic dataset."""
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def register(commands):
    # Register the command names and arguments that users can type.
    query = commands.add_parser("query", help="Look up an observed local timestamp")
    query.add_argument("timestamp", help="YYYY-MM-DD HH:MM")
    peak = commands.add_parser("peak", help="Rank hours by average traffic")
    peak.add_argument("--day-type", choices=["weekday", "weekend"], default="weekday")
    peak.add_argument("--top", type=int, default=3)
    commands.add_parser("compare", help="Compare weekday with weekend traffic")
    recommend = commands.add_parser("recommend", help="Find a lower-traffic travel window")
    recommend.add_argument("--day-type", choices=["weekday", "weekend"], default="weekday")
    recommend.add_argument("--start", type=int, default=7)
    recommend.add_argument("--end", type=int, default=19)
    recommend.add_argument("--weather")


def summary(group):
    return group.traffic_volume.agg(average_vehicles="mean", observed_hours="size")


def answer(args, frame):
    if args.command == "query":
        try:
            # Check the requested date and time before looking up a row.
            timestamp = datetime.strptime(args.timestamp, "%Y-%m-%d %H:%M")
        except ValueError as exc:
            raise ValueError("Use YYYY-MM-DD HH:MM for the timestamp") from exc
        found = frame.loc[frame.date_time.eq(timestamp)]
        if found.empty:
            return f"No observation at {timestamp:%Y-%m-%d %H:%M}."
        row = found.iloc[0]
        return (f"{timestamp:%Y-%m-%d %H:%M}: {row.traffic_volume:,.0f} vehicles, "
                f"{row.weather_main}, {row.temp_c:.2f} °C, traffic band {row.traffic_category_bi}.")
    # Summarise the average and number of observations for each day type.
    if args.command == "compare":
        day_type = frame.is_weekend.map({0: "Weekday", 1: "Weekend"})
        return summary(frame.groupby(day_type)).round(2).to_string()
    subset = frame.loc[frame.is_weekend.eq(int(args.day_type == "weekend"))]
    # Rank hours from highest to lowest historical average volume.
    if args.command == "peak":
        if not 1 <= args.top <= 24:
            raise ValueError("--top must be between 1 and 24")
        return summary(subset.groupby("hour")).nlargest(args.top, "average_vehicles").round(2).to_string()
    if not 0 <= args.start < args.end <= 24:
        raise ValueError("Use 0 <= --start < --end <= 24")
    subset = subset.loc[subset.hour.between(args.start, args.end - 1)]
    if args.weather:
        subset = subset.loc[subset.weather_main.str.casefold().eq(args.weather.casefold())]
    profile = summary(subset.groupby("hour"))
    # Only recommend hours backed by at least 20 observations.
    eligible = profile.loc[profile.observed_hours.ge(20)]
    if eligible.empty:
        return "No eligible hour has at least 20 observations for these filters."
    hour = int(eligible.average_vehicles.idxmin())
    row = eligible.loc[hour]
    return (f"Consider {hour:02d}:00–{hour + 1:02d}:00 for a {args.day_type} trip. "
            f"Historical mean: {row.average_vehicles:,.0f} vehicles across "
            f"{int(row.observed_hours):,} observations.")
