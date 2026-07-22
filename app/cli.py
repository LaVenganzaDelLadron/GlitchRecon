from __future__ import annotations

import argparse
import asyncio
import logging
from collections.abc import Callable, Sequence
from app.config import get_llm_provider
from app.core.base import LLMProvider

logger = logging.getLogger(__name__)
DEFAULT_PROMPT = "Explain the supplied scanner evidence without inventing vulnerabilities."


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send a prompt to the configured LLM.")
    parser.add_argument(
        "prompt",
        nargs="*",
        help="Prompt to send. The default prompt is used when this is omitted.",
    )
    return parser.parse_args(argv)


def main(
    argv: Sequence[str] | None = None,
    provider_factory: Callable[[], LLMProvider] = get_llm_provider,
) -> int:
    """Run the CLI and return a process exit code."""

    args = parse_args(argv)
    prompt = " ".join(args.prompt) if args.prompt else DEFAULT_PROMPT
    answer = asyncio.run(provider_factory().generate(prompt))
    logger.info("LLM response: %s", answer)
    return 0
