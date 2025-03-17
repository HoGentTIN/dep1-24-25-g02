

CREATE TABLE FactNetworkOperator (
    NetworkOperatorID INT IDENTITY(1,1) PRIMARY KEY,
    NetworkOperator NVARCHAR(255) UNIQUE
);


INSERT INTO FactNetworkOperator (NetworkOperator)
SELECT DISTINCT NetworkOperator FROM FactNetwork;


ALTER TABLE FactNetwork ADD NetworkOperatorID INT;


UPDATE FactNetwork
SET NetworkOperatorID = fno.NetworkOperatorID
FROM FactNetwork fn
JOIN FactNetworkOperator fno ON fn.NetworkOperator = fno.NetworkOperator;

ALTER TABLE FactNetwork DROP COLUMN NetworkOperator;

ALTER TABLE FactNetwork 
ADD CONSTRAINT FK_FactNetwork_NetworkOperator FOREIGN KEY (NetworkOperatorID)
REFERENCES FactNetworkOperator(NetworkOperatorID);
