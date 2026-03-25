"""GitHub Issues + Discussions search via the free GitHub REST API."""

import os
import requests
from langchain_core.tools import tool


@tool
def search_github_issues(query: str) -> str:
    """
    Search GitHub Issues and Pull Requests for bug reports, discussions, and fixes.
    Best for library errors, version-specific bugs, and open-source project questions.
    Use this when Stack Overflow doesn't have the answer or for library-specific errors.

    Args:
        query: The issue, error, or topic to search for on GitHub.
    """
    try:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        token = os.getenv("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"

        url = "https://api.github.com/search/issues"
        params = {
            "q": f"{query} is:issue",
            "sort": "reactions",
            "order": "desc",
            "per_page": 4,
        }
        resp = requests.get(url, headers=headers, params=params, timeout=8)

        if resp.status_code == 403:
            return "GitHub API rate limit reached. Try again in a minute or set GITHUB_TOKEN in your .env file."
        resp.raise_for_status()

        data = resp.json()
        items = data.get("items", [])

        if not items:
            return "No GitHub issues found for this query."

        results = []
        for issue in items[:4]:
            title = issue.get("title", "")
            state = issue.get("state", "")
            comments = issue.get("comments", 0)
            reactions = issue.get("reactions", {}).get("total_count", 0)
            body = (issue.get("body") or "")[:500].strip()
            html_url = issue.get("html_url", "")
            repo = html_url.split("/issues/")[0].replace("https://github.com/", "") if "/issues/" in html_url else ""

            state_icon = "✅" if state == "closed" else "🔴"

            results.append(
                f"{state_icon} [{repo}] {title}\n"
                f"  Status: {state} | Comments: {comments} | Reactions: {reactions}\n"
                f"  Link: {html_url}\n"
                f"  Description: {body[:400]}{'...' if len(body) > 400 else ''}\n"
            )

        return "=== GitHub Issues Results ===\n\n" + "\n---\n".join(results)

    except requests.exceptions.Timeout:
        return "GitHub search timed out. Try the web fallback."
    except Exception as e:
        return f"GitHub Issues search failed: {str(e)}"
