---
name: aarambh-erp-domain
description: Core product/domain knowledge for the Aarambh Institute ERP — the course/batch/enrollment model, the four portals, the student journey, and key business rules. Load this before working on any Aarambh ERP task so implementation matches the product spec without re-reading the full specification every time.
---

# Skill: Aarambh Institute ERP Domain Knowledge

## What Aarambh Is

A coaching-institute ERP for Classes 8–12 (CBSE / MP Board / ICSE; streams PCM / PCB /
Commerce / Arts for Classes 11–12). Four connected portals — **Admin, Teacher, Student,
Parent** — are four views of one shared student journey, not four separate products
(spec §98).

## The Core Domain Backbone

```
Board → Class → (Stream, Classes 11–12 only) → Course → Subjects → Batch
```

...and separately, **Enrollment** = the actual student ↔ course ↔ batch relationship.
One student can hold multiple simultaneous enrollments (e.g. a main course plus an
add-on course, each possibly in a different batch). Keep Board / Class / Stream /
Course / Subject / Batch as distinct entities — never collapse them into each other
(spec §3–§4).

## The Student Journey (what every module hangs off)

Enquiry → Counselling → Admission → Course Selection → Batch Assignment → Fee Plan →
Enrollment → Student/Parent Account → Daily Classes → Attendance → Homework → Study
Material → Tests → Results → Performance Analysis → Parent Communication → Fee
Follow-up → Course Completion / Next Course (spec §5).

## Four Portals — Purpose in One Line Each

- **Admin** — the institute's control room: everything, institute-wide.
- **Teacher** — "what do I need to do today": scoped to own batches only.
- **Student** — "what do I need to do today, and how am I performing."
- **Parent** — "how is my child doing": one or more children.

## Key Business Rules to Respect

1. Enrollment history (attendance, results) is preserved across batch transfers —
   never wiped (spec §17).
2. Admission completion is one atomic operation: student record + Student ID + Roll
   Number + enrollment + course/batch link + parent link + fee record + student login +
   parent login, created together (spec §10).
3. Chat contact lists are computed from live enrollment data (a student's current
   subject teachers) — never a manually maintained contact list (spec §71, §84).
4. Teacher remarks' visibility to parents is a configurable institute setting; default
   conservative (OFF) until an institute enables it (spec §45).
5. Attendance below 75% and overdue fees are the two standard "alert" thresholds used
   throughout Admin, Student, and Parent views (spec §8, §22).
6. Fee amounts are always computed/verified server-side against the stored fee plan and
   installment schedule — never trusted from a client request (spec §28, §66).
7. Chat stays scoped to academic topics — classes, homework, tests, attendance, doubts,
   performance, PTM, institute communication — not general messaging (spec §70).
8. Announcement (one-way, institute → audience) and Chat (two-way, student/parent ↔
   teacher) are distinct data models and distinct UI surfaces (spec §78).

## Reference Module List (the Admin menu is the superset of every module)

Dashboard, Admissions/Enquiries, Students, Parents, Courses, Subjects, Batches,
Enrollments, Timetable, Teachers & Staff, Staff Attendance, Payroll, Student Attendance,
Examinations, Question Bank, Results, Study Material, Homework, Fees & Payments,
Receipts, Communication & Chat, Reports & Analytics, Settings (spec §6, §99).

## Worked Example to Validate Against

Rahul Sharma's full journey (spec §97) is the canonical end-to-end example: enquiry →
admission into Class 10 CBSE Complete → assigned to Batch 10-A → fee ₹60,000 with
₹20,000 paid → student + parent accounts created → attendance marked → homework
assigned/submitted/reviewed → study material shared → test taken (84/100) → result
published → performance breakdown shown → parent chats with teacher → next installment
reminder → payment → receipt generated. Any module's implementation should be able to
reproduce its piece of this example correctly.

## Where to Look for More Detail

- Full narrative spec: `Aarambh_Institute_ERP_Complete_Specification.md`
- Data model detail: `systemdesign.md`
- System layout and tech stack: `architecture.md`
