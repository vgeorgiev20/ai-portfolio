from openai import OpenAI
from pgvector.psycopg2 import register_vector


EMBEDDING_MODEL = "text-embedding-ada-002"
TOP_K = 5


def retrieve(query: str, conn, top_k: int = TOP_K) -> list[str]:
    """Embed the query and return the top-k most similar chunks from pgvector."""
    client = OpenAI()

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=query
    )
    query_embedding = response.data[0].embedding

    with conn.cursor() as cur:
        cur.execute("""
            SELECT content
            FROM eval_embeddings
            ORDER BY embedding <=> %s::vector
            LIMIT %s;
        """, (query_embedding, top_k))

        rows = cur.fetchall()

    return [row[0] for row in rows]