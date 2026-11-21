WITH hourly AS (
    SELECT
        date_time,
        COUNT(*) AS raw_rows, -- counts all CSV records for the timestamp.
        SUM(traffic_volume) AS raw_volume, --sum of traffic volume across all records for that timestamp
        MAX(traffic_volume) AS hourly_volume --Take one traffic volume per observed timestamp
    FROM Traffic_Volume
    WHERE date_time >= '2012-01-01'
      AND date_time <  '2018-01-01'
    GROUP BY date_time
),
annual AS ( --group the hourly rows by year
    SELECT
        substr(date_time, 1, 4) AS year,
        SUM(raw_rows) AS raw_rows,
        SUM(raw_volume) AS raw_csv_total,
        COUNT(*) AS observed_hours, -- count the hour with at least one record
        SUM(hourly_volume) AS total_vehicles,
        AVG(hourly_volume) AS Avg_vehicles_per_observed_hour
    FROM hourly
    GROUP BY substr(date_time, 1, 4)
),
comparison AS ( --compare with previous year’s total
    SELECT
        *,
        LAG(total_vehicles) OVER (ORDER BY year) AS prior_year_total
    FROM annual
)
SELECT
    year,
    raw_rows,
    raw_csv_total,
    observed_hours,
    total_vehicles,
    ROUND(Avg_vehicles_per_observed_hour, 2) AS Avg_vehicles_per_observed_hour,
    total_vehicles - prior_year_total AS yoy_change_vehicles,
    ROUND(
        100.0 * (total_vehicles - prior_year_total)
        / NULLIF(prior_year_total, 0),
        2
    ) AS yoy_change_pct,
    CASE
        WHEN prior_year_total IS NULL THEN 'Reference'
        WHEN total_vehicles > prior_year_total THEN 'Increase'
        WHEN total_vehicles < prior_year_total THEN 'Decrease'
        ELSE 'No change'
    END AS yoy_inference
FROM comparison
ORDER BY year;