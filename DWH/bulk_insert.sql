-- Eerst een tijdelijke tabel maken om de CSV-gegevens in te laden
DROP TABLE IF EXISTS #TempUserData;

CREATE TABLE #TempUserData (
    EAN_ID VARCHAR(50),
    Datum DATE,
    Datum_Startuur VARCHAR(500),
    Volume_Afname_kWh VARCHAR(30),
    Volume_Injectie_kWh VARCHAR(30),
    Warmtepomp_Indicator BIT,
    Elektrisch_Voertuig_Indicator BIT,
    [PV-Installatie_Indicator] BIT,
    Contract_Categorie NVARCHAR(100)
);

-- Bulk insert van CSV naar de tijdelijke tabel
BULK INSERT #TempUserData
FROM 'C:\Users\jaakd\PycharmProjects\dep1-24-25-g02\data\input\P6269_1_50_DMK_Sample_Elek.csv' -- verander naar correcte pad
WITH (
    FIELDTERMINATOR = ';',
    ROWTERMINATOR = '0x0a',
    FIRSTROW = 2,
    CODEPAGE = '65001'  -- UTF-8
);


-- Alleen unieke gebruikers naar DimUser kopiëren met DISTINCT
INSERT INTO DimUser (EAN_ID, ContractCategory, PVInstallationIndicator, ElectricVehicleIndicator, HeatPumpIndicator)
SELECT
    EAN_ID,
    MAX(Contract_Categorie) AS ContractCategory,
    MAX(CAST([PV-Installatie_Indicator] AS INT)) AS PVInstallationIndicator,
    MAX(CAST(Elektrisch_Voertuig_Indicator AS INT)) AS ElectricVehicleIndicator,
    MAX(CAST(Warmtepomp_Indicator AS INT)) AS HeatPumpIndicator
FROM #TempUserData
GROUP BY EAN_ID;

-- Voeg de gegevens toe aan de FactEnergyUsage tabel
INSERT INTO FactEnergyUsage (DateKey, TimeKey, UserKey, ConsumptionVolume_kWh, InjectionVolume_kWh)
SELECT
    CONVERT(INT, FORMAT(CAST(Datum AS DATE), 'yyyyMMdd')) AS DateKey,
    CAST(SUBSTRING(Datum_Startuur, 12, 2) + SUBSTRING(Datum_Startuur, 15, 2) AS INT) AS TimeKey,
    EAN_ID AS UserKey,
    ISNULL(TRY_CAST(Volume_Afname_kWh AS DECIMAL(18,2)), 0.00) AS ConsumptionVolume_kWh,
    ISNULL(TRY_CAST(Volume_Injectie_kWh AS DECIMAL(18,2)), 0.00) AS InjectionVolume_kWh
FROM #TempUserData;


-- Tijdelijke tabel opruimen
DROP TABLE #TempUserData;
