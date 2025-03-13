-- aantal metingen ìn maart 2025
SELECT count(*) AS 'Aantal records 2025' FROM FactWeather
WHERE DateKey > 20250206

-- max gemiddelde temperatuur in 2025
SELECT * FROM FactWeather
WHERE DateKey > 20250000
and TempAvg = (SELECT max(TempAvg) FROM FactWeather WHERE DateKey > 20250000)

-- max regen in Melle in 2025
USE DEP1_DWH;

SELECT 
    f.DateKey, 
    f.WeatherKey, 
    f.PrecipQuantity, 
    d.WeatherStationName
FROM FactWeather f
INNER JOIN DimWeatherStation d ON f.WeatherStationKey = d.WeatherStationKey
WHERE f.DateKey > 20250000
AND UPPER(d.WeatherStationName) = 'MELLE'
AND f.PrecipQuantity = (
    SELECT MAX(fw.PrecipQuantity)
    FROM FactWeather fw
    INNER JOIN DimWeatherStation dw ON fw.WeatherStationKey = dw.WeatherStationKey
    WHERE fw.DateKey > 20250000
    AND UPPER(dw.WeatherStationName) = 'MELLE'
);


-- Hoeveel uren zonlicht werden reeds gemeten in Stabroek deze maand?
USE DEP1_DWH;

SELECT 
    f.DateKey, 
    f.WeatherKey, 
    f.SunDuration, 
    d.WeatherStationName
FROM FactWeather f
INNER JOIN DimWeatherStation d ON f.WeatherStationKey = d.WeatherStationKey
WHERE f.DateKey > 20250300
AND UPPER(d.WeatherStationName) = 'STABROEK'
AND f.SunDuration = (
    SELECT MAX(fw.SunDuration)
    FROM FactWeather fw
    INNER JOIN DimWeatherStation dw ON fw.WeatherStationKey = dw.WeatherStationKey
    WHERE fw.DateKey > 20250300
    AND UPPER(dw.WeatherStationName) = 'STABROEK'
);