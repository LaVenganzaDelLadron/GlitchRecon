#app/pipeline/pipeline.py
from app.pipeline.base import PipelineStage
from app.pipeline.context import PipelineContext


class Pipeline:
    def __init__(self) -> None:
        self._stages: list[PipelineStage] = []

    def add_stage(self, stage: PipelineStage) -> None:
        self._stages.append(stage)

    async def run(self, target: str) -> PipelineContext:
        context = PipelineContext(target=target)

        for stage in self._stages:
            await stage.run(context)

            if context.errors:
                context.status = "failed"
                break

        if not context.errors:
            context.status = "completed"

        return context