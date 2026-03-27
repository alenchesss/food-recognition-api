from fastapi.responses import JSONResponse


def error_response(
    *,
    status_code: int,
    code: str,
    message: str,
    meta: dict | None = None,
) -> JSONResponse:
    error = {
        "code": code,
        "message": message,
    }

    content = {
        "data": None,
        "errors": [error],
    }

    if meta is not None:
        content["meta"] = meta

    return JSONResponse(
        status_code=status_code,
        content=content,
    )
