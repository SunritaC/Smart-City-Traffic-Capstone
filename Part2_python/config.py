"""Shared schema, ranking and thresholds."""
# These nine column names must be present before the pipeline can clean the CSV.
COLUMNS = ("holiday", "temp", "rain_1h", "snow_1h", "clouds_all",
           "weather_main", "weather_description", "date_time", "traffic_volume")
# The list starts at the lowest severity. Positions become scores starting from one.
ORDER = ("Clear", "Clouds", "Mist", "Haze", "Smoke", "Fog", "Drizzle",
         "Rain", "Snow", "Squall", "Thunderstorm")
RANK = {name: value for value, name in enumerate(ORDER, 1)}
# The Part 1 review identified these two zero-volume readings as sensor dropouts.
DROP_OUTS = ("2016-07-23 18:00:00", "2016-07-23 23:00:00")
SEVERE = {"Thunderstorm", "Snow", "Squall"}
LOW_VISIBILITY = {"Fog", "Mist", "Haze", "Smoke"}
CONGESTION = 5500
