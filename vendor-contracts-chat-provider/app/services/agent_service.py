from app.services.workflow_service import create_workflow
from app.utils.tools import perform_research, review_research
from typing import Dict

def process_research_request(session_id: str, user_prompt: str) -> str:
    workflow = create_workflow()
    
    initial_state = {
        "user_input": user_prompt,
        "research": "",
        "additional_research_requested": False,
        "attempt_count": 0,
        "messages": [{"role": "user", "content": user_prompt}]
    }
    
    try:
        output = workflow.invoke(initial_state)
        messages = output.get("messages", [])
        research_count = len([msg for msg in messages if msg["role"] == "researcher"])
        
        return _format_response(messages, research_count)
    except Exception as e:
        raise Exception(f"Research processing error: {str(e)}")

def _format_response(messages: list, research_count: int) -> str:
    response = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
    return f"{response}\nResearch was performed {research_count} time(s)."