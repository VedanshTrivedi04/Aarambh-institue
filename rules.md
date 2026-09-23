# Aarambh ERP — Project Rules

Non-negotiable conventions and constraints for anyone (human or AI agent) working on
this codebase. `agent.md` describes *how* an AI agent should work; this file describes
the hard rules it (and everyone else) must follow.

## 1. Code Style

- **Backend**: Black + Ruff + isort; type hints on every function; Pydantic models at
  every I/O boundary (no raw dicts in/out of routers).
- **Frontend**: ESLint + Prettier; TypeScript strict mode; no `any` without an inline
  comment explaining why.

## 2. Naming

- `snake_case` for Python and database identifiers; `camelCase` for TypeScript/JS;
  `PascalCase` for React components and Pydantic model classes.
- Table names: plural, `snake_case` (`students`, `fee_plans`).
- Enum values: `UPPER_SNAKE_CASE`.

## 3. Git Workflow

- Branch naming: `feature/<module>-<short-desc>`, `fix/<...>`, `chore/<...>`.
- Conventional commits: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`.
- One logical change per PR. PR description references the relevant spec section, e.g.
  "Implements Spec §28 Fees & Payments dashboard."

## 4. Security — Non-Negotiable

- **Never trust a client-supplied user id or role.** Always derive identity from the
  verified JWT on the server.
- **Every query is scoped server-side by ownership** — teacher → own batches, parent →
  own children, student → own records. Security is never enforced by hiding a UI
  element alone.
- All file uploads are validated for type and size **server-side**, regardless of what
  the client already checked.
- No secrets in source code or in the frontend bundle; all secrets come from
  environment variables.
- Rate-limit authentication endpoints and the chat-send endpoint.
- Sanitize/escape all chat messages, remarks, and session notes before storage/render
  to prevent stored XSS.

## 5. Data Privacy

- Student/parent PII (mobile number, address, date of birth) is visible only to roles
  with a legitimate relationship: Admin, the student's own teachers, and the student's
  own linked parent — never exposed across unrelated batches or families.
- Teacher remarks visibility to parents is a configurable institute setting (spec §45)
  — default it OFF until an institute explicitly enables it.

## 6. Business-Rule Integrity

- Never delete or overwrite enrollment, attendance, or result history on a batch
  transfer — always preserve it via the enrollment-history chain (spec §17,
  `systemdesign.md` §2).
- Admission completion (spec §10) is one atomic database transaction covering the
  student record, enrollment, fee record, and both new logins. Partial/half-completed
  admissions must never be possible.
- Payments and receipts are **append-only** — corrections are new adjustment records,
  never in-place edits of an existing payment.

## 7. Testing Gate

No merge to `main` without: passing tests for the changed module, at least one
ownership/RBAC-boundary test for any new endpoint, and a reviewed migration if the
schema changed.

## 8. Documentation Gate

- Any change to the core domain model (course/subject/batch/enrollment and their
  relationships) updates `systemdesign.md` in the **same** PR.
- Any new module updates the module map in `architecture.md`.

## 9. Things to Never Do

- Never hard-code institute-specific values (board/class lists, fee rules) — these stay
  configurable through the Settings module (spec §32).
- Never build portal-specific duplicate business logic — one shared service per domain,
  portal-specific routers/UI only.
- Never expose sequential integer IDs in student/parent-facing URLs where enumeration
  could leak another family's data — use UUIDs for externally-referenced resources.
- Never accept a fee/payment amount from the frontend for a transaction — always
  compute and verify it server-side against the stored fee plan.

## 10. Communication Feature Rules

- Chat contact lists are always derived live from current enrollment data (spec §71,
  §84) — never a manually maintained contact list that can drift out of sync.
- The Report/Block feature (spec §86) ships with chat, not after it — chat does not go
  to production without a moderation path.
