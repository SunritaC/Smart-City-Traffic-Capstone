WITH holiday_dates(holiday_date, remarks) AS ( --lists the dates to analyse
    VALUES
        ('2014-01-01', 'Reference for missing 2015'),
        ('2015-01-01', 'Falls inside the dataset gap'),
        ('2016-01-01', 'Clean date'),
        ('2017-01-02', 'New Year''s Day date flagged in the CSV'),
        ('2015-09-07', 'Clean date'),
        ('2016-09-05', 'Clean date'),
        ('2017-09-04', 'Clean date')
),

-- We Select all observed hours on the required dates and then Rank duplicate records within each timestamp by weather severity.
--The ranking is needed because one hour can appear multiple times in the table.
ranked_hours AS (
    SELECT
        date(date_time) AS holiday_date,
        date_time,
        temp,
        traffic_volume,
        ROW_NUMBER() OVER (
            PARTITION BY date_time
            ORDER BY CASE weather_main
                WHEN 'Thunderstorm' THEN 11
                WHEN 'Squall'       THEN 10
                WHEN 'Snow'         THEN 9
                WHEN 'Rain'         THEN 8
                WHEN 'Drizzle'      THEN 7
                WHEN 'Fog'          THEN 6
                WHEN 'Smoke'        THEN 5
                WHEN 'Haze'         THEN 4
                WHEN 'Mist'         THEN 3
                WHEN 'Clouds'       THEN 2
                WHEN 'Clear'        THEN 1
                ELSE 0
            END DESC, weather_description, rowid
        ) AS weather_rank
    FROM Traffic_Volume
    WHERE date(date_time) IN (SELECT holiday_date FROM holiday_dates)
),

-- Keep one record per hour and add a placeholder for every requested date.
-- NULL measurements let missing dates appear without affecting the aggregates.
holiday_rows AS (
    SELECT holiday_date, NULL AS remarks, date_time, temp, traffic_volume
    FROM ranked_hours
    WHERE weather_rank = 1

    UNION ALL

    SELECT holiday_date, remarks, NULL, NULL, NULL
    FROM holiday_dates
),

-- Among the listed dates, January represents New Year's Day
-- and September represents Labor Day.
daily AS (
    SELECT
        CASE
            WHEN substr(holiday_date, 6, 2) = '01' THEN 'New Year''s Day'
            ELSE 'Labor Day'
        END AS holiday,
        holiday_date,
        MAX(remarks) AS remarks,
        COUNT(date_time) AS observed_hours,
        COUNT(NULLIF(temp, 0)) AS valid_temperature_hours,
        -- Exclude 0 Kelvin readings and convert to Celsius.
        MIN(NULLIF(temp, 0)) - 273.15 AS min_temp_c,
        AVG(NULLIF(temp, 0)) - 273.15 AS avg_temp_c,
        MAX(NULLIF(temp, 0)) - 273.15 AS max_temp_c,
        AVG(traffic_volume) AS avg_vehicles_per_hour
    FROM holiday_rows
    GROUP BY holiday_date
),

-- We derive the preceding year's averages for the same holiday.
-- The missing 2015 values make the 2016 New Year's Day changes NULL.
comparison AS (
    SELECT
        *,
        LAG(avg_temp_c) OVER holiday_years AS prior_avg_temp_c,
        LAG(avg_vehicles_per_hour) OVER holiday_years AS prior_avg_traffic
    FROM daily
    WINDOW holiday_years AS (
        PARTITION BY holiday
        ORDER BY holiday_date
    )
)

SELECT
    holiday,
    holiday_date,
    remarks,
    observed_hours,
    valid_temperature_hours,
    ROUND(min_temp_c, 2) AS min_temp_c,
    ROUND(avg_temp_c, 2) AS avg_temp_c,
    ROUND(max_temp_c, 2) AS max_temp_c,
    ROUND(avg_vehicles_per_hour, 2) AS avg_vehicles_per_hour,
    ROUND(avg_temp_c - prior_avg_temp_c, 2) AS yoy_temp_change_c,
    ROUND(
        100.0 * (avg_vehicles_per_hour - prior_avg_traffic)
        / NULLIF(prior_avg_traffic, 0),
        2
    ) AS yoy_traffic_change_pct
FROM comparison
ORDER BY CASE WHEN holiday = 'Labor Day' THEN 2 ELSE 1 END, holiday_date;