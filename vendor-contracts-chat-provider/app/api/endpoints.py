from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from uuid import UUID
from app.services.agent_service import process_research_request

router = APIRouter()

class ResearchRequest(BaseModel):
    session_id: UUID
    user_prompt: str

@router.post("/research")
async def research(request: ResearchRequest):
    try:
        response = process_research_request(
            str(request.session_id),
            request.user_prompt
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))