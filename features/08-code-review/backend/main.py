import os
from openai import AsyncOpenAI
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

from reviewer import review_code, CodeReviewResult

load_dotenv()

app = FastAPI(title="08-code-review")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class ReviewRequest(BaseModel):
    code: str
    context: Optional[str] = None  # optional: what is this code supposed to do?


@app.post("/review", response_model=CodeReviewResult)
async def review(request: ReviewRequest):
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty.")

    if len(request.code) > 10000:
        raise HTTPException(status_code=400, detail="Code exceeds maximum length of 10,000 characters.")

    try:
        result = await review_code(request.code, request.context, client)
        return result
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Review failed: {str(e)}")


@app.get("/health")
def health():
    return {"status": "ok", "feature": "08-code-review"}