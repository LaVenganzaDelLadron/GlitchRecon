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
                        "observation": "cookie_secure_flag_absent",
                        "cookie_name": cookie.name,
                        "cookie_domain": cookie.domain,
                        "cookie_path": cookie.path,
                        "secure_observed": False,
                        "httponly_observed": httponly,
                        "response_status_code": response.status_code,
                        "response_url": str(response.url),
                    },
                    scanner_name=self.name,
                )

            if not httponly:

                context.add_finding(
                    title=f"Cookie Missing HttpOnly ({cookie.name})",
                    severity="Medium",
                    description="Cookie is accessible via JavaScript.",
                    evidence={
                        "observation": "cookie_httponly_flag_absent",
                        "cookie_name": cookie.name,
                        "cookie_domain": cookie.domain,
                        "cookie_path": cookie.path,
                        "secure_observed": secure,
                        "httponly_observed": False,
                        "response_status_code": response.status_code,
                        "response_url": str(response.url),
                    },
                    scanner_name=self.name,
                )
