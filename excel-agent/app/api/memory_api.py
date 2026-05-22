from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/memory", tags=["memory"])


class MemoryResponse(BaseModel):
    session_id: str
    messages: list[dict]
    state: dict | None = None


class ClearResponse(BaseModel):
    session_id: str
    cleared: bool = True


@router.get("/{session_id}", response_model=MemoryResponse)
async def get_memory(session_id: str):
    from app.main import app

    memory = app.state.memory_manager
    messages = await memory.get_chat_history(session_id)
    state = await memory.get_agent_state(session_id)
    return MemoryResponse(session_id=session_id, messages=messages, state=state)


@router.delete("/{session_id}", response_model=ClearResponse)
async def clear_memory(session_id: str):
    from app.main import app

    memory = app.state.memory_manager
    await memory.clear_session(session_id)
    return ClearResponse(session_id=session_id)
