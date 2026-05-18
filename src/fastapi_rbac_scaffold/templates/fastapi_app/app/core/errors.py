from __future__ import annotations


class AppError(Exception):
    def __init__(self, message: str, code: int = 40000) -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class PermissionDeniedError(AppError):
    def __init__(self, message: str = "Permission denied") -> None:
        super().__init__(message=message, code=40300)


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message=message, code=40400)

