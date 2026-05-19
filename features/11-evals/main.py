"""
11-evals — RAG Evaluation Pipeline
====================================
Self-contained Python eval harness for the tenancy.pdf RAG system.

Metrics:
  - Faithfulness:    Is the answer grounded in retrieved chunks? (catches hallucination)
  - Relevance:       Does the answer address the question? (catches topic drift)
  - Context Recall:  Did retrieval surface the right content? (judges the retrieval step)

LLM-as-judge: gpt-4o-mini scores each metric 0.0-1.0.

Usage:
  Copy tenancy.pdf to documents/tenancy.pdf, then:
    python main.py
"""

import os
from dotenv import load_dotenv
from rag.chunker import chunk_pdf
from rag.embedder import get_connection, setup_table, is_already_indexed, embed_and_store
from evals.runner import run_evals
from evals.report import save_and_print


PDF_PATH = "documents/tenancy.pdf"
SOURCE_NAME = "tenancy.pdf"


def main():
    load_dotenv()

    if not os.environ.get("OPENAI_API_KEY"):
        raise EnvironmentError("OPENAI_API_KEY not set in .env")

    if not os.path.exists(PDF_PATH):
        raise FileNotFoundError(
            f"Document not found: {PDF_PATH}\n"
            f"Copy tenancy.pdf from 01-rag-chat/api/Documents/ into documents/"
        )

    conn = get_connection()
    setup_table(conn)

    # Ingest — skip if already indexed (safe to rerun)
    if is_already_indexed(conn, SOURCE_NAME):
        print(f"✓ {SOURCE_NAME} already indexed — skipping embedding step")
    else:
        print(f"  Chunking {PDF_PATH}...")
        chunks = chunk_pdf(PDF_PATH)
        print(f"  {len(chunks)} chunks — embedding and storing in pgvector...")
        stored = embed_and_store(chunks, SOURCE_NAME, conn)
        print(f"✓ Indexed {stored} chunks into pgvector")

    # Eval
    results = run_evals(conn)

    # Report
    save_and_print(results)

    conn.close()


if __name__ == "__main__":
    main()