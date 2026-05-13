from typing import Any

from fastapi.responses import JSONResponse


def error_response(
    *,
    status_code: int,
    code: str,
    message: str,
    meta: dict | None = None,
) -> JSONResponse:
   
    error: dict[str, Any] = {
        "code": code,
        "message": message,
    }

    content: dict[str, Any] = {
        "data": None,
        "errors": [error],
    }

    if meta is not None:
        content["meta"] = meta

    return JSONResponse(
        status_code=status_code,
        content=content,
    )
