import os
from typing import Optional
from openai import AsyncOpenAI
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from database import init_db, get_pool, close_pool
from memory import (
    create_conversation,
    conversation_exists,
    save_message,
    load_history,
    get_conversation_summary,
    delete_conversation,
)

load_dotenv()

app = FastAPI(title="06-memory")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You are a helpful assistant with memory of the conversation.
You remember what was discussed earlier in this conversation and refer back to it when relevant.
Be concise and helpful."""


# ── Lifecycle ─────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup():
    await init_db()
    print("Database initialised.")


@app.on_event("shutdown")
async def shutdown():
    await close_pool()


# ── Request / Response Models ─────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None  # None = start new conversation


class ChatResponse(BaseModel):
    reply: str
    conversation_id: str  # always return so frontend can track it


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    pool = await get_pool()

    # ── Resolve conversation ──────────────────────────────────────────────────
    if request.conversation_id:
        if not await conversation_exists(pool, request.conversation_id):
            raise HTTPException(status_code=404, detail="Conversation not found.")
        conversation_id = request.conversation_id
    else:
        conversation_id = await create_conversation(pool)

    # ── Load history ──────────────────────────────────────────────────────────
    history = await load_history(pool, conversation_id)

    # ── Build messages for OpenAI ─────────────────────────────────────────────
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": request.message})

    # ── Save user message ─────────────────────────────────────────────────────
    await save_message(pool, conversation_id, "user", request.message)

    # ── Call OpenAI ───────────────────────────────────────────────────────────
    try:
        completion = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
        )
        reply = completion.choices[0].message.content or ""
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # ── Save assistant response ───────────────────────────────────────────────
    await save_message(pool, conversation_id, "assistant", reply)

    return ChatResponse(reply=reply, conversation_id=conversation_id)


@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    pool = await get_pool()
    if not await conversation_exists(pool, conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return await get_conversation_summary(pool, conversation_id)


@app.get("/conversations/{conversation_id}/history")
async def get_history(conversation_id: str):
    pool = await get_pool()
    if not await conversation_exists(pool, conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found.")
    history = await load_history(pool, conversation_id)
    return {"conversation_id": conversation_id, "messages": history}


@app.delete("/conversations/{conversation_id}")
async def remove_conversation(conversation_id: str):
    pool = await get_pool()
    deleted = await delete_conversation(pool, conversation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return {"deleted": True, "conversation_id": conversation_id}


@app.get("/health")
def health():
    return {"status": "ok", "feature": "06-memory"}