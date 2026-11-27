# Capstone Part 2 Traffic Analytics

## Run
Install dependencies with python -m pip install -r requirements.txt.
Run python -m cli_app.main build /path/to/Metro_Interstate_Traffic_Volume.csv.
Pass --debug before build to include monthly medians, scaling parameters and quartiles.

## Project structure
- pipeline.py validates, deduplicates and imputes the hourly data.
- feature_engineering.py creates model-ready features.
- visualizations.py produces four PNG plots.
- cli_app/main.py configures logging and runs the build and CLI.
- cli_app/cli.py contains the four traffic queries.
- data/processed/Metro_Interstate_Clean.csv is the Part 3 handoff.
- data/processed/traffic_hourly_baseline.csv preserves the Part 1 comparison.
- Methodology_and_Findings.md and pipeline.log document a completed run.

## Commands
    python -m cli_app.main query "2017-01-02 16:00"
    python -m cli_app.main peak --day-type weekday --top 3
    python -m cli_app.main compare
    python -m cli_app.main recommend --day-type weekday --start 7 --end 19 --weather Clear

## Logging
The entry point configures console and file handlers for the traffic package.
The default file is pipeline.log. Each line has timestamp, level, module and message.
INFO records loads, commands, shapes and outputs. WARNING records cleaning changes and reasons.
ERROR records failures. DEBUG logs intermediate values only when enabled.
User-facing CLI answers go to standard output.

## Data contract
Weather scores run from Thunderstorm (11), Squall (10), Snow (9), Rain (8),
Drizzle (7), Fog (6), Smoke (5), Haze (4), Mist (3), Clouds (2), and Clear (1)
to other weather (0). Break ties by weather description and original row order.
Quartile targets are Low through Q1, Medium through Q2, High through Q3,
and Severe above Q3. For Part 3, recompute thresholds and scaling from training
data and omit target-derived variables from model predictors.

The project includes five local Git commits. Use git log --oneline to review them.
Publish to your own GitHub repository if submitting by repository link.
