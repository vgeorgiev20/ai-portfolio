import json
from openai import OpenAI


def judge_relevance(question: str, answer: str) -> dict:
    """
    Score whether the answer actually addresses the question asked.
    Returns a score 0.0-1.0 and reasoning.

    Catches topic drift — answers that are factually correct but don't
    respond to what was actually asked.
    """
    client = OpenAI()

    prompt = f"""You are an expert evaluator assessing a RAG system.

Your job: determine whether the ANSWER directly and completely addresses the QUESTION.

Rules:
- Score 1.0 if the answer fully addresses what was asked
- Score 0.5 if the answer is partially relevant but misses key parts of the question
- Score 0.0 if the answer is off-topic or ignores the question entirely
- "I don't have enough information to answer that" scores 1.0 if the question is genuinely unanswerable from a tenancy law document

QUESTION: {question}

ANSWER: {answer}

Respond with ONLY valid JSON in this exact format:
{{"score": 0.0, "reasoning": "brief explanation"}}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    raw = response.choices[0].message.content.strip()
    result = json.loads(raw)
    return {"score": float(result["score"]), "reasoning": result["reasoning"]}