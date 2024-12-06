from typing import Dict
from app.utils.tools import perform_research, review_research
from app.core.models import GraphState

def researcher_node(state: GraphState) -> Dict:
    research_result = perform_research(state["user_input"])
    return {
        **state,
        "research": research_result,
        "attempt_count": state["attempt_count"] + 1,
        "messages": state["messages"] + [{"role": "researcher", "content": research_result}]
    }

def reviewer_node(state: GraphState) -> Dict:
    review_result = review_research(state["research"])
    needs_more = "more" in review_result.lower()
    return {
        **state,
        "additional_research_requested": needs_more,
        "messages": state["messages"] + [{"role": "reviewer", "content": review_result}]
    }

def supervisor_node(state: GraphState) -> Dict:
    return {
        **state,
        "messages": state["messages"] + [
            {"role": "supervisor", "content": f"Initiating research for: {state['user_input']}"}
        ]
    }