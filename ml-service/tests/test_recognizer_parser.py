"""
Тесты парсера ответа Yandex GPT в IngredientRecognizer._parse_response.

"""
import pytest

from app.recognizer import IngredientRecognizer, RecognizedIngredient


def test_parse_valid_json():
    text = '{"ingredients": [{"name": "tomato"}, {"name": "cheese"}]}'
    result = IngredientRecognizer._parse_response(text)
    assert result == [
        RecognizedIngredient(name="tomato"),
        RecognizedIngredient(name="cheese"),
    ]


def test_parse_empty_string_returns_empty_list():
    assert IngredientRecognizer._parse_response("") == []
    assert IngredientRecognizer._parse_response("   \n  ") == []


def test_parse_strips_whitespace_in_names():
    text = '{"ingredients": [{"name": "  tomato  "}]}'
    result = IngredientRecognizer._parse_response(text)
    assert result == [RecognizedIngredient(name="tomato")]


def test_parse_skips_empty_names():
    text = '{"ingredients": [{"name": ""}, {"name": "tomato"}, {"name": "  "}]}'
    result = IngredientRecognizer._parse_response(text)
    assert result == [RecognizedIngredient(name="tomato")]


def test_parse_empty_ingredients_list():
    text = '{"ingredients": []}'
    assert IngredientRecognizer._parse_response(text) == []


def test_parse_invalid_json_raises():
    with pytest.raises(ValueError, match="Model returned invalid JSON"):
        IngredientRecognizer._parse_response("not json {{{")


def test_parse_non_object_root_raises():
    with pytest.raises(ValueError, match="Model response must be an object"):
        IngredientRecognizer._parse_response('["tomato"]')


def test_parse_missing_ingredients_field_raises():
    with pytest.raises(ValueError, match="must contain 'ingredients'"):
        IngredientRecognizer._parse_response('{"foo": "bar"}')


def test_parse_ingredients_not_list_raises():
    with pytest.raises(ValueError, match="must be a list"):
        IngredientRecognizer._parse_response('{"ingredients": "tomato"}')


def test_parse_item_not_object_raises():
    with pytest.raises(ValueError, match="Each ingredient must be an object"):
        IngredientRecognizer._parse_response('{"ingredients": ["tomato"]}')


def test_parse_name_not_string_raises():
    with pytest.raises(ValueError, match="'name' must be a string"):
        IngredientRecognizer._parse_response('{"ingredients": [{"name": 123}]}')


def test_parse_missing_name_raises():
    with pytest.raises(ValueError, match="'name' must be a string"):
        IngredientRecognizer._parse_response('{"ingredients": [{}]}')
