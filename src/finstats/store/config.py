import os


def get_pg_url_from_env(use_psycopg: bool = False) -> str:
    host = os.environ.get("POSTGRES_HOST", "localhost")
    port = os.environ.get("POSTGRES_PORT", "5431")
    user = os.environ.get("POSTGRES_USER", "test")
    password = os.environ.get("POSTGRES_PASSWORD", "test")
    dbname = os.environ.get("POSTGRES_DBNAME", "finstats")
    if use_psycopg:
        return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{dbname}"
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{dbname}"
