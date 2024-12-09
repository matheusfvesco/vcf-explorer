FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

COPY pyproject.toml .
COPY api.py .

RUN apt update \
    && apt install -y gcc curl zip perl \
    && rm -rf /var/lib/apt/lists/* \
    && uv sync \
    && uv cache clean

CMD ["uv", "run", "api.py"]