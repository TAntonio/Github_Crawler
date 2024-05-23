import asyncio

import backoff
import httpx

from src.constants import BASE_URL


DEFAULT_TIMEOUT = 5
DEFAULT_HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,"
    "image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
    "accept-encoding": "gzip, deflate",
    "connection": "keep-alive",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:125.0) Gecko/20100101 Firefox/125.0",
    "host": "github.com",
}


class GithubClient:

    def __init__(self, concurrency: int = 2):
        self.semaphore = asyncio.Semaphore(concurrency)

    @staticmethod
    def get_search_endpoint():
        return f"{BASE_URL}/search"

    @staticmethod
    def get_prepared_proxies_param(proxy: str):
        if not proxy.startswith("http"):
            proxy = "http://" + proxy
        proxies = {"http://": proxy, "https://": proxy}
        return proxies

    async def get_search_results_page(
        self,
        query: str,
        search_type: str,
        proxy: str,
    ) -> str:
        endpoint = self.get_search_endpoint()
        params = {"q": query, "type": search_type}
        response = await self._perform_request(
            "GET",
            full_url=endpoint,
            params=params,
            proxy=proxy,
        )
        return response.text

    async def get_detailed_repository_info_page(
        self,
        repo_url: str,
        proxy: str,
    ) -> str:
        response = await self._perform_request(
            "GET",
            full_url=repo_url,
            proxy=proxy,
        )
        return response.text

    @backoff.on_exception(backoff.fibo, httpx.RequestError, max_tries=2)
    async def _perform_request(
        self,
        method: str,
        full_url: str,
        proxy: str,
        **kwargs,
    ):
        async with self.semaphore:
            proxies = self.get_prepared_proxies_param(proxy)
            async with httpx.AsyncClient(
                headers=DEFAULT_HEADERS,
                proxies=proxies,
            ) as client:
                response = await client.request(
                    method, full_url, timeout=DEFAULT_TIMEOUT, **kwargs
                )
                response.raise_for_status()
                return response
