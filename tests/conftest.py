import pathlib

import pytest

from src.client import GithubClient


@pytest.fixture(scope="session")
def get_mocked_response():
    current_path = pathlib.Path(__file__).parent.resolve()

    def wrapper(prefix: str, file_name: str):
        with open(
            f"{current_path}/mocked_responses/{prefix}_{file_name}.html", "r"
        ) as html_file:
            return html_file.read()

    return wrapper


@pytest.fixture(scope="session")
def get_repositories_search_response(get_mocked_response):
    def wrapper(file_name: str):
        html_file = get_mocked_response(
            prefix="search/repositories_search_response", file_name=file_name
        )
        return html_file

    return wrapper


@pytest.fixture(scope="session")
def get_repo_detailed_info_response(get_mocked_response):
    def wrapper(file_name: str):
        html_file = get_mocked_response(
            prefix="repo_detailed_info/repo_detailed_response", file_name=file_name
        )
        return html_file

    return wrapper


@pytest.fixture(scope="session")
def get_issues_search_response(get_mocked_response):
    def wrapper(file_name: str):
        html_file = get_mocked_response(
            prefix="search/issues_search_response", file_name=file_name
        )
        return html_file

    return wrapper


@pytest.fixture(scope="session")
def get_wikis_search_response(get_mocked_response):
    def wrapper(file_name: str):
        html_file = get_mocked_response(
            prefix="search/wikis_search_response", file_name=file_name
        )
        return html_file

    return wrapper


@pytest.fixture()
def github_client():
    return GithubClient()
