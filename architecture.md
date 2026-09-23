# Aarambh ERP — System Architecture

Source of truth for product scope: `Aarambh_Institute_ERP_Complete_Specification.md`.
This document defines how that product is realized technically.

## 1. Overview

Aarambh ERP is a coaching-institute management platform for Classes 8–12 (CBSE / MP Board /
ICSE) with four connected portals — **Admin, Teacher, Student, Parent**. It is built as a
**single Next.js frontend** and a **single FastAPI backend** on **one PostgreSQL database**.
The four portals are role-based views of one shared student journey, not four separate
applications (spec §98) — this is the single most important architectural constraint.

## 2. Tech Stack

| Layer | Choice |
|---|---|
| Backend framework | FastAPI (Python 3.11+), Pydantic v2 |
| ORM / migrations | SQLAlchemy 2.0 (async), Alembic |
| Database | PostgreSQL 15+ |
| Frontend framework | Next.js 14+ (App Router), TypeScript |
| Styling / UI | Tailwind CSS, shadcn/ui |
| Server-state (frontend) | TanStack Query |
| Forms/validation | react-hook-form + zod (frontend), Pydantic (backend) |
| Auth | JWT access + refresh tokens, RBAC |
| Cache / queue | Redis (dashboard caching + Celery/RQ background jobs) |
| Object storage | S3-compatible storage (local disk in dev) |
| Real-time | Polling (Phase 1) → WebSockets (Phase 2) for chat/notifications |
| Testing | pytest + httpx (backend), Vitest/RTL + Playwright (frontend) |

## 3. High-Level Request Flow

```
Browser (Next.js app, role-based routes)
   │  JWT access token
   ▼
FastAPI (routers) ──► Services (business logic) ──► SQLAlchemy models ──► PostgreSQL
   │                        │
   │                        └──► Redis (cache) / Celery (background jobs)
   ▼
Object storage (study material, homework files, photos, generated PDF receipts)
```

## 4. The Four Portals as One Product

- One Next.js app with route groups: `app/admin`, `app/teacher`, `app/student`, `app/parent`.
- One FastAPI app with routers grouped the same way, all calling **shared services**.
- Shared UI components (attendance badge, fee status pill, chat window, performance chart)
  live once and are reused with different permissions/data scope per portal.
- No portal-specific duplicate business logic — see `rules.md` §9.

## 5. Core Domain Backbone

```
Board → Class → (Stream, Classes 11–12 only) → Course → Subjects → Batch
                                                              │
                                                         Enrollment ── Student
```

Every feature module (attendance, homework, study material, tests, fees, chat) attaches to
**Enrollment**, not directly to Student or Batch alone — this is what makes batch transfer
and multi-course students (spec §3–§4) work without losing history.

## 6. Module Map

| Spec module | Backend domain package | Portals that touch it |
|---|---|---|
| Admissions / Enquiry | `admission` | Admin |
| Academic structure (Board/Class/Stream/Course/Subject/Batch) | `academic_structure` | Admin, all (read) |
| Enrollment | `enrollment` | Admin, all (read) |
| Timetable | `timetable` | Admin, Teacher, Student, Parent |
| Teachers & Staff, Staff Attendance, Payroll | `staff` | Admin |
| Student Attendance | `attendance` | Admin, Teacher, Student, Parent |
| Examinations, Question Bank, Results | `exams` | Admin, Teacher, Student, Parent |
| Study Material | `study_material` | Admin, Teacher, Student |
| Homework | `homework` | Admin, Teacher, Student, Parent |
| Fees & Payments, Receipts | `fees` | Admin, Parent |
| Communication & Chat, Announcements, PTM | `communication` | Admin, Teacher, Student, Parent |
| Reports & Analytics | `reports` | Admin |
| Settings | `settings` | Admin |

## 7. Authentication & Authorization Architecture

- Single `users` table with a `role` enum: `ADMIN`, `TEACHER`, `STUDENT`, `PARENT` (admin
  sub-roles such as accountant/counsellor/coordinator can extend this later — spec §19).
- JWT access token (short-lived, ~15–30 min) + refresh token (httpOnly cookie, longer-lived).
- Every route declares the roles allowed **and** the service layer re-scopes every query by
  ownership: a teacher only ever sees their own batches; a parent only their own children; a
  student only their own records. This is enforced server-side unconditionally — see
  `rules.md` §4.

## 8. Communication / Chat Architecture

- The chat "contact graph" is **derived, not stored**: a student can message a teacher only if
  that teacher currently teaches a subject the student is enrolled in (spec §71, §84).
- MVP: database-backed messages, short-interval polling for unread counts/new messages.
- Phase 2: WebSocket channel per conversation for live delivery + presence (spec §80, §87).
- Announcements (one-way) and Chat (two-way) are modeled as separate entities (spec §78).

## 9. File & Document Architecture

- A storage abstraction (`StorageBackend` interface) with a local-disk implementation for dev
  and an S3-compatible implementation for staging/prod, used for: student/teacher photos,
  study material, homework attachments, chat attachments, and generated fee-receipt PDFs.
- Only the storage key/URL is persisted in PostgreSQL — never file contents.

## 10. Environments

`dev` → `staging` → `prod`, each with its own database and object storage bucket/prefix.
A seed script populates the sample Boards/Classes/Courses/Batches used as examples throughout
the spec (e.g. "10-CBSE-MATH-A") for demo and E2E testing.

## 11. Multi-Branch Readiness (Non-Goal, but Design-Aware)

Spec §102 lists multi-branch institute support as a future item. It is **not** built now, but
core tables (students, batches, fees, staff) include an unused `institute_id` /
`branch_id` column from day one so this doesn't require a destructive migration later. See
`superpower.md` §9.

## 12. Non-Functional Requirements

- **Availability**: fee/payment and attendance endpoints are the most latency-sensitive during
  peak hours (evening class times, fee due dates) — see `codeoptimisation.md`.
- **Privacy**: student/parent PII access is role- and relationship-scoped — see `rules.md` §5.
- **Auditability**: fee edits, result publishing, and admin overrides are logged to an audit
  table (`backend.md` §14).
