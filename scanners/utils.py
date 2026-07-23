"""Shared, non-invasive helpers for scanner plugins."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any
from urllib.parse import urljoin, urlparse

import httpx

from app.pipeline.context import PipelineContext

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT_SECONDS = 15.0
USER_AGENT = "GlitchRecon/0.4 (authorized security observation)"


def normalized_target(context: PipelineContext) -> str:
    """Return a target URL with a normalized trailing path."""

    return context.target.rstrip("/") + "/"


def target_url(context: PipelineContext, path: str) -> str:
    """Build a same-origin URL for a passive, known resource path."""

    return urljoin(normalized_target(context), path.lstrip("/"))


def target_host(context: PipelineContext) -> str:
    """Return the parsed hostname for the scan target."""

    host = urlparse(context.target).hostname
    if not host:
        raise ValueError("Pipeline context target has no hostname")
    return host


async def get(
    context: PipelineContext,
    url: str,
    *,
    follow_redirects: bool = True,
    headers: Mapping[str, str] | None = None,
) -> httpx.Response:
    """Issue one bounded GET request, reusing the manager client when available."""

    request_headers = {"User-Agent": USER_AGENT, **(dict(headers) if headers else {})}
    shared_client = getattr(context, "http_client", None)
    if isinstance(shared_client, httpx.AsyncClient):
        return await shared_client.get(url, headers=request_headers, follow_redirects=follow_redirects)
    timeout = httpx.Timeout(DEFAULT_TIMEOUT_SECONDS)
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=follow_redirects) as client:
        return await client.get(url, headers=request_headers)


def response_evidence(response: httpx.Response) -> dict[str, Any]:
    """Return safe, reproducible metadata about an observed HTTP response."""

    return {
        "response_url": str(response.url),
        "response_status_code": response.status_code,
        "response_content_type": response.headers.get("content-type", ""),
    }


def bounded_text(response: httpx.Response, maximum_characters: int = 200_000) -> str:
    """Return response text limited to a safe inspection size."""

    return response.text[:maximum_characters]
