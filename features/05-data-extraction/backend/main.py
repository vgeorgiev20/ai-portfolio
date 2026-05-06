import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from schemas import SchemaType
import extractor

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY is not set. Add it to your .env file.")

app = FastAPI(title="05-data-extraction")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)



class ExtractionRequest(BaseModel):
    schema_type: SchemaType
    text: str


class ExtractionResponse(BaseModel):
    schema_type: str
    result: dict
    character_count: int


@app.get("/health")
def health():
    return {"status": "ok", "service": "05-data-extraction"}


@app.get("/api/schemas")
def get_schemas():
    return [
        {"value": "legal_contract", "label": "Legal Contract"},
        {"value": "invoice", "label": "Invoice"},
        {"value": "resume", "label": "Resume / CV"},
    ]


@app.options("/api/extract")
async def extract_options():
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "http://localhost:5173",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )


@app.post("/api/extract", response_model=ExtractionResponse)
async def extract(request: ExtractionRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    if len(request.text) > 8000:
        raise HTTPException(status_code=400, detail="Text exceeds 8000 character limit.")

    try:
        result = await extractor.extract(request.schema_type, request.text)
        return ExtractionResponse(
            schema_type=request.schema_type.value,
            result=result.model_dump(),
            character_count=len(request.text),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))