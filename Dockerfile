FROM python:3.14.2

RUN apt-get update \
  && apt-get install -y --no-install-recommends postgresql-client ca-certificates \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev || true

COPY . .

COPY .docker/entrypoint_server.sh /entrypoint_server.sh
COPY .docker/entrypoint_sync_daemon.sh /entrypoint_sync_daemon.sh
RUN chmod +x /entrypoint_server.sh /entrypoint_sync_daemon.sh

ENV PORT=8000
EXPOSE 8000

ENTRYPOINT ["/entrypoint_server.sh"]
CMD ["uv", "run", "finstats", "--serve"]