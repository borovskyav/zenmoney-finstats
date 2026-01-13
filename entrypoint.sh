#!/usr/bin/env sh
set -e

DB_HOST="${POSTGRES_HOST:-db}"
DB_PORT="${POSTGRES_PORT:-5432}"

echo "Resolving ${DB_HOST}..."
getent hosts "${DB_HOST}" || true

export DATABASE_URL="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@127.0.0.1:5432/${POSTGRES_DB}?sslmode=disable"

until pg_isready -h "${DB_HOST}" -p "${DB_PORT}" -U "${POSTGRES_USER}"; do
  i=$((i+1))
  echo "pg_isready failed (attempt $i). env: POSTGRES_USER=${POSTGRES_USER} POSTGRES_DB=${POSTGRES_DB}"
  sleep 1
done
echo "Postgres is ready."

echo "Migrate..."
uv run finstats --migrate

echo "Sync..."
if [ -z "${ZENTOKEN:-}" ]; then
  echo "ERROR: ZENTOKEN is empty"
  exit 1
fi
uv run finstats --sync

echo "Starting HTTP..."
exec "$@"