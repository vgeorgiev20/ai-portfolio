import uuid
from typing import Optional
from asyncpg import Pool

# ── Constants ─────────────────────────────────────────────────────────────────

MEMORY_WINDOW = 10  # max messages to load per conversation (context window strategy)


# ── Conversations ─────────────────────────────────────────────────────────────

async def create_conversation(pool: Pool) -> str:
    """Create a new conversation and return its UUID."""
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO conversations DEFAULT VALUES RETURNING id"
        )
        return str(row["id"])


async def conversation_exists(pool: Pool, conversation_id: str) -> bool:
    """Check if a conversation exists."""
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id FROM conversations WHERE id = $1",
            uuid.UUID(conversation_id)
        )
        return row is not None


# ── Messages ──────────────────────────────────────────────────────────────────

async def save_message(
    pool: Pool,
    conversation_id: str,
    role: str,
    content: str,
) -> str:
    """Save a message to the database and return its UUID."""
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO messages (conversation_id, role, content)
            VALUES ($1, $2, $3)
            RETURNING id
            """,
            uuid.UUID(conversation_id),
            role,
            content,
        )
        return str(row["id"])


async def load_history(
    pool: Pool,
    conversation_id: str,
    limit: int = MEMORY_WINDOW,
) -> list[dict]:
    """
    Load the last N messages for a conversation, ordered oldest first.
    Returns list of {role, content} dicts ready to pass to OpenAI.
    """
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT role, content
            FROM (
                SELECT role, content, created_at
                FROM messages
                WHERE conversation_id = $1
                ORDER BY created_at DESC
                LIMIT $2
            ) recent
            ORDER BY created_at ASC
            """,
            uuid.UUID(conversation_id),
            limit,
        )
        return [{"role": row["role"], "content": row["content"]} for row in rows]


async def get_conversation_summary(pool: Pool, conversation_id: str) -> dict:
    """
    Return metadata about a conversation — message count and last activity.
    Useful for the frontend to display conversation info.
    """
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT
                COUNT(*)           AS message_count,
                MAX(created_at)    AS last_message_at,
                MIN(created_at)    AS started_at
            FROM messages
            WHERE conversation_id = $1
            """,
            uuid.UUID(conversation_id),
        )
        return {
            "conversation_id": conversation_id,
            "message_count": row["message_count"],
            "last_message_at": row["last_message_at"].isoformat() if row["last_message_at"] else None,
            "started_at": row["started_at"].isoformat() if row["started_at"] else None,
        }


async def delete_conversation(pool: Pool, conversation_id: str) -> bool:
    """
    Delete a conversation and all its messages (CASCADE handles messages).
    Returns True if deleted, False if not found.
    """
    async with pool.acquire() as conn:
        result = await conn.execute(
            "DELETE FROM conversations WHERE id = $1",
            uuid.UUID(conversation_id)
        )
        return result == "DELETE 1"