from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.enums.error_codes import ErrorCode, ERROR_STATUS_MAP


class APIError(Exception):
    def __init__(self, code: ErrorCode, message: str, details: dict | None = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    status_code = ERROR_STATUS_MAP.get(exc.code, 500)
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code.value,
                "message": exc.message,
                **exc.details,
            },
        },
    )


async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": ErrorCode.INTERNAL_ERROR.value,
                "message": "An unexpected error occurred",
            },
        },
    )
