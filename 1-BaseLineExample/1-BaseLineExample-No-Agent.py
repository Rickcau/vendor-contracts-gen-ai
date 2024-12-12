from ast import Name
import os
import json
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
from pathlib import Path
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.tools import tool
from openai import AzureOpenAI 
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from pydantic import BaseModel

# Define the input schema for our tool
class MoreInfomationInput(BaseModel):
    contract_id: str
    client_name: str

def generate_embeddings(text, model="text-embedding-ada-002"): # model = "deployment_name"
    return aoai_client.embeddings.create(input = [text], model=model).data[0].embedding

def perform_azure_ai_search_vendors(query: str, filter: str = None) -> str:
    search_client = SearchClient(endpoint=search_endpoint, index_name=index_name, credential=AzureKeyCredential(search_key))
    query_vector = generate_embeddings(query)
    top = 3
    vector_query = VectorizedQuery(vector=query_vector, k_nearest_neighbors=top, fields="vendorNameVector", kind="vector")

    print(f"\nPerforming search for: {query} with filter: {filter}")

    # Build arguments for the search call
    search_args = {
        "search_text": query,
        "vector_queries": [vector_query],
        "select": [
            "id", "contractId", "vendorName", "clientName",
            "effectiveDate", "endDate", "signingDate", "status",
            "compensation", "terminationTerms", "parentContractId",
            "amendmentNumber", "sourceFileName"
        ],
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
            "sourceFileName": result.get('sourceFileName')
        }
        records.append(record)


    # vendor_names = [r.get("vendorName", "Unknown") for r in all_results]
    # return "\n".join(vendor_names)
    # Return as JSON string or just the list
    print (json.dumps(records, default=str, indent=2))
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

print(f"API Key: {  api_key[:4] + '*' * 28 + api_key[-4:] }")

# Create a message
system_prompt = """
You are an AI assistant tasked with answering questions about vendor contracts and their amendments. 
You have access to a memory of previously found contracts and amendments, and you can also use tools 
to look up new information. Your primary goals are:

1. When the user asks a question about a vendor contract, first try to recall from your memory if 
   you have the necessary contract details. Only if you lack sufficient information should you 
   consider invoking any external tools or performing additional research.

2. If the user's question involves a vendor for which multiple contracts are found and it’s not 
   clear which specific contract applies, ask clarifying questions to the user before proceeding. 
   Do not make assumptions. For example, if the user asks about "Vendor X" and you find multiple 
   contracts (Contract X1, Contract X2, etc.), prompt the user to specify which contract they are 
   referring to.

3. If one contract matches exactly and you have enough detail, provide the answer directly. If 
   details are missing, you may then use tools to perform further research.

4. If no contracts are found for the requested vendor, state that you have no record of a contract 
   with that vendor.

5. Always respond accurately and concisely. If asked about a specific detail (e.g., termination 
   terms, renewal date, data protection clauses), provide that detail if it’s available in memory. 
   If not available, conduct additional research by invoking the appropriate tool.

6. Maintain a helpful and professional tone, and be sure to guide the user through the process 
   of clarifying which contract they mean if multiple options are available.

Use these instructions for all subsequent user queries.
"""

user_query = "Do we have an active contract with Vendor Y"
system_msg = SystemMessage(content=system_prompt , name="System")
user_msg = HumanMessage(content=user_query, name="Rick")
# messages = [HumanMessage(content=f"Why is the Sky blue?",name="Rick"))
messages = []
messages.append(system_msg)
messages.append(user_msg)

# 1. Search for vendors and add the results to the messages
# Example filter: only return contracts where parentContractId and amendmentNumber are null
filter_expression = "parentContractId eq null"

results = perform_azure_ai_search_vendors(user_query, filter=filter_expression)
messages.append(HumanMessage(content=results, Name="VendorSearch"))

# 2. Give LLM the messages and get the response

llm = AzureChatOpenAI(model_name="gpt-4o")
result= llm.invoke(messages)
print(result)
type(result)


