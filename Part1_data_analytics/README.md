# Part 1 Traffic Data Analytics

## Rebuild the SQLite database

Open PowerShell in the `Part1_data_analytics` folder and run:

python rebuild_sqlite.py --csv "sql/Metro_Interstate_Traffic_Volume.csv" --output "sql/trafficdata_rebuilt.db"


The script imports the CSV into `Traffic_Volume`, normalises timestamps to `YYYY-MM-DD HH:MM:SS`, and runs `create_traffic_hourly.sql` from the `Part1_data_analytics` folder. It saves the rebuilt database as `sql/trafficdata_rebuilt.db`. To rebuild again, give `--output` a new filename.

Open the rebuilt database or the submitted `sql/Task 1/trafficdata.db` in a SQLite application that supports window functions and `SQRT`. Run the queries in task order. The load check should show **48,204 raw records** and **40,575 observed hours**.

The hourly view keeps the highest-ranked weather record per timestamp, with ties broken by weather description and source row order. The ranking from highest to lowest is Thunderstorm, Squall, Snow, Rain, Drizzle, Fog, Smoke, Haze, Mist, Clouds, Clear, and other or missing labels. 
 
- The original Task 1.2 query uses one traffic count per timestamp by taking MAX(traffic_volume). Repeated timestamps in this dataset have identical traffic counts, so this gives the same annual results as the shared hourly view. Raw CSV totals are labelled separately for comparison.
- The original Task 1.3 query applies the same weather ranking and tie-break logic within the query. It preserves the missing 2015 New Year's Day as an explicit row and uses 2 January 2017 as flagged in the CSV.

## Power BI and insights

Open [PowerBI.pbix](powerbi/PowerBI.pbix) in Power BI Desktop. The [Part 1 Insights Report](insight_report/Part1_Insights_Report.pdf) summarises the findings.

Select **Home → Refresh** to reload the data. If Power BI prompts for the CSV location, update the **Source** step in Power Query to point to `sql/Metro_Interstate_Traffic_Volume.csv`. Confirm that timestamps are interpreted in day/month/year order.

On the **KPI cards and filters** page, check the following:

- With all slicers cleared, the cards displayed **40,575 observed hours**, **3,290.65 vehicles per observed hour**, and an average temperature of **8.24 °C**.
- Selecting **Clear** in the weather slicer reduced the hours count to **13,364**, matching the SQLite result.

On the Hourly2017 page, the chart displays hours in clock order and peaks at 16:00, at approximately 5,834 vehicles per observed hour