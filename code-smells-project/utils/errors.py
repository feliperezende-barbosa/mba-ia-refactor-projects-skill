class AppError(Exception):
    status = 500

    def __init__(self, message, status=None):
        super().__init__(message)
        if status is not None:
            self.status = status


class ValidationError(AppError):
    status = 400


class NotFoundError(AppError):
    status = 404


class ForbiddenError(AppError):
    status = 403


class UnauthorizedError(AppError):
    status = 401
