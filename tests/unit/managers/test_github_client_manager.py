from unittest.mock import AsyncMock, call
from itertools import cycle

import pytest

from src.managers.github_client_manager import GithubClientManager, InvalidHtmlError
from src.client import GithubClient
from src.models import SearchRequestParams
from src.enums import SearchType


@pytest.fixture()
def github_client_mocked():
    return AsyncMock(GithubClient)


@pytest.fixture()
def github_client_manager(github_client_mocked):
    return GithubClientManager(github_client=github_client_mocked)


@pytest.mark.parametrize(
    "input_html",
    [
        "<body>1</body>",
        '{"iamjs": 1}',
    ],
)
@pytest.mark.parametrize(
    "search_type",
    [
        SearchType.REPOSITORIES,
        SearchType.WIKIS,
        SearchType.ISSUES,
    ],
)
@pytest.mark.asyncio
async def test_search_response_handle_invalid_html(
    github_client_manager: GithubClientManager,
    search_type: SearchType,
    input_html: str,
):
    payload = SearchRequestParams(
        keywords=["python"], proxies=["194.126.37.94:8080"], type=search_type
    )
    github_client_manager.github_client.get_search_results_page = AsyncMock(
        side_effect=[input_html]
    )
    with pytest.raises(InvalidHtmlError):
        await github_client_manager.get_search_results_response(payload.json())

    github_client_manager.github_client.get_search_results_page.assert_called_once_with(
        query=payload.keywords[0],
        search_type=payload.type,
        proxy=str(payload.proxies[0]),
    )


@pytest.mark.asyncio
async def test_repositories_search_response_success(
    github_client_manager: GithubClientManager,
    get_repositories_search_response,
    get_repo_detailed_info_response,
):
    items_count_per_page = 10
    payload = SearchRequestParams(
        keywords=["python", "django"], proxies=["1.1.1.1"], type=SearchType.REPOSITORIES
    )
    search_responses = []
    for keyword in payload.keywords:
        response_text = get_repositories_search_response(keyword)
        search_responses.append(response_text)

    # for testing purposes we will use the same info from 2 repos for all items
    sample_detailed_repos_responses = [
        get_repo_detailed_info_response(index) for index in range(1, 3)
    ]
    detailed_repos_responses = []

    for index, response in enumerate(cycle(sample_detailed_repos_responses)):
        if index == (len(payload.keywords) * items_count_per_page):
            break
        detailed_repos_responses.append(response)

    github_client_manager.github_client.get_search_results_page = AsyncMock(
        side_effect=search_responses
    )
    github_client_manager.github_client.get_detailed_repository_info_page = AsyncMock(
        side_effect=detailed_repos_responses
    )
    response = await github_client_manager.get_search_results_response(payload.json())
    expected_language_stats = [
        {
            "Python": 97.2,
            "HTML": 1.4,
            "JavaScript": 0.9,
            "CSS": 0.5,
            "Smarty": 0.0,
            "Makefile": 0.0,
        },
        {"HTML": 48.6, "Just": 41.7, "Ruby": 7.6, "SCSS": 2.1},
    ]

    expected_response = [
        {
            "url": "https://github.com/kubernetes-client/python",
            "extra": {
                "owner": "kubernetes-client",
                "language_stats": expected_language_stats[0],
            },
        },
        {
            "url": "https://github.com/xxg1413/python",
            "extra": {"owner": "xxg1413", "language_stats": expected_language_stats[1]},
        },
        {
            "url": "https://github.com/gxcuizy/Python",
            "extra": {
                "owner": "gxcuizy",
                "language_stats": expected_language_stats[0],
            },
        },
        {
            "url": "https://github.com/jakevdp/PythonDataScienceHandbook",
            "extra": {"owner": "jakevdp", "language_stats": expected_language_stats[1]},
        },
        {
            "url": "https://github.com/AtsushiSakai/PythonRobotics",
            "extra": {
                "owner": "AtsushiSakai",
                "language_stats": expected_language_stats[0],
            },
        },
        {
            "url": "https://github.com/vinta/awesome-python",
            "extra": {"owner": "vinta", "language_stats": expected_language_stats[1]},
        },
        {
            "url": "https://github.com/Tanu-N-Prabhu/Python",
            "extra": {
                "owner": "Tanu-N-Prabhu",
                "language_stats": expected_language_stats[0],
            },
        },
        {
            "url": "https://github.com/Pierian-Data/Complete-Python-3-Bootcamp",
            "extra": {
                "owner": "Pierian-Data",
                "language_stats": expected_language_stats[1],
            },
        },
        {
            "url": "https://github.com/poise/python",
            "extra": {"owner": "poise", "language_stats": expected_language_stats[0]},
        },
        {
            "url": "https://github.com/yidao620c/python3-cookbook",
            "extra": {
                "owner": "yidao620c",
                "language_stats": expected_language_stats[1],
            },
        },
        {
            "url": "https://github.com/django/django",
            "extra": {"owner": "django", "language_stats": expected_language_stats[0]},
        },
        {
            "url": "https://github.com/liangliangyy/DjangoBlog",
            "extra": {
                "owner": "liangliangyy",
                "language_stats": expected_language_stats[1],
            },
        },
        {
            "url": "https://github.com/encode/django-rest-framework",
            "extra": {"owner": "encode", "language_stats": expected_language_stats[0]},
        },
        {
            "url": "https://github.com/django-cms/django-cms",
            "extra": {
                "owner": "django-cms",
                "language_stats": expected_language_stats[1],
            },
        },
        {
            "url": "https://github.com/cookiecutter/cookiecutter-django",
            "extra": {
                "owner": "cookiecutter",
                "language_stats": expected_language_stats[0],
            },
        },
        {
            "url": "https://github.com/pennersr/django-allauth",
            "extra": {
                "owner": "pennersr",
                "language_stats": expected_language_stats[1],
            },
        },
        {
            "url": "https://github.com/django-oscar/django-oscar",
            "extra": {
                "owner": "django-oscar",
                "language_stats": expected_language_stats[0],
            },
        },
        {
            "url": "https://github.com/stephenmcd/mezzanine",
            "extra": {
                "owner": "stephenmcd",
                "language_stats": expected_language_stats[1],
            },
        },
        {
            "url": "https://github.com/wsvincent/awesome-django",
            "extra": {
                "owner": "wsvincent",
                "language_stats": expected_language_stats[0],
            },
        },
        {
            "url": "https://github.com/sclorg/django-ex",
            "extra": {"owner": "sclorg", "language_stats": expected_language_stats[1]},
        },
    ]

    assert response == expected_response
    assert github_client_manager.github_client.get_search_results_page.mock_calls == [
        call(query="python", search_type=SearchType.REPOSITORIES, proxy="1.1.1.1"),
        call(query="django", search_type=SearchType.REPOSITORIES, proxy="1.1.1.1"),
    ]


@pytest.mark.asyncio
async def test_issues_search_response_success(
    github_client_manager: GithubClientManager,
    get_issues_search_response,
):
    payload = SearchRequestParams(
        keywords=["python", "django"], proxies=["1.1.1.1"], type=SearchType.ISSUES
    )
    responses = []
    for keyword in payload.keywords:
        response_text = get_issues_search_response(keyword)
        responses.append(response_text)

    github_client_manager.github_client.get_search_results_page = AsyncMock(
        side_effect=responses
    )
    response = await github_client_manager.get_search_results_response(payload.json())

    expected_response = [
        {"url": "https://github.com/ahmadabos/ahmed-abbous/issues/2"},
        {"url": "https://github.com/CodeWithHarry/100-days-of-code-youtube/issues/15"},
        {"url": "https://github.com/abdulraheem48/Course/issues/1"},
        {"url": "https://github.com/Afwanshaik/Afwan-demo/issues/1"},
        {"url": "https://github.com/SaiRupaViswanadh/BigDataBootCamp2.0/issues/1"},
        {"url": "https://github.com/mouredev/Hello-Python/issues/61"},
        {"url": "https://github.com/kevin2045/Trabalho-do-curso-/issues/1"},
        {"url": "https://github.com/beomseok3/test/issues/2"},
        {
            "url": "https://github.com/CodeStrong2023/BrigadaBinaria-tercer-semestre/issues/25"
        },
        {"url": "https://github.com/Asabeneh/30-Days-Of-Python/issues/520"},
        {"url": "https://github.com/SaidParaBellum/git/issues/1"},
        {"url": "https://github.com/odundoB/IBL/issues/1"},
        {"url": "https://github.com/muturi254/open_waters/issues/28"},
        {"url": "https://github.com/jonas-rem/lwm2m_server/issues/12"},
        {"url": "https://github.com/V-FOR-VEND3TTA/news-aggregator/issues/3"},
        {"url": "https://github.com/amy-1989/the-bakery/issues/43"},
        {"url": "https://github.com/ichinose9372/ft_transcendense_42/issues/69"},
        {"url": "https://github.com/javieb/ProyectoFinal/issues/1"},
        {"url": "https://github.com/abaddonpuff/commandCenter/issues/1"},
        {"url": "https://github.com/kmmbvnr/django-guardian-ng/issues/104"},
    ]
    assert response == expected_response
    assert github_client_manager.github_client.get_search_results_page.mock_calls == [
        call(query="python", search_type=SearchType.ISSUES, proxy="1.1.1.1"),
        call(query="django", search_type=SearchType.ISSUES, proxy="1.1.1.1"),
    ]


@pytest.mark.asyncio
async def test_wikis_search_response_success(
    github_client_manager: GithubClientManager,
    get_issues_search_response,
):
    payload = SearchRequestParams(
        keywords=["python", "django"], proxies=["1.1.1.1"], type=SearchType.WIKIS
    )
    responses = []
    for keyword in payload.keywords:
        response_text = get_issues_search_response(keyword)
        responses.append(response_text)

    github_client_manager.github_client.get_search_results_page = AsyncMock(
        side_effect=responses
    )
    response = await github_client_manager.get_search_results_response(payload.json())

    expected_response = [
        {"url": "https://github.com/ahmadabos/ahmed-abbous/issues/2"},
        {"url": "https://github.com/CodeWithHarry/100-days-of-code-youtube/issues/15"},
        {"url": "https://github.com/abdulraheem48/Course/issues/1"},
        {"url": "https://github.com/Afwanshaik/Afwan-demo/issues/1"},
        {"url": "https://github.com/SaiRupaViswanadh/BigDataBootCamp2.0/issues/1"},
        {"url": "https://github.com/mouredev/Hello-Python/issues/61"},
        {"url": "https://github.com/kevin2045/Trabalho-do-curso-/issues/1"},
        {"url": "https://github.com/beomseok3/test/issues/2"},
        {
            "url": "https://github.com/CodeStrong2023/BrigadaBinaria-tercer-semestre/issues/25"
        },
        {"url": "https://github.com/Asabeneh/30-Days-Of-Python/issues/520"},
        {"url": "https://github.com/SaidParaBellum/git/issues/1"},
        {"url": "https://github.com/odundoB/IBL/issues/1"},
        {"url": "https://github.com/muturi254/open_waters/issues/28"},
        {"url": "https://github.com/jonas-rem/lwm2m_server/issues/12"},
        {"url": "https://github.com/V-FOR-VEND3TTA/news-aggregator/issues/3"},
        {"url": "https://github.com/amy-1989/the-bakery/issues/43"},
        {"url": "https://github.com/ichinose9372/ft_transcendense_42/issues/69"},
        {"url": "https://github.com/javieb/ProyectoFinal/issues/1"},
        {"url": "https://github.com/abaddonpuff/commandCenter/issues/1"},
        {"url": "https://github.com/kmmbvnr/django-guardian-ng/issues/104"},
    ]
    assert response == expected_response
    assert github_client_manager.github_client.get_search_results_page.mock_calls == [
        call(query="python", search_type=SearchType.WIKIS, proxy="1.1.1.1"),
        call(query="django", search_type=SearchType.WIKIS, proxy="1.1.1.1"),
    ]
