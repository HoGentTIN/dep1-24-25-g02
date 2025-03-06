-- Bulk Insert into DimUser
BULK INSERT dbo.DimUser
FROM 'C:\Users\jaakd\PycharmProjects\dep1-24-25-g02\data\input\P6269_1_50_DMK_Sample_Elek.csv'
WITH (
    FIELDTERMINATOR = ';', -- Semicolon as delimiter in the CSV
    ROWTERMINATOR = '\n',  -- New line as row terminator
    FIRSTROW = 2,          -- Skip the header row
    TABLOCK,               -- Lock table for performance
    MAXERRORS = 10
);

-- Bulk Insert into FactEnergyUsage
BULK INSERT dbo.FactEnergyUsage
FROM 'C:\Users\jaakd\PycharmProjects\dep1-24-25-g02\data\input\P6269_1_50_DMK_Sample_Elek.csv'
WITH (
    FIELDTERMINATOR = ';',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2,
    TABLOCK,
    MAXERRORS = 10
);
