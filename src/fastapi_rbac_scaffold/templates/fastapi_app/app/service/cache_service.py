from __future__ import annotations

import json
from typing import Any

from redis.asyncio import Redis


async def get_json_cache(redis: Redis, key: str) -> dict[str, Any] | None:
    raw = await redis.get(key)
    if raw is None:
        return None
    return json.loads(raw)


async def set_json_cache(
    redis: Redis,
    key: str,
    value: dict[str, Any],
    *,
    expire_seconds: int = 300,
) -> None:
    await redis.set(key, json.dumps(value), ex=expire_seconds)


async def delete_cache(redis: Redis, *keys: str) -> None:
    if keys:
        await redis.delete(*keys)

