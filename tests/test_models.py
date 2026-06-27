"""Tests for models module."""

from datetime import datetime, timezone
from typing import Literal, cast

import pytest
from pydantic import HttpUrl, ValidationError

from scholar_paper_mcp.models import (
    Author,
    AuthorBrief,
    AuthorSearchResult,
    CacheMetadata,
    CitationEdge,
    Paper,
    PaperBrief,
    PaperSearchResult,
    SearchResult,
    ToolResponse,
)


def test_paper_minimal() -> None:
    """Paper validates with only paper_id."""
    p = Paper(paper_id="abc")
    assert p.paper_id == "abc"
    assert p.title is None
    assert p.abstract is None
    assert p.year is None


def test_paper_all_optional_defaults() -> None:
    """All optional Paper fields have sensible defaults."""
    p = Paper(paper_id="abc")
    assert p.citation_count == 0
    assert p.reference_count == 0
    assert p.influential_citation_count == 0
    assert p.is_open_access is False
    assert p.publication_types == []
    assert p.fields_of_study == []
    assert p.external_ids == {}
    assert p.authors == []
    assert p.embedding is None


def test_paper_embedding_default_none() -> None:
    """Paper.embedding defaults to None."""
    p = Paper(paper_id="abc")
    assert p.embedding is None


def test_paper_with_embedding() -> None:
    """Paper.embedding accepts list[float]."""
    p = Paper(paper_id="abc", embedding=[0.1, 0.2, 0.3])
    assert p.embedding == [0.1, 0.2, 0.3]


def test_author_brief_minimal() -> None:
    """AuthorBrief validates with required fields only."""
    a = AuthorBrief(author_id="123", name="Dr. Smith")
    assert a.author_id == "123"
    assert a.name == "Dr. Smith"
    assert a.affiliations == []


def test_author_with_papers() -> None:
    """Author validates with nested PaperBrief list."""
    a = Author(
        author_id="123",
        name="Dr. Smith",
        papers=[PaperBrief(paper_id="abc")],
    )
    assert len(a.papers) == 1
    assert a.papers[0].paper_id == "abc"


def test_author_aliases() -> None:
    """Author aliases default to empty list."""
    a = Author(author_id="123", name="Dr. Smith")
    assert a.aliases == []


def test_search_result_generic_paper() -> None:
    """SearchResult[Paper] validates."""
    sr = SearchResult[Paper](query="machine learning", total=0, data=[])
    assert sr.query == "machine learning"
    assert sr.total == 0
    assert sr.offset == 0
    assert sr.next_offset is None


def test_search_result_with_data() -> None:
    """SearchResult[Paper] holds Paper instances."""
    sr = SearchResult[Paper](
        query="test",
        total=2,
        data=[Paper(paper_id="a"), Paper(paper_id="b")],
    )
    assert len(sr.data) == 2
    assert sr.data[0].paper_id == "a"


def test_paper_search_result_alias() -> None:
    """PaperSearchResult is an alias for SearchResult[Paper]."""
    pr = PaperSearchResult(query="q", total=0, data=[])
    assert isinstance(pr, SearchResult)


def test_author_search_result_alias() -> None:
    """AuthorSearchResult is an alias for SearchResult[Author]."""
    ar = AuthorSearchResult(query="q", total=0, data=[])
    assert isinstance(ar, SearchResult)


def test_cache_metadata_minimal() -> None:
    """CacheMetadata validates with required fields."""
    cm = CacheMetadata(
        cached=True,
        fetched_at=datetime.now(timezone.utc),
        source="cache",
    )
    assert cm.cached is True
    assert cm.offline is False
    assert cm.ttl_until is None


def test_cache_metadata_valid_sources() -> None:
    """CacheMetadata accepts all valid sources."""
    now = datetime.now(timezone.utc)
    for source in ("cache", "api", "offline_cache"):
        cm = CacheMetadata(cached=True, fetched_at=now, source=source)  # type: ignore[arg-type]
        assert cm.source == source


def test_cache_metadata_invalid_source() -> None:
    """CacheMetadata rejects invalid source literal."""
    with pytest.raises(ValidationError):
        CacheMetadata(
            cached=True,
            fetched_at=datetime.now(timezone.utc),
            source=cast(Literal["cache", "api", "offline_cache"], "invalid"),
        )


def test_tool_response_generic() -> None:
    """ToolResponse[PaperSearchResult] validates with nested types."""
    sr = SearchResult[Paper](
        query="test",
        total=1,
        data=[Paper(paper_id="abc")],
    )
    cm = CacheMetadata(
        cached=False,
        fetched_at=datetime.now(timezone.utc),
        source="api",
    )
    tr = ToolResponse[PaperSearchResult](data=sr, meta=cm)
    assert tr.data.total == 1
    assert tr.meta.source == "api"
    assert tr.data.data[0].paper_id == "abc"


def test_tool_response_generic_author() -> None:
    """ToolResponse[Author] validates."""
    a = Author(author_id="1", name="Researcher")
    cm = CacheMetadata(
        cached=True,
        fetched_at=datetime.now(timezone.utc),
        source="cache",
    )
    tr = ToolResponse[Author](data=a, meta=cm)
    assert tr.data.name == "Researcher"


def test_extra_fields_ignored() -> None:
    """Extra fields are silently ignored."""
    p = Paper.model_validate({"paper_id": "abc", "title": "X", "unknown_field": "ignored"})
    assert p.title == "X"


def test_http_url_valid() -> None:
    """HttpUrl accepts valid URL string."""
    url = HttpUrl("https://example.com/p.pdf")
    p = Paper(paper_id="abc", open_access_pdf_url=url)
    assert p.open_access_pdf_url is not None
    assert str(p.open_access_pdf_url) == "https://example.com/p.pdf"


def test_http_url_invalid() -> None:
    """HttpUrl rejects invalid URL string."""
    with pytest.raises(ValidationError):
        Paper.model_validate({"paper_id": "abc", "open_access_pdf_url": "not a url"})


def test_citation_edge_minimal() -> None:
    """CitationEdge validates with required fields."""
    ce = CitationEdge(from_paper_id="a", to_paper_id="b")
    assert ce.from_paper_id == "a"
    assert ce.to_paper_id == "b"
    assert ce.is_influential is False
    assert ce.context_intent is None


def test_citation_edge_with_intent() -> None:
    """CitationEdge with context_intent."""
    ce = CitationEdge(
        from_paper_id="a",
        to_paper_id="b",
        context_intent=["background"],
        is_influential=True,
    )
    assert ce.context_intent == ["background"]
    assert ce.is_influential is True


def test_paper_brief_minimal() -> None:
    """PaperBrief validates with only paper_id."""
    pb = PaperBrief(paper_id="abc")
    assert pb.citation_count == 0
    assert pb.venue is None
