# Document-writing workflow

scholar-paper-mcp pairs with the `document-writing` skill for academic writing workflows.

## Use cases

- Hackathon proposal: search, track, export BibTeX, paste into pandoc
- Thesis: bulk collect references over weeks, export at the end
- Article: targeted search, track relevant papers, cite in manuscript

## Typical flow

1. Search: `search_papers("machine learning interpretability")`
2. Track interesting results: `add_paper_to_session("manuscript-v1", paper_id)` for each
3. Review: `list_session_papers_tool("manuscript-v1")`
4. Export: `export_session_bibtex("manuscript-v1")` returns a BibTeX string
5. Paste into your document (manuscript.tex, proposal.md, etc.)

## Citation style

Papers come with full metadata. Default BibTeX export uses `@article` entry type. For other formats (CSL-JSON, RIS, EndNote), convert externally.

## Offline mode

If Semantic Scholar is unreachable mid-session, the server falls back to cache. Look for `meta.offline: true` in tool responses to detect this.

For planned offline work, set `SPM_OFFLINE_MODE=true` to skip API calls entirely.

## Multilingual queries

Embeddings are multilingual (100+ languages). Search in Indonesian:

```
search_papers("machine learning interpretabilitas")
```

Finds the same papers as English queries. Try the language that matches your source material.
