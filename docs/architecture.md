# Keystone architecture

- Frontend: Next.js App Router, Clerk auth, TanStack Query + Zod typed fetch layer.
- Backend: FastAPI + async SQLAlchemy + Alembic + Redis/RQ jobs.
- Tenancy: `clerk_org_id` enforced on all domain records.
- Currency v1: USD-only (`currency_code = USD`).
