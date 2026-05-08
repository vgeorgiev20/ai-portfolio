import os
from typing import Optional
from openai import AsyncOpenAI
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from router import route, RoutingDecision

load_dotenv()

app = FastAPI(title="12-model-routing")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class ChatRequest(BaseModel):
    message: str
    force_model: Optional[str] = None  # "fast" | "smart" | None


class ChatResponse(BaseModel):
    reply: str
    routing: RoutingDecision  # expose routing decision to frontend


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    # ── Route ─────────────────────────────────────────────────────────────────
    decision = route(request.message, request.force_model)


    # ── Call selected model ───────────────────────────────────────────────────
    try:
        completion = await client.chat.completions.create(
            model=decision.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": request.message},
            ],
            temperature=0.7,
        )
        reply = completion.choices[0].message.content or ""
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return ChatResponse(reply=reply, routing=decision)


@app.post("/route-only", response_model=RoutingDecision)
async def route_only(request: ChatRequest):
    """
    Dry-run endpoint — returns routing decision without calling the LLM.
    Useful for testing routing logic without spending credits.
    """
    return route(request.message, request.force_model)


@app.get("/health")
def health():
    return {"status": "ok", "feature": "12-model-routing"}