-- Rebuild steps are in the Part 1 README. Run this query after importing.

/*Verify the data load by checking the distinct records and max and min values from the source file*/
/* 1.1 Load the data Set */
SELECT COUNT(*) AS original_rows,                          -- expected: 48204
       COUNT(DISTINCT date_time) AS distinct_hours,   -- expected: 40575
       MIN(date_time) AS first_row_entry,
       MAX(date_time) AS last_row_entry,
       MIN(temp) AS min_temp,
       MAX(temp) AS max_temp,
       COUNT(CASE WHEN temp = 0 THEN 1 END) AS zero_kelvin_rows, --identify 0 Kelvin readings that are invalid for outdoor weather
       MAX(rain_1h) AS max_rain_mm,
       MIN(traffic_volume) AS min_traffic,
       MAX(traffic_volume) AS max_traffic
FROM Traffic_Volume;
