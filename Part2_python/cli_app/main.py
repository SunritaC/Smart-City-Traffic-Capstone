"""Build the project or run a traffic query."""
import argparse
import logging
from pathlib import Path

import pandas as pd

from . import cli
import feature_engineering
import pipeline

logger = logging.getLogger(__name__)


# Set up console and file logging at the entry point so all modules use the same format.
def configure_logging(path, debug):
    path.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    console = logging.StreamHandler()
    log_file = logging.FileHandler(path, encoding="utf-8")
    for handler in (console, log_file):
        handler.setFormatter(formatter)

    # Configure logging once at the CLI entry point for all modules.
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        handlers=[console, log_file],
        force=True,
    )


class LoggedParser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError(message)


def main():
    parser = LoggedParser(description="I-94 hourly traffic analytics")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--data", type=Path, default=Path("data/processed/Metro_Interstate_Clean.csv"))
    parser.add_argument("--log", type=Path, default=Path("pipeline.log"))
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build", help="Clean data, engineer features and save charts")
    build.add_argument("csv", type=Path)
    cli.register(commands)
    try:
        args = parser.parse_args()
    except ValueError as exc:
        configure_logging(Path("pipeline.log"), False)
        logger.error("Invalid arguments: %s", exc)
        return 2
    configure_logging(args.log, args.debug)
    logger.info("Command invoked: %s", vars(args))
    try:
        # The build command runs cleaning, feature engineering and figure generation in order.
        if args.command == "build":
            baseline = args.data.with_name("traffic_hourly_baseline.csv")
            frame = feature_engineering.engineer(pipeline.build_hourly(args.csv, baseline))
            args.data.parent.mkdir(parents=True, exist_ok=True)
            frame.to_csv(args.data, index=False)
            logger.info("Saved feature dataset to %s", args.data)
            from visualizations import save_figures
            save_figures(frame, Path("figures"))
        else:
            frame = pd.read_csv(args.data, parse_dates=["date_time"])
            # Print the answer requested by the user. Progress and errors go through the logger.
            print(cli.answer(args, frame))
        return 0
    except (OSError, ValueError, KeyError, AssertionError, ImportError) as exc:
        logger.error("%s failed: %s", args.command, exc, exc_info=args.command == "build")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
