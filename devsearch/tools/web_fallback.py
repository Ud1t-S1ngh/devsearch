"""General DuckDuckGo web search — the final fallback when other sources come up empty."""

from langchain_core.tools import tool


@tool
def search_web(query: str) -> str:
    """
    General web search using DuckDuckGo. Use this as a LAST RESORT when Stack Overflow,
    official docs, and GitHub Issues have not provided a satisfactory answer.
    Also useful for very recent topics, blog posts, and tutorials.

    Args:
        query: The search query. Be specific — include error messages, library names,
               and versions for best results.
    """
    try:
        from duckduckgo_search import DDGS

        results = []
        with DDGS() as ddgs:
            hits = list(ddgs.text(query, max_results=5))

        if not hits:
            return (
                "No web results found. The query may be too specific or the search is rate-limited.\n"
                "Suggested links to check manually:\n"
                f"  • https://stackoverflow.com/search?q={query.replace(' ', '+')}\n"
                f"  • https://github.com/search?q={query.replace(' ', '+')}&type=issues\n"
                f"  • https://www.google.com/search?q={query.replace(' ', '+')}"
            )

        for hit in hits:
            title = hit.get("title", "")
            snippet = hit.get("body", "")[:400]
            url = hit.get("href", "")
            results.append(f"🌐 {title}\n   {url}\n   {snippet}\n")

        return "=== Web Search Results ===\n\n" + "\n---\n".join(results)

    except ImportError:
        return "duckduckgo-search package not installed. Run: pip install duckduckgo-search"
    except Exception as e:
        return f"Web search failed: {str(e)}"
