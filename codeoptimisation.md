# Aarambh ERP — Code & Performance Optimization (Backend + Frontend)

## Backend (FastAPI / PostgreSQL)

### Query optimization
- Eager-load relationships needed for the 360° Student Profile (spec §12) — personal
  info, enrollments, attendance, fees, results, homework, remarks — in one query
  (`selectinload`/`joinedload`) instead of N+1 round trips.
- Composite indexes for the hottest access patterns: `(batch_id, date)` on
  `class_sessions`, `(enrollment_id, status)` on `installments`,
  `(conversation_id, sent_at)` on `messages`. See `systemdesign.md` §6 for the full list.
- **Paginate every list endpoint** — students, batches, messages, homework, question
  bank — never return an unbounded list.
- Use a materialized view or scheduled aggregation job for heavy dashboard numbers
  (batch performance averages, fee collection totals, attendance %) instead of
  computing them live on every dashboard load (`systemdesign.md` §5).
- Keep async routes non-blocking: PDF receipt generation, bulk notification fan-out, and
  report aggregation run as background jobs, never inline in the request path.

### Caching
- Redis in front of: dashboard summary cards (short TTL, 1–5 min), academic-structure
  lookups (boards/classes/courses — changes rarely; invalidate on write), a teacher's
  batch list.

### Background processing
- Fee reminders, bulk announcement fan-out, receipt PDF generation, nightly report
  aggregation → Celery/RQ queue, never synchronous in the request/response cycle.

### Query safety
- Every list/detail query is filtered by ownership at the query level (teacher_id,
  parent's linked children, student's own enrollments) — never fetch broadly and filter
  in Python afterward.

### API efficiency
- Support sparse fieldsets / summary vs. detail schemas for list views (don't return
  full student objects — remarks, full fee history, etc. — in a student *list* screen).
- Provide one aggregated endpoint per dashboard (Admin, Teacher, Student, Parent) rather
  than making the frontend assemble it from several calls.

## Frontend (Next.js)

### Rendering & bundle size
- Route-based code splitting is automatic with the App Router; additionally
  `dynamic()`-import heavy pieces (chat window, chart libraries, PDF viewer).
- Server components for static/SSR-friendly dashboard sections; client components only
  where interactivity is required (forms, chat, filterable tables).
- Memoize expensive derived values (performance charts, attendance %) with `useMemo`;
  virtualize long lists (`react-virtual` or similar) once student/batch lists grow large.

### Data-fetching efficiency
- Prefetch likely-next data with `queryClient.prefetchQuery` (e.g. prefetch a student's
  profile on row hover in the Admin student list).
- Set `staleTime` per data type: long for rarely-changing data (course/batch lists),
  short for live data (attendance, chat, notifications).
- Avoid waterfalls — fetch the Parent Dashboard as one aggregated call, not six
  sequential child calls.

### Images & assets
- `next/image` for all photos and material thumbnails with correct sizing; compress
  uploads client-side before sending where practical (homework photos in particular).

### Perceived performance
- Optimistic UI for attendance marking, homework review, chat send, PTM response —
  roll back cleanly on server error.
- Skeleton loaders (not spinners) for dashboard cards and list screens.

## Cross-Cutting Priorities

- **Load-test the modules that spike with real usage**: attendance marking during peak
  evening class hours, the fee dashboard around installment due dates, and chat/result
  notifications right after a batch's results are published.
- Watch Postgres's slow-query log before adding indexes or denormalized columns beyond
  what's listed in `systemdesign.md` §6 — measure first, optimize second.
- Denormalizing `attendance_percentage` onto `enrollments` (updated via background job
  after each attendance event) is the one pre-approved denormalization, since it's read
  on every dashboard/profile view across all four portals.
