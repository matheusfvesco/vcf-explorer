FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

COPY src/api/pyproject.toml .
COPY .python-version .
COPY uv.lock .

RUN apt update \
    && apt install -y gcc \
    && rm -rf /var/lib/apt/lists/* \
    && uv sync \
    && uv clean

COPY src/api/Snakefile .

COPY src/api/api .
COPY src/api/annotate .

COPY src/api/run.sh .

COPY data/NIST.vcf.gz /data/NIST.vcf.gz


RUN chmod +x run.sh

CMD ["./run.sh"]