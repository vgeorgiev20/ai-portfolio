import json
from openai import OpenAI


def judge_context_recall(
    question: str,
    ground_truth: str | None,
    chunks: list[str],
    expected_in_context: bool
) -> dict:
    """
    Score whether retrieval surfaced the chunks needed to answer the question.
    This judges the RETRIEVAL step, not the generation step.

    For adversarial cases (expected_in_context=False, ground_truth=None):
    - Score 1.0 if chunks correctly contain NO relevant answer (retrieval correctly returned unrelated content)
    - Score 0.0 if chunks somehow contain the answer (shouldn't happen for out-of-domain questions)
    """
    client = OpenAI()

    if not expected_in_context:
        # Adversarial case: we expect retrieval NOT to find relevant content
        context = "\n\n---\n\n".join(chunks) if chunks else "No context retrieved."
        prompt = f"""You are an expert evaluator assessing a RAG retrieval system.

This question is OUT OF SCOPE for a tenancy law document. The retrieval system should NOT have found relevant context.

QUESTION: {question}

RETRIEVED CONTEXT:
{context}

Does the retrieved context contain a direct answer to the question?
- Score 0.0 if the context DOES contain a relevant answer (retrieval failure — returned wrong content)
- Score 1.0 if the context does NOT contain a relevant answer (correct — nothing relevant retrieved)

Respond with ONLY valid JSON:
{{"score": 0.0, "reasoning": "brief explanation"}}"""
    else:
        # Normal case: we expect retrieval to find chunks containing the ground truth
        context = "\n\n---\n\n".join(chunks) if chunks else "No context retrieved."
        prompt = f"""You are an expert evaluator assessing a RAG retrieval system.

Your job: determine whether the RETRIEVED CONTEXT contains the information needed to answer the QUESTION, based on the GROUND TRUTH answer.

QUESTION: {question}

GROUND TRUTH ANSWER: {ground_truth}

RETRIEVED CONTEXT:
{context}

Rules:
- Score 1.0 if the context clearly contains the information from the ground truth
- Score 0.5 if the context partially contains the relevant information
- Score 0.0 if the context is missing the information needed (retrieval failure)

Respond with ONLY valid JSON:
{{"score": 0.0, "reasoning": "brief explanation"}}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    raw = response.choices[0].message.content.strip()
    result = json.loads(raw)
    return {"score": float(result["score"]), "reasoning": result["reasoning"]}