"""Verify documentation stays consistent with code."""

import json
import re
from pathlib import Path

import pytest

from scholar_paper_mcp.config import Settings


@pytest.mark.asyncio
async def test_readme_lists_all_tools() -> None:
    """README tools table must include all 15 tool names."""
    from scholar_paper_mcp.server import mcp

    readme = Path(__file__).parent.parent / "README.md"
    text = readme.read_text()
    tools = await mcp.list_tools()
    for tool in tools:
        assert tool.name in text, f"tool {tool.name} not in README"


def test_configuration_documents_all_env_vars() -> None:
    """CONFIGURATION.md must document every SPM_* env var in Settings."""
    doc = Path(__file__).parent.parent / "docs" / "CONFIGURATION.md"
    text = doc.read_text()
    settings_fields = Settings.model_fields
    for name in settings_fields:
        env_var = f"SPM_{name.upper()}"
        assert env_var in text, f"{env_var} not in CONFIGURATION.md"


def test_opencode_registration_is_valid_json() -> None:
    """OpenCode JSON snippet in README must parse."""
    readme = Path(__file__).parent.parent / "README.md"
    text = readme.read_text()
    match = re.search(r"```json\n(.*?)\n```", text, re.DOTALL)
    assert match, "no ```json``` block in README"
    parsed = json.loads(match.group(1))
    assert "mcpServers" in parsed
    assert "scholar-paper-mcp" in parsed["mcpServers"]


def test_agents_md_mentions_current_state() -> None:
    """AGENTS.md should reflect current project state."""
    agents = Path(__file__).parent.parent / "AGENTS.md"
    text = agents.read_text()
    assert "Status" in text
    assert "15 tools" in text
    assert "TDD" in text
    assert "ponytail" in text
