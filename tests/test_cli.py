from glitchrecon import cli


class FakeProvider:
    def __init__(self) -> None:
        self.prompt: str | None = None

    def generate(self, prompt: str) -> str:
        self.prompt = prompt
        return "response"


def test_cli_uses_default_prompt(capsys) -> None:
    provider = FakeProvider()

    assert cli.main([], provider_factory=lambda: provider) == 0
    assert provider.prompt == cli.DEFAULT_PROMPT
    assert capsys.readouterr().out == "response\n"


def test_cli_uses_supplied_prompt(capsys) -> None:
    provider = FakeProvider()

    cli.main(["Explain", "this"], provider_factory=lambda: provider)

    assert provider.prompt == "Explain this"
    assert capsys.readouterr().out == "response\n"
