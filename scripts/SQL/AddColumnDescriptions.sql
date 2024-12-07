

EXEC sp_addextendedproperty 
    @name = N'MS_Description',
    @value = N'Unique identifier for each contract.',
    @level0type = N'Schema', @level0name = 'dbo',
    @level1type = N'Table', @level1name = 'Contracts', 
    @level2type = N'Column', @level2name = 'ContractID';

-- VendorName description
EXEC sp_addextendedproperty 
    @name = N'MS_Description',
    @value = N'Name of the vendor or contractor involved in the agreement.',
    @level0type = N'Schema', @level0name = 'dbo',
    @level1type = N'Table', @level1name = 'Contracts', 
    @level2type = N'Column', @level2name = 'VendorName';

-- ClientName description
EXEC sp_addextendedproperty 
    @name = N'MS_Description',
    @value = N'Name of the client or contracting entity.',
    @level0type = N'Schema', @level0name = 'dbo',
    @level1type = N'Table', @level1name = 'Contracts', 
    @level2type = N'Column', @level2name = 'ClientName';

-- ContractTitle description
EXEC sp_addextendedproperty 
    @name = N'MS_Description',
    @value = N'A brief title describing the contract (e.g., "Service Agreement").',
    @level0type = N'Schema', @level0name = 'dbo',
    @level1type = N'Table', @level1name = 'Contracts', 
    @level2type = N'Column', @level2name = 'ContractTitle';

-- ContractType description
EXEC sp_addextendedproperty 
    @name = N'MS_Description',
    @value = N'The category or type of contract (e.g., NDA, SLA, Service Agreement).',
    @level0type = N'Schema', @level0name = 'dbo',
    @level1type = N'Table', @level1name = 'Contracts', 
    @level2type = N'Column', @level2name = 'ContractType';

-- EffectiveDate description
EXEC sp_addextendedproperty 
    @name = N'MS_Description',
    @value = N'The date when the contract becomes effective.',
    @level0type = N'Schema', @level0name = 'dbo',
    @level1type = N'Table', @level1name = 'Contracts', 
    @level2type = N'Column', @level2name = 'EffectiveDate';

-- EndDate description
EXEC sp_addextendedproperty 
    @name = N'MS_Description',
    @value = N'The expiration or termination date of the contract, if applicable.',
    @level0type = N'Schema', @level0name = 'dbo',
    @level1type = N'Table', @level1name = 'Contracts', 
    @level2type = N'Column', @level2name = 'EndDate';

-- SigningDate description
EXEC sp_addextendedproperty 
    @name = N'MS_Description',
    @value = N'The date on which the contract was signed by all parties.',
    @level0type = N'Schema', @level0name = 'dbo',
    @level1type = N'Table', @level1name = 'Contracts', 
    @level2type = N'Column', @level2name = 'SigningDate';

-- Status description
EXEC sp_addextendedproperty 
    @name = N'MS_Description',
    @value = N'Current status of the contract (e.g., Active, Draft, Terminated).',
    @level0type = N'Schema', @level0name = 'dbo',
    @level1type = N'Table', @level1name = 'Contracts', 
    @level2type = N'Column', @level2name = 'Status';

-- Compensation description
EXEC sp_addextendedproperty 
    @name = N'MS_Description',
    @value = N'The total financial value of the contract.',
    @level0type = N'Schema', @level0name = 'dbo',
    @level1type = N'Table', @level1name = 'Contracts', 
    @level2type = N'Column', @level2name = 'Compensation';

-- PaymentTerms description
EXEC sp_addextendedproperty 
    @name = N'MS_Description',
    @value = N'Payment terms, including frequency or milestones (e.g., "Net 30 days").',
    @level0type = N'Schema', @level0name = 'dbo',
    @level1type = N'Table', @level1name = 'Contracts', 
    @level2type = N'Column', @level2name = 'PaymentTerms';

-- Currency description
EXEC sp_addextendedproperty 
    @name = N'MS_Description',
    @value = N'The currency used in the financial details (e.g., USD, EUR).',
    @level0type = N'Schema', @level0name = 'dbo',
    @level1type = N'Table', @level1name = 'Contracts', 
    @level2type = N'Column', @level2name = 'Currency';

-- ScopeOfWork description
EXEC sp_addextendedproperty 
    @name = N'MS_Description',
    @value = N'A summary of the scope or deliverables defined in the contract.',
    @level0type = N'Schema', @level0name = 'dbo',
    @level1type = N'Table', @level1name = 'Contracts', 
    @level2type = N'Column', @level2name = 'ScopeOfWork';

-- GoverningLaw description
EXEC sp_addextendedproperty 
    @name = N'MS_Description',
    @value = N'The legal jurisdiction governing the contract.',
    @level0type = N'Schema', @level0name = 'dbo',
    @level1type = N'Table', @level1name = 'Contracts', 
    @level2type = N'Column', @level2name = 'GoverningLaw';

-- TerminationClause description
EXEC sp_addextendedproperty 
    @name = N'MS_Description',
    @value = N'Key details about the termination conditions outlined in the contract.',
    @level0type = N'Schema', @level0name = 'dbo',
    @level1type = N'Table', @level1name = 'Contracts', 
    @level2type = N'Column', @level2name = 'TerminationClause';

-- ConfidentialityClause description
EXEC sp_addextendedproperty 
    @name = N'MS_Description',
    @value = N'Indicates whether a confidentiality clause is included in the contract.',
    @level0type = N'Schema', @level0name = 'dbo',
    @level1type = N'Table', @level1name = 'Contracts', 
    @level2type = N'Column', @level2name = 'ConfidentialityClause';

-- ParentContractID description
EXEC sp_addextendedproperty 
    @name = N'MS_Description',
    @value = N'The ID of the original contract if this is an amendment or addendum.',
    @level0type = N'Schema', @level0name = 'dbo',
    @level1type = N'Table', @level1name = 'Contracts', 
    @level2type = N'Column', @level2name = 'ParentContractID';

-- AmendmentNumber description
EXEC sp_addextendedproperty 
    @name = N'MS_Description',
    @value = N'The sequential number of the amendment or addendum to the contract.',
    @level0type = N'Schema', @level0name = 'dbo',
    @level1type = N'Table', @level1name = 'Contracts', 
    @level2type = N'Column', @level2name = 'AmendmentNumber';

-- Notes description
EXEC sp_addextendedproperty
    @name = N'MS_Description',
    @value = N'Any additional notes or comments about the contract.',
    @level0type = N'Schema', @level0name = 'dbo',
    @level1type = N'Table', @level1name = 'Contracts', 
    @level2type = N'Column', @level2name = 'Notes';

-- Metadata description
EXEC sp_addextendedproperty
    @name = N'MS_Description',
    @value = N'A JSON column to store unstructured or custom data extracted from the contract.',
    @level0type = N'Schema', @level0name = 'dbo',
    @level1type = N'Table', @level1name = 'Contracts', 
    @level2type = N'Column', @level2name = 'Metadata';
