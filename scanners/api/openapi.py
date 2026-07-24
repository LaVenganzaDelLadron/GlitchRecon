"""OpenAPI document discovery scanner."""
import asyncio
from pathlib import Path
from typing import Iterable

from app.models.schemas import Finding, Severity
from app.pipeline.context import PipelineContext
from scanners.base import Scanner
from scanners.utils import bounded_text, get, response_evidence, target_url


class OpenAPIScanner(Scanner):
    """Retrieves known public OpenAPI document locations and fuzzes common API endpoints."""
    id = "api.openapi"
    name = "OpenAPI Discovery Scanner"
    category = "api"
    description = "Discovers publicly exposed OpenAPI documents and common API paths."
    severity = Severity.INFO
    tags = frozenset({"api", "openapi", "documentation", "passive", "fuzz"})
    enabled = True

    # --------------------------------------------------------------------- #
    # Helper – read a wordlist once and return a clean iterator of words.
    # --------------------------------------------------------------------- #
    @staticmethod
    def _load_wordlist(wordlist_path: str | Path) -> Iterable[str]:
        """Yield non‑empty, stripped words from *wordlist_path*."""
        path = Path(wordlist_path)
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                word = line.strip()
                if word:                     # skip blanks / comments
                    yield word

    # --------------------------------------------------------------------- #
    # Main scan routine – discovery + ffuf‑style fuzzing.
    # --------------------------------------------------------------------- #
    async def scan(self, context: PipelineContext) -> list[Finding]:
        findings: list[Finding] = []

        # ---------- 1️⃣  OpenAPI document discovery ----------
        for path in ("/openapi.json", "/api/openapi.json"):
            response = await get(context, target_url(context, path))
            if response.status_code == 200 and "openapi" in bounded_text(response, 5_000).lower():
                findings.append(
                    Finding(
                        scanner_id=self.id,
                        scanner_name=self.name,
                        title="Public OpenAPI document discovered",
                        severity=self.severity,
                        confidence=0.95,
                        description=(
                            "A public OpenAPI document was found; documented endpoints were not invoked."
                        ),
                        evidence={
                            **response_evidence(response),
                            "observation": "openapi_document_available",
                            "location": path,
                        },
                        references=["https://spec.openapis.org/oas/latest.html"],
                    )
                )
                # We keep scanning – a public doc does not preclude hidden endpoints.

        # ---------- 2️⃣  ffuf‑style endpoint fuzzing ----------
        # Adjust these values to suit your environment.
        WORDLIST = "/usr/share/wordlists/seclists/Discovery/Web-Content/common.txt"
        BASE_PATH = "/api"                     # the part before the FUZZ token
        MATCH_CODES = {200, 401, }               # same as `-mc 200,401`
        CONCURRENCY = 20                       # how many requests run in parallel

        # Load the wordlist once.
        words = list(self._load_wordlist(WORDLIST))

        # Semaphore limits the number of simultaneous HTTP calls.
        semaphore = asyncio.Semaphore(CONCURRENCY)

        async def _probe(word: str) -> None:
            """Request `<base>/<word>` and record a finding if the status matches."""
            async with semaphore:
                url_path = f"{BASE_PATH}/{word}"
                response = await get(context, target_url(context, url_path))

                if response.status_code in MATCH_CODES:
                    # Grab a short snippet of the body for evidence (max 500 chars).
                    snippet = bounded_text(response, 500)
                    findings.append(
                        Finding(
                            scanner_id=self.id,
                            scanner_name=self.name,
                            title="Potential API endpoint discovered",
                            severity=self.severity,
                            confidence=0.85,
                            description=(
                                f"The path `{url_path}` returned HTTP {response.status_code}. "
                                "It may be a valid endpoint."
                            ),
                            evidence={
                                **response_evidence(response),
                                "observation": "fuzzed_endpoint",
                                "location": url_path,
                                "status_code": response.status_code,
                                "snippet": snippet,
                            },
                            references=[],
                        )
                    )

        # Fire off all probes concurrently (but throttled by the semaphore).
        await asyncio.gather(*[_probe(word) for word in words])

        return findings
