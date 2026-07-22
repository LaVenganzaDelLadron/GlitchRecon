# GlitchRecon

A small command-line client for sending prompts to Groq or Ollama.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Configure one provider in `.env`:

- Groq (the default): set `GROQ_API_KEY`; optionally set `GROQ_MODEL`,
  `GROQ_BASE_URL`, and `GROQ_TIMEOUT`.
- Ollama: set `LLM_PROVIDER=ollama` and `OLLAMA_MODEL`; optionally set
  `OLLAMA_HOST` and `OLLAMA_TIMEOUT`.

## Usage

Run the default prompt:

```bash
python main.py
```

Send a custom prompt:

```bash
python main.py "Explain what model you are."
```

Run tests without contacting an LLM service:

```bash
pytest
```
