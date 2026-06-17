import json
import os
import signal
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from models.scan import Scan
from services.command_runner import CommandExecutionError, _validate_argv
from services.tool_registry import CommandSpec


SCAN_JOBS_DIR = Path("storage/scan_jobs")
WORK_DIR = Path("/tmp/glitchrecon-scans")
MAX_LOG_CHARS = 16_000


WRAPPER_CODE = r"""
import json
import subprocess
import sys
from pathlib import Path

log_path = Path(sys.argv[1])
exit_path = Path(sys.argv[2])
work_dir = sys.argv[3]
stdin_path = sys.argv[4]
argv = json.loads(sys.argv[5])

log_path.parent.mkdir(parents=True, exist_ok=True)
stdin_handle = None

try:
    if stdin_path:
        stdin_handle = open(stdin_path, "r", encoding="utf-8", errors="replace")
    with open(log_path, "a", encoding="utf-8", errors="replace") as log:
        log.write("$ " + " ".join(argv) + "\n\n")
        log.flush()
        proc = subprocess.Popen(
            argv,
            stdin=stdin_handle,
            stdout=log,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=work_dir,
            shell=False,
        )
        code = proc.wait()
except Exception as exc:
    with open(log_path, "a", encoding="utf-8", errors="replace") as log:
        log.write(f"\n[scan wrapper error] {exc}\n")
    code = 127
finally:
    if stdin_handle:
        stdin_handle.close()
    exit_path.write_text(str(code), encoding="utf-8")
"""


class ScanJobError(RuntimeError):
    pass


def _now():
    return datetime.now(timezone.utc)


def _job_paths(scan_id: int) -> dict[str, Path]:
    SCAN_JOBS_DIR.mkdir(parents=True, exist_ok=True)
    return {
        "log": SCAN_JOBS_DIR / f"{scan_id}.log",
        "exit": SCAN_JOBS_DIR / f"{scan_id}.exit",
        "stdin": SCAN_JOBS_DIR / f"{scan_id}.stdin",
    }


def _pid_alive(pid: int | None) -> bool:
    if not pid:
        return False
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def _kill_process_group(pid: int | None):
    if not pid:
        return
    try:
        os.killpg(pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    except Exception:
        try:
            os.kill(pid, signal.SIGTERM)
        except Exception:
            return


def _read_exit_code(exit_path: Path) -> int:
    try:
        return int(exit_path.read_text(encoding="utf-8").strip() or "1")
    except Exception:
        return 1


def _truncate_middle(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    half = max_chars // 2
    return text[:half] + "\n...[truncated]...\n" + text[-half:]


def read_scan_logs(scan: Scan, max_chars: int = MAX_LOG_CHARS) -> dict[str, Any]:
    log_path = Path(scan.log_path) if scan.log_path else None
    output = ""
    if log_path and log_path.exists():
        output = log_path.read_text(encoding="utf-8", errors="replace")
    output = _truncate_middle(output, max_chars)
    return {
        "scan_id": scan.id,
        "status": scan.status,
        "command": json.loads(scan.executed_command or "[]"),
        "output": output,
        "stdout": scan.stdout,
        "stderr": scan.stderr,
        "return_code": scan.return_code,
        "error_message": scan.error_message,
        "pid": scan.pid,
        "log_path": scan.log_path,
        "timed_out": bool(scan.timed_out),
    }


def start_scan_job(scan: Scan, command_spec: CommandSpec) -> Scan:
    _validate_argv(command_spec)
    WORK_DIR.mkdir(parents=True, exist_ok=True)

    paths = _job_paths(scan.id)
    paths["log"].write_text("", encoding="utf-8")
    if paths["exit"].exists():
        paths["exit"].unlink()

    stdin_path = ""
    if command_spec.stdin is not None:
        paths["stdin"].write_text(command_spec.stdin, encoding="utf-8")
        stdin_path = str(paths["stdin"])

    proc = subprocess.Popen(
        [
            sys.executable,
            "-c",
            WRAPPER_CODE,
            str(paths["log"]),
            str(paths["exit"]),
            str(WORK_DIR),
            stdin_path,
            json.dumps(command_spec.argv),
        ],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
        shell=False,
    )

    scan.status = "running"
    scan.pid = proc.pid
    scan.log_path = str(paths["log"])
    scan.exit_path = str(paths["exit"])
    scan.executed_command = json.dumps(command_spec.argv)
    scan.started_at = _now()
    scan.finished_at = None
    scan.return_code = None
    scan.error_message = None
    scan.timed_out = False
    scan.cancelled_at = None
    return scan


def refresh_scan_status(scan: Scan) -> Scan:
    if scan.status != "running":
        return scan

    exit_path = Path(scan.exit_path) if scan.exit_path else None
    if exit_path and exit_path.exists():
        code = _read_exit_code(exit_path)
        scan.return_code = code
        scan.status = "completed" if code == 0 else "failed"
        scan.finished_at = _now()
        if code != 0:
            scan.error_message = f"Command exited with code {code}"
        _set_output_summary(scan)
        return scan

    started_at = scan.started_at
    timeout_seconds = _timeout_seconds(scan)
    if started_at and timeout_seconds and (_now() - started_at).total_seconds() > timeout_seconds:
        _kill_process_group(scan.pid)
        scan.status = "failed"
        scan.return_code = -1
        scan.timed_out = True
        scan.finished_at = _now()
        scan.error_message = f"Scan timed out after {timeout_seconds}s"
        _set_output_summary(scan)
        return scan

    if scan.pid and not _pid_alive(scan.pid):
        scan.status = "failed"
        scan.return_code = -1
        scan.finished_at = _now()
        scan.error_message = "Scan process died before writing an exit code"
        _set_output_summary(scan)

    return scan


def cancel_scan(scan: Scan) -> Scan:
    if scan.status != "running":
        raise ScanJobError("Only running scans can be cancelled")

    _kill_process_group(scan.pid)
    scan.status = "cancelled"
    scan.return_code = -1
    scan.cancelled_at = _now()
    scan.finished_at = scan.cancelled_at
    scan.error_message = "Scan cancelled by user"
    _set_output_summary(scan)
    return scan


def _timeout_seconds(scan: Scan) -> int | None:
    try:
        plan = json.loads(scan.proposed_plan or "{}")
    except json.JSONDecodeError:
        return None
    timeout = plan.get("timeout_seconds")
    return int(timeout) if timeout else None


def _set_output_summary(scan: Scan):
    logs = read_scan_logs(scan, max_chars=MAX_LOG_CHARS)
    scan.stdout = logs["output"]
    scan.stderr = ""

