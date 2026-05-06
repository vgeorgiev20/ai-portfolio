import os
import instructor
from openai import AsyncOpenAI
from schemas import (
    SchemaType,
    LegalContractExtraction,
    InvoiceExtraction,
    ResumeExtraction,
)

MODEL = "gpt-4o-mini"

SYSTEM_PROMPTS = {
    SchemaType.legal_contract: (
        "You are a legal document analyst. Extract structured information precisely from the "
        "provided contract or legal document text. Be conservative — if a field is not clearly "
        "stated in the document, return null. Do not infer or assume values not present in the text."
    ),
    SchemaType.invoice: (
        "You are an accounts processing assistant. Extract billing information exactly as written. "
        "Preserve currency symbols in all monetary values. Return null for any fields not present."
    ),
    SchemaType.resume: (
        "You are an HR data extraction specialist. Extract candidate information accurately "
        "from this resume or CV. Be precise with dates, job titles, and company names."
    ),
}

RESPONSE_MODELS = {
    SchemaType.legal_contract: LegalContractExtraction,
    SchemaType.invoice: InvoiceExtraction,
    SchemaType.resume: ResumeExtraction,
}


async def extract(schema_type: SchemaType, text: str):
    client = instructor.from_openai(AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY")))
    response_model = RESPONSE_MODELS[schema_type]
    system_prompt = SYSTEM_PROMPTS[schema_type]

    result = await client.chat.completions.create(
        model=MODEL,
        response_model=response_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Extract structured data from the following text:\n\n{text}"},
        ],
    )

    return result