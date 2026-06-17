from services.tool_registry import build_command


def build_amass_command(domain: str, mode: str = "passive") -> list[str]:
    options = [mode] if mode else []
    return build_command("amass", "domain", domain, options).argv


def extract_subdomains(output: str) -> list[str]:
    seen = set()
    subdomains = []
    for line in output.splitlines():
        domain = line.strip()
        if not domain or domain in seen:
            continue
        seen.add(domain)
        subdomains.append(domain)
    return subdomains

