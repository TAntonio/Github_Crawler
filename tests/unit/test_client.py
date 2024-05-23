import httpx
import pytest

from src.client import GithubClient, DEFAULT_HEADERS
from src.enums import SearchType


@pytest.mark.asyncio
async def test_get_search_results_page_success(
    respx_mock,
    github_client: GithubClient,
    get_repositories_search_response,
):
    query = "django"
    expected_full_url = (
        f"{github_client.get_search_endpoint()}?q={query}&type=Repositories"
    )
    expected_response_text = get_repositories_search_response("django")
    route = respx_mock.get(expected_full_url).mock(
        return_value=httpx.Response(200, text=expected_response_text)
    )

    page_content = await github_client.get_search_results_page(
        query=query,
        search_type=str(SearchType.REPOSITORIES),
        proxy="1.1.1.1:8080",
    )
    assert page_content == expected_response_text
    assert route.called

    request = route.calls[0][0]
    assert dict(request.headers) == DEFAULT_HEADERS


@pytest.mark.parametrize("expected_status_code", [305, 401, 500])
@pytest.mark.asyncio
async def test_get_search_results_handle_invalid_responses(
    respx_mock,
    github_client: GithubClient,
    get_repositories_search_response,
    expected_status_code: int,
):
    query = "django"
    expected_full_url = (
        f"{github_client.get_search_endpoint()}?q={query}&type=Repositories"
    )
    route = respx_mock.get(expected_full_url).mock(
        return_value=httpx.Response(expected_status_code)
    )

    with pytest.raises(httpx.HTTPError):
        await github_client.get_search_results_page(
            query=query,
            search_type=str(SearchType.REPOSITORIES),
            proxy="1.1.1.1:8080",
        )
    assert route.called


@pytest.mark.asyncio
async def test_get_repo_detailed_info_page_success(
    respx_mock,
    github_client: GithubClient,
    get_repo_detailed_info_response,
):
    full_url = f"{github_client.get_search_endpoint()}/django/django"
    expected_response_text = get_repo_detailed_info_response(1)
    route = respx_mock.get(full_url).mock(
        return_value=httpx.Response(200, text=expected_response_text)
    )

    page_content = await github_client.get_detailed_repository_info_page(
        repo_url=full_url,
        proxy="1.1.1.1:8080",
    )
    assert page_content == expected_response_text
    assert route.called

    request = route.calls[0][0]
    assert dict(request.headers) == DEFAULT_HEADERS


@pytest.mark.parametrize(
    "input_proxy, is_valid",
    [
        ("1.1.1.1:80", False),
        ("http://1.1.1.1:80", True),
        ("https://1.1.1.1:80", True),
    ],
)
def test_prepared_proxies_param(
    github_client: GithubClient, input_proxy: str, is_valid: bool
):
    actual_proxies_param = github_client.get_prepared_proxies_param(input_proxy)
    if not is_valid:
        expected_proxy = f"http://{input_proxy}"
    else:
        expected_proxy = input_proxy

    expected_proxies_param = {"http://": expected_proxy, "https://": expected_proxy}
    assert actual_proxies_param == expected_proxies_param
