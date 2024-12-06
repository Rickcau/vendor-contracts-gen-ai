from langchain_core.tools import tool
from app.core.config import get_settings
from langchain_openai import AzureChatOpenAI

settings = get_settings()

# Mock research data for development/testing
MOCK_RESEARCH = "AI is having a significant impact on society, affecting various sectors."
MOCK_RESEARCH_DETAILED = """
AI is having a profound impact on society:
1. Healthcare: AI is improving diagnosis accuracy, drug discovery, and personalized treatment plans.
2. Education: AI-powered adaptive learning systems are tailoring education to individual needs.
3. Employment: While AI is automating some jobs, it's also creating new roles and industries.
4. Ethics and Privacy: The use of AI raises concerns about data privacy and ethical decision-making.
5. Economic Impact: AI is driving economic growth but also potentially widening wealth gaps.
"""

@tool
def perform_research(query: str) -> str:
    """Perform research based on the user's request."""
    # Initialize Azure OpenAI client
    client = AzureChatOpenAI(
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_key=settings.AZURE_OPENAI_API_KEY,
        api_version=settings.AZURE_OPENAI_API_VERSION
    )
    
    # TODO: Implement actual research logic using Azure OpenAI
    # For now, return mock data
    return MOCK_RESEARCH_DETAILED

@tool
def review_research(research: str) -> str:
    """Review the research results and determine if more details are needed."""
    if len(research) < 100:
        return "More detailed research needed."
    return f"Research review complete. Found comprehensive information: {research}"