import json

import redis.asyncio as aioredis

from app.core.config import settings
from app.core.logger import logger


class RedisMemory:
    """Redis-backed short-term memory keyed only by session_id."""

    def __init__(self):
        self._client: aioredis.Redis | None = None
        self._ttl = settings.redis_memory_ttl
        self._max_messages = settings.redis_max_messages

    # ── lifecycle ──────────────────────────────────────────────

    async def connect(self):
        try:
            self._client = aioredis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password or None,
                decode_responses=True,
            )
            await self._client.ping()
            logger.info(
                f"Redis connected: {settings.redis_host}:{settings.redis_port}/{settings.redis_db}"
            )
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Memory will be unavailable.")
            self._client = None

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None
            logger.info("Redis connection closed")

    @property
    def available(self) -> bool:
        return self._client is not None

    # ── key helpers ────────────────────────────────────────────

    @staticmethod
    def _chat_key(session_id: str) -> str:
        return f"agent:chat:{session_id}"

    @staticmethod
    def _state_key(session_id: str) -> str:
        return f"agent:state:{session_id}"

    # ── chat messages ──────────────────────────────────────────

    async def add_message(self, session_id: str, role: str, content: str, metadata: dict | None = None):
        if not self._client:
            return
        key = self._chat_key(session_id)
        entry = {"role": role, "content": content}
        if metadata:
            entry["metadata"] = metadata
        pipe = self._client.pipeline(transaction=False)
        pipe.rpush(key, json.dumps(entry, ensure_ascii=False))
        # keep only the last N messages
        pipe.ltrim(key, -self._max_messages, -1)
        pipe.expire(key, self._ttl)
        await pipe.execute()

    async def get_messages(self, session_id: str) -> list[dict]:
        if not self._client:
            return []
        key = self._chat_key(session_id)
        raw = await self._client.lrange(key, 0, -1)
        return [json.loads(item) for item in raw]

    async def clear_messages(self, session_id: str):
        if not self._client:
            return
        await self._client.delete(self._chat_key(session_id))

    # ── agent state ────────────────────────────────────────────

    async def save_state(self, session_id: str, state: dict):
        if not self._client:
            return
        key = self._state_key(session_id)
        await self._client.set(key, json.dumps(state, ensure_ascii=False), ex=self._ttl)

    async def get_state(self, session_id: str) -> dict | None:
        if not self._client:
            return None
        key = self._state_key(session_id)
        raw = await self._client.get(key)
        if raw is None:
            return None
        return json.loads(raw)

    async def clear_state(self, session_id: str):
        if not self._client:
            return
        await self._client.delete(self._state_key(session_id))

    # ── clear all ──────────────────────────────────────────────

    async def clear_session(self, session_id: str):
        await self.clear_messages(session_id)
        await self.clear_state(session_id)
