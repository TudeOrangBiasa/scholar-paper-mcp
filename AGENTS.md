# scholar-paper-mcp

Hybrid MCP server for Semantic Scholar with local SQLite cache and offline fallback.

Status: planning. No code yet. First build slice is issue #1.

Stack: Python 3.13, FastMCP, httpx, SQLite + sqlite-vec, ONNX MiniLM, pytest + ruff + ty.

Conventions:
- Caveman prose for written content (no em-dash, no ASCII art, Mermaid for diagrams).
- "Author (Year)" citation style for academic refs.
- Type hints everywhere.
- uv for deps, pyproject.toml is source of truth.

See `docs/PLAN.md` for full plan.
