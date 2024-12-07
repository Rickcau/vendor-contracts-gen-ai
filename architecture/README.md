# Solution Architecture and Approach

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
