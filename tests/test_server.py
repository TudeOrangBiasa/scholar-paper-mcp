"""Tests for FastMCP server entry point."""

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from scholar_paper_mcp.exceptions import EmbeddingError
from scholar_paper_mcp.models import CacheMetadata
from scholar_paper_mcp.storage.cache import CachedSemanticScholarClient
from scholar_paper_mcp.storage.db import apply_migrations, connect


def _meta() -> CacheMetadata:
    return CacheMetadata(cached=False, fetched_at=datetime.now(UTC), source="api")


def _empty_search() -> dict:
    return {"data": [], "total": 0, "offset": 0, "next": None}


@pytest.fixture
def real_conn(tmp_path: Path) -> sqlite3.Connection:
    c = connect(tmp_path / "test.db")
    apply_migrations(c)
    c.execute("PRAGMA foreign_keys = OFF")
    return c


def _mock_ctx(conn=None, embedder=None) -> MagicMock:
    cached = AsyncMock(spec=CachedSemanticScholarClient)
    meta = _meta()
    empty = _empty_search()
    cached.search_papers.return_value = (empty, meta)
    cached.get_paper.return_value = (
        {"paperId": "p1", "title": "T", "authors": [{"authorId": "a1", "name": "A"}]},
        meta,
    )
    cached.get_citations.return_value = (
        {"data": [{"citingPaper": {"paperId": "p2"}, "isInfluential": False}]},
        meta,
    )
    cached.get_references.return_value = (
        {"data": [{"citedPaper": {"paperId": "p3"}, "isInfluential": False}]},
        meta,
    )
    cached.search_authors.return_value = (empty, meta)
    cached.get_author.return_value = (
        {"authorId": "a1", "name": "A", "papers": []},
        meta,
    )
    cached.get_author_papers.return_value = (
        {"data": [{"paperId": "p1", "title": "T"}], "total": 1, "offset": 0, "next": None},
        meta,
    )
    cached.get_recommendations.return_value = ({"recommendedPapers": []}, meta)
    state = SimpleNamespace(cached=cached, conn=conn, raw_client=AsyncMock(), embedder=embedder)
    ctx = MagicMock()
    ctx.request_context = state
    ctx.lifespan_context = state
    return ctx


# ── Server setup ───────────────────────────────────────────


def test_server_imports() -> None:
    from scholar_paper_mcp import server

    assert server.mcp is not None
    assert server.lifespan is not None


@pytest.mark.asyncio
async def test_server_registers_all_15_tools() -> None:
    from scholar_paper_mcp.server import mcp

    tools = await mcp.list_tools()
    names = {t.name for t in tools}
    expected = {
        "search_papers",
        "get_paper_details",
        "get_paper_citations",
        "get_paper_references",
        "search_authors",
        "get_author_details",
        "get_author_top_papers",
        "find_author_duplicates",
        "consolidate_authors",
        "get_paper_recommendations",
        "get_related_papers",
        "add_paper_to_session",
        "list_session_papers_tool",
        "remove_from_session_tool",
        "export_session_bibtex",
    }
    missing = expected - names
    assert not missing, f"missing tools: {missing}"
    extra = names - expected
    assert not extra, f"unexpected tools: {extra}"


# ── Wrapper tests (delegate to correct tool function) ──────


@pytest.mark.asyncio
async def test_search_papers_wrapper() -> None:
    from scholar_paper_mcp.server import search_papers

    ctx = _mock_ctx()
    result = await search_papers(ctx, "quantum", limit=5)
    ctx.request_context.cached.search_papers.assert_awaited_once_with(
        "quantum", limit=5, offset=0, fields=None
    )
    parsed = json.loads(result)
    assert "data" in parsed
    assert "meta" in parsed


@pytest.mark.asyncio
async def test_get_paper_details_wrapper(real_conn) -> None:
    from scholar_paper_mcp.server import get_paper_details

    ctx = _mock_ctx(conn=real_conn)
    result = await get_paper_details(ctx, "abc")
    ctx.request_context.cached.get_paper.assert_awaited_once()
    parsed = json.loads(result)
    assert "data" in parsed


@pytest.mark.asyncio
async def test_get_paper_citations_wrapper(real_conn) -> None:
    from scholar_paper_mcp.server import get_paper_citations

    ctx = _mock_ctx(conn=real_conn)
    result = await get_paper_citations(ctx, "abc", limit=50)
    ctx.request_context.cached.get_citations.assert_awaited_once_with(
        "abc", limit=50, offset=0, fields=None
    )
    parsed = json.loads(result)
    assert "data" in parsed


@pytest.mark.asyncio
async def test_get_paper_references_wrapper(real_conn) -> None:
    from scholar_paper_mcp.server import get_paper_references

    ctx = _mock_ctx(conn=real_conn)
    result = await get_paper_references(ctx, "abc", limit=50)
    ctx.request_context.cached.get_references.assert_awaited_once()
    parsed = json.loads(result)
    assert "data" in parsed


@pytest.mark.asyncio
async def test_search_authors_wrapper() -> None:
    from scholar_paper_mcp.server import search_authors

    ctx = _mock_ctx()
    result = await search_authors(ctx, "smith", limit=20)
    ctx.request_context.cached.search_authors.assert_awaited_once_with(
        "smith", limit=20, offset=0, fields=None
    )
    parsed = json.loads(result)
    assert "data" in parsed


@pytest.mark.asyncio
async def test_get_author_details_wrapper(real_conn) -> None:
    from scholar_paper_mcp.server import get_author_details

    ctx = _mock_ctx(conn=real_conn)
    result = await get_author_details(ctx, "a1")
    ctx.request_context.cached.get_author.assert_awaited_once_with("a1", fields=None)
    parsed = json.loads(result)
    assert "data" in parsed


@pytest.mark.asyncio
async def test_get_author_top_papers_wrapper() -> None:
    from scholar_paper_mcp.server import get_author_top_papers

    ctx = _mock_ctx()
    result = await get_author_top_papers(ctx, "a1", limit=15)
    ctx.request_context.cached.get_author_papers.assert_awaited_once_with(
        "a1", limit=100, offset=0, fields=None
    )
    parsed = json.loads(result)
    assert "data" in parsed


@pytest.mark.asyncio
async def test_find_author_duplicates_wrapper() -> None:
    from scholar_paper_mcp.server import find_author_duplicates

    ctx = _mock_ctx()
    result = await find_author_duplicates(ctx, "smith", limit=30, threshold=0.9)
    ctx.request_context.cached.search_authors.assert_awaited_once_with("smith", limit=30, offset=0)
    parsed = json.loads(result)
    assert "data" in parsed


@pytest.mark.asyncio
async def test_get_paper_recommendations_wrapper() -> None:
    from scholar_paper_mcp.server import get_paper_recommendations

    ctx = _mock_ctx()
    result = await get_paper_recommendations(ctx, "src", limit=10)
    ctx.request_context.cached.get_recommendations.assert_awaited_once()
    parsed = json.loads(result)
    assert "data" in parsed


@pytest.mark.asyncio
async def test_add_paper_to_session_wrapper(real_conn) -> None:
    from scholar_paper_mcp.server import add_paper_to_session

    ctx = _mock_ctx(conn=real_conn)
    result = await add_paper_to_session(ctx, "s1", "p1")
    ctx.request_context.cached.get_paper.assert_awaited_once()
    parsed = json.loads(result)
    assert "data" in parsed


# ── Wrapper tests (storage-only, no cached client) ────────


@pytest.mark.asyncio
async def test_list_session_papers_wrapper(real_conn) -> None:
    from scholar_paper_mcp.server import list_session_papers_tool

    ctx = _mock_ctx(conn=real_conn)
    result = await list_session_papers_tool(ctx, "s1")
    parsed = json.loads(result)
    assert "data" in parsed


@pytest.mark.asyncio
async def test_remove_from_session_wrapper(real_conn) -> None:
    from scholar_paper_mcp.server import remove_from_session_tool

    ctx = _mock_ctx(conn=real_conn)
    result = await remove_from_session_tool(ctx, "s1", "p1")
    parsed = json.loads(result)
    assert "data" in parsed


@pytest.mark.asyncio
async def test_export_session_bibtex_wrapper(real_conn) -> None:
    from scholar_paper_mcp.server import export_session_bibtex

    ctx = _mock_ctx(conn=real_conn)
    result = await export_session_bibtex(ctx, "s1")
    parsed = json.loads(result)
    assert "data" in parsed


# ── Wrapper tests (need embedder) ─────────────────────────


@pytest.mark.asyncio
async def test_get_related_papers_wrapper(real_conn) -> None:
    from scholar_paper_mcp.server import get_related_papers

    mock_embedder = MagicMock()
    mock_embedder.encode.return_value = [[0.0] * 384]
    ctx = _mock_ctx(conn=real_conn, embedder=mock_embedder)
    with pytest.raises(EmbeddingError):
        await get_related_papers(ctx, "src", k=5)


@pytest.mark.asyncio
async def test_consolidate_authors_wrapper(real_conn) -> None:
    from scholar_paper_mcp.server import consolidate_authors

    now = datetime.now(UTC)
    real_conn.execute(
        "INSERT INTO authors (author_id, name, affiliations, h_index, paper_count, "
        "aliases, papers_json, fetched_at, ttl_until) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            "canon",
            "Smith, J",
            "[]",
            0,
            0,
            "[]",
            "[]",
            now.isoformat(),
            now.isoformat(),
        ),
    )
    real_conn.commit()
    ctx = _mock_ctx(conn=real_conn)
    result = await consolidate_authors(ctx, "canon", [])
    parsed = json.loads(result)
    assert "data" in parsed


@pytest.mark.asyncio
async def test_lifespan_cleans_up_on_setup_failure() -> None:
    """If apply_migrations raises, conn must close."""
    from scholar_paper_mcp import server

    with patch.object(server, "connect") as mock_connect:
        mock_conn = MagicMock()
        mock_conn.close = MagicMock()
        mock_connect.return_value = mock_conn

        with patch.object(server, "SemanticScholarClient") as mock_cls:
            mock_client = AsyncMock()
            mock_client.close = AsyncMock()
            mock_cls.return_value = mock_client

        with (
            patch.object(server, "apply_migrations", side_effect=RuntimeError("boom")),
            pytest.raises(RuntimeError),
        ):
            async with server.lifespan(server.mcp):
                pass

        mock_conn.close.assert_called_once()
        # raw_client never created (exception before assignment), so close not called
        mock_client.close.assert_not_called()
