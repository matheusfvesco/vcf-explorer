FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

COPY pyproject.toml .

RUN apt update \
    && apt install -y gcc \
    && rm -rf /var/lib/apt/lists/* \
    && uv sync \
    && uv cache clean