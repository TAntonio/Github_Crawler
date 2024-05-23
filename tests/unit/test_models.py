import pytest
from pydantic import ValidationError

from src.models import SearchRequestParams


@pytest.mark.parametrize(
    "json_payload",
    [
        '{"keywords": ["python", "drf"], "proxies": ["1.1.1.1:8080"], "type": "Repositories"}',
        '{"keywords": ["unity"], "proxies": ["1.1.1.2:8080"], "type": "Issues"}',
        '{"keywords": ["unreal engine"], "proxies": ["1.1.1.2:8080", "4.5.6.7:8080"], "type": "Wikis"}',
    ],
)
def test_search_request_params_success(json_payload: str):
    request_params = SearchRequestParams.model_validate_json(json_payload)
    assert request_params


@pytest.mark.parametrize(
    "json_payload",
    [
        "{}",
        '{"proxies": ["1.1.1.1:8080"], "type": "Repositories"}',
        '{"keywords": [], "proxies": ["1.1.1.1:8080"], "type": "Repositories"}',
        '{"keywords": ["unity"], "proxies": [], "type": "Wikis"}',
        '{"keywords": ["unity"], "type": "Wikis"}',
        '{"keywords": ["drf"], "proxies": ["1.1.1.2:8080"]}',
    ],
)
def test_search_request_raise_exc_if_invalid_payload(json_payload: str):
    with pytest.raises(ValidationError):
        SearchRequestParams.model_validate_json(json_payload)
