ALTER TABLE dbo.FactWeather NOCHECK CONSTRAINT FK_FactWeather_WeatherStation;
GO

WITH CTE AS (
    SELECT 
        *, 
        ROW_NUMBER() OVER (PARTITION BY WeatherStationName ORDER BY (SELECT NULL)) AS row_num
    FROM DimWeatherStation
)
DELETE FROM DimWeatherStation WHERE WeatherStationName IN (
    SELECT WeatherStationName FROM CTE WHERE row_num > 1
);

ALTER TABLE dbo.FactWeather CHECK CONSTRAINT FK_FactWeather_WeatherStation;
GO