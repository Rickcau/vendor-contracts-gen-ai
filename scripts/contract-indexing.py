from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SimpleField,
    SearchFieldDataType,
    SearchableField,
    SearchField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SemanticConfiguration,
    SemanticPrioritizedFields,
    SemanticField,
    SemanticSearch,
    SearchIndex
)
from datetime import datetime, timezone
import json
import hashlib
from typing import Any
#import lib for pypdf2


from azure.core.credentials import AzureKeyCredential  
from azure.search.documents import SearchClient  
from datetime import datetime
import os  
from dotenv import load_dotenv  
from azure.core.credentials import AzureKeyCredential  

from openai import AzureOpenAI  
import os
from langchain_openai import AzureChatOpenAI
import itertools

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult

from azure.core.credentials import AzureKeyCredential

import tiktoken
from dotenv import load_dotenv 
import requests

from pathlib import Path

# Get root directory path
root_dir = Path().absolute().parent
env_path = root_dir / '.env'

# Load .env from root
load_dotenv(dotenv_path=env_path)
print(f"Loaded .env from {env_path}")
# Access variables
aoai_key = os.getenv('AZURE_OPENAI_API_KEY')

print(f"API Key: {  api_key[:4] + '*' * 28 + api_key[-4:] }")

connect_str = os.getenv("STORAGE_ACCOUNT_CONNECTION_STRING")
container_name = "vendor-contracts"
storage_account_name = os.getenv("STORAGE_ACCOUNT_NAME")

form_recognizer_endpoint = os.getenv("FORM_RECOGNIZER_ENDPOINT")
form_recognizer_key = os.getenv("FORM_RECOGNIZER_KEY")

ai_search_endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
ai_search_key = os.environ["AZURE_SEARCH_KEY"]
ai_search_index = os.environ["AZURE_SEARCH_INDEX"]

# Azure OpenAI
aoai_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
aoai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

endpoint = form_recognizer_endpoint

print(f"STORAGE_ACCOUNT_CONNECTION_STRING: {  connect_str[:4] + '*' * 28 + connect_str[-4:] }")
print(f"Container Name: {  container_name }")
print(f"STORAGE_ACCOUNT_NAME: {  storage_account_name }")
print(f"FORM_RECOGNIZER_ENDPOINT: {  form_recognizer_endpoint }")
print(f"FORM_RECOGNIZER_KEY: {  form_recognizer_key[:4] + '*' * 28 + form_recognizer_key[-4:] }")
print(f"AZURE_SEARCH_ENDPOINT: {  ai_search_endpoint }")
print(f"AZURE_SEARCH_KEY: {  ai_search_key[:4] + '*' * 28 + ai_search_key[-4:] }")
print(f"AZURE_SEARCH_INDEX: {  ai_search_index }")
print(f"AZURE_OPENAI_DEPLOYMENT_NAME: {  aoai_deployment }")
print(f"AZURE_OPENAI_ENDPOINT: {  aoai_endpoint }")

credential = AzureKeyCredential(form_recognizer_key)
document_intelligence_client = DocumentIntelligenceClient(endpoint, credential)

search_index_client = SearchIndexClient(ai_search_endpoint, AzureKeyCredential(ai_search_key))
search_client = SearchClient(ai_search_endpoint, ai_search_index, AzureKeyCredential(ai_search_key))

aoai_client = AzureOpenAI(
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
        api_key=os.getenv("AZURE_OPENAI_KEY"),  
        api_version="2023-05-15"
        )

primary_llm = AzureChatOpenAI(
    azure_deployment=aoai_deployment,
    api_version="2024-05-01-preview",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=aoai_key,
    azure_endpoint=aoai_endpoint
)

primary_llm_json = AzureChatOpenAI(
    azure_deployment=aoai_deployment,
    api_version="2024-05-01-preview",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=aoai_key,
    azure_endpoint=aoai_endpoint,
    model_kwargs={"response_format": {"type": "json_object"}}
)

contract_indexing_prompt = """You are an AI assistant. Your job is to read the input contract, 
and output certain info in valid JSON format. Here is what you should be extracting:

1. experienceLevel - either entry, mid, or senior
2. jobTitle - the title of the job the resume is for
3. skills_and_experience - a succinct list of 3-5 top skills and experiences.   


#Examples#

User: Steve Smith
CAREER SUMMARY
Resourceful and detail-oriented general contractor with 5+ years of experience recruiting and coordinating labor across construction sites.
Adept at obtaining permits, inspecting sites, ensuring building code compliance, offering cost estimates, and employing skilled labor.
Articulate communicator and effective negotiator with the ability to foster strong relationships with organizational management, key clients, vendors, and team members.
PROFESSIONAL EXPERIENCE
March 2020 - Present | Precision Pro 5, New York, NY
General Contractor
· Manage various construction projects with budgets of up to $5M each
· Train subcontractors on company standards and protocols
· Attained high client satisfaction by optimizing project efficiency and ensuring timely completion
· Achieved annual cost control targets in 2020 and 2021 through strategic planning and execution
June 2017 - March 2020 | YPC, New York, NY
General Contractor
· Performed pre-construction inspections and managed post-
construction audits for 3+ projects per year
· Streamlined project-related functions by developing schedules,
overseeing quality control, and ensuring within-budget project
completion
· Reported progress and project modifications to superintendents
and clients
· Supervised team of 6 subcontractors to resolve complex issues
and prevent unnecessary delays
(917) 828-9045
eloise.plaza@email.com
in
linkedin.com/in/eloise-plaza/
EDUCATION
Bachelor of Science in
Construction Management
Honors: cum laude (3.6/4.0)
Columbia University,
New York, NY
May 2017
SKILLS
Cost reduction & elimination
Project estimation
Residential construction
House renovation & remodeling
Subcontractor management
Workforce planning & scheduling
Complex problem-solving
Contract negotiation
Microsoft Office
Google Suite


Assistant: {'experienceLevel': 'mid', 'jobTitle': 'General Contractor', 'skills_and_experience': ['Cost reduction & elimination', 'Project estimation', 'Subcontractor management', 'Workforce planning & scheduling', 'Contract negotiation']}

"""

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

def generate_embeddings(text, model="text-embedding-ada-002"): # model = "deployment_name"
    return aoai_client.embeddings.create(input = [text], model=model).data[0].embedding    

def read_pdf(input_file):
    blob_url = f"https://{storage_account_name}.blob.core.windows.net/{container_name}/{input_file}"
    analyze_request = {
        "urlSource": blob_url
    }
    poller = document_intelligence_client.begin_analyze_document("prebuilt-layout", analyze_request=analyze_request)
    result: AnalyzeResult = poller.result()
    #print(result.content)
    
    #read result object into a full text variable
    full_text = result.content
    print("Successfully read the PDF from blob storage with doc intelligence and extracted text.")
    
    return full_text

# RDC: We may or may not need this function, if we do the prompt will need to be changed
def llm_extraction(full_text):

    messages = [{"role": "system", "content": contract_indexing_prompt}]
    messages.append({"role": "user", "content": full_text})

    response = primary_llm_json.invoke(messages)
    extraction_json = json.loads(response.content)


    return extraction_json

from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import uuid

def generate_document_id(blob_name):
    """Generate a unique, deterministic ID for a document."""
    unique_string = f"{blob_name}"  # Use first 100 characters of content for uniqueness
    return hashlib.md5(unique_string.encode()).hexdigest()

def list_blobs_in_folder(container_client, folder_name):
    return [blob for blob in container_client.list_blobs() if blob.name.startswith(folder_name)]

def move_blob(source_container_client, destination_container_client, source_blob_name, destination_blob_name):
    source_blob = source_container_client.get_blob_client(source_blob_name)
    destination_blob = destination_container_client.get_blob_client(destination_blob_name)
    
    destination_blob.start_copy_from_url(source_blob.url)
    source_blob.delete_blob()

def populate_index():
    print("Populating index...")
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    container_client = blob_service_client.get_container_client(container_name)
    
    stage_blobs = list_blobs_in_folder(container_client, "source/")
    print(f"Found {len(stage_blobs)} blobs in the 'source' folder")
    
    for blob in stage_blobs:
        print(f"Processing {blob.name}")
        print(blob.name)
        
        try:
            full_text = read_pdf(blob.name)
            extraction_json = llm_extraction(full_text)

            experienceLevel = extraction_json["experienceLevel"]
            jobTitle = extraction_json["jobTitle"]
            skills_and_experience = extraction_json["skills_and_experience"]
            skills_and_experience_str = ", ".join(skills_and_experience)
            searchVector = generate_embeddings(skills_and_experience_str)
            current_date = datetime.now(timezone.utc).isoformat()
            document_id = generate_document_id(blob.name)
            fileName = os.path.basename(blob.name)
            print(f"Extracted experience level: {experienceLevel}")
            print(f"Extracted job title: {jobTitle}")
            print(f"Extracted skills and experience: {skills_and_experience_str}")
            print(f"Current date: {current_date}")
            
            document = {
                "id": document_id,
                "date": current_date,
                "jobTitle": jobTitle,
                "experienceLevel": experienceLevel,
                "content": full_text,
                "sourceFileName": fileName,
                "searchVector": searchVector
            }
            
            search_client.upload_documents(documents=[document])
            
            # Move the processed file to the 'processed' folder
            destination_blob_name = blob.name.replace("source/", "processed/")
            move_blob(container_client, container_client, blob.name, destination_blob_name)
            
            print(f"Successfully processed and moved {blob.name}")
        
        except Exception as e:
            print(f"Error processing {blob.name}: {str(e)}")
