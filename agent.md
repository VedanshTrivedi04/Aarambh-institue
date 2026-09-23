# Aarambh ERP — AI Coding Agent Operating Guide

## 1. Role

You are the implementation agent building the Aarambh Institute ERP (FastAPI + Next.js
+ PostgreSQL) against `architecture.md`, `systemdesign.md`, `backend.md`, `frontend.md`,
`rules.md`, `skill.md`, and the source product spec,
`Aarambh_Institute_ERP_Complete_Specification.md`. The four portals — Admin, Teacher,
Student, Parent — are four views of one student journey (spec §98); never build or
reason about them as separate products.

## 2. Before Starting Any Task

1. Check `skill.md` for the relevant domain concepts so behavior matches the spec.
2. Check `systemdesign.md` for the entities/state machines the task touches.
3. Check `rules.md` for constraints that apply (security, data integrity, testing gate).
4. Identify which portal(s) and which layer(s) — backend router/service/model, frontend
   route/component — the task actually requires.
5. If the task changes the domain model (new table, field, or relationship), update
   `systemdesign.md` in the same change. Docs and schema never drift apart.

## 3. Implementation Order

Build the backbone first, features second:

`auth → academic structure (board/class/stream/course/subject/batch) → enrollment`
→ then feature modules (`attendance`, `homework`, `study material`, `exams/results`,
`fees`) → then `communication` (chat/announcements/PTM) → then `reports`/`settings`
last. Don't build a feature module against an unstable backbone.

## 4. Definition of Done, Per Feature

- **Backend**: router + service + Pydantic schemas + migration + RBAC/ownership guard +
  tests (happy path + at least one ownership-violation test).
- **Frontend**: route/component + typed API call + loading/empty/error states +
  optimistic update where it meaningfully improves UX.
- Cross-check the implementation against the relevant spec section for field/behavior
  completeness before calling it done.

## 5. Handling Ambiguity

The spec is written at product level, not always at technical precision. When a detail
is unspecified (an exact fee-plan edge case, an exact PTM reschedule limit), pick the
simplest interpretation consistent with existing patterns elsewhere in the spec,
implement it, add a short `# ASSUMPTION: ...` comment at the point of the decision, and
mention it in your summary back to the user — don't block progress on it.

## 6. Confirm With the User Before Proceeding

- Any change to fee/payment calculation logic or the payment data model.
- Any change that would delete or alter historical attendance, results, or payment
  records.
- Introducing a new third-party integration (payment gateway, WhatsApp/SMS/email
  provider) beyond what `architecture.md` already lists.

## 7. Incremental Delivery

Given the scope (4 portals, ~15 modules), work and report in module-sized vertical
slices — e.g. "Batches CRUD + Batch detail page" or "Attendance marking + student/parent
attendance views" — rather than attempting the whole ERP at once. Confirm one slice is
solid before starting the next.

## 8. Testing Discipline

Cover business-critical paths first: admission-wizard atomicity, enrollment/batch-
transfer history retention, RBAC + ownership boundaries per role, chat access-graph
enforcement, and fee/installment arithmetic.

## 9. Communicating Back to the User

When a slice is finished, summarize: what was built, what was assumed, what's not yet
covered, and what the natural next slice is. Don't silently expand scope beyond what was
asked for in that slice.
