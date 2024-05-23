from enum import Enum


class SearchType(str, Enum):
    WIKIS = "Wikis"
    REPOSITORIES = "Repositories"
    ISSUES = "Issues"

    def __str__(self):
        return self.value
