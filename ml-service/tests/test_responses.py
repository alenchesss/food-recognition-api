"""
Тесты хелпера error_response 
"""
import json

from app.core.responses import error_response


def test_error_response_basic_format():
    resp = error_response(
        status_code=400, code="BadRequestHttpException", message="bad input"
    )
    assert resp.status_code == 400
    body = json.loads(resp.body)
    assert body == {
        "data": None,
        "errors": [{"code": "BadRequestHttpException", "message": "bad input"}],
    }


def test_error_response_with_meta():
    resp = error_response(
        status_code=400,
        code="ValidationException",
        message="Validation failed",
        meta={"validation": {"details": ["x"]}},
    )
    body = json.loads(resp.body)
    # meta попал в правильное место — на верхний уровень
    assert "meta" in body
    assert body["meta"] == {"validation": {"details": ["x"]}}
    # data и errors на месте
    assert body["data"] is None
    assert body["errors"][0]["code"] == "ValidationException"


def test_error_response_omits_meta_when_none():
    resp = error_response(
        status_code=500, code="InternalServerError", message="oops"
    )
    body = json.loads(resp.body)
    assert "meta" not in body
