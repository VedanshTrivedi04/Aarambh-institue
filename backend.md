# Aarambh ERP — Backend Guidelines (FastAPI)

## 1. Stack

FastAPI, Pydantic v2, SQLAlchemy 2.0 (async), Alembic, PostgreSQL, asyncpg, Uvicorn,
pytest + pytest-asyncio + httpx, Redis, Celery or RQ, python-jose/authlib (JWT),
passlib[bcrypt] (password hashing), pydantic-settings (config).

## 2. Project Structure

```
backend/
  app/
    main.py                 # FastAPI app factory, router registration, middleware
    core/
      config.py              # pydantic-settings, env-driven
      security.py             # JWT encode/decode, password hashing
      logging.py
    db/
      base.py                  # SQLAlchemy declarative base
      session.py               # async session/engine
    models/                    # SQLAlchemy ORM models, one file per domain
      academic_structure.py
      enrollment.py
      attendance.py
      homework.py
      study_material.py
      exams.py
      fees.py
      communication.py
      staff.py
    schemas/                   # Pydantic Create/Update/Read schemas, mirrors models/
    api/
      v1/
        auth/
        admin/
        teacher/
        student/
        parent/
      deps.py                  # get_current_user, require_role(), get_db
    services/                  # business logic, one per domain
      enrollment_service.py
      admission_service.py
      attendance_service.py
      fee_service.py
      chat_service.py
      report_service.py
    tasks/                     # Celery/RQ background jobs
    tests/
  alembic/
    versions/
  pyproject.toml
```

## 3. Layering Rule

**Router (I/O only) → Service (business logic) → ORM/DB.**
Routers parse/validate the request, call exactly one service method, and shape the
response. They must never contain raw SQL, transaction logic, or cross-entity business
rules directly — that always lives in `services/`.

## 4. Domain Modules (mirror the spec 1:1)

`auth`, `academic_structure` (board/class/stream/course/subject/batch), `enrollment`,
`admission` (enquiry → admission), `attendance`, `homework`, `study_material`, `exams`
(tests/question bank/results), `fees` (plans/installments/payments/receipts),
`communication` (chat/announcements/PTM/notifications), `staff` (teachers/staff/staff
attendance/payroll), `timetable`, `reports`, `settings`.

## 5. Auth & RBAC

- JWT access token (~15–30 min TTL) + refresh token (httpOnly cookie, longer TTL).
- `role` enum on `users`: `ADMIN`, `TEACHER`, `STUDENT`, `PARENT`.
- `deps.require_role(*roles)` FastAPI dependency guards route access.
- **Ownership is re-verified inside the service, every time** — e.g. before a teacher
  marks attendance for a batch, the service checks `batch.teacher_id ==
  current_user.teacher_id`; before a parent reads a child's fees, the service checks the
  `student_parent` link. Never rely on the route guard alone (see `rules.md` §4).

```python
# Example pattern (illustrative, not literal file content)
async def mark_attendance(db, current_user, batch_id, entries):
    batch = await get_batch_or_404(db, batch_id)
    if batch.teacher_id != current_user.teacher_id:
        raise ForbiddenError("Not your batch")
    ...
```

## 6. Schema Conventions

- Separate `XCreate`, `XUpdate`, `XRead`/`XOut` Pydantic schemas per entity.
- `XRead` schemas use `model_config = ConfigDict(from_attributes=True)`.
- Consistent pagination envelope for every list endpoint:
  `{"items": [...], "total": int, "page": int, "page_size": int}`.

## 7. Error Handling

Central exception handlers registered in `main.py` translate domain exceptions to a
consistent JSON shape: `{"detail": "...", "code": "BATCH_FULL"}`. Define domain
exceptions per module (`BatchFullError`, `DuplicateEnrollmentError`,
`InstallmentAlreadyPaidError`, `ForbiddenError`) rather than raising raw
`HTTPException` deep inside services.

## 8. File Uploads

Study material, homework attachments, chat attachments, profile photos, and generated
fee receipts all go through a single `StorageBackend` abstraction (local disk in dev,
S3-compatible in staging/prod). Validate file type and size **server-side** on every
upload endpoint regardless of frontend validation. Only the storage key/URL is persisted
in Postgres.

## 9. Background / Async Tasks

Use Celery or RQ (backed by Redis) for anything that shouldn't block a request:
fee-reminder generation, bulk announcement/notification fan-out, PDF receipt generation,
nightly report aggregation. Lightweight, best-effort side effects (e.g. a single
in-app notification insert) can use FastAPI's built-in `BackgroundTasks`.

## 10. Testing

- pytest + `httpx.AsyncClient` + pytest-asyncio.
- One test database, transactional rollback per test for isolation.
- Priority coverage: admission-wizard atomicity, enrollment/batch-transfer history
  retention, fee/installment math, RBAC + ownership boundaries per role, chat
  access-graph enforcement (a student can't message a teacher they're not enrolled
  under).

## 11. Migrations

- Alembic, one migration per PR, reviewed alongside the model change.
- Never hand-edit schema directly in staging/prod.
- A seed script populates sample Boards/Classes/Streams/Courses/Batches (the exact
  examples used in the spec, e.g. `10-CBSE-MATH-A`) for local dev and demo.

## 12. Config & Secrets

`pydantic-settings` reads all config from environment variables; never commit `.env`;
one settings profile per environment (`dev`, `staging`, `prod`).

## 13. API Versioning

All routes under `/api/v1/...`. Breaking changes get a new `/api/v2/...` prefix rather
than mutating v1 contracts in place.

## 14. Logging & Observability

Structured JSON logging including request id, authenticated user id, and role on every
request. A dedicated `audit_log` table records sensitive actions — fee/payment edits,
result publishing, admin overrides of student/enrollment data — with actor, timestamp,
before/after where relevant.
