import json
import uuid
from pydantic import BaseModel
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sse_starlette.sse import EventSourceResponse
from app.deps import get_session_id
from app.db.store import (
    db_get_key,
    db_get_document,
    db_ensure_conversation,
    db_get_messages,
    db_save_message
)
from app.security.crypto import decrypt_key
from app.llm.router import stream_llm_response, get_provider_for_model
from app.llm.tools import get_registered_tools, execute_tool_call

router = APIRouter()

class ChatPayload(BaseModel):
    conversation_id: Optional[str] = None
    message: str
    model: str = "gemini/gemini-1.5-flash"
    document_id: Optional[str] = None

@router.post("/chat")
def chat_endpoint(payload: ChatPayload, session_id: str = Depends(get_session_id)):
    conv_id = payload.conversation_id or str(uuid.uuid4())
    
    provider = get_provider_for_model(payload.model)
    user_api_key = None
    user_tavily_key = None
    
    enc_key = db_get_key(session_id, provider)
    if enc_key:
        try:
            user_api_key = decrypt_key(enc_key)
        except Exception:
            pass

    enc_tavily = db_get_key(session_id, "tavily")
    if enc_tavily:
        try:
            user_tavily_key = decrypt_key(enc_tavily)
        except Exception:
            pass

    db_ensure_conversation(conv_id, session_id)
    history = db_get_messages(conv_id, limit=20)

    system_prompt = ""
    if payload.document_id:
        doc = db_get_document(payload.document_id)
        if doc and doc.get("extracted_text"):
            system_prompt = f"Context Document Content:\n{doc['extracted_text']}\n"

    messages_payload = []
    if system_prompt:
        messages_payload.append({"role": "system", "content": system_prompt})

    for msg in history:
        messages_payload.append({"role": msg["role"], "content": msg["content"]})
    
    messages_payload.append({"role": "user", "content": payload.message})
    db_save_message(conv_id, "user", payload.message, payload.model)

    tools = get_registered_tools()

    def event_generator():
        full_response = []
        pending_tool_calls: Dict[int, Dict[str, Any]] = {}
        
        try:
            for chunk_data in stream_llm_response(messages_payload, payload.model, api_key=user_api_key, tools=tools):
                token = chunk_data.get("token", "")
                tool_calls = chunk_data.get("tool_calls")
                
                if token:
                    full_response.append(token)
                    yield {"data": json.dumps({"token": token, "conversation_id": conv_id})}
                
                if tool_calls:
                    for tc in tool_calls:
                        idx = getattr(tc, "index", 0)
                        if idx not in pending_tool_calls:
                            pending_tool_calls[idx] = {
                                "id": getattr(tc, "id", None) or str(uuid.uuid4()),
                                "name": "",
                                "arguments": ""
                            }
                        if getattr(tc, "function", None):
                            fn = tc.function
                            if getattr(fn, "name", None):
                                pending_tool_calls[idx]["name"] += fn.name
                            if getattr(fn, "arguments", None):
                                pending_tool_calls[idx]["arguments"] += fn.arguments

            if pending_tool_calls:
                tool_context = {"tavily_api_key": user_tavily_key}
                for idx, tc_data in pending_tool_calls.items():
                    tool_name = tc_data["name"]
                    yield {"data": json.dumps({"tool_used": tool_name, "conversation_id": conv_id})}
                    
                    try:
                        args = json.loads(tc_data["arguments"]) if tc_data["arguments"] else {}
                    except Exception:
                        args = {}
                    
                    tool_result = execute_tool_call(tool_name, args, context=tool_context)
                    
                    messages_payload.append({
                        "role": "assistant",
                        "tool_calls": [{
                            "id": tc_data["id"],
                            "type": "function",
                            "function": {"name": tool_name, "arguments": tc_data["arguments"]}
                        }]
                    })
                    messages_payload.append({
                        "role": "tool",
                        "tool_call_id": tc_data["id"],
                        "name": tool_name,
                        "content": tool_result
                    })

                for chunk_data in stream_llm_response(messages_payload, payload.model, api_key=user_api_key):
                    token = chunk_data.get("token", "")
                    if token:
                        full_response.append(token)
                        yield {"data": json.dumps({"token": token, "conversation_id": conv_id})}

        except Exception as e:
            yield {"data": json.dumps({"error": str(e), "conversation_id": conv_id})}

        assistant_content = "".join(full_response)
        if assistant_content:
            db_save_message(conv_id, "assistant", assistant_content, payload.model)

    return EventSourceResponse(event_generator())
