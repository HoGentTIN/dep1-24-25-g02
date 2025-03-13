-- Hoeveel tariefkaarten heb je toegevoegd voor DATS 24 Elektriciteit?
SELECT COUNT(*) as 'Aantal' FROM FactEnergyCost JOIN dbo.DimEnergyContract D on FactEnergyCost.ContractKey = D.ContractKey WHERE Provider = 'DATS24' AND ContractName = 'ELEKTRICITEIT'

-- Hoe vaak veranderde het verbruikstarief met een enkelvoudige teller binnen het contract Eneco Zon & Wind Flex?
SELECT DISTINCT SingleMeterVariableMeterFactor FROM FactEnergyCost  JOIN dbo.DimEnergyContract D on FactEnergyCost.ContractKey = D.ContractKey WHERE ContractName = 'ZON WIND FLEX'

-- Wat was in 2024 het verschil tussen de hoogste en de laagste abonnementskost (per maand)? Tussen welke twee contracten was dit?
-- Antwoord: Zon en flex Variabel & octa+ fixed
SELECT * FROM FactEnergyCost JOIN dbo.DimEnergyContract D on D.ContractKey = FactEnergyCost.ContractKey
WHERE DateKey LIKE '2024%' AND (AdministrativeCosts = (SELECT MIN(AdministrativeCosts) FROM FactEnergyCost)
   OR AdministrativeCosts = (SELECT MAX(AdministrativeCosts) FROM FactEnergyCost));

-- Wat was over alle vaste contracten heen in 2024 het contract met het laagste tarief (op jaarbasis) voor 1 kWu stroom met een enkelvoudige meter?
SELECT MIN(SingleMeterFixed) FROM FactEnergyCost


-- Met welk contract kreeg je in januari 2025 de hoogste prijs per kWu voor geïnjecteerde stroom als je rekent met een constante Belpex-waarde van 100 euro? Hoeveel per kWu?
WITH InjectionPrices AS (
    SELECT
        f.ContractKey,
        (100 * ISNULL(f.SingleMeterInjectionMeterFactor, 0) + ISNULL(f.SingleMeterInjectionBalancingCost, 0)) AS SingleMeterInjectionPrice,
        (100 * ISNULL(f.DualMeterDayInjectionMeterFactor, 0) + ISNULL(f.DualMeterDayInjectionBalancingCost, 0)) AS DualMeterDayInjectionPrice,
        (100 * ISNULL(f.DualMeterNightInjectionMeterFactor, 0) + ISNULL(f.DualMeterNightInjectionBalancingCost, 0)) AS DualMeterNightInjectionPrice
    FROM
        FactEnergyCost f
    WHERE
        f.DateKey LIKE '202501%'
),
MaxPrices AS (
    SELECT
        ContractKey,
        CASE
            WHEN SingleMeterInjectionPrice >= DualMeterDayInjectionPrice AND SingleMeterInjectionPrice >= DualMeterNightInjectionPrice THEN SingleMeterInjectionPrice
            WHEN DualMeterDayInjectionPrice >= SingleMeterInjectionPrice AND DualMeterDayInjectionPrice >= DualMeterNightInjectionPrice THEN DualMeterDayInjectionPrice
            ELSE DualMeterNightInjectionPrice
        END AS MaxInjectionPrice,
        CASE
            WHEN SingleMeterInjectionPrice >= DualMeterDayInjectionPrice AND SingleMeterInjectionPrice >= DualMeterNightInjectionPrice THEN 'SingleMeter'
            WHEN DualMeterDayInjectionPrice >= SingleMeterInjectionPrice AND DualMeterDayInjectionPrice >= DualMeterNightInjectionPrice THEN 'DualMeterDay'
            ELSE 'DualMeterNight'
        END AS MeterType
    FROM
        InjectionPrices
)
SELECT TOP 1
    ContractKey,
    MaxInjectionPrice AS HoogstePrijsPerKWu,
    MeterType
FROM
    MaxPrices
ORDER BY
    MaxInjectionPrice DESC;


-- Query om het contract te vinden met de hoogste bijdrage voor groene stroom en WKK samen over 2024
WITH ContractContributions AS (
    SELECT
        ContractKey,
        SUM(ISNULL(GreenElectricity, 0) + ISNULL(WKK, 0)) AS TotalContribution
    FROM
        FactEnergyCost
    WHERE
        DateKey >= 20240101 AND DateKey < 20250101
    GROUP BY
        ContractKey
)
SELECT TOP 1
    ContractKey,
    TotalContribution AS HoogsteBijdragePerKWu
FROM
    ContractContributions
ORDER BY
    TotalContribution DESC;



-- Voor welk contract en tarieftype(s) had je vorige maand de laagste meterfactor? Hoeveel?
-- De meterfactor is de X uit de tariefformule 'Belpex * X + Y'
WITH MeterfactorData AS (
    SELECT
        ContractKey,
        'SingleMeter' AS MeterType,
        SingleMeterInjectionMeterFactor AS Meterfactor
    FROM
        FactEnergyCost
    WHERE
        DateKey LIKE '202502%'
        AND SingleMeterInjectionMeterFactor IS NOT NULL

    UNION ALL

    SELECT
        ContractKey,
        'DualMeterDay' AS MeterType,
        DualMeterDayInjectionMeterFactor AS Meterfactor
    FROM
        FactEnergyCost
    WHERE
        DateKey LIKE '202502%'
        AND DualMeterDayInjectionMeterFactor IS NOT NULL

    UNION ALL

    SELECT
        ContractKey,
        'DualMeterNight' AS MeterType,
        DualMeterNightInjectionMeterFactor AS Meterfactor
    FROM
        FactEnergyCost
    WHERE
        DateKey LIKE '202502%'
        AND DualMeterNightInjectionMeterFactor IS NOT NULL
)
SELECT TOP 1
    ContractKey,
    MeterType,
    Meterfactor AS LaagsteMeterfactor
FROM
    MeterfactorData
ORDER BY
    Meterfactor ASC;

