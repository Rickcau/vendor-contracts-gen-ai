# Scripts used for Indexing etc.

## Resume-Indexing.py
This Python file has examples that we will make use for for this solution.

## Indexing Notes
In speaking to our Azure AI Search it's best to not empower the users to add documents to the index, this should be in total control of the developers.

### Developer Team in control of the indexing
- Either one or more Blob Containers can be leveraged
- Indexing will occur on a schedule or via manual invoke (only by the Dev Team)

#### Why this approach?
Because when users are allowed to update documents for indexing you aer likely to experience issues.  With the Dev Team in control of this you can ensure that the data being indexing is proper for the solution.

#### The indexing concept
- Devs are in total control of what will and when will the documents be indexed
- This appraoch ensures the solution is providing a quality index and user experience
