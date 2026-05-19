import os
import psycopg2
from pgvector.psycopg2 import register_vector
from openai import OpenAI


EMBEDDING_MODEL = "text-embedding-ada-002"
EMBEDDING_DIM = 1536


def get_connection():
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    register_vector(conn)
    return conn


def setup_table(conn):
    """Create the eval embeddings table if it doesn't exist."""
    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS eval_embeddings (
                id SERIAL PRIMARY KEY,
                chunk_id TEXT UNIQUE NOT NULL,
                content TEXT NOT NULL,
                embedding vector({EMBEDDING_DIM}),
                source TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
        conn.commit()


def is_already_indexed(conn, source: str) -> bool:
    """Check if a document source is already indexed — skip re-embedding on reruns."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) FROM eval_embeddings WHERE source = %s;",
            (source,)
        )
        count = cur.fetchone()[0]
    return count > 0


def embed_and_store(chunks: list[str], source: str, conn) -> int:
    """Embed chunks with OpenAI and store in pgvector. Returns number of chunks stored."""
    client = OpenAI()
    stored = 0

    with conn.cursor() as cur:
        for i, chunk in enumerate(chunks):
            chunk_id = f"{source}::chunk-{i}"

            response = client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=chunk
            )
            embedding = response.data[0].embedding

            cur.execute("""
                INSERT INTO eval_embeddings (chunk_id, content, embedding, source)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (chunk_id) DO NOTHING;
            """, (chunk_id, chunk, embedding, source))

            stored += 1

    conn.commit()
    return stored