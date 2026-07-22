#app/pipeline/stages/validation.py
from urllib.parse import urlparse
from app.pipeline.base import PipelineStage
from app.pipeline.context import PipelineContext


class ValidationStage(PipelineStage):
    async def run(self, context: PipelineContext) -> None:
        parsed = urlparse(context.target)

        if parsed.scheme not in ("http", "https"):
            context.add_error("Target must use HTTP or HTTPS.")
            return

        if not parsed.netloc:
            context.add_error("Invalid target.")
            return

        context.valid = True