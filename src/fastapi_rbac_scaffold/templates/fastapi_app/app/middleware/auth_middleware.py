from __future__ import annotations

from collections.abc import Iterable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.status import HTTP_401_UNAUTHORIZED


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        *,
        exclude_paths: Iterable[str] | None = None,
    ) -> None:
        super().__init__(app)
        self.exclude_paths = tuple(exclude_paths or ())

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.method == "OPTIONS":
            return await call_next(request)
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.lower().startswith("bearer "):
            return JSONResponse(
                status_code=HTTP_401_UNAUTHORIZED,
                content={"code": 40100, "message": "Missing bearer token"},
            )
        return await call_next(request)

