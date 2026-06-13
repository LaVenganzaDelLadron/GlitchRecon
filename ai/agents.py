from ai.ollama_client import generate
from ai.prompts import vulnerability_analysis


def analyze_vulnerability(vulnerability: str):
    prompt = vulnerability_analysis(vulnerability)

    return generate(prompt)