WITH flags AS (
    SELECT
        traffic_volume > 5500 AS congested,
        weather_main,
        temp
    FROM traffic_hourly
),
counts AS (
    SELECT
        COUNT(*) AS observed_hours,
        COUNT(CASE WHEN congested THEN 1 END) AS congested_hours,
        COUNT(CASE WHEN weather_main = 'Clear' THEN 1 END) AS clear_hours,

        -- Four counts for the clear-versus-cloudy odds ratio.
        COUNT(CASE WHEN congested AND weather_main = 'Clear' THEN 1 END)
            AS clear_congested,
        COUNT(CASE WHEN NOT congested AND weather_main = 'Clear' THEN 1 END)
            AS clear_not_congested,
        COUNT(CASE WHEN congested AND weather_main = 'Clouds' THEN 1 END)
            AS cloudy_congested,
        COUNT(CASE WHEN NOT congested AND weather_main = 'Clouds' THEN 1 END)
            AS cloudy_not_congested,

        -- valid temperature readings for the temperature probability.
        COUNT(CASE WHEN congested AND temp > 0 THEN 1 END)
            AS congested_valid_temp,
        COUNT(CASE WHEN congested AND temp > 292 THEN 1 END)
            AS congested_high_temp
    FROM flags
)
SELECT
    observed_hours,
    congested_hours,
    clear_congested,
    clear_not_congested,
    cloudy_congested,
    cloudy_not_congested,
    congested_valid_temp,
    congested_high_temp,

    ROUND(100.0 * clear_congested / NULLIF(congested_hours, 0), 2)
        AS p_clear_given_congestion_pct,
    ROUND(100.0 * congested_high_temp / NULLIF(congested_valid_temp, 0), 2)
        AS p_high_temp_given_congestion_pct,

  
    ROUND(100.0 * clear_congested / NULLIF(observed_hours, 0), 2)
        AS observed_joint_pct,
    ROUND(
        100.0 * congested_hours * clear_hours /
        NULLIF(1.0 * observed_hours * observed_hours, 0),
        2
    ) AS joint_pct_if_independent,

    CASE
        WHEN observed_hours = 0 THEN 'No data'
        WHEN clear_congested * observed_hours = congested_hours * clear_hours
            THEN 'Equal'
        ELSE 'Different'
    END AS independence_check,

    -- (Clear congestion odds) / (Cloudy congestion odds).
    ROUND(
        1.0 * clear_congested * cloudy_not_congested /
        NULLIF(clear_not_congested * cloudy_congested, 0),
        3
    ) AS clear_vs_cloudy_odds_ratio
FROM counts;