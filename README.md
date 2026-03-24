```
 ██████╗ ███████╗██╗   ██╗███████╗███████╗ █████╗ ██████╗  ██████╗██╗  ██╗
 ██╔══██╗██╔════╝██║   ██║██╔════╝██╔════╝██╔══██╗██╔══██╗██╔════╝██║  ██║
 ██║  ██║█████╗  ██║   ██║███████╗█████╗  ███████║██████╔╝██║     ███████║
 ██║  ██║██╔══╝  ╚██╗ ██╔╝╚════██║██╔══╝  ██╔══██║██╔══██╗██║     ██╔══██║
 ██████╔╝███████╗ ╚████╔╝ ███████║███████╗██║  ██║██║  ██║╚██████╗██║  ██║
 ╚═════╝ ╚══════╝  ╚═══╝  ╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝
```

**An AI-powered CLI that researches coding questions using real sources — Stack Overflow, official docs, GitHub Issues, and the web — and returns a cited, structured answer with working code.**

---

## Why This Exists

When you hit a bug, a normal LLM often gives you the same vague answer it has given a thousand times before — or worse, it hallucinates details that sound right but are wrong.

DevSearch avoids that by searching real sources first. Instead of guessing from memory, it gathers evidence, compares results across sources, and returns a grounded answer with working code and citations.

One command:

* searches Stack Overflow, official docs, GitHub Issues, and the web
* evaluates and cross-checks results across sources
* returns a synthesized answer with code and citations

---

## Why Not Just Use ChatGPT?

Standard LLMs:

* give generic answers that may not match your exact issue
* hallucinate APIs, method signatures, or outdated solutions
* repeat common patterns without checking whether they are still correct

DevSearch:

* searches real Q&A threads and official docs before answering
* cross-references multiple independent sources
* returns cited, verifiable answers with a confidence score
* says "I don't know" instead of guessing when sources are unclear

---

## Example

```bash
devs --context "TypeError: cannot unpack non-iterable NoneType object" "fix python unpack error"
```

```
╭────────────────────── Explanation ──────────────────────────╮
│ This error occurs when you try to unpack a None value.      │
│ It usually means a function returned None instead of        │
│ an iterable like a tuple or list. Guard against it by       │
│ checking the return value before unpacking.                 │
╰─────────────────────────────────────────────────────────────╯

╭────────────────────── Code (python) ────────────────────────╮
│  1  def get_coords():                                        │
│  2      if found:                                            │
│  3          return (10, 20)                                  │
│  4      return None   # this causes the error               │
│  5                                                           │
│  6  result = get_coords()                                    │
│  7                                                           │
│  8  if result is not None:                                   │
│  9      x, y = result                                        │
│ 10  else:                                                    │
│ 11      print("No result returned")                          │
╰─────────────────────────────────────────────────────────────╯

  #   Source
  1   https://stackoverflow.com/questions/5182575/...
  2   Python Documentation — Iterables and Unpacking

  🟢 Confidence: High  —  Multiple independent sources agree.
  ⏱  Completed in 1.9s
```

---

## Features

* **ReAct Agent** — Runs a Reasoning + Acting loop. The agent thinks about what to search, calls a tool, reads the result, and decides whether to search more or synthesize. It is adaptive, not a fixed pipeline.
* **Four-source fallback chain** — Stack Overflow → Official Docs → GitHub Issues → DuckDuckGo. Uses the minimum number of sources needed to reach a confident answer.
* **Confidence scoring** — Every answer includes a High / Medium / Low rating and a one-line explanation of why.
* **Source transparency** — Every answer lists the URLs it drew from. You can verify or read further.
* **Verbose mode** — `--verbose` streams the agent's Thought → Action → Observation loop in real time so you can watch it reason.
* **Debug mode** — `--debug` prints the raw LLM output before parsing, useful when an answer looks unexpected.
* **Honest when stuck** — If sources come up empty, you get direct search links instead of a guess.

---

## How It Works

```
You type: devs --lang python "flatten a nested list"
                        │
                        ▼
              ┌─────────────────────────────────────────────┐
              │         ReAct Agent  (LangChain + Groq)     │
              │                                             │
              │  Thought: "I'll start with Stack Overflow"  │
              │                  │                          │
              │                  ▼                          │
              │         search_stackoverflow(...)           │
              │                  │                          │
              │  Observation: [real SO results]             │
              │                  │                          │
              │  Thought: "Good. Let me also check docs."   │
              │                  │                          │
              │                  ▼                          │
              │            search_docs(...)                 │
              │                  │                          │
              │  Observation: [real docs results]           │
              │                  │                          │
              │  Thought: "I have enough. Synthesizing."    │
              └─────────────────────────────────────────────┘
                        │
                        ▼
              Structured Answer
              ├── Explanation
              ├── Working code snippet
              ├── Sources with URLs
              └── Confidence level + reason
```

---

## Tech Stack

| Component       | Technology                     | Notes                                            |
| --------------- | ------------------------------ | ------------------------------------------------ |
| Agent framework | LangChain ReAct                | Handles the Thought / Action / Observation loop  |
| LLM             | Groq — LLaMA 3.3 70B           | Free tier available, very fast inference         |
| Stack Overflow  | Stack Exchange API v2.3        | Free, no API key required                        |
| GitHub Issues   | GitHub REST API                | Free tier, optional token for higher rate limits |
| Docs Search     | DuckDuckGo scoped to doc sites | Targets official documentation domains           |
| Web Fallback    | DuckDuckGo general search      | Last resort for anything else                    |
| Terminal UI     | Rich                           | Panels, syntax highlighting, tables, spinners    |
| CLI             | Python argparse                | Standard library, no extra dependency            |

---

## Prerequisites

* Python 3.10 or higher
* A free Groq API key — sign up at https://console.groq.com (no credit card required)
* Git

---

## Installation

**1. Clone the repository**

```bash
git clone https://github.com/YOUR_USERNAME/devsearch.git
cd devsearch
```

**2. Create and activate a virtual environment**

```bash
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

**3. Install the package**

```bash
pip install -e .
```

This installs all dependencies and registers `devs` as a terminal command.

**4. Configure your API key**

```bash
cp .env.example .env
```

Open `.env` and add your key:

```env
GROQ_API_KEY=gsk_your_key_here
```

**5. Verify it works**

```bash
devs "what is a Python list comprehension"
```

---

## Usage

```
devs [OPTIONS] "your question"
```

### Examples

```bash
devs "how do I read a file line by line in Python"
devs --lang javascript "how does event delegation work"
devs --lang rust "error handling with the ? operator"
devs --context "ModuleNotFoundError: No module named 'cv2'" "install opencv python"
devs --verbose "difference between FAISS and Pinecone"
devs --debug "pandas groupby aggregate multiple columns"
devs
```

### All Flags

| Flag              | Short | Description                |
| ----------------- | ----- | -------------------------- |
| `--lang LANGUAGE` | `-l`  | Language or framework hint |
| `--context ERROR` | `-c`  | Paste an error message     |
| `--verbose`       | `-v`  | Stream agent reasoning     |
| `--debug`         | `-d`  | Print raw LLM output       |
| `--version`       |       | Show version               |

---

## Project Structure

```
devsearch/
├── devsearch/
│   ├── cli.py
│   ├── agent.py
│   ├── output.py
│   └── tools/
│       ├── stackoverflow.py
│       ├── github_issues.py
│       ├── docs_search.py
│       └── web_fallback.py
├── .env 
├── pyproject.toml
└── README.md
```

---

## Configuration

```env
GROQ_API_KEY=gsk_your_key_here
GITHUB_TOKEN=ghp_optional
```

---

## Troubleshooting

**Missing API key**

```bash
export GROQ_API_KEY=your_key
```

**LangChain import error**

```bash
pip install langchain-classic
```

**Command not found**

```bash
pip install -e .
```

---

## Extending DevSearch

Add a tool:

```python
@tool
def search_my_source(query: str) -> str:
    return "results"
```

Register it in `tools/__init__.py`.

---

## Contributing

```bash
git clone https://github.com/YOUR_USERNAME/devsearch.git
cd devsearch
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

---

## Reality Check

* External APIs = latency + rate limits
* Weak sources → weak answers
* Not reliable for bleeding-edge issues

Use it to accelerate research, not replace understanding.

---

Built with LangChain · Groq · Rich · Stack Exchange API · GitHub API
