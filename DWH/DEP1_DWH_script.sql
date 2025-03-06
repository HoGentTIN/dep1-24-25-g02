IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'DEP1_DWH')
BEGIN
    CREATE DATABASE [DEP1_DWH];
END;
GO

USE [DEP1_DWH];

-- Dimension Tables
CREATE TABLE [dbo].[DimEnergyContract] (
    [ContractType] VARCHAR(255) PRIMARY KEY
);

CREATE TABLE [dbo].[DimWeatherStation] (
    [WeatherStationKey] INT IDENTITY(1,1) PRIMARY KEY,
    [WeatherStationID] VARCHAR(255),
    [WeatherStationName] VARCHAR(255),
    [Latitude] DECIMAL(9,6),
    [Longitude] DECIMAL(9,6),
    [Altitude] DECIMAL(9,2)
);

CREATE TABLE [dbo].[DimTime] (
    [TimeKey] INT PRIMARY KEY,
    [Hour] INT,
    [Minutes] INT,
    [FullTime] TIME,
    [TimeAM_PM] VARCHAR(2)
);

CREATE TABLE [dbo].[DimDate] (
    [DateKey] INT PRIMARY KEY,
    [FullDate] DATE NOT NULL,
    [DayName] VARCHAR(50),
    [MonthNameDutch] VARCHAR(50),
    [MonthNameEN] VARCHAR(50),
    [DayNameDutch] VARCHAR(50),
    [DayNameEN] VARCHAR(50),
    [QuarterName] VARCHAR(50),
    [QuarterNumber] INT
);

CREATE TABLE [dbo].[DimUser] (
    [UserKey] INT IDENTITY(1,1) PRIMARY KEY,
    [EAN_ID] VARCHAR(255),
    [ContractCategory] VARCHAR(255),
    [PVInstallationIndicator] BIT,
    [ElectricVehicleIndicator] BIT,
    [HeatPumpIndicator] BIT
);

-- Fact Tables
CREATE TABLE [dbo].[FactWeather] (
    [WeatherKey] INT IDENTITY(1,1) PRIMARY KEY,
    [DateKey] INT NOT NULL,
    [TimeKey] INT,
    [WeatherStationKey] INT,
    [PrecipQuantity] DECIMAL(5,2),
    [TempAvg] DECIMAL(5,2),
    [TempMax] DECIMAL(5,2),
    [TempMin] DECIMAL(5,2),
    [TempGrassPt100Avg] DECIMAL(5,2),
    [TempSoilAvg] DECIMAL(5,2),
    [TempSoilAvg5cm] DECIMAL(5,2),
    [TempSoilAvg10cm] DECIMAL(5,2),
    [TempSoilAvg20cm] DECIMAL(5,2),
    [TempSoilAvg50cm] DECIMAL(5,2),
    [WindSpeed10m] DECIMAL(5,2),
    [WindSpeedAvg30m] DECIMAL(5,2),
    [WindGustsSpeed] DECIMAL(5,2),
    [HumidityRelShelterAvg] DECIMAL(5,2),
    [Pressure] DECIMAL(7,2),
    [SunDuration] DECIMAL(5,2),
    [ShortWaveFromSkyAvg] DECIMAL(5,2),
    [SunIntAvg] DECIMAL(5,2)
);

CREATE TABLE [dbo].[FactBelpex] (
    [BelpexKey] INT IDENTITY(1,1) PRIMARY KEY,
    [DateKey] INT NOT NULL,
    [TimeKey] INT,
    [BelpexPrice] DECIMAL(10,4),
    [Belpex_RLP_MPrice] DECIMAL(10,4)
);

CREATE TABLE [dbo].[FactEnergyUsage] (
    [UsageKey] INT IDENTITY(1,1) PRIMARY KEY,
    [DateKey] INT NOT NULL,
    [TimeKey] INT,
    [UserKey] INT,
    [ConsumptionVolume_kWh] DECIMAL(10,2),
    [InjectionVolume_kWh] DECIMAL(10,2)
);

CREATE TABLE [dbo].[FactNetworkCosts] (
    [NetworkCostKey] INT IDENTITY(1,1) PRIMARY KEY,
    [DateKey] INT NOT NULL,
    [UserKey] INT,
    [NetworkOperator] VARCHAR(255),
    [TransmissionCost] DECIMAL(10,2),
    [CapacityTariff_DigitalMeter] DECIMAL(10,2),
    [ConsumptionTariff_DigitalMeter_Normal] DECIMAL(10,2),
    [ConsumptionTariff_DigitalMeter_ExclusiveNight] DECIMAL(10,2),
    [BalancingCost] DECIMAL(10,2),
    [MeterFactor] DECIMAL(10,2),
    [CapacityTariff_ClassicMeter] DECIMAL(10,2),
    [ConsumptionTariff_ClassicMeter_Normal] DECIMAL(10,2),
    [ConsumptionTariff_ClassicMeter_ExclusiveNight] DECIMAL(10,2),
    [ProsumerTariff] DECIMAL(10,2),
    [DataManagementTariff_YearlyMonthlyReadMeters] DECIMAL(10,2),
    [DataManagementTariff_QuarterlyReadMeters] DECIMAL(10,2)
);

-- Adding Constraints
ALTER TABLE [dbo].[FactWeather] WITH CHECK ADD CONSTRAINT [FK_FactWeather_Date] FOREIGN KEY ([DateKey]) REFERENCES [dbo].[DimDate]([DateKey]);
ALTER TABLE [dbo].[FactWeather] CHECK CONSTRAINT [FK_FactWeather_Date];
ALTER TABLE [dbo].[FactWeather] WITH CHECK ADD CONSTRAINT [FK_FactWeather_Time] FOREIGN KEY ([TimeKey]) REFERENCES [dbo].[DimTime]([TimeKey]);
ALTER TABLE [dbo].[FactWeather] CHECK CONSTRAINT [FK_FactWeather_Time];
ALTER TABLE [dbo].[FactWeather] WITH CHECK ADD CONSTRAINT [FK_FactWeather_WeatherStation] FOREIGN KEY ([WeatherStationKey]) REFERENCES [dbo].[DimWeatherStation]([WeatherStationKey]);
ALTER TABLE [dbo].[FactWeather] CHECK CONSTRAINT [FK_FactWeather_WeatherStation];

ALTER TABLE [dbo].[FactBelpex] WITH CHECK ADD CONSTRAINT [FK_FactBelpex_Date] FOREIGN KEY ([DateKey]) REFERENCES [dbo].[DimDate]([DateKey]);
ALTER TABLE [dbo].[FactBelpex] CHECK CONSTRAINT [FK_FactBelpex_Date];
ALTER TABLE [dbo].[FactBelpex] WITH CHECK ADD CONSTRAINT [FK_FactBelpex_Time] FOREIGN KEY ([TimeKey]) REFERENCES [dbo].[DimTime]([TimeKey]);
ALTER TABLE [dbo].[FactBelpex] CHECK CONSTRAINT [FK_FactBelpex_Time];

ALTER TABLE [dbo].[FactEnergyUsage] WITH CHECK ADD CONSTRAINT [FK_FactEnergyUsage_Date] FOREIGN KEY ([DateKey]) REFERENCES [dbo].[DimDate]([DateKey]);
ALTER TABLE [dbo].[FactEnergyUsage] CHECK CONSTRAINT [FK_FactEnergyUsage_Date];
ALTER TABLE [dbo].[FactEnergyUsage] WITH CHECK ADD CONSTRAINT [FK_FactEnergyUsage_Time] FOREIGN KEY ([TimeKey]) REFERENCES [dbo].[DimTime]([TimeKey]);
ALTER TABLE [dbo].[FactEnergyUsage] CHECK CONSTRAINT [FK_FactEnergyUsage_Time];
ALTER TABLE [dbo].[FactEnergyUsage] WITH CHECK ADD CONSTRAINT [FK_FactEnergyUsage_User] FOREIGN KEY ([UserKey]) REFERENCES [dbo].[DimUser]([UserKey]);
ALTER TABLE [dbo].[FactEnergyUsage] CHECK CONSTRAINT [FK_FactEnergyUsage_User];
