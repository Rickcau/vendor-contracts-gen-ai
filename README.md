# Vendor Contracts GenAI Solution

## Licensing

This project uses a dual license model:

- **Commercial License**: Required for Azure-hosted production deployments
- **MIT License**: Applies to open source use cases

See [LICENSE.md](LICENSE.md) for details.

## Introduction

The goal of this solution is to develop an advanced Retrieval-Augmented Generation (RAG) ChatBot designed to assist users in accessing vendor contract information.  This ChatBot will identify and retrieve the specific contracts and amendments relevant to the user's query.  By focusing on pertinent documents, the ChatBot will provide precise answers based on the content of these documents.

By simplifying access to the contract details, amendments and specific clauses, this tool aims to streamline the contract management and enhance user experience.  Users will receive quick, actionable information presented in a user-friendly format, making the retrieval process more efficient and intuitive.

## Setup

### Python version

Please ensure you're using Python 3.11 or later. 
This version is required for optimal compatibility with LangGraph. If you're on an older version, 
upgrading will ensure everything runs smoothly.

Open a terminal window in VS Code and run the following command

```
python --version
```

### Clone repo
    ```
        git clone https://github.com/rickcau/vendor-contracts-gen-ai.git
        $ cd vendor-contracts-gen-ai
    ```

### Create an environment and install dependencies
#### From VS Code
Open a terminal window and run the following commands.

    ```
        python -m venv vendor-contracts-env
        .\vendor-contracts-env\Scripts\activate
        pip install -r requirements.txt
    ```

### Running notebooks
If you don't have Jupyter set up, install the Jupter extension in VS Code.  We will leverage notebooks to demo various examples.
=======

### Collect all your resouce details from Azure
* Naviagte to the Azure Portal and collect all the AI resource detatils for both AI Search and Azure OpenAI endpoints.

### Setting up .env variables
Briefly going over how to set up environment variables. You will find an example .env file in the root folder `env.example` you need to rename that file
to `.env` and make sure to see all the variables to point to your Azure Resources.

### Running notebooks
If you don't have Jupyter set up, install the Jupter extension in VS Code.  We will leverage notebooks to demo various examples.


