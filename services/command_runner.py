import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from services.tool_registry import CommandSpec, TOOL_REGISTRY


class CommandExecutionError(RuntimeError):
    pass


@dataclass(frozen=True)
class CommandResult:
    argv: list[str]
    stdout: str
    stderr: str
    return_code: int
    started_at: datetime
    finished_at: datetime

    def to_dict(self):
        data = asdict(self)
        data["started_at"] = self.started_at.isoformat()
        data["finished_at"] = self.finished_at.isoformat()
        return data


SHELL_METACHARS = {";", "|", "&", "`", "$", "(", ")", "<", ">"}
MAX_OUTPUT_CHARS = 100_000
WORK_DIR = Path("/tmp/glitchrecon-scans")


def _validate_argv(spec: CommandSpec):
    if not spec.argv:
        raise CommandExecutionError("Command cannot be empty")

    allowed_binaries = {tool.command[0] for tool in TOOL_REGISTRY.values()}
    if spec.argv[0] not in allowed_binaries:
        raise CommandExecutionError(f"Executable is not allowlisted: {spec.argv[0]}")

    for arg in spec.argv:
        if any(char in arg for char in SHELL_METACHARS):
            raise CommandExecutionError(f"Unsafe shell metacharacter detected in argument: {arg}")


def run_command(spec: CommandSpec) -> CommandResult:
    _validate_argv(spec)
    WORK_DIR.mkdir(parents=True, exist_ok=True)

    started_at = datetime.now(timezone.utc)
    completed = subprocess.run(
        spec.argv,
        input=spec.stdin,
        capture_output=True,
        text=True,
        timeout=spec.timeout_seconds,
        cwd=WORK_DIR,
        shell=False,
    )
    finished_at = datetime.now(timezone.utc)

    return CommandResult(
        argv=spec.argv,
        stdout=(completed.stdout or "")[:MAX_OUTPUT_CHARS],
        stderr=(completed.stderr or "")[:MAX_OUTPUT_CHARS],
        return_code=completed.returncode,
        started_at=started_at,
        finished_at=finished_at,
    )

