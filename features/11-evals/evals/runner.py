import os
import json
from openai import OpenAI
from rag.retriever import retrieve
from evals.judges.faithfulness import judge_faithfulness
from evals.judges.relevance import judge_relevance
from evals.judges.context_recall import judge_context_recall


GENERATION_MODEL = "gpt-4o-mini"
DATASET_PATH = "dataset/eval_dataset.json"


def _load_dataset() -> list[dict]:
    with open(DATASET_PATH) as f:
        return json.load(f)


def _generate_answer(question: str, chunks: list[str]) -> str:
    """RAG generation — same pattern as 01-rag-chat but owned by the eval pipeline."""
    client = OpenAI()
    context = "\n\n".join(chunks) if chunks else "No relevant context found."

    prompt = f"""You are a helpful NSW tenancy law assistant.
Answer ONLY using the context provided below.
If the context does not contain enough information to answer, say exactly:
"I don't have enough information to answer that."
Do not use any outside knowledge.

Context:
{context}

Question: {question}"""

    response = client.chat.completions.create(
        model=GENERATION_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content.strip()


def run_evals(conn) -> list[dict]:
    """Run the full eval suite. Returns scored results for each test case."""
    dataset = _load_dataset()
    results = []

    print(f"\n Running {len(dataset)} eval cases...\n")

    for case in dataset:
        tc_id = case["id"]
        category = case["category"]
        question = case["question"]
        ground_truth = case.get("ground_truth")
        expected_in_context = case["expected_in_context"]

        print(f"  [{tc_id}] {category}: {question[:60]}...")

        # 1. Retrieve
        chunks = retrieve(question, conn)

        # 2. Generate
        answer = _generate_answer(question, chunks)

        # 3. Score
        faithfulness = judge_faithfulness(question, answer, chunks)
        relevance = judge_relevance(question, answer)
        context_recall = judge_context_recall(
            question, ground_truth, chunks, expected_in_context
        )

        result = {
            "id": tc_id,
            "category": category,
            "question": question,
            "ground_truth": ground_truth,
            "expected_in_context": expected_in_context,
            "answer": answer,
            "retrieved_chunks": chunks,
            "scores": {
                "faithfulness": faithfulness,
                "relevance": relevance,
                "context_recall": context_recall,
            }
        }

        results.append(result)

        print(f"         faithfulness={faithfulness['score']:.2f}  "
              f"relevance={relevance['score']:.2f}  "
              f"context_recall={context_recall['score']:.2f}")

    return results