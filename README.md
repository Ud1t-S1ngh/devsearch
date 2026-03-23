# 🔍 DevSearch

**AI-powered CLI that researches your coding questions across Stack Overflow, official docs, GitHub Issues, and the web — in under 15 seconds.**

```
 ██████╗ ███████╗██╗   ██╗███████╗███████╗ █████╗ ██████╗  ██████╗██╗  ██╗
 ██╔══██╗██╔════╝██║   ██║██╔════╝██╔════╝██╔══██╗██╔══██╗██╔════╝██║  ██║
 ██║  ██║█████╗  ██║   ██║███████╗█████╗  ███████║██████╔╝██║     ███████║
 ██║  ██║██╔══╝  ╚██╗ ██╔╝╚════██║██╔══╝  ██╔══██║██╔══██╗██║     ██╔══██║
 ██████╔╝███████╗ ╚████╔╝ ███████║███████╗██║  ██║██║  ██║╚██████╗██║  ██║
 ╚═════╝ ╚══════╝  ╚═══╝  ╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝
```

## Features

- 🤖 **ReAct Agent** — LangChain + Groq LLaMA 3.3 70B autonomously decides which sources to check
- 🔁 **Fallback chain** — Stack Overflow → Official Docs → GitHub Issues → DuckDuckGo Web
- 💡 **Live reasoning** — `--verbose` shows Thought → Action → Observation in real time
- 📊 **Confidence scoring** — High / Medium / Low with reasoning
- 🔗 **Source transparency** — every part of the answer cites its source
- 🚫 **Never hallucinates** — flags uncertainty, gives manual search links when stuck

## Quick Start

### 1. Install

```bash
git clone https://github.com/yourname/devsearch
cd devsearch
pip install -e .
```

### 2. Get your free Groq API key

Sign up at [console.groq.com](https://console.groq.com) — it's free, no credit card needed.

### 3. Configure

```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

Or export directly:
```bash
export GROQ_API_KEY=gsk_your_key_here
```

### 4. Run

```bash
devs "how do I flatten a nested list in Python"
```

## Usage

```bash
# Basic question
devs "how do I flatten a nested list in Python"

# With error context (paste your traceback)
devs --context "RecursionError: maximum depth exceeded" "fix recursion in Python"

# With language hint
devs --lang javascript "async await error handling best practices"

# Verbose mode — see full agent reasoning
devs --verbose "what is the difference between FAISS and Pinecone"

# Short flags
devs -l rust -v "how to handle Option in a match statement"
devs -c "ModuleNotFoundError: No module named 'cv2'" "install opencv python"

# Interactive mode (no query argument)
devs
```

## Example Output

```
┌─────────────────────────────────────────────────────────────┐
│ Explanation                                                  │
│                                                              │
│ To flatten a nested list in Python, the most idiomatic     │
│ approach is using itertools.chain.from_iterable() for       │
│ one level deep, or a recursive function / sum() trick for   │
│ arbitrary depth...                                           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────── Code (python) ───────────────┐
│  1  import itertools                                         │
│  2                                                           │
│  3  # One level deep                                        │
│  4  nested = [[1, 2], [3, 4], [5]]                         │
│  5  flat = list(itertools.chain.from_iterable(nested))      │
│  6  # [1, 2, 3, 4, 5]                                      │
└─────────────────────────────────────────────────────────────┘

  #  Source
  1  https://stackoverflow.com/questions/952914/...
  2  https://docs.python.org/3/library/itertools.html

  🟢 Confidence: High  —  Multiple high-voted SO answers agree.

  ⏱  Completed in 8.3s
```

## Verbose Mode

```bash
devs --verbose "why does my pandas groupby lose columns"
```

```
─────────────────── 🔍 Agent Reasoning ───────────────────

→ [Step 1] Using tool: search_stackoverflow
    Query: "pandas groupby lose columns"
    ↳ === Stack Overflow Results === [Q] Pandas groupby...

→ [Step 2] Using tool: search_docs
    Query: "pandas groupby as_index parameter"
    ↳ === Official Docs Results === 📄 pandas.DataFrame.groupby...

✓ Agent finished reasoning.
```

## Architecture

```
User Query / Error
       ↓
  ReAct Agent (LangChain + Groq LLaMA 3.3 70B)
       ↓
  Thinks: "What sources should I check?"
       ↓
┌──────────────────────────────────────┐
│  Tool 1: Stack Overflow Search       │
│  Tool 2: Official Docs Search        │
│  Tool 3: GitHub Issues Search        │
│  Tool 4: DuckDuckGo Web Fallback     │
└──────────────────────────────────────┘
       ↓
  Agent synthesizes across sources
       ↓
  Structured Answer:
  - Explanation
  - Working code snippet
  - Sources ranked by relevance
  - Confidence level
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Agent logic | LangChain ReAct |
| LLM | Groq / LLaMA 3.3 70B |
| Stack Overflow | Stack Exchange API (free, no key) |
| GitHub Issues | GitHub REST API (free tier) |
| Docs Search | DuckDuckGo scoped search |
| Web Fallback | DuckDuckGo |
| CLI | Python argparse + Rich |

## Optional: GitHub Token

For higher GitHub API rate limits (60 → 5000 req/hr):

1. Go to [github.com/settings/tokens](https://github.com/settings/tokens)
2. Generate a token with no scopes needed
3. Add to `.env`: `GITHUB_TOKEN=ghp_your_token`

## Troubleshooting

**`GROQ_API_KEY not found`** — Create a `.env` file with your key, or `export GROQ_API_KEY=...`

**`GitHub API rate limit`** — Add a `GITHUB_TOKEN` to `.env` (free, no scopes needed)

**`duckduckgo_search` errors** — DuckDuckGo may rate-limit. Wait 30s and retry.

**Slow responses** — Groq is very fast, but network calls to 4 sources add up. Normal range: 5–20s.

## License

MIT
