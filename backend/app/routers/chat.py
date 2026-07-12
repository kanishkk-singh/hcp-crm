from fastapi import APIRouter
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from app.schemas import ChatMessage, ChatResponse
from app.agent.graph import agent_executor

router = APIRouter(prefix="/api/chat", tags=["Chat"])

# naive in-memory per-hcp session store, fine for a demo/assignment
_sessions: dict[str, list] = {}


@router.post("/", response_model=ChatResponse)
def chat(payload: ChatMessage):
    session_key = payload.hcp_id or "default"
    history = _sessions.get(session_key, [])

    context_prefix = ""
    if payload.hcp_id:
        context_prefix += f"[Context: hcp_id={payload.hcp_id}] "
    if payload.interaction_id:
        context_prefix += f"[Context: interaction_id={payload.interaction_id}] "

    history.append(HumanMessage(content=context_prefix + payload.message))

    result = agent_executor.invoke({"messages": history})
    messages = result["messages"]
    _sessions[session_key] = messages

    # find the last AI text reply and any tool call that ran
    reply_text = ""
    tool_used = None
    for m in reversed(messages):
        if isinstance(m, AIMessage) and m.content:
            reply_text = m.content
            break

    for m in messages:
        if isinstance(m, ToolMessage):
            tool_used = m.name

    return ChatResponse(reply=reply_text or "Done.", tool_used=tool_used)
