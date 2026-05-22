from app.core.logger import logger
from app.memory.redis_memory import RedisMemory


class MemoryManager:
    """High-level memory interface. All methods keyed by session_id only."""

    def __init__(self, redis: RedisMemory):
        self._redis = redis

    # ── append helpers ─────────────────────────────────────────

    async def append_user_message(self, session_id: str, content: str, metadata: dict | None = None):
        try:
            await self._redis.add_message(session_id, "user", content, metadata)
        except Exception as e:
            logger.warning(f"Failed to save user message: {e}")

    async def append_assistant_message(self, session_id: str, content: str, metadata: dict | None = None):
        try:
            await self._redis.add_message(session_id, "assistant", content, metadata)
        except Exception as e:
            logger.warning(f"Failed to save assistant message: {e}")

    async def append_tool_message(self, session_id: str, content: str, metadata: dict | None = None):
        try:
            await self._redis.add_message(session_id, "tool", content, metadata)
        except Exception as e:
            logger.warning(f"Failed to save tool message: {e}")

    # ── read ───────────────────────────────────────────────────

    async def get_chat_history(self, session_id: str) -> list[dict]:
        try:
            return await self._redis.get_messages(session_id)
        except Exception as e:
            logger.warning(f"Failed to read chat history: {e}")
            return []

    # ── state ──────────────────────────────────────────────────

    async def save_agent_state(self, session_id: str, state: dict):
        try:
            await self._redis.save_state(session_id, state)
        except Exception as e:
            logger.warning(f"Failed to save agent state: {e}")

    async def get_agent_state(self, session_id: str) -> dict | None:
        try:
            return await self._redis.get_state(session_id)
        except Exception as e:
            logger.warning(f"Failed to read agent state: {e}")
            return None

    # ── clear ──────────────────────────────────────────────────

    async def clear_session(self, session_id: str):
        try:
            await self._redis.clear_session(session_id)
        except Exception as e:
            logger.warning(f"Failed to clear session: {e}")
