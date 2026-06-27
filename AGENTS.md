# scholar-paper-mcp

Hybrid MCP server for Semantic Scholar. 15 tools, persistent SQLite cache, offline fallback, multilingual semantic search.

Status: 13/14 issues done, server live. Tranche F (docs) in progress.

Stack: Python 3.13, FastMCP, httpx, SQLite + sqlite-vec, ONNX (multilingual-e5-small), pytest + ruff + ty.

Conventions:
- Caveman prose for written content (no em-dash, no ASCII art, Mermaid for diagrams).
- "Author (Year)" citation style for academic refs.
- Type hints everywhere.
- uv for deps, pyproject.toml is source of truth.
- TDD + ponytail: tests first via public interfaces, minimum code, no premature abstractions.

Workflow pattern: TDD (red-green-refactor) + ponytail (full intensity) + database-migrations for DDL.

Skills stack:
- tdd, ponytail, coding-standards (every issue)
- database-migrations (DDL changes)
- mcp-server-patterns (server wiring)
- humanizer (any prose, auto-loaded)

Test stats: 239 pass, 9 model-skip (mE5 not downloaded).

See `docs/PLAN.md` for the full plan, `docs/CONFIGURATION.md` for env vars, `docs/WORKFLOW.md` for document-writing integration.
