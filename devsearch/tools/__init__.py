from .stackoverflow import search_stackoverflow
from .github_issues import search_github_issues
from .docs_search import search_docs
from .web_fallback import search_web

ALL_TOOLS = [search_stackoverflow, search_github_issues, search_docs, search_web]
