WITH counts AS (
    SELECT
        COUNT(*) AS observed_hours,
        COUNT(CASE WHEN traffic_volume > 5500 THEN 1 END)
            AS congested_hours,
        COUNT(CASE WHEN weather_main = 'Clear' THEN 1 END)
            AS clear_hours,
        COUNT(CASE
            WHEN traffic_volume > 5500 AND weather_main = 'Clear' THEN 1
        END) AS congested_and_clear_hours
    FROM traffic_hourly
)
SELECT
    observed_hours,
    congested_hours,
    clear_hours,
    congested_and_clear_hours,
    ROUND(100.0 * congested_hours / observed_hours, 2)
        AS p_congestion_pct,
    ROUND(100.0 * clear_hours / observed_hours, 2)
        AS p_clear_weather_pct,
    ROUND(100.0 * congested_and_clear_hours / observed_hours, 2)
        AS p_congestion_and_clear_pct
FROM counts;