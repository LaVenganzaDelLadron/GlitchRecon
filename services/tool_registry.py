from dataclasses import dataclass, field
from typing import Any


class ToolRegistryError(ValueError):
    pass


@dataclass(frozen=True)
class ToolOption:
    args: tuple[str, ...] = ()
    stdin: bool = False
    timeout_seconds: int | None = None


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    category: str
    risk_level: str
    command: tuple[str, ...]
    target_arg: str | None
    accepted_target_types: tuple[str, ...]
    default_timeout_seconds: int
    output_parser: str = "line"
    options: dict[str, ToolOption] = field(default_factory=dict)


@dataclass(frozen=True)
class CommandSpec:
    tool_name: str
    argv: list[str]
    stdin: str | None
    timeout_seconds: int
    parser: str
    risk_level: str


TOOL_REGISTRY: dict[str, ToolDefinition] = {
    "amass": ToolDefinition(
        name="amass",
        category="enumeration",
        risk_level="medium",
        command=("amass", "enum"),
        target_arg="-d",
        accepted_target_types=("domain", "hostname"),
        default_timeout_seconds=600,
        options={
            "passive": ToolOption(args=("-passive",)),
            "active": ToolOption(args=("-active",), timeout_seconds=900),
            "brute": ToolOption(args=("-brute",), timeout_seconds=1200),
        },
    ),
    "assetfinder": ToolDefinition(
        name="assetfinder",
        category="enumeration",
        risk_level="low",
        command=("assetfinder",),
        target_arg=None,
        accepted_target_types=("domain", "hostname"),
        default_timeout_seconds=180,
        options={"subs_only": ToolOption(args=("--subs-only",))},
    ),
    "ffuf": ToolDefinition(
        name="ffuf",
        category="enumeration",
        risk_level="medium",
        command=("ffuf",),
        target_arg="-u",
        accepted_target_types=("url",),
        default_timeout_seconds=600,
        options={
            "common": ToolOption(args=("-w", "/usr/share/wordlists/seclists/Web-Content/common.txt")),
        },
    ),
    "gitleaks": ToolDefinition(
        name="gitleaks",
        category="secrets",
        risk_level="low",
        command=("gitleaks", "detect"),
        target_arg="--source",
        accepted_target_types=("path", "repo"),
        default_timeout_seconds=300,
        output_parser="json",
    ),
    "hakrawler": ToolDefinition(
        name="hakrawler",
        category="reconnaissance",
        risk_level="low",
        command=("hakrawler",),
        target_arg=None,
        accepted_target_types=("url",),
        default_timeout_seconds=300,
        options={
            "depth_3": ToolOption(args=("-d", "3"), stdin=True),
            "subs": ToolOption(args=("-subs",), stdin=True),
            "json": ToolOption(args=("-json",), stdin=True),
        },
    ),
    "katana": ToolDefinition(
        name="katana",
        category="reconnaissance",
        risk_level="low",
        command=("katana",),
        target_arg="-u",
        accepted_target_types=("url",),
        default_timeout_seconds=300,
        options={
            "depth_3": ToolOption(args=("-d", "3")),
            "include_subdomains": ToolOption(args=("-include-subdomains",)),
            "javascript": ToolOption(args=("-jc",)),
        },
    ),
    "nuclei": ToolDefinition(
        name="nuclei",
        category="vulnerability_scanning",
        risk_level="medium",
        command=("nuclei",),
        target_arg="-u",
        accepted_target_types=("url",),
        default_timeout_seconds=900,
        output_parser="jsonl",
        options={
            "fast": ToolOption(args=("-severity", "low,medium,high,critical")),
            "cve": ToolOption(args=("-tags", "cve,exposure,misconfig")),
        },
    ),
    "trufflehog": ToolDefinition(
        name="trufflehog",
        category="secrets",
        risk_level="low",
        command=("trufflehog", "filesystem"),
        target_arg=None,
        accepted_target_types=("path", "repo"),
        default_timeout_seconds=300,
        output_parser="json",
    ),
}


def list_tools() -> list[dict[str, Any]]:
    return [
        {
            "name": tool.name,
            "category": tool.category,
            "risk_level": tool.risk_level,
            "accepted_target_types": list(tool.accepted_target_types),
            "options": list(tool.options.keys()),
            "timeout_seconds": tool.default_timeout_seconds,
        }
        for tool in TOOL_REGISTRY.values()
    ]


def build_command(tool_name: str, target_type: str, target_value: str, options: list[str] | None = None) -> CommandSpec:
    if tool_name not in TOOL_REGISTRY:
        raise ToolRegistryError(f"Unsupported tool: {tool_name}")

    tool = TOOL_REGISTRY[tool_name]
    if target_type not in tool.accepted_target_types:
        accepted = ", ".join(tool.accepted_target_types)
        raise ToolRegistryError(f"{tool_name} does not accept target type {target_type}; expected one of: {accepted}")

    argv = list(tool.command)
    stdin = None
    timeout = tool.default_timeout_seconds

    for option_name in options or []:
        option = tool.options.get(option_name)
        if not option:
            raise ToolRegistryError(f"Unsupported option for {tool_name}: {option_name}")
        argv.extend(option.args)
        if option.stdin:
            stdin = target_value
        if option.timeout_seconds:
            timeout = option.timeout_seconds

    if tool.name == "ffuf":
        argv.extend([tool.target_arg or "-u", f"{target_value.rstrip('/')}/FUZZ"])
    elif tool.target_arg:
        argv.extend([tool.target_arg, target_value])
    elif stdin is None:
        argv.append(target_value)

    return CommandSpec(
        tool_name=tool.name,
        argv=argv,
        stdin=stdin,
        timeout_seconds=timeout,
        parser=tool.output_parser,
        risk_level=tool.risk_level,
    )

