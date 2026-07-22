from __future__ import annotations

import argparse
from collections.abc import Callable, Sequence
from app.config import get_llm_provider
from app.core.base import LLMProvider


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send a prompt to the configured LLM.")
    parser.add_argument(
        "prompt",
        nargs="*",
        help="Prompt to send. The default prompt is used when this is omitted.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None, provider_factory: Callable[[], LLMProvider] = get_llm_provider,) -> int:
    """Run the CLI and return a process exit code."""

    DEFAULT_PROMPT = input("Enter a word: ")

    args = parse_args(argv)
    prompt = " ".join(args.prompt) if args.prompt else DEFAULT_PROMPT
    answer = provider_factory().generate(prompt)
    print(answer)
    return 0
