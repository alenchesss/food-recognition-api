import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.responses import error_response

logger = logging.getLogger(__name__)

_STATUS_TO_CODE = {
    400: "BadRequestHttpException",
    401: "UnauthorizedHttpException",
    403: "ForbiddenHttpException",
    404: "NotFoundHttpException",
    500: "InternalServerError",
}


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    error_code = _STATUS_TO_CODE.get(exc.status_code, "HttpException")
    return error_response(
        status_code=exc.status_code,
        code=error_code,
        message=str(exc.detail),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return error_response(
        status_code=400,
        code="ValidationException",
        message="Validation failed",
        meta={"validation": {"details": exc.errors()}},
    )


async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled internal error")
    return error_response(
        status_code=500,
        code="InternalServerError",
        message="Internal server error",
    )
