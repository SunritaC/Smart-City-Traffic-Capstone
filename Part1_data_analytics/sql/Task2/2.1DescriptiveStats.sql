WITH hourly AS (
    -- Repeated records for a timestamp share the same traffic volume.
    -- MAX keeps that value once per timestamp.
    SELECT
        date_time,
        MAX(traffic_volume) AS traffic_volume
    FROM Traffic_Volume
    GROUP BY date_time
),
ranked AS (
    SELECT
        traffic_volume,
        ROW_NUMBER() OVER (ORDER BY traffic_volume) AS rn,
        COUNT(*) OVER () AS total_hours
    FROM hourly
),
stats AS (
    SELECT
        COUNT(*) AS observed_hours,
        AVG(traffic_volume) AS mean_vehicles,
        AVG(CASE
            WHEN rn IN ((total_hours + 1) / 2, (total_hours + 2) / 2)
            THEN traffic_volume
        END) AS median_vehicles,
        AVG(1.0 * traffic_volume * traffic_volume)
            - AVG(traffic_volume) * AVG(traffic_volume) AS population_variance,
        MAX(traffic_volume) - MIN(traffic_volume) AS traffic_range
    FROM ranked
)
SELECT
    observed_hours,
    ROUND(mean_vehicles, 2) AS mean_vehicles,
    ROUND(median_vehicles, 2) AS median_vehicles,
    ROUND(SQRT(population_variance), 2) AS population_std_dev,
    ROUND(population_variance, 2) AS population_variance,
    traffic_range
FROM stats;