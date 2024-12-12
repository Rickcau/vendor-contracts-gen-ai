# Vendor Contracts Chat Provider

FastAPI service that processes user queries using a multi-agent research system.
### Python version

Please ensure you're using Python 3.11 or later. 
This version is required for optimal compatibility with LangGraph. If you're on an older version, 
upgrading will ensure everything runs smoothly.

Open a terminal window in VS Code and run the following command

```
python --version
```

```

## Setup

1. Clone repository
2. Create virtual environment:
```bash
python -m venv venv
.\venv\Scripts\activate   # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
- Copy `.env.template` to `.env`
- Update values in `.env` with your Azure OpenAI credentials

## Running the Service

```bash
uvicorn app.main:app --reload
```

Access API documentation: http://localhost:8000/docs

## API Endpoints

### POST /research
```json
{
    "session_id": "uuid-string",
    "user_prompt": "your research question"
}
```

## Project Structure

```
vendor-contracts-chat-provider/
├── app/
│   ├── api/          # API routes
│   ├── core/         # Core configurations
│   ├── services/     # Business logic
│   └── utils/        # Utility functions
└── requirements.txt
```

## Requirements

- Python 3.11+
- FastAPI
- Azure OpenAI access
- Azure AI Search
- See requirements.txt for full list