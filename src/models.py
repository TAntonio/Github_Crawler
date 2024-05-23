from typing import Optional, Dict
from pydantic import BaseModel, conlist

from src.enums import SearchType


class SearchRequestParams(BaseModel):
    keywords: conlist(str, min_length=1)
    proxies: conlist(str, min_length=1)
    type: SearchType


class DetailedRepoInfoResponse(BaseModel):
    owner: str
    language_stats: Dict[str, float]


class SearchResultResponse(BaseModel):
    url: str
    extra: Optional[DetailedRepoInfoResponse] = None
