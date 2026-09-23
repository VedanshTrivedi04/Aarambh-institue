"""
app/schemas/landing.py
-----------------------
Pydantic schemas for the public landing page API and website lead capture.
"""

from __future__ import annotations

import uuid
from typing import Any
from pydantic import BaseModel, EmailStr, Field


# ─────────────────────────────────────────────────────────────────────────────
# Public Enquiry / Lead Capture
# ─────────────────────────────────────────────────────────────────────────────

class PublicEnquiryCreate(BaseModel):
    student_name: str = Field(..., min_length=2, max_length=150, description="Name of student")
    parent_name: str = Field(..., min_length=2, max_length=150, description="Parent or guardian name")
    phone: str = Field(..., min_length=10, max_length=20, description="Contact phone / WhatsApp number")
    email: EmailStr | None = Field(None, description="Optional contact email")
    target_class: str = Field(..., description="Target class, e.g., 'Class 10th' or 'B.Com'")
    stream: str | None = Field(None, description="Target stream: PCM, PCB, Commerce, etc.")
    remarks: str | None = Field(None, max_length=1000, description="Message or specific questions")


class PublicEnquiryResponse(BaseModel):
    id: uuid.UUID
    student_name: str
    parent_name: str
    phone: str
    message: str


# ─────────────────────────────────────────────────────────────────────────────
# Landing Page Structured Content Schemas
# ─────────────────────────────────────────────────────────────────────────────

class InstituteContactInfo(BaseModel):
    name: str
    tagline: str
    established_year: int
    city: str
    full_address: str
    primary_phone: str
    secondary_phone: str
    whatsapp_number: str
    email: str
    website_domain: str
    google_maps_url: str
    working_hours: str
    boards_covered: list[str]
    classes_taught: str
    footer_tagline: str


class HeroStats(BaseModel):
    years_experience: str
    total_students: str
    highest_board_score: str
    board_pass_rate: str
    faculty_count: str
    batch_size_limit: str


class AboutSectionData(BaseModel):
    title: str
    paragraphs: list[str]
    director_name: str
    director_designation: str
    director_experience: str
    director_quote: str
    award_title: str
    core_values: list[dict[str, str]]


class CourseItem(BaseModel):
    id: str
    category: str
    title: str
    subtitle: str
    target: str
    duration: str
    board: str
    timings: str
    batch_size: str
    fee: str
    badge: str
    badge_color: str
    features: list[str]
    popular: bool


class FacultyMember(BaseModel):
    name: str
    subject: str
    experience: str
    highlight: str
    specialty: str
    initials: str
    avatar_bg: str
    subject_badge: str


class TopperStudent(BaseModel):
    name: str
    grade: str
    board: str
    score: str
    marks: str
    rank: str
    year: str
    subjects: str
    quote: str
    initials: str
    badge_color: str


class StudentRollItem(BaseModel):
    name: str
    class_name: str
    board: str
    score: str
    year: str
    highlight: str


class TestimonialItem(BaseModel):
    name: str
    class_info: str
    year: str
    review: str
    role: str


class UspFeature(BaseModel):
    number: int
    title: str
    description: str


class NoticeItem(BaseModel):
    date: str
    title: str
    desc: str
    priority: str
    color: str


class HolidayItem(BaseModel):
    holiday: str
    date: str
    status: str


class StudyMaterialItem(BaseModel):
    title: str
    target_class: str
    pages: str
    size: str
    downloads: str
    author: str
    badge: str
    badge_color: str


class LandingPageBundle(BaseModel):
    contact: InstituteContactInfo
    stats: HeroStats
    about: AboutSectionData
    courses: list[CourseItem]
    faculty: list[FacultyMember]
    featured_toppers: list[TopperStudent]
    all_toppers: list[StudentRollItem]
    testimonials: list[TestimonialItem]
    usps: list[UspFeature]
    notices: list[NoticeItem]
    holidays: list[HolidayItem]
    materials: list[StudyMaterialItem]
