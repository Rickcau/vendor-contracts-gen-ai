CREATE TABLE dbo.Contracts
(
    ContractID INT PRIMARY KEY,
    VendorName NVARCHAR(255),
    ClientName NVARCHAR(255),
    ContractTitle NVARCHAR(255),
    ContractType NVARCHAR(100),
    EffectiveDate DATE,
    EndDate DATE,
    SigningDate DATE,
    Status NVARCHAR(50),
    Compensation DECIMAL(18, 2),
    PaymentTerms NVARCHAR(100),
    Currency NVARCHAR(10),
    ScopeOfWork NVARCHAR(MAX),
    GoverningLaw NVARCHAR(255),
    TerminationClause NVARCHAR(MAX),
    ConfidentialityClause BIT,
    ParentContractID INT,
    AmendmentNumber INT,
    Notes NVARCHAR(MAX),
    Metadata NVARCHAR(MAX)
);
GO