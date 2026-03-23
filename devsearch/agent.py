"""
Core ReAct agent — LangChain + Groq LLaMA 3.3 70B.
Handles query routing, tool orchestration, and structured answer synthesis.
"""

from __future__ import annotations

import re
import time
from typing import Callable

from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

from .tools import ALL_TOOLS

# ─── Prompt ──────────────────────────────────────────────────────────────────

REACT_PROMPT = PromptTemplate.from_template(
    """You are DevSearch, an expert programming assistant that researches coding questions
and errors using real sources. You NEVER hallucinate — if you don't know, say so.

## Research Strategy (follow this order):
1. **search_stackoverflow** — always try this first for any coding Q&A
2. **search_docs** — use for official API/function docs and language features
3. **search_github_issues** — use for library bugs, version errors, framework issues
4. **search_web** — last resort fallback for anything not found above

## Rules:
- Use tools to find REAL answers, never guess
- For error messages, always search the exact error text
- Combine findings from multiple sources when relevant
- If nothing useful is found, honestly say so and provide manual search links
- Always cite which sources your answer came from

## FINAL ANSWER FORMAT:
When you have enough information, respond with Final Answer using EXACTLY this structure:

```
EXPLANATION:
[Clear explanation of the problem and solution in 2-5 sentences]

CODE:
[Working code snippet if applicable. Use ``` fences with language tag. Write "No code needed" if N/A]

SOURCES:
[Numbered list of sources used, ranked by relevance. Include URLs.]

CONFIDENCE: [High / Medium / Low]
REASON: [One sentence explaining your confidence level]
```

## Available tools:
{tools}

Tool names: {tool_names}

## Question:
{input}

{agent_scratchpad}"""
)

# ─── Callback for live reasoning display ─────────────────────────────────────

from langchain_core.callbacks.base import BaseCallbackHandler


class ReasoningCallback(BaseCallbackHandler):
    """Streams agent Thought → Action → Observation to a Rich-aware printer."""

    def __init__(self, print_fn: Callable[[str, str], None]):
        """
        Args:
            print_fn: callable(text, style) for Rich-aware printing.
        """
        self.print_fn = print_fn
        self._step = 0

    def on_agent_action(self, action, **kwargs):
        self._step += 1
        self.print_fn(
            f"[Step {self._step}] Using tool: {action.tool}",
            "action",
        )
        if action.tool_input:
            query = (
                action.tool_input.get("query", action.tool_input)
                if isinstance(action.tool_input, dict)
                else str(action.tool_input)
            )
            self.print_fn(f'  Query: "{query}"', "query")

    def on_tool_end(self, output: str, **kwargs):
        preview = output[:120].replace("\n", " ").strip()
        self.print_fn(f"  ↳ {preview}{'...' if len(output) > 120 else ''}", "observation")

    def on_agent_finish(self, finish, **kwargs):
        self.print_fn("Agent finished reasoning.", "done")


# ─── Agent builder ────────────────────────────────────────────────────────────


def build_agent(groq_api_key: str, verbose: bool = False) -> AgentExecutor:
    """Build and return the configured AgentExecutor."""
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        groq_api_key=groq_api_key,
        temperature=0.1,
        max_tokens=2048,
    )

    agent = create_react_agent(llm=llm, tools=ALL_TOOLS, prompt=REACT_PROMPT)

    return AgentExecutor(
        agent=agent,
        tools=ALL_TOOLS,
        verbose=False,  # We handle our own output via callbacks
        handle_parsing_errors=True,
        max_iterations=8,
        max_execution_time=30,
        return_intermediate_steps=True,
    )


# ─── Answer parser ────────────────────────────────────────────────────────────


def parse_answer(raw: str) -> dict:
    """
    Parse the structured Final Answer into components.
    Returns dict with keys: explanation, code, sources, confidence, reason, raw.
    """
    result = {
        "explanation": "",
        "code": "",
        "sources": [],
        "confidence": "Low",
        "reason": "",
        "raw": raw,
    }

    # Extract EXPLANATION
    m = re.search(r"EXPLANATION:\s*(.*?)(?=CODE:|SOURCES:|CONFIDENCE:|$)", raw, re.DOTALL)
    if m:
        result["explanation"] = m.group(1).strip()

    # Extract CODE block
    m = re.search(r"CODE:\s*(.*?)(?=SOURCES:|CONFIDENCE:|$)", raw, re.DOTALL)
    if m:
        code_text = m.group(1).strip()
        if code_text.lower() not in ("no code needed", "n/a", ""):
            result["code"] = code_text

    # Extract SOURCES
    m = re.search(r"SOURCES:\s*(.*?)(?=CONFIDENCE:|$)", raw, re.DOTALL)
    if m:
        sources_raw = m.group(1).strip()
        sources = [
            line.lstrip("0123456789.-) ").strip()
            for line in sources_raw.splitlines()
            if line.strip()
        ]
        result["sources"] = [s for s in sources if s]

    # Extract CONFIDENCE
    m = re.search(r"CONFIDENCE:\s*(High|Medium|Low)", raw, re.IGNORECASE)
    if m:
        result["confidence"] = m.group(1).capitalize()

    # Extract REASON
    m = re.search(r"REASON:\s*(.+?)(?:\n|$)", raw)
    if m:
        result["reason"] = m.group(1).strip()

    return result


# ─── Main run function ────────────────────────────────────────────────────────


def run_query(
    query: str,
    context: str = "",
    lang: str = "",
    groq_api_key: str = "",
    verbose: bool = False,
    print_fn: Callable[[str, str], None] | None = None,
) -> dict:
    """
    Run the DevSearch agent on a query.

    Args:
        query:       The user's coding question.
        context:     Optional error traceback or code context.
        lang:        Optional language hint (python, javascript, etc.).
        groq_api_key: Groq API key.
        verbose:     Whether to show live reasoning.
        print_fn:    Callback for live reasoning output (text, style).

    Returns:
        Parsed answer dict from parse_answer().
    """
    # Build the full question
    full_query = query
    if lang:
        full_query = f"[Language: {lang}] {full_query}"
    if context:
        full_query += f"\n\nError/Context:\n```\n{context}\n```"

    # Set up callbacks
    callbacks = []
    if verbose and print_fn:
        callbacks.append(ReasoningCallback(print_fn=print_fn))

    # Build and run agent
    executor = build_agent(groq_api_key=groq_api_key, verbose=verbose)

    start = time.time()
    result = executor.invoke(
        {"input": full_query},
        config={"callbacks": callbacks},
    )
    elapsed = time.time() - start

    raw_output = result.get("output", "")
    parsed = parse_answer(raw_output)
    parsed["elapsed"] = round(elapsed, 1)
    return parsed
