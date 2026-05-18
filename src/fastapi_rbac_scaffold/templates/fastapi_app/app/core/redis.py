from __future__ import annotations

from redis.asyncio import Redis

from app.config import get_settings


async def create_redis_client() -> Redis:
    settings = get_settings()
    client = Redis.from_url(settings.redis_url, decode_responses=True)
    await client.ping()
    return client


async def close_redis_client(client: Redis | None) -> None:
    if client is not None:
        await client.aclose()

