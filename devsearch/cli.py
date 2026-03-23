"""
DevSearch CLI — entry point.

Usage:
    devs "how do I flatten a nested list in Python"
    devs --context "RecursionError: maximum depth exceeded" "fix recursion in Python"
    devs --lang javascript "async await error handling best practices"
    devs --verbose "what is the difference between FAISS and Pinecone"
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Load .env if present (before any other imports that need env vars)
try:
    from dotenv import load_dotenv
    # Look for .env in CWD, home dir, and package dir
    for env_path in [Path.cwd() / ".env", Path.home() / ".devsearch" / ".env"]:
        if env_path.exists():
            load_dotenv(env_path)
            break
    else:
        load_dotenv()  # Try default locations
except ImportError:
    pass


def _get_groq_key() -> str:
    key = os.getenv("GROQ_API_KEY", "").strip()
    if not key:
        from .output import console, render_error
        render_error(
            "GROQ_API_KEY not found.\n\n"
            "Get a free key at: https://console.groq.com\n"
            "Then set it in your .env file:\n\n"
            "  echo 'GROQ_API_KEY=gsk_your_key_here' > .env\n\n"
            "Or export it:\n"
            "  export GROQ_API_KEY=gsk_your_key_here"
        )
        sys.exit(1)
    return key


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="devs",
        description="DevSearch — AI coding assistant that researches across SO, Docs, GitHub & Web",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  devs "how do I flatten a nested list in Python"
  devs --lang javascript "async await error handling best practices"
  devs --context "RecursionError: maximum depth exceeded" "fix recursion in Python"
  devs --verbose "what is the difference between FAISS and Pinecone"
  devs --version
        """,
    )

    parser.add_argument(
        "query",
        nargs="?",
        help="Your coding question or error message",
    )
    parser.add_argument(
        "--context", "-c",
        metavar="ERROR",
        default="",
        help="Paste your error message or traceback here for more accurate results",
    )
    parser.add_argument(
        "--lang", "-l",
        metavar="LANGUAGE",
        default="",
        help="Language or framework hint (python, javascript, rust, react, etc.)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show live agent reasoning: Thought → Action → Observation",
    )
    parser.add_argument(
        "--debug", "-d",
        action="store_true",
        help="Print the raw LLM output before parsing (useful for troubleshooting)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="DevSearch 0.1.0",
    )

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    from .output import (
        console,
        print_logo,
        render_answer,
        render_error,
        render_not_found,
        reasoning_print,
        print_reasoning_header,
        searching_spinner,
    )

    print_logo()

    # Prompt interactively if no query given
    if not args.query:
        try:
            args.query = console.input("[bold cyan]Ask a coding question:[/bold cyan] ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Bye![/dim]")
            sys.exit(0)

    if not args.query:
        parser.print_help()
        sys.exit(1)

    groq_key = _get_groq_key()

    try:
        from .agent import run_query

        if args.verbose:
            print_reasoning_header(args.query)

            result = run_query(
                query=args.query,
                context=args.context,
                lang=args.lang,
                groq_api_key=groq_key,
                verbose=True,
                debug=args.debug,
                print_fn=reasoning_print,
            )
        else:
            # Non-verbose: show spinner
            result = None
            with searching_spinner(args.query):
                result = run_query(
                    query=args.query,
                    context=args.context,
                    lang=args.lang,
                    groq_api_key=groq_key,
                    verbose=False,
                    debug=args.debug,
                    print_fn=None,
                )

        if not result or not result.get("explanation"):
            render_not_found(args.query)
        else:
            render_answer(result, args.query)

    except KeyboardInterrupt:
        console.print("\n[dim]Search cancelled.[/dim]")
        sys.exit(0)
    except ImportError as e:
        render_error(
            f"Missing dependency: {e}\n\n"
            "Install all dependencies:\n"
            "  pip install -e ."
        )
        sys.exit(1)
    except Exception as e:
        render_error(f"Unexpected error: {str(e)}")
        if args.verbose:
            import traceback
            console.print_exception()
        sys.exit(1)


if __name__ == "__main__":
    main()