"""Official documentation search — scoped DuckDuckGo queries to known doc sites."""

from langchain_core.tools import tool

DOCS_DOMAINS = {
    "python": "docs.python.org",
    "javascript": "developer.mozilla.org",
    "typescript": "www.typescriptlang.org/docs",
    "react": "react.dev",
    "nodejs": "nodejs.org/docs",
    "rust": "doc.rust-lang.org",
    "go": "pkg.go.dev",
    "java": "docs.oracle.com/en/java",
    "cpp": "en.cppreference.com",
    "c": "en.cppreference.com",
    "django": "docs.djangoproject.com",
    "fastapi": "fastapi.tiangolo.com",
    "flask": "flask.palletsprojects.com",
    "pandas": "pandas.pydata.org/docs",
    "numpy": "numpy.org/doc",
    "pytorch": "pytorch.org/docs",
    "tensorflow": "www.tensorflow.org/api_docs",
    "langchain": "python.langchain.com",
    "docker": "docs.docker.com",
    "kubernetes": "kubernetes.io/docs",
    "aws": "docs.aws.amazon.com",
    "sql": "dev.mysql.com/doc",
    "postgresql": "www.postgresql.org/docs",
    "mongodb": "www.mongodb.com/docs",
}

FALLBACK_DOMAINS = [
    "docs.python.org",
    "developer.mozilla.org",
    "devdocs.io",
    "dev.docs.microsoft.com",
]


def _detect_domain(query: str, lang_hint: str = "") -> list[str]:
    """Detect relevant doc domains from query keywords and language hint."""
    combined = (query + " " + lang_hint).lower()
    matched = []
    for key, domain in DOCS_DOMAINS.items():
        if key in combined:
            matched.append(domain)
    return matched[:2] if matched else FALLBACK_DOMAINS[:2]


@tool
def search_docs(query: str) -> str:
    """
    Search official documentation for functions, APIs, and language features.
    Best for understanding how something works, API signatures, and official examples.
    Use this when you need precise, authoritative information about a library or language feature.

    Args:
        query: The function, API, or concept to look up in official documentation.
               Include the language or library name for better results (e.g., 'python list comprehension',
               'react useEffect hook', 'pandas groupby agg').
    """
    try:
        from duckduckgo_search import DDGS

        domains = _detect_domain(query)
        site_filter = " OR ".join(f"site:{d}" for d in domains)
        search_query = f"{query} ({site_filter})"

        results = []
        with DDGS() as ddgs:
            hits = list(ddgs.text(search_query, max_results=4))

        if not hits:
            with DDGS() as ddgs:
                hits = list(ddgs.text(f"{query} official documentation", max_results=4))

        if not hits:
            return "No official documentation results found."

        for hit in hits[:4]:
            title = hit.get("title", "")
            snippet = hit.get("body", "")[:400]
            url = hit.get("href", "")
            results.append(f"📄 {title}\n   {url}\n   {snippet}\n")

        return "=== Official Docs Results ===\n\n" + "\n---\n".join(results)

    except ImportError:
        return "duckduckgo-search package not installed. Run: pip install duckduckgo-search"
    except Exception as e:
        return f"Docs search failed: {str(e)}"
