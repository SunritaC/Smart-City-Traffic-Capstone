# Part 1 Traffic Data Analytics

## Rebuild the SQLite database

From this folder, run `python sql/rebuild_sqlite.py`. This imports the CSV into `Traffic_Volume`, normalises timestamps to `YYYY-MM-DD HH:MM:SS`, and applies `sql/create_traffic_hourly.sql`. It creates `sql/trafficdata_rebuilt.db`. Use `--output` with a new path to rebuild again.

Open the rebuilt database or the submitted `sql/Task 1/trafficdata.db` in a SQLite application that supports window functions and `SQRT`. Run the seven numbered queries in task order. The load check should show **48,204 raw records** and **40,575 observed hours**.

The hourly view keeps the highest-ranked weather record per timestamp, with ties broken by weather description and source row order. The ranking from highest to lowest is Thunderstorm, Squall, Snow, Rain, Drizzle, Fog, Smoke, Haze, Mist, Clouds, Clear, and other or missing labels. Task 1.2 keeps raw totals separately labelled. Task 1.3 retains the missing 2015 New Year observation and uses 2 January 2017 as flagged in the CSV.

## Power BI and insights

Open `powerbi/PowerBI.pbix` in Power BI Desktop and `insight_report/Part1_Insights_Report.pdf` for the findings. If refresh requires a local source path, point Power Query to the included traffic CSV and confirm the day/month/year timestamp format. With filters cleared, the expected KPIs are 40,575 hours, 3,290.65 vehicles per observed hour, and 8.24 degrees Celsius. The hourly chart is configured to sort by hour and peaks at 16:00 in 2017. The Clear weather filter should show 13,364 hours. Check that the hour, weather, and traffic category slicers update their intended visuals in Desktop.
