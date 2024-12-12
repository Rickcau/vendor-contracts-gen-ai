import base64
import json
import hashlib
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from dotenv import load_dotenv

from langchain_openai import AzureChatOpenAI
from azure.search.documents import SearchClient
from openai import AzureOpenAI


class DataIngestion:
    def __init__(self):
        # Get root directory path
        root_dir = Path().absolute().parent
        env_path = root_dir / '.env'

        # Load .env from root
        load_dotenv(dotenv_path=env_path)
        print(f"Loaded .env from {env_path}")

        # Access environment variables
        self.ai_search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        self.ai_search_key = os.getenv("AZURE_SEARCH_KEY")
        self.ai_search_admin_key = os.getenv("AZURE_SEARCH_ADMIN_KEY")
        self.ai_search_index = "rdc-contracts-v1"

        # Azure Document Intelligence settings
        self.form_recognizer_endpoint = os.getenv('FORM_RECOGNIZER_ENDPOINT')
        self.form_recognizer_key = os.getenv('FORM_RECOGNIZER_KEY')

        # Azure Storage settings
        self.storage_account_connection_string = os.getenv('STORAGE_ACCOUNT_CONNECTION_STRING')
        self.storage_account_name = os.getenv('STORAGE_ACCOUNT_NAME')
        self.storage_account_key = os.getenv('STORAGE_ACCOUNT_KEY')
        self.container_name = "source"

        # Azure OpenAI settings
        self.aoai_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        self.aoai_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.aoai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

        # Initialize Azure OpenAI clients
        self.aoai_client = AzureOpenAI(
            azure_endpoint=self.aoai_endpoint,
            api_key=self.aoai_key,
            api_version="2023-05-15"
        )

        self.primary_llm = AzureChatOpenAI(
            azure_deployment=self.aoai_deployment,
            api_version="2024-05-01-preview",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            api_key=self.aoai_key,
            azure_endpoint=self.aoai_endpoint
        )

        self.primary_llm_json = AzureChatOpenAI(
            azure_deployment=self.aoai_deployment,
            api_version="2024-05-01-preview",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            api_key=self.aoai_key,
            azure_endpoint=self.aoai_endpoint,
            model_kwargs={"response_format": {"type": "json_object"}}
        )

        # Initialize Azure Search client
        self.search_client = SearchClient(
            self.ai_search_endpoint,
            self.ai_search_index,
            AzureKeyCredential(self.ai_search_admin_key)
        )

        # Define the contract extraction prompt with examples
        self.contract_extraction_prompt = """You are an AI assistant. Your job is to read the input contract, 
and output certain info in valid JSON format. Here is what you should be extracting:
1. id - unique identifier for the document
2. contractId - unique identifier for the contract
3. vendorName - name of the vendor/supplier/contractor
4. clientName - name of the client/customer
5. contractTitle - title of the contract document
6. effectiveDate - when the contract becomes effective
7. endDate - when the contract expires
8. signingDate - when the contract was signed
9. status - current status of the contract (e.g., Active, Expired, Pending)
10. compensation - monetary value of the contract
11. terminationTerms - terms of termination
12. paymentTerms - terms of payment
13. currency - currency used in the contract
14. parentContractId - ID of the parent contract (if this is an amendment)
15. amendmentNumber - amendment number (if applicable) make sure it's converted to a string
16. sourceFileName - name of the source file

#Examples#
User: MASTER SERVICES AGREEMENT
This Master Services Agreement (the "Agreement") is made effective as of January 15, 2024 (the "Effective Date"), by and between:
TechCorp Solutions Inc. ("Vendor")
123 Tech Lane
Silicon Valley, CA 94025
and
Global Enterprise Ltd. ("Client")
456 Business Park
New York, NY 10001
Contract ID: MSA-2024-001
1. SERVICES
The Vendor agrees to provide software development services as outlined in Exhibit A.
2. TERM
This Agreement shall commence on the Effective Date and continue for a period of 24 months, ending on January 15, 2026.
3. COMPENSATION
Client agrees to pay Vendor a total of $250,000 USD for the services rendered.
4. PAYMENT TERMS
Payment shall be made in monthly installments of $10,416.67, due within 30 days of invoice date.
Signed and executed on: January 10, 2024
Status: Active
File: MSA_TechCorp_Global_2024.pdf

Assistant: {
'id': 'DOC-20240115-001',
'contractId': 'MSA-2024-001',
'vendorName': 'TechCorp Solutions Inc.',
'clientName': 'Global Enterprise Ltd.',
'contractTitle': 'Master Services Agreement',
'effectiveDate': '2024-01-15',
'endDate': '2026-01-15',
'signingDate': '2024-01-10',
'status': 'Active',
'compensation': 250000,
'terminationTerms': 'This Agreement shall commence on the Effective Date and continue for a period of 24 months, ending on January 15, 2026',
'paymentTerms': 'Payment shall be made in monthly installments of $10,416.67, due within 30 days of invoice date',
'currency': 'USD',
'parentContractId': null,
'amendmentNumber': null,
'sourceFileName': 'MSA_TechCorp_Global_2024.pdf'
}
"""

    def llm_extraction(self, full_text):
        """
        Extract contract information using the LLM model
        """
        messages = [{"role": "system", "content": self.contract_extraction_prompt}]
        messages.append({"role": "user", "content": full_text})

        response = self.primary_llm_json.invoke(messages)
        extraction_json = json.loads(response.content)

        return extraction_json

    def generate_sas_url(self, blob_name: str) -> str:
        """
        Generate a full URL with SAS token for a specific blob
        """
        sas_permissions = BlobSasPermissions(read=True)
        expiry_time = datetime.now(timezone.utc) + timedelta(hours=1)

        sas_token = generate_blob_sas(
            account_name=self.storage_account_name,
            account_key=self.storage_account_key,
            container_name=self.container_name,
            blob_name=blob_name,
            permission=sas_permissions,
            expiry=expiry_time
        )

        blob_url = f"https://{self.storage_account_name}.blob.core.windows.net/{self.container_name}/{blob_name}?{sas_token}"
        return blob_url

    def read_pdf(self, input_file: str) -> str:
        """
        Read and analyze a PDF file using Azure Document Intelligence.
        """
        try:
            document_url = self.generate_sas_url(input_file)
            print(f"Starting document analysis for {input_file}...")

            credential = AzureKeyCredential(self.form_recognizer_key)
            doc_intelligence_client = DocumentIntelligenceClient(self.form_recognizer_endpoint, credential)

            poller = doc_intelligence_client.begin_analyze_document(
                model_id="prebuilt-read",
                analyze_request={"urlSource": document_url}
            )

            result = poller.result()
            print(f"Successfully analyzed document: {input_file}")
            return result.content

        except Exception as e:
            print(f"Error analyzing document {input_file}: {str(e)}")
            raise

    def generate_embeddings(self, text, model="text-embedding-ada-002"):
        """Generate embeddings for the input text using the specified model."""
        return self.aoai_client.embeddings.create(input=[text], model=model).data[0].embedding

    def generate_document_id(self, blob_name):
        """Generate a unique, deterministic ID for a document."""
        unique_string = f"{blob_name}"
        return hashlib.md5(unique_string.encode()).hexdigest()

    def populate_index(self, file_name: str):
        """
        Ingest a single file into the Azure Search index.
        """
        print(f"Populating index with file: {file_name}")

        try:
            full_text = self.read_pdf(file_name)
            extraction_json = self.llm_extraction(full_text)

            document_id = self.generate_document_id(file_name)
            contract_id = extraction_json.get("contractId")
            vendor_name = extraction_json.get("vendorName")
            client_name = extraction_json.get("clientName")
            contract_title = extraction_json.get("contractTitle")
            effective_date = extraction_json.get("effectiveDate")
            end_date = extraction_json.get("endDate")
            signing_date = extraction_json.get("signingDate")
            status = extraction_json.get("status")
            compensation = extraction_json.get("compensation")
            termination_terms = extraction_json.get("terminationTerms")
            parent_contract_id = extraction_json.get("parentContractId")
            amendment_number = extraction_json.get("amendmentNumber")
            creation_date = datetime.now(timezone.utc)
            content = full_text
            vendor_name_vector = self.generate_embeddings(vendor_name)
            source_file_name = os.path.basename(file_name)

            print(f"Extracted contract ID: {contract_id}")
            print(f"Extracted vendor name: {vendor_name}")
            print(f"Extracted client name: {client_name}")
            print(f"Extracted contract title: {contract_title}")
            print(f"Extracted effective date: {effective_date}")
            print(f"Extracted end date: {end_date}")
            print(f"Extracted signing date: {signing_date}")
            print(f"Status: {status}")
            print(f"Extracted compensation: {compensation}")
            print(f"Termination Terms: {termination_terms}")
            print(f"Extracted parent contract ID: {parent_contract_id}")
            print(f"Extracted amendment number: {amendment_number}")
            print(f"Extracted creation date: {creation_date}")
            print(f"Extracted source file name: {source_file_name}")

            document = {
                "id": document_id,
                "contractId": contract_id,
                "vendorName": vendor_name,
                "clientName": client_name,
                "contractTitle": contract_title,
                "effectiveDate": effective_date,
                "endDate": end_date,
                "signingDate": signing_date,
                "status": status,
                "compensation": compensation,
                "terminationTerms": termination_terms,
                "parentContractId": parent_contract_id,
                "amendmentNumber": amendment_number,
                "creationDate": creation_date.isoformat(),
                "sourceFileName": source_file_name,
                "content": content,
                "vendorNameVector": vendor_name_vector
            }

            # Upload the document to Azure Search
            self.search_client.upload_documents(documents=[document])
            print(f"Successfully processed and indexed {file_name}")

        except Exception as e:
            print(f"Error processing {file_name}: {str(e)}")


# Example usage
if __name__ == "__main__":
    try:
        ingestion = DataIngestion()
        file_to_ingest = "Vertex-Dynamics-VendorAmendment-8003341-A1.pdf"
        ingestion.populate_index(file_to_ingest)
        print("\nData ingestion completed successfully.")
    except Exception as e:
        print(f"Failed to ingest data: {str(e)}")
