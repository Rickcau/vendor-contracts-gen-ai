from typing import TypedDict, List, Dict

class GraphState(TypedDict):
    user_input: str
    research: str
    additional_research_requested: bool
    attempt_count: int
    messages: List[Dict[str, str]]