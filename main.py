"""Convenience ASGI entry point for GlitchRecon."""

from app.api.application import app


__all__ = ["app"]

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
