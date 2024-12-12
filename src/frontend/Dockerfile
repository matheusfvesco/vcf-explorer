FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

COPY src/frontend/pyproject.toml .
COPY .python-version .
COPY uv.lock .

COPY src/frontend/frontend.py .

RUN uv sync \
    && uv clean

CMD ["uv", "run", "streamlit", "run", "frontend.py", "--server.fileWatcherType", "none"]