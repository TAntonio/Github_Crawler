from src.managers import GithubClientManager
from src.managers.args_parse_manager import ArgsParseManager

import asyncio


async def main():
    args = ArgsParseManager().parse_args()
    github_client_manager = GithubClientManager()
    results = await github_client_manager.get_search_results_response(args.json_payload)
    print(results)


if __name__ == "__main__":
    asyncio.run(main())
