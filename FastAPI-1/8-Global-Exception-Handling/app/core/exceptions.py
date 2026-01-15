class AppException(Exception):
    def __init__(
        self,
        error_code: str,
        message: str,
        status_code: int = 400,
        details=None
    ):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        self.details = details


class NotFoundException(AppException):
    def __init__(self, message="Resource not found", details=None):
        super().__init__(
            error_code="NOT_FOUND",
            message=message,
            status_code=404,
            details=details
        )


class BadRequestException(AppException):
    def __init__(self, message="Bad request", details=None):
        super().__init__(
            error_code="BAD_REQUEST",
            message=message,
            status_code=400,
            details=details
        )
