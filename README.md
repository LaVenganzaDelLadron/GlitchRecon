# GlitchRecon

An evidence-driven web vulnerability scanner with AI-assisted analysis and
reporting. Scanners collect the evidence; the LLM only enriches, prioritizes,
and reports on the findings.

## Run the API

Create and activate a virtual environment, then install the dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file and select an LLM provider. For Groq:

```dotenv
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b
```

Or, for a running local Ollama instance:

```dotenv
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2
OLLAMA_HOST=http://localhost:11434
```

Start the server:

```bash
uvicorn app.api.application:app --reload
```

Open `http://127.0.0.1:8000/docs` for the interactive API documentation.

Start an authorized scan with curl:

```bash
curl -X POST http://127.0.0.1:8000/scans \
  -H 'Content-Type: application/json' \
  -d '{"target":"https://example.com"}'
```

The response is the completed report. The service also stores the scan in the
configured repository for the lifetime of this API process. Use the returned
scan ID to retrieve it later:

```bash
curl http://127.0.0.1:8000/scans/<scan-id>
curl http://127.0.0.1:8000/reports/<scan-id>
```

Only scan targets you own or are explicitly authorized to test.
