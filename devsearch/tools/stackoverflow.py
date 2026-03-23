"""Stack Overflow search via the free Stack Exchange API — no key required."""

import requests
from langchain_core.tools import tool


@tool
def search_stackoverflow(query: str) -> str:
    """
    Search Stack Overflow for answers to a coding question or error.
    Returns top answers with vote counts and links.
    Use this FIRST for any programming question or error message.

    Args:
        query: The coding question or error to search for.
    """
    try:
        # Search for questions
        search_url = "https://api.stackexchange.com/2.3/search/advanced"
        params = {
            "q": query,
            "site": "stackoverflow",
            "order": "desc",
            "sort": "relevance",
            "accepted": "True",
            "pagesize": 3,
            "filter": "withbody",
        }
        resp = requests.get(search_url, params=params, timeout=8)
        resp.raise_for_status()
        data = resp.json()

        if not data.get("items"):
            # Fallback: search without requiring accepted answer
            params.pop("accepted")
            resp = requests.get(search_url, params=params, timeout=8)
            data = resp.json()

        items = data.get("items", [])
        if not items:
            return "No Stack Overflow results found for this query."

        results = []
        for item in items[:3]:
            question_id = item["question_id"]
            title = item.get("title", "")
            score = item.get("score", 0)
            answer_count = item.get("answer_count", 0)
            link = item.get("link", "")

            # Fetch the top answer
            answer_url = f"https://api.stackexchange.com/2.3/questions/{question_id}/answers"
            a_params = {
                "site": "stackoverflow",
                "order": "desc",
                "sort": "votes",
                "pagesize": 1,
                "filter": "withbody",
            }
            a_resp = requests.get(answer_url, params=a_params, timeout=8)
            a_data = a_resp.json()
            answers = a_data.get("items", [])

            answer_text = ""
            answer_score = 0
            if answers:
                import html
                import re
                raw = answers[0].get("body", "")
                # Strip HTML tags for readability
                clean = re.sub(r"<[^>]+>", "", html.unescape(raw))
                answer_text = clean[:800].strip()
                answer_score = answers[0].get("score", 0)

            results.append(
                f"[Q] {title}\n"
                f"  Votes: {score} | Answers: {answer_count} | Link: {link}\n"
                f"  Top Answer (score {answer_score}):\n  {answer_text}\n"
            )

        return "=== Stack Overflow Results ===\n\n" + "\n---\n".join(results)

    except requests.exceptions.Timeout:
        return "Stack Overflow search timed out. Try the web fallback."
    except Exception as e:
        return f"Stack Overflow search failed: {str(e)}"
