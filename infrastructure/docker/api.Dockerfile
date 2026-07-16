FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY apps ./apps
COPY connectors ./connectors
COPY services ./services
COPY shared ./shared
COPY domain-packs ./domain-packs

RUN pip install --no-cache-dir -e ".[dev]"

EXPOSE 8000

