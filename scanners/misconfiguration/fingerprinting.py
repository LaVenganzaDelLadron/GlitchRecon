import httpx

from app.pipeline.context import PipelineContext
from scanners.base import Scanner


class FingerprintScanner(Scanner):

    name = "Fingerprint Scanner"

    async def scan(self, context: PipelineContext) -> None:

        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=15,
        ) as client:

            response = await client.get(context.target)

        headers = response.headers

        server = headers.get("Server")

        powered = headers.get("X-Powered-By")

        if server:
            context.technologies.append(server)

        if powered:
            context.technologies.append(powered)

        html = response.text.lower()

        if "wp-content" in html:
            context.technologies.append("WordPress")

        if "__next" in html:
            context.technologies.append("Next.js")

        if "react" in html:
            context.technologies.append("React")

        if "vue" in html:
            context.technologies.append("Vue")

        if "laravel" in html:
            context.technologies.append("Laravel")