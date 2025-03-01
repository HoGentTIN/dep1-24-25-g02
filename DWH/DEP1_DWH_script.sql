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
    [WeatherStationID] INT IDENTITY(1,1) PRIMARY KEY,
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
    [MonthName] VARCHAR(50),
    [MonthNumber] INT,
    [DayName] VARCHAR(50),
    [DayNumber] INT,
    [QuarterName] VARCHAR(50),
    [QuarterNumber] INT
);

CREATE TABLE [dbo].[DimUser] (
    [UserKey] INT IDENTITY(1,1) PRIMARY KEY,
    [CAN_ID] VARCHAR(255),
    [ContractCategory] VARCHAR(255),
    [DistributionCategory] VARCHAR(255),
    [RetailProvider] VARCHAR(255),
    [HasPPAContract] BIT
);

-- Fact Tables
CREATE TABLE [dbo].[FactWeather] (
    [WeatherKey] INT IDENTITY(1,1) PRIMARY KEY,
    [DateKey] INT NOT NULL,
    [WeatherStationKey] INT NOT NULL,
    [PrecipProbability] DECIMAL(5,2),
    [PrecipIntensity] DECIMAL(5,2),
    [Temperature] DECIMAL(5,2),
    [TempMin] DECIMAL(5,2),
    [TempMax] DECIMAL(5,2),
    [TempFeelsLike] DECIMAL(5,2),
    [TempDewPoint] DECIMAL(5,2),
    [TempMinDiff8to9h] DECIMAL(5,2),
    [TempFeelsLikeAvg] DECIMAL(5,2),
    [TempFeelsLikeMorning] DECIMAL(5,2),
    [TempFeelsLikeAfternoon] DECIMAL(5,2),
    [WindSpeed] DECIMAL(5,2),
    [WindGust] DECIMAL(5,2),
    [WindSpeedAvg] DECIMAL(5,2),
    [WindDirection] INT,
    [ShortWaveRadiationAvg] DECIMAL(5,2),
    [SunFraction] DECIMAL(5,2)
);

CREATE TABLE [dbo].[FactBifex] (
    [BifexKey] INT IDENTITY(1,1) PRIMARY KEY,
    [DateKey] INT NOT NULL,
    [UserKey] INT NOT NULL,
    [BifexPrice] DECIMAL(10,4),
    [Bifex_PLP_Uplift] DECIMAL(10,4)
);

CREATE TABLE [dbo].[FactEnergyUsage] (
    [EnergyUsageKey] INT IDENTITY(1,1) PRIMARY KEY,
    [DateKey] INT NOT NULL,
    [TimeKey] INT NOT NULL,
    [UserKey] INT NOT NULL,
    [ConsumptionVolume_kWh] DECIMAL(10,2),
    [InjectionVolume_kWh] DECIMAL(10,2)
);

CREATE TABLE [dbo].[FactNetworkCosts] (
    [NetworkCostKey] INT IDENTITY(1,1) PRIMARY KEY,
    [DateKey] INT NOT NULL,
    [UserKey] INT NOT NULL,
    [NetworkSegment] VARCHAR(255),
    [TransmissionCost] DECIMAL(10,2),
    [CongestionTariff_Daylight] DECIMAL(10,2),
    [CongestionTariff_Daylight_Normal] DECIMAL(10,2),
    [CongestionTariff_Daylight_ReducedHeight] DECIMAL(10,2),
    [MarketCost] DECIMAL(10,2),
    [CapacityTariff] DECIMAL(10,2),
    [CapacityTariff_ClassMarket] DECIMAL(10,2),
    [CapacityTariff_ClassMarket_Normal] DECIMAL(10,2),
    [ProcurementTariff] DECIMAL(10,2),
    [DataManagementTariff_Supplier] DECIMAL(10,2),
    [DataManagementTariff_QueryForOtherMarkets] DECIMAL(10,2)
);

-- Adding Constraints
ALTER TABLE [dbo].[FactWeather]  WITH CHECK ADD CONSTRAINT [FK_FactWeather_Date] FOREIGN KEY ([DateKey])
REFERENCES [dbo].[DimDate]([DateKey]);
GO
ALTER TABLE [dbo].[FactWeather] CHECK CONSTRAINT [FK_FactWeather_Date];
GO
ALTER TABLE [dbo].[FactWeather]  WITH CHECK ADD CONSTRAINT [FK_FactWeather_WeatherStation] FOREIGN KEY ([WeatherStationKey]) 
REFERENCES [dbo].[DimWeatherStation]([WeatherStationID]);
GO
ALTER TABLE [dbo].[FactWeather] CHECK CONSTRAINT [FK_FactWeather_WeatherStation];
GO

ALTER TABLE [dbo].[FactBifex]  WITH CHECK ADD CONSTRAINT [FK_FactBifex_Date] FOREIGN KEY ([DateKey])
REFERENCES [dbo].[DimDate]([DateKey]);
GO
ALTER TABLE [dbo].[FactBifex] CHECK CONSTRAINT [FK_FactBifex_Date];
GO
ALTER TABLE [dbo].[FactBifex]  WITH CHECK ADD CONSTRAINT [FK_FactBifex_User] FOREIGN KEY ([UserKey]) 
REFERENCES [dbo].[DimUser]([UserKey]);
GO
ALTER TABLE [dbo].[FactBifex] CHECK CONSTRAINT [FK_FactBifex_User];
GO

ALTER TABLE [dbo].[FactEnergyUsage]  WITH CHECK ADD CONSTRAINT [FK_FactEnergyUsage_Date] FOREIGN KEY ([DateKey]) 
REFERENCES [dbo].[DimDate]([DateKey]);
GO
ALTER TABLE [dbo].[FactEnergyUsage] CHECK CONSTRAINT [FK_FactEnergyUsage_Date];
GO
ALTER TABLE [dbo].[FactEnergyUsage]  WITH CHECK ADD CONSTRAINT [FK_FactEnergyUsage_Time] FOREIGN KEY ([TimeKey]) 
REFERENCES [dbo].[DimTime]([TimeKey]);
GO
ALTER TABLE [dbo].[FactEnergyUsage] CHECK CONSTRAINT [FK_FactEnergyUsage_Time];
GO
ALTER TABLE [dbo].[FactEnergyUsage]  WITH CHECK ADD CONSTRAINT [FK_FactEnergyUsage_User] FOREIGN KEY ([UserKey]) 
REFERENCES [dbo].[DimUser]([UserKey]);
GO
ALTER TABLE [dbo].[FactEnergyUsage] CHECK CONSTRAINT [FK_FactEnergyUsage_User];
GO

ALTER TABLE [dbo].[FactNetworkCosts]  WITH CHECK ADD CONSTRAINT [FK_FactNetworkCosts_Date] FOREIGN KEY ([DateKey]) 
REFERENCES [dbo].[DimDate]([DateKey]);
GO
ALTER TABLE [dbo].[FactNetworkCosts] CHECK CONSTRAINT [FK_FactNetworkCosts_Date];
GO
ALTER TABLE [dbo].[FactNetworkCosts]  WITH CHECK ADD CONSTRAINT [FK_FactNetworkCosts_User] FOREIGN KEY ([UserKey]) 
REFERENCES [dbo].[DimUser]([UserKey]);
GO
ALTER TABLE [dbo].[FactNetworkCosts] CHECK CONSTRAINT [FK_FactNetworkCosts_User];
GO
