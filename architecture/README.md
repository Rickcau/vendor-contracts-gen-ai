# Solution Architecture and Approach

## Conceptual Architecture
Below is a rendering of a conceptual architecture for this solution.

![Solution Architecture](./images/Vendor-Contracts-ChatBot.png)

## Considerations
- Using a Hybrid approach, i.e. AI Search for embeddings and semantic searches and SQL for NL2SQL
- Considering that Addendums play an important role in fully understanding the agreement is very important
    - By creating a genaric schema in SQL that be be leveraged for any contract will provide a lot of flexibility
- All documents we would create embeddings for so users can perform NL searachs against the contracts
- But, for the situations in which there are Addendums it makes more sense so have those relation ships stored in SQL
    - We would have the general details stored in SQL (see details below) along with the relationships between contracts and addendums
    - Users would ask a question and we would first perform a SQL query to see if we can find any details, if found, we and perform a search to find the embeddings for the contract and any addendums

## Document Structure
Understanding the document structure for each document / vendor contract is extremly important.  There must be a clear way to identify how the contracts are related to any addendums, otherwise how can we establish a relationship between the two?

## AI Search Index Structure
We will need to make some decisions on the common fields that should be included in the index beyond just the contact and the embeddings for the content.  Below is an example of the fields we may need to consider for the index.

```
  document = {
                "id": document_id,
                "contractId": contract_id,
                "vendorName": vendor_name,
                "clientName": client_name,
                "contractTitle": contract_title,
                "effectiveDate": effective_date,
                "endDate": end_date,
                "signingDate": signing_date,
                "status" : status,
                "compensation": compensation,
                "paymentTerms": payment_terms,
                "currency": currency,
                "parentContractId": parent_contract_id,
                "amendmentNumber": amendment_number 
                "date": current_date,
                "sourceFileName": fileName,
                "searchVector": searchVector
            }
```

## SQL Schema Example
The schema below is a generic schema that should be usable for any contract type.  The purpose of this schema is to store contract details that should be generic to all contracts and amendments.  If can also be used to store amendments and the amendments would be related to the parent contract, which allows us to search for contract and amendments that are related.  For those contracts that have uncommon data, we can store that in the Metadata column which allows us to capture additional data without having to add a lot of columns that will not be common across contracts.

We are adding comments as these will be used to create the column descriptions.

```
CREATE TABLE Contracts (
    ContractID INT PRIMARY KEY COMMENT 'Unique identifier for each contract',
    VendorName VARCHAR(255) NOT NULL COMMENT 'Name of the vendor or contractor involved in the agreement',
    ClientName VARCHAR(255) NOT NULL COMMENT 'Name of the client or contracting entity',
    ContractTitle VARCHAR(255) COMMENT 'A brief title describing the contract (e.g., "Service Agreement")',
    ContractType VARCHAR(100) COMMENT 'Category or type of contract (e.g., NDA, SLA, Service Agreement)',
    EffectiveDate DATE COMMENT 'The date when the contract becomes effective',
    EndDate DATE COMMENT 'The expiration or termination date of the contract, if applicable',
    SigningDate DATE COMMENT 'The date on which the contract was signed by all parties',
    Status VARCHAR(50) COMMENT 'Current status of the contract (e.g., Active, Draft, Terminated)',
    Compensation DECIMAL(15, 2) COMMENT 'The total financial value of the contract',
    PaymentTerms TEXT COMMENT 'Payment terms, including frequency or milestones (e.g., "Net 30 days")',
    Currency VARCHAR(10) COMMENT 'The currency used in the financial details (e.g., USD, EUR)',
    ScopeOfWork TEXT COMMENT 'A summary of the scope or deliverables defined in the contract',
    GoverningLaw VARCHAR(100) COMMENT 'The legal jurisdiction governing the contract',
    TerminationClause TEXT COMMENT 'Key details about the termination conditions outlined in the contract',
    ConfidentialityClause BOOLEAN COMMENT 'Indicates whether a confidentiality clause is included in the contract',
    ParentContractID INT COMMENT 'The ID of the original contract if this is an amendment or addendum',
    AmendmentNumber INT COMMENT 'The sequential number of the amendment or addendum to the contract',
    Notes TEXT COMMENT 'Any additional notes or comments about the contract',
    Metadata JSON COMMENT 'A JSON column to store unstructured or custom data extracted from the contract',
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Timestamp for when the record was created',
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last updated timestamp'
);

```

### Column Descriptions

When leveraging NL2SQL it's very important to have column descriptions for the schema so when you dynamically extract the Schema from SQL, you alos have the descriptions for the columns, as this helps the LLM with generation of the SQL Query.

| **Column Name**         | **Description**                                                                 |
|--------------------------|--------------------------------------------------------------------------------|
| **ContractID**           | Unique identifier for each contract.                                           |
| **VendorName**           | Name of the vendor or contractor involved in the agreement.                    |
| **ClientName**           | Name of the client or contracting entity.                                      |
| **ContractTitle**        | A brief title describing the contract (e.g., "Service Agreement").             |
| **ContractType**         | The category or type of contract (e.g., NDA, SLA, Service Agreement).          |
| **EffectiveDate**        | The date when the contract becomes effective.                                  |
| **EndDate**              | The expiration or termination date of the contract, if applicable.             |
| **SigningDate**          | The date on which the contract was signed by all parties.                      |
| **Status**               | Current status of the contract (e.g., Active, Draft, Terminated).              |
| **Compensation**         | The total financial value of the contract.                                     |
| **PaymentTerms**         | Payment terms, including frequency or milestones (e.g., "Net 30 days").        |
| **Currency**             | The currency used in the financial details (e.g., USD, EUR).                   |
| **ScopeOfWork**          | A summary of the scope or deliverables defined in the contract.                |
| **GoverningLaw**         | The legal jurisdiction governing the contract.                                 |
| **TerminationClause**    | Key details about the termination conditions outlined in the contract.         |
| **ConfidentialityClause**| Indicates whether a confidentiality clause is included in the contract.        |
| **ParentContractID**     | The ID of the original contract if this is an amendment or addendum.           |
| **AmendmentNumber**      | The sequential number of the amendment or addendum to the contract.            |
| **Notes**                | Any additional notes or comments about the contract.                           |
| **Metadata**             | A JSON column to store unstructured or custom data extracted from the contract.|

### Add column descriptions to table
The below script will iterate over the columns 

```
DECLARE @tableName NVARCHAR(255) = 'Contracts';
DECLARE @columnName NVARCHAR(255);
DECLARE @columnDescription NVARCHAR(255);

-- Cursor to iterate over each column in the table
DECLARE column_cursor CURSOR FOR
SELECT c.name, ep.value
FROM sys.columns c
JOIN sys.extended_properties ep ON ep.major_id = c.object_id AND ep.minor_id = c.column_id
WHERE c.object_id = OBJECT_ID(@tableName) AND ep.name = 'MS_Description';

OPEN column_cursor;
FETCH NEXT FROM column_cursor INTO @columnName, @columnDescription;

-- Loop through each column and add description (if missing)
WHILE @@FETCH_STATUS = 0
BEGIN
    IF @columnDescription IS NULL
    BEGIN
        EXEC sp_addextendedproperty 
            @name = N'MS_Description',
            @value = 'Description for column ' + @columnName,
            @level0type = N'Schema', @level0name = N'dbo', 
            @level1type = N'Table', @level1name = @tableName, 
            @level2type = N'Column', @level2name = @columnName;
    END

    FETCH NEXT FROM column_cursor INTO @columnName, @columnDescription;
END

CLOSE column_cursor;
DEALLOCATE column_cursor;
