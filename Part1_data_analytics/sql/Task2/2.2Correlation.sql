WITH pairs AS (
    -- Use one record per observed hour and exclude invalid 0 Kelvin readings.
    SELECT
        strftime('%H', date_time) AS hour_of_day,
        temp - 273.15 AS temp_c,
        traffic_volume
    FROM traffic_hourly
    WHERE temp > 0
      AND traffic_volume IS NOT NULL
),
deviations AS (
    SELECT
        -- Subtract the overall averages for the main Pearson correlation.
        temp_c - AVG(temp_c) OVER () AS temp_diff,
        traffic_volume - AVG(traffic_volume) OVER () AS traffic_diff,

        -- Subtract the averages for the same clock hour.
        -- For example, compare an 08:00 reading with the average for 08:00.
        temp_c - AVG(temp_c) OVER (PARTITION BY hour_of_day)
            AS temp_diff_by_hour,
        traffic_volume - AVG(traffic_volume) OVER (PARTITION BY hour_of_day)
            AS traffic_diff_by_hour
    FROM pairs
)
SELECT
    COUNT(*) AS paired_hours,
    ROUND(
        SUM(temp_diff * traffic_diff) /
        NULLIF(SQRT(SUM(temp_diff * temp_diff) *
                    SUM(traffic_diff * traffic_diff)), 0),
        4
    ) AS pearson_r,
    ROUND(
        SUM(temp_diff_by_hour * traffic_diff_by_hour) /
        NULLIF(SQRT(SUM(temp_diff_by_hour * temp_diff_by_hour) *
                    SUM(traffic_diff_by_hour * traffic_diff_by_hour)), 0),
        4
    ) AS pearson_r_adjusted_for_hour
FROM deviations;