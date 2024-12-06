def create_index():

   

    
    #Check if index exists, return if so
    try:
        # Try to get the index
        search_index_client.get_index(ai_search_index)
        # If no exception is raised, the index exists and we return
        print("Index already exists")
        return
    except:
        # If an exception is raised, the index does not exist and we continue with the logic to create it
        pass

    # Rest of your code...

    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True, filterable=True),
        SimpleField(name="date", type=SearchFieldDataType.DateTimeOffset, filterable=True, facetable=True),
        SimpleField(name="jobTitle", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SimpleField(name="experienceLevel", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SearchableField(name="sourceFileName", type=SearchFieldDataType.String, filterable=True),
        SearchField(name="searchVector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile")

    ]

    vector_search = VectorSearch(
    algorithms=[
        HnswAlgorithmConfiguration(
            name="myHnsw"
        )
    ],
    profiles=[
        VectorSearchProfile(
            name="myHnswProfile",
            algorithm_configuration_name="myHnsw",
        )
    ]
)
    index = SearchIndex(name=ai_search_index, fields=fields,
                    vector_search=vector_search)
    result = search_index_client.create_or_update_index(index)

    print("Index has been created")
