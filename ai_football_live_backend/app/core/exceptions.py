from app.core.enums.error_codes import ErrorCode


class AppException(Exception):
    """Application-level exception.

    Prefer APIError from app.api.error_handlers for HTTP-facing errors.
    This class is available for non-HTTP service-layer exceptions.
    """

    def __init__(self, code: ErrorCode, message: str, details: dict | None = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)
