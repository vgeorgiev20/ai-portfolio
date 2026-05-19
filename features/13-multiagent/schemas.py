# schemas.py

from pydantic import BaseModel


class ResearchRequest(BaseModel):
    query: str


class ResearchResponse(BaseModel):
    query: str
    query_type: str        # "simple" | "complex" — useful for the frontend to show routing info
    sub_questions: list[str]  # empty for simple queries
    final_answer: str