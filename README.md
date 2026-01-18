# Finstats

API connector for [ZenMoney](https://zenmoney.app) designed to be used as a ChatGPT Action.

## Overview

This service syncs data from ZenMoney to a local PostgreSQL database and provides a REST API for managing transactions, accounts, tags, and merchants. Primary use case — connecting to ChatGPT as a Custom Action for voice/text-based personal finance management.

## ChatGPT Action Setup

1. **OpenAPI Schema**: `/docs/openapi.json` — import this URL in Action settings
2. **Instructions**: copy contents of `.etc/chat_gpt_instructions.txt` into the Instructions field
3. **Authentication**: Bearer token — header `Authorization: {{token}}`

**Note:** ChatGPT Actions require HTTPS. You need to deploy this service to a hosting provider (e.g., Fly.io, Railway, Render) before connecting it to ChatGPT.

## Local Setup

```bash
# Edit docker-compose.local.yml and replace PUT-YOUR-TOKEN-HERE with your ZenMoney token

# Run with docker-compose
docker compose -f docker-compose.local.yml up -d
```

Service will be available at `http://localhost:8080`. OpenAPI docs: `http://localhost:8080/docs/openapi.json`

### Services

- **server** — HTTP API on port 8080
- **sync_daemon** — background sync with ZenMoney
- **db** — PostgreSQL 16

## Getting ZenMoney Token

The easiest way to get a token is through [Zerro](https://zerro.app):

1. Log in at [zerro.app](https://zerro.app)
2. Navigate to [zerro.app/token](https://zerro.app/token)
3. Copy your token

## API Endpoints

- `GET /transactions` — list transactions with filtering and pagination
- `POST /transactions/expense` — create expense
- `POST /transactions/income` — create income
- `GET /accounts` — list accounts
- `GET /tags` — list tags/categories
- `GET /merchants` — list merchants
- `GET /instruments` — list currencies