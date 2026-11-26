CREATE VIEW traffic_hourly AS
SELECT date_time, holiday_any AS holiday, temp, rain_1h, snow_1h, clouds_all,
       weather_main, weather_description, traffic_volume
FROM (
    SELECT t.*,
           COALESCE(MAX(NULLIF(holiday, 'None')) OVER (PARTITION BY date_time), 'None') AS holiday_any,
           ROW_NUMBER() OVER (
               PARTITION BY date_time
               ORDER BY CASE weather_main
                            WHEN 'Thunderstorm' THEN 11 WHEN 'Squall' THEN 10
                            WHEN 'Snow'  THEN 9  WHEN 'Rain'  THEN 8
                            WHEN 'Drizzle' THEN 7 WHEN 'Fog'  THEN 6
                            WHEN 'Smoke' THEN 5  WHEN 'Haze'  THEN 4
                            WHEN 'Mist'  THEN 3  WHEN 'Clouds' THEN 2
                            WHEN 'Clear' THEN 1  ELSE 0 END DESC,
                        weather_description, rowid) AS rn
    FROM Traffic_Volume t
)
WHERE rn = 1;
