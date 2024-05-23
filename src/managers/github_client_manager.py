import asyncio
import random

from typing import Optional, List
from urllib.parse import urljoin
from lxml import html

from src.client import GithubClient
from src.models import (
    SearchRequestParams,
    SearchResultResponse,
    DetailedRepoInfoResponse,
)
from src.constants import BASE_URL
from src.enums import SearchType


RESULTS_LIST_XPATH = '//div[@data-testid="results-list"]'
RESULTS_ITEM_CONTAINER_XPATH = (
    f'{RESULTS_LIST_XPATH}//div[contains(@class, "search-title")]'
)
DETAILED_INFO_LANGUAGES_CONTAINER_XPATH = (
    f"//div[@class='Layout-sidebar']//div[(./h2/text()='Languages')]/ul/li/a"
)


class InvalidHtmlError(Exception):
    pass


class GithubClientManager:

    def __init__(self, github_client: Optional[GithubClient] = None):
        self.github_client = github_client or GithubClient()

    async def get_search_results_response(self, json_payload: str):
        request_params = SearchRequestParams.model_validate_json(json_payload)
        random_proxy = self._get_random_proxy(request_params.proxies)

        items_collection = await self._fill_with_base_info(request_params, random_proxy)
        if request_params.type == SearchType.REPOSITORIES:
            await self._extend_repos_with_detailed_info(items_collection, random_proxy)

        items_collection = [
            item.model_dump(exclude_unset=True) for item in items_collection
        ]
        return items_collection

    async def _fill_with_base_info(
        self,
        request_params: SearchRequestParams,
        random_proxy: str,
    ):
        tasks = []
        for keyword in request_params.keywords:
            result_page_content_coro = self.github_client.get_search_results_page(
                query=keyword,
                search_type=request_params.type,
                proxy=random_proxy,
            )
            tasks.append(result_page_content_coro)

        results = await asyncio.gather(*tasks)
        items_collection = []
        for result_page_content in results:
            response_tree = self._parse_response_text(result_page_content)
            items_tree = response_tree.xpath(RESULTS_ITEM_CONTAINER_XPATH)
            if not items_tree:
                raise InvalidHtmlError("Items section not found")

            for item in items_tree:
                item_path = item.xpath("./a/@href")[0]
                item_full_url = urljoin(BASE_URL, item_path)
                item_response = SearchResultResponse(url=item_full_url)
                items_collection.append(item_response)

        return items_collection

    async def _extend_repos_with_detailed_info(
        self, items_collection: List[SearchResultResponse], random_proxy: str
    ):
        urls = [item.url for item in items_collection]
        tasks = []
        for url in urls:
            result_page_coro = self.github_client.get_detailed_repository_info_page(
                repo_url=url,
                proxy=random_proxy,
            )
            tasks.append(result_page_coro)

        results = await asyncio.gather(*tasks)
        for index, result_page_content in enumerate(results, 0):
            response_tree = self._parse_response_text(result_page_content)
            languages = response_tree.xpath(DETAILED_INFO_LANGUAGES_CONTAINER_XPATH)

            owner = urls[index].split("/")[-2]
            languages_stats = {}
            for language in languages:
                language, percent = language.xpath("./span/text()")
                languages_stats[language] = percent.replace("%", "")

            detailed = DetailedRepoInfoResponse(
                owner=owner, language_stats=languages_stats
            )
            items_collection[index].extra = detailed

    @staticmethod
    def _parse_response_text(response_text: str):
        return html.fromstring(response_text)

    @staticmethod
    def _get_random_proxy(proxies_list: List[str]):
        return str(random.choice(proxies_list))
