# Keystone Monorepo

Keystone is an AI-powered financial command center for operators.

## Repo layout

- `apps/web`: Next.js App Router frontend (Clerk auth, Stripe billing UI, Plaid connect UI)
- `services/api`: FastAPI backend (Clerk JWT verification, Stripe/Plaid integrations, forecasting/anomalies/guidance)
- `packages/shared`: shared TypeScript contracts/constants
- `docker-compose.yml`: local Postgres/Redis/API/worker

## Prerequisites

- Node.js 20+
- pnpm 10+
- Docker + Docker Compose

## Setup

1. Copy environment templates:

```bash
cp .env.example .env
cp apps/web/.env.example apps/web/.env.local
cp services/api/.env.example services/api/.env
```

2. Install frontend workspace deps:

```bash
pnpm install
```

3. Start infra + API + worker:

```bash
pnpm db:up
docker compose up -d api worker
```

4. Run migrations:

```bash
pnpm api:migrate
```

5. Seed demo data (explicit):

```bash
pnpm api:seed
```

6. Run web app:

```bash
pnpm dev
```

Web: `http://localhost:3000`
API docs: `http://localhost:8000/docs`

## Local integrations

### Clerk

- Set `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` and `CLERK_SECRET_KEY` in `apps/web/.env.local`.
- Set `CLERK_JWKS_URL` or `CLERK_ISSUER` in `services/api/.env`.
- Backend requires `org_id` claim in tokens.

### Stripe

- Set `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRO_PRICE_ID` in `services/api/.env`.
- Use Stripe CLI for webhook forwarding:

```bash
stripe listen --forward-to localhost:8000/v1/webhooks/stripe
```

### Plaid

- Set `PLAID_CLIENT_ID`, `PLAID_SECRET`, `PLAID_ENV` in `services/api/.env`.
- Frontend uses `/v1/plaid/link-token` and `/v1/plaid/exchange`.

## Tests

Backend tests:

```bash
docker compose run --rm api uv run --extra dev pytest
```

Frontend typecheck/lint:

```bash
pnpm typecheck
pnpm lint
```

## Deploy notes

### Frontend (Vercel)

- Deploy `apps/web` as a Vercel project.
- Set env vars from `apps/web/.env.example`.
- Point `NEXT_PUBLIC_API_URL` to deployed API.

### Backend (AWS-compatible)

- Run FastAPI container on ECS/Fargate, EKS, or App Runner.
- Use AWS RDS/Aurora Postgres and ElastiCache Redis.
- Run Alembic migrations in CI/CD before rollout.
- Keep secrets in AWS Secrets Manager / Parameter Store.
