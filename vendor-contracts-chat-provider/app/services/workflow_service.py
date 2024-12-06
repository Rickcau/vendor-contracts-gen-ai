from langgraph.graph import StateGraph, END
from app.core.models import GraphState
from app.services.research_service import researcher_node, reviewer_node, supervisor_node

def create_workflow():
    workflow = StateGraph(GraphState)
    
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("reviewer", reviewer_node)
    
    workflow.set_entry_point("supervisor")
    workflow.add_edge("supervisor", "researcher")
    workflow.add_edge("researcher", "reviewer")
    
    workflow.add_conditional_edges(
        "reviewer",
        is_finished,
        {True: END, False: "researcher"}
    )
    
    return workflow.compile()

def is_finished(state: GraphState) -> bool:
    return state["attempt_count"] >= 2 or not state.get("additional_research_requested")