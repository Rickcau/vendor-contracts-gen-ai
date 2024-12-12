from ast import Name
import os
import json
from langchain_openai import AzureChatOpenAI
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
from pathlib import Path
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain.tools import tool
from openai import AzureOpenAI 
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from pkg_resources import vendor_path
from pydantic import BaseModel, Field


# Define the input schema for our tool
class MoreInfomationInput(BaseModel):
    contract_id: str
    client_name: str


# Define a Pydantic model for the input arguments
class GetAmendmentsInput(BaseModel):
    contract_id: str = Field(description="The ID of the contract to retrieve")
    client_name: str = Field(description="The client name for the contract to retrieve")
    vendor_name: str = Field(description="The vendor name for the contract to retrieve")
    verbose: bool = Field(default=False, description="Whether to print verbose output")

@tool(args_schema=GetAmendmentsInput)
def get_ammendments(contract_id: str, client_name: str, vendor_name: str, verbose: bool = False) -> str:
    """
    Retrieves more details about a contract for a given contract ID and client name.
    This tool is used when the AI needs more information to provide a complete answer.
    
    Args:
        contract_id: The ID of the contract to retrieve    
        client_name: The client name for the contract to retrieve
        vendor_name: The vendor name for the contract to retrieve
        verbose: Whether to print verbose output

    Returns:
        str: Returns a string with the details of the contract
    """
    filter_expression = f"parentContractId eq '{contract_id}' and clientName eq '{client_name}'" 
    
    print(f"\nPerforming amendment info search for: {contract_id} with filter: {filter_expression}")

    results = perform_azure_ai_search(vendor_name, filter=filter_expression, verbose=verbose)
    
    return results

# Define a Pydantic model for the input arguments
class VendorSearchInput(BaseModel):
    query: str = Field(description="The actual user query to search for")
    verbose: bool = Field(default=False, description="Whether to print verbose output")

@tool(args_schema=VendorSearchInput)
def vendor_search(query: str, verbose: bool = False) -> str:
    """
    Retrieves contract details for a vendor given a vendor name.
    This tool performs a hybrid semantic search to find the most relevant vendor contracts.
    
    Args:
        query: The actual user query to search for
        verbose: Whether to print verbose output

    Returns:
        str: Returns a string with the vendor details 
    """
    filter_expression = "parentContractId eq null"
    
    print(f"\nPerforming vendor search for: {query} with filter: {filter_expression}")
    results = perform_azure_ai_search(query, filter=filter_expression, verbose=verbose) 
    return results

def generate_embeddings(text, model="text-embedding-ada-002"): # model = "deployment_name"
    return aoai_client.embeddings.create(input = [text], model=model).data[0].embedding

def perform_azure_ai_search(query: str, filter: str = None, verbose: bool = False) -> str:
    search_client = SearchClient(endpoint=search_endpoint, index_name=index_name, credential=AzureKeyCredential(search_key))
    query_vector = generate_embeddings(query)
    top = 3
    vector_query = VectorizedQuery(vector=query_vector, k_nearest_neighbors=top, fields="vendorNameVector", kind="vector")

    # # Build arguments for the search call
    # search_args = {
    #     "search_text": query,
    #     "vector_queries": [vector_query],
    #     "select": [
    #         "id", "contractId", "vendorName", "clientName",
    #         "effectiveDate", "endDate", "signingDate", "status",
    #         "compensation", "terminationTerms", "parentContractId",
    #         "amendmentNumber", "sourceFileName" ,"content"
    #     ],
    # }
    
    # Build arguments for the search call
    search_args = {
        "search_text": query,
        "vector_queries": [vector_query],
        "select": [
            "id", "contractId", "vendorName", "clientName",
            "effectiveDate", "endDate", "signingDate", "status",
            "compensation", "terminationTerms", "parentContractId",
            "amendmentNumber", "sourceFileName", "content"
        ],
        "highlight_fields": "vendorName",
        "query_type": "semantic",  # Enable semantic search
        "semantic_configuration_name": "default"  # Must be set up in the search service
    }

    # Only add filter if it's provided
    if filter:
        search_args["filter"] = filter

    results = search_client.search(**search_args)
    
    all_results = list(results)
    if not all_results:
        return "No results found."

    # Construct a list of dictionaries with the desired fields
    records = []
    for result in all_results:
        record = {
            "id": result.get('id'),
            "contractId": result.get('contractId'),
            "vendorName": result.get('vendorName'),
            "clientName": result.get('clientName'),
            "effectiveDate": result.get('effectiveDate'),
            "endDate": result.get('endDate'),
            "signingDate": result.get('signingDate'),
            "status": result.get('status'),
            "compensation": result.get('compensation'),
            "terminationTerms": result.get('terminationTerms'),
            "parentContractId": result.get('parentContractId'),
            "amendmentNumber": result.get('amendmentNumber'),
            "sourceFileName": result.get('sourceFileName'),
            "content": result.get('content')
        }
        # Only add content if verbose is True
        if verbose and 'content' in result:
            record["content"] = result.get('content')
        records.append(record)
    return json.dumps(records, default=str, indent=2)


# Get root directory path
root_dir = Path().absolute().parent
env_path = root_dir / '.env'

# Load .env from root
load_dotenv(dotenv_path=env_path)
print(f"Loaded .env from {env_path}")
# Access variables
api_key = os.getenv('AZURE_OPENAI_API_KEY')

search_endpoint = os.getenv('AZURE_SEARCH_ENDPOINT')
search_key = os.getenv('AZURE_SEARCH_KEY')
index_name = os.getenv('AZURE_SEARCH_INDEX')

aoai_client = AzureOpenAI(
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
        api_key=os.getenv("AZURE_OPENAI_KEY"),  
        api_version="2023-05-15"
        )

# Initialize the Caht Completion model
model = AzureChatOpenAI(model_name="gpt-4o", temperature=0.5) # Example model initialization

print(f"API Key: {  api_key[:4] + '*' * 28 + api_key[-4:] }")

# Create a message
system_prompt = """
You are an AI assistant whose sole purpose is to answer questions related to vendor contracts and their amendments.  
If the user asks about anything not related to vendor contracts, politely inform them that you can only assist with vendor contract-related inquiries.

You have access to a memory of previously found contracts and amendments, and you can also use tools to look up new information. Your primary goals and guidelines are:

1. **Scope Limitation:**  
   - If the user’s query does not clearly relate to vendor contracts or their amendments, politely respond that you can only assist with vendor contract-related questions.

2. **Vendor Identification and Confirmation:**  
   - When the user asks a question involving a vendor, first check if you have a vendor in your memory that matches the user’s description.  
   - If multiple potential matches exist or if there is any ambiguity, list the vendor names that might be relevant and ask the user to confirm which one they mean before proceeding.  
   - Never assume that a vendor mentioned by the user refers to a different vendor without explicit confirmation. Do not provide any details until you are 100% certain which vendor and contract the user is asking about.

3. **Contract Amendments Handling:**  
   - If the user asks about contract amendments, use the `get_ammendments` tool to retrieve details, passing the appropriate `contract_id`.  
   - If the user requests a verbose explanation, set the verbose flag to `True` when calling the tool.

4. **No Assumptions Without Data:**  
   - If you lack sufficient information on a vendor or contract, ask clarifying questions before providing details.  
   - If the user’s question pertains to a vendor with multiple contracts and it’s unclear which specific contract they mean, ask for clarification. For example, if you find multiple matching contracts (e.g., “Contract X1” and “Contract X2” for “Vendor X”), prompt the user to specify which contract they are referring to before providing details.

5. **Single Exact Match:**  
   - If exactly one contract matches the request and sufficient detail is available in memory, answer directly.  
   - If details are insufficient, you may then invoke tools for further research.

6. **No Contract Found:**  
   - If no contracts are found for the requested vendor, inform the user that you have no record of a contract with that vendor.

7. **Accuracy and Detail-Specific Answers:**  
   - Always respond accurately and concisely.  
   - If asked about a specific contract detail (e.g., termination terms, renewal date, data protection clauses), provide that detail if available. If not available, use the appropriate tools to find it.

8. **Professional and Guiding Tone:**  
   - Maintain a helpful, professional, and polite tone.  
   - Guide the user through the clarification process if multiple vendor names or multiple contracts are available.

9. **Explanation of Reasoning:**  
   - Always include an explanation of how you arrived at your answer, ensuring transparency in the reasoning process.

Use these instructions for all subsequent user queries.
"""

# Add our custom tool to the tools list
tools = [vendor_search, get_ammendments]

# Define a dynamic system message
def state_modifier(state):
    return [
        SystemMessage(content=system_prompt),
        *state["messages"]
    ]
    
# Create the agent with the state modifier and tools
langgraph_agent_executor = create_react_agent(model, tools, state_modifier=state_modifier)

user_query = "Do we have an active contract with Vendor Y"
user_msg = HumanMessage(content=user_query, name="Rick")
# messages = [HumanMessage(content=f"Why is the Sky blue?",name="Rick"))

# Initialize an empty message list to maintain conversation history
messages = []

while True:
    try:
        # Get user input
        user_query = input("\nEnter your question (or 'quit' to exit): ")
        
        # Check for exit condition
        if user_query.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
            
        # Add the user message to the conversation history
        user_msg = HumanMessage(content=user_query, name="Rick")
        messages.append(user_msg)
        
        # Invoke the agent with the updated message history
        response = langgraph_agent_executor.invoke({
            "messages": messages
        })
        
        # Update the message history with the response
        messages = response['messages']
        
        # Print the agent's response
        print("\nAgent Response:")
        last_message = messages[-1]
        if isinstance(last_message, AIMessage):
            print(last_message.content)
        else:
            print("Unexpected message type:", type(last_message))
            
    except KeyboardInterrupt:
        print("\nExiting program...")
        break
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Continuing with next query...")
    


