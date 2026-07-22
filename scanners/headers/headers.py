import httpx

from app.pipeline.context import PipelineContext
from scanners.base import Scanner


class HeaderScanner(Scanner):

    name = "Header Scanner"

    SECURITY_HEADERS = [
        "Content-Security-Policy",
        "Strict-Transport-Security",
        "X-Frame-Options",
        "X-Content-Type-Options",
        "Referrer-Policy",
        "Permissions-Policy",
    ]

    async def scan(self, context: PipelineContext) -> None:

        async with httpx.AsyncClient(follow_redirects=True, timeout=15,) as client:
            response = await client.get(context.target)

        context.headers = dict(response.headers)

        for header in self.SECURITY_HEADERS:

            if header not in response.headers:

                context.add_finding(
                    title=f"Missing Header: {header}",
                    severity="Low",
                    description=f"{header} is missing.",
                    evidence={
                        "observation": "header_absent",
                        "header_checked": header,
                        "header_present": False,
                        "response_status_code": response.status_code,
                        "response_url": str(response.url),
                    },
                    scanner_name=self.name,
                )
