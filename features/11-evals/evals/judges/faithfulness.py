import json
from openai import OpenAI


def judge_faithfulness(question: str, answer: str, chunks: list[str]) -> dict:
    """
    Score whether the answer is grounded in the retrieved chunks.
    Returns a score 0.0-1.0 and reasoning.

    A low score means the model answered from outside knowledge (hallucination).
    A high score means every claim in the answer can be traced to the chunks.
    """
    client = OpenAI()
    context = "\n\n---\n\n".join(chunks) if chunks else "No context retrieved."

    prompt = f"""You are an expert evaluator assessing a RAG system.

Your job: determine whether the ANSWER is faithfully grounded in the CONTEXT provided.

Rules:
- Score 1.0 if every claim in the answer can be verified from the context
- Score 0.0 if the answer contains claims not present in the context, or confidently answers when context is irrelevant
- Score between 0.0-1.0 for partial grounding
- If the answer says "I don't have enough information" and the context is truly irrelevant, score 1.0 (correct behaviour)

QUESTION: {question}

CONTEXT:
{context}

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