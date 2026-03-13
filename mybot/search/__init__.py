"""Village search module.

Phase 4: Enemy village searching, resource reading, and filtering.

- resources: OCR-based resource reading and threshold comparison
- search: Main village search loop
- prepare: Search preparation and state setup
"""

from mybot.search.prepare import PrepareResult, is_search_active, prepare_search
from mybot.search.resources import SearchFilter, SearchLoot, compare_resources, get_resources
from mybot.search.search import SearchConfig, SearchResult, village_search

__all__ = [
    "compare_resources",
    "get_resources",
    "is_search_active",
    "prepare_search",
    "PrepareResult",
    "SearchConfig",
    "SearchFilter",
    "SearchLoot",
    "SearchResult",
    "village_search",
]
