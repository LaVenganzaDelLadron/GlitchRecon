"""Convenience entry point for running the GlitchRecon API server."""

import uvicorn


if __name__ == "__main__":
    uvicorn.run("app.api.application:app", host="127.0.0.1", port=8000, reload=True)
