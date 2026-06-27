from scholar_paper_mcp.tools.authors import (
    consolidate_authors,
    find_author_duplicates,
    get_author_details,
    get_author_top_papers,
    search_authors,
)
from scholar_paper_mcp.tools.papers import (
    get_paper_citations,
    get_paper_details,
    get_paper_references,
    search_papers,
)
from scholar_paper_mcp.tools.recommendations import (
    get_paper_recommendations,
    get_related_papers,
)

__all__ = [
    "consolidate_authors",
    "find_author_duplicates",
    "get_author_details",
    "get_author_top_papers",
    "get_paper_citations",
    "get_paper_details",
    "get_paper_recommendations",
    "get_paper_references",
    "get_related_papers",
    "search_authors",
    "search_papers",
]
