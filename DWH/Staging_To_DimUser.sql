INSERT INTO DimUser (EAN_ID, ContractCategory, PVInstallationIndicator, ElectricVehicleIndicator, HeatPumpIndicator)
SELECT 
    EAN_ID, 
    MAX(Contract_Categorie),
    MAX(CAST(PV_Installatie_Indicator AS INT)),
    MAX(CAST(Elektrisch_Voertuig_Indicator AS INT)),
    MAX(CAST(Warmtepomp_Indicator AS INT))
FROM DimUser_Staging
GROUP BY EAN_ID;
