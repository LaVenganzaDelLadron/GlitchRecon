import httpx
from app.pipeline.context import PipelineContext
from scanners.base import Scanner


class CookieScanner(Scanner):

    name = "Cookie Scanner"

    async def scan(self, context: PipelineContext) -> None:

        async with httpx.AsyncClient(follow_redirects=True, timeout=15,) as client:

            response = await client.get(context.target)

        for cookie in response.cookies.jar:

            secure = cookie.secure

            httponly = "HttpOnly" in str(cookie)

            if not secure:

                context.add_finding(
                    title=f"Insecure Cookie ({cookie.name})",
                    severity="Medium",
                    description="Cookie is missing Secure flag.",
                    evidence={
                        "cookie": cookie.name
                    },
                    scanner_name=self.name,
                )

            if not httponly:

                context.add_finding(
                    title=f"Cookie Missing HttpOnly ({cookie.name})",
                    severity="Medium",
                    description="Cookie is accessible via JavaScript.",
                    evidence={
                        "cookie": cookie.name
                    },
                    scanner_name=self.name,
                )
