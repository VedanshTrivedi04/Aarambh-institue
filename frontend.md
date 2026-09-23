# Aarambh ERP — Frontend Guidelines (Next.js)

## 1. Stack

Next.js 14+ (App Router), TypeScript (strict mode), Tailwind CSS, shadcn/ui, TanStack
Query, react-hook-form + zod, Zustand (light client-only state), a thin typed API client
over the FastAPI backend.

## 2. Project Structure

```
frontend/
  app/
    (auth)/
      login/
      forgot-password/
    admin/           # route group, layout enforces role === ADMIN
      dashboard/
      admissions/
      students/
      batches/
      ...
    teacher/          # layout enforces role === TEACHER
    student/          # layout enforces role === STUDENT
    parent/           # layout enforces role === PARENT
    middleware.ts     # edge-level auth/role redirect
  components/
    ui/                # shadcn primitives (button, card, dialog, table, ...)
    shared/             # cross-portal: StudentCard, AttendanceBadge, FeeStatusPill,
                         # PerformanceChart, ChatWindow, Timeline
    admin/  teacher/  student/  parent/   # portal-specific composition components
  lib/
    api/                # typed client functions per domain (students.ts, fees.ts, ...)
    auth/
    utils/
  hooks/                # useCurrentUser, useChildSelector, useUnreadCount, ...
  types/                # shared TS types, ideally generated from backend OpenAPI schema
  styles/
```

## 3. One App, Four Portals

Route groups under `app/` map 1:1 to the four portals. Each portal's layout performs a
role check (via `middleware.ts` and again in the layout server component) and redirects
unauthenticated users to `/login` and wrong-role users to their own dashboard. **Shared
behavior lives in `components/shared/`** — e.g. an attendance view is one component that
takes a `scope` prop (`"own" | "batch" | "child" | "institute"`), not four separate
implementations.

## 4. Auth Handling

- Access token kept in memory (or a short-lived, non-httpOnly cookie if SSR needs it);
  refresh token in an httpOnly cookie only the backend can read.
- `middleware.ts` blocks unauthenticated/wrong-role requests before the page renders.
- Silent refresh on 401 via the API client's response interceptor.

## 5. Data Fetching

- **All server state goes through TanStack Query** — dashboards, lists, profiles,
  messages. No server data duplicated into component state or Zustand.
- Server components handle the initial SSR fetch for dashboard pages (faster first
  paint); client components take over for interactive parts (forms, chat, tables with
  client-side filtering).
- Mutations (`useMutation`) with optimistic updates for high-frequency actions:
  attendance marking, homework review, chat send, PTM response.
- Prefer one aggregated endpoint per dashboard (e.g. Parent Dashboard) over several
  sequential calls — avoid request waterfalls.

## 6. Forms

react-hook-form + zod. Keep zod schemas as close as practical to the backend Pydantic
validation rules for each entity (course, batch, admission, fee plan) so client and
server reject the same invalid input for the same reason.

## 7. Component Conventions

- shadcn/ui + Tailwind, with a small design-token layer for status colors used
  everywhere: attendance (`present` / `absent` / `late`), fees (`paid` / `pending` /
  `overdue`), homework (`submitted` / `pending` / `reviewed` / `needs_improvement`).
- Reusable primitives: `StatusBadge`, `ProgressBar` (performance %), `Timeline`
  (student activity history / journey, spec §12), `ChildSwitcher` (Parent portal,
  spec §60).

## 8. Real-Time / Near-Real-Time

- **Phase 1**: TanStack Query short-interval polling for unread chat counts and
  notifications (spec §69, §83).
- **Phase 2**: WebSocket subscription per open conversation for live message delivery
  and online/offline presence (spec §80, §87).

## 9. Multilingual (Hinglish) Content

Chat messages, teacher remarks, and session notes routinely mix Hindi (Devanagari or
Romanized) and English in the same string (spec §96). Treat all such fields as free
UTF-8 text with no language-specific validation; ensure fonts render Devanagari
correctly across the app, not just in chat.

## 10. Mobile Responsiveness

Parent and Student portals are the primary mobile-browser surfaces and must be fully
usable there (attendance check, fee payment, homework status, chat). Admin and Teacher
portals are desktop-first but must remain responsive down to tablet width (teachers may
mark attendance from a phone/tablet in class — spec §37).

## 11. File Upload UX

Homework submissions (PDF/image), study material uploads, and profile photos use a
shared upload component with drag-and-drop, progress indication, and client-side
type/size validation — mirrored, never replaced, by server-side validation
(`backend.md` §8).

## 12. State Management Boundaries

- Server state → TanStack Query, always.
- Ephemeral UI-only state (open modal, selected child in `ChildSwitcher`, active chat
  thread id) → local component state or a small Zustand store.
- Never mirror server data into Zustand "for convenience" — it will drift.

## 13. Testing

- Vitest + React Testing Library for components.
- Playwright for critical end-to-end flows: admission wizard, attendance marking, fee
  payment + receipt download, chat send/receive across roles, PTM request → approve →
  confirm.
