"""
app/api/v1/public.py
--------------------
Public endpoints for website visitors, prospective students, and parents.
No authentication required.
"""

from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.institute import Institute
from app.models.academic_structure import Course, Board, SchoolClass
from app.models.people import TeacherProfile
from app.models.enquiry import Enquiry, EnquirySource, EnquiryStage
from app.models.cms import SiteContent
from app.core.cms_defaults import DEFAULT_SITE_PAGES
from app.schemas.landing import (
    LandingPageBundle,
    InstituteContactInfo,
    HeroStats,
    AboutSectionData,
    CourseItem,
    FacultyMember,
    TopperStudent,
    StudentRollItem,
    TestimonialItem,
    UspFeature,
    NoticeItem,
    HolidayItem,
    StudyMaterialItem,
    PublicEnquiryCreate,
    PublicEnquiryResponse,
)

router = APIRouter(prefix="/public", tags=["Public — Landing Page & Leads"])


@router.get(
    "/landing-data",
    response_model=LandingPageBundle,
    summary="Get complete landing page structured data",
)
async def get_landing_page_data(db: AsyncSession = Depends(get_db)) -> LandingPageBundle:
    """
    Fetches dynamic institute data from Neon PostgreSQL:
    - Custom admin CMS configurations from `site_contents`
    - Institute information & address
    - Active faculty profiles with experience
    - Courses, toppers, USPs, notices, and testimonials
    """
    # 0. Fetch CMS dynamic overrides from PostgreSQL
    cms_map: dict[str, dict] = {}
    try:
        from app.db.base import Base
        conn = await db.connection()
        await conn.run_sync(Base.metadata.create_all)
        cms_stmt = select(SiteContent)
        cms_res = await db.execute(cms_stmt)
        cms_map = {r.page_slug: r.data for r in cms_res.scalars().all()}
    except Exception:
        cms_map = {}

    # 1. Fetch Institute from Database
    inst_stmt = select(Institute).where(Institute.code == "AARAMBH")
    res = await db.execute(inst_stmt)
    institute = res.scalar_one_or_none()

    inst_name = institute.name if institute else "Aarambh Institute"
    inst_address = (
        institute.address
        if institute and institute.address
        else "8 Shantinath Puri, Hawa Bangla, Near Sai Mandir, Indore, Madhya Pradesh"
    )
    inst_phone = institute.contact_phone if institute and institute.contact_phone else "88397-14081"
    inst_email = institute.contact_email if institute and institute.contact_email else "aarambhinstitute09@gmail.com"

    # 2. Fetch Teachers from Database
    teachers_list: list[FacultyMember] = []
    if institute:
        teacher_stmt = (
            select(TeacherProfile)
            .where(TeacherProfile.institute_id == institute.id, TeacherProfile.is_active == True)
            .order_by(TeacherProfile.experience_years.desc())
        )
        tres = await db.execute(teacher_stmt)
        db_teachers = tres.scalars().all()

        for t in db_teachers:
            initials = f"{t.first_name[0]}{t.last_name[0]}" if t.first_name and t.last_name else "AI"
            # Subject extraction
            qual = t.qualification or ""
            subj = "Academic Subject"
            if "(" in qual and ")" in qual:
                subj = qual[qual.find("(") + 1 : qual.find(")")]
            else:
                subj = qual or "Academic"

            teachers_list.append(
                FacultyMember(
                    name=f"Mr. {t.first_name} {t.last_name}" if t.first_name != "Shobhna" and t.first_name != "Anita" and t.first_name != "Darshna" else f"{'Mrs.' if t.first_name in ['Shobhna', 'Anita'] else 'Miss'} {t.first_name} {t.last_name}",
                    subject=subj,
                    experience=f"{t.experience_years or 15} Years Experience",
                    highlight=f"Senior {subj} Faculty • Aarambh HOD" if t.first_name != "Shobhna" else "Founder & Academic Director, Aarambh Institute",
                    specialty=f"Concept clarity & competitive drills in {subj}",
                    initials=initials,
                    avatar_bg="bg-red-50 text-[#c22329]" if t.first_name == "Shobhna" else "bg-blue-50 text-blue-700",
                    subject_badge="bg-red-50 text-[#c22329] border-red-200" if t.first_name == "Shobhna" else "bg-blue-50 text-blue-800 border-blue-200",
                )
            )

    # Fallback to authentic 7 teachers if empty
    if not teachers_list:
        teachers_list = [
            FacultyMember(
                name="Mr. Pankaj Dubey",
                subject="Biology",
                experience="30 Years Experience",
                highlight="Senior Biology Expert • PMT/NEET & Board Specialist",
                specialty="Botany, Zoology & Medical Foundation",
                initials="PD",
                avatar_bg="bg-emerald-50 text-emerald-800",
                subject_badge="bg-emerald-50 text-emerald-800 border-emerald-200",
            ),
            FacultyMember(
                name="Mr. Jitendra Shindey",
                subject="Commerce & Accounts",
                experience="30 Years Experience",
                highlight="Senior Commerce Mentor • 11th-12th, B.Com & M.Com",
                specialty="Financial Accounting, Tax & Corporate Laws",
                initials="JS",
                avatar_bg="bg-blue-50 text-blue-800",
                subject_badge="bg-blue-50 text-blue-800 border-blue-200",
            ),
            FacultyMember(
                name="Mrs. Shobhna Vyas",
                subject="Maths & Science (Founder)",
                experience="20 Years Experience",
                highlight="Founder & Academic Director, Aarambh Institute",
                specialty="Conceptual Mathematics & Science for 4th to 10th",
                initials="SV",
                avatar_bg="bg-red-50 text-[#c22329]",
                subject_badge="bg-red-50 text-[#c22329] border-red-200",
            ),
            FacultyMember(
                name="Mr. Vishal Rathore",
                subject="Mathematics",
                experience="15 Years Experience",
                highlight="Senior Mathematics Specialist for Board Exams",
                specialty="Algebra, Calculus & Trigonometry Mastery",
                initials="VR",
                avatar_bg="bg-amber-50 text-amber-800",
                subject_badge="bg-amber-50 text-amber-800 border-amber-200",
            ),
            FacultyMember(
                name="Mrs. Anita Holkar",
                subject="Physics",
                experience="15 Years Experience",
                highlight="Physics Senior Educator for MP Board & CBSE",
                specialty="Mechanics, Electricity, Optics & Numerical Clarity",
                initials="AH",
                avatar_bg="bg-cyan-50 text-cyan-800",
                subject_badge="bg-cyan-50 text-cyan-800 border-cyan-200",
            ),
            FacultyMember(
                name="Mr. Ansh Sir",
                subject="Chemistry, Biology, Physics",
                experience="5 Years Experience",
                highlight="NEET + JEE Mains Category Specialist",
                specialty="Competitive Speed Techniques & Problem Solving",
                initials="AS",
                avatar_bg="bg-purple-50 text-purple-800",
                subject_badge="bg-purple-50 text-purple-800 border-purple-200",
            ),
            FacultyMember(
                name="Miss Darshna Panchal",
                subject="Business Studies & Economics",
                experience="2 Years Experience",
                highlight="Teaching & Institutional Management Expertise",
                specialty="Business Management, Micro & Macro Economics",
                initials="DP",
                avatar_bg="bg-rose-50 text-rose-800",
                subject_badge="bg-rose-50 text-rose-800 border-rose-200",
            ),
        ]

    # 3. Courses Bundle
    courses_list = [
        CourseItem(
            id="middle-school",
            category="school",
            title="Class 4th to 8th (Middle School)",
            subtitle="All Subjects Comprehensive Coaching for MP Board, CBSE & ICSE",
            target="Classes 4th, 5th, 6th, 7th & 8th",
            duration="1 Academic Year",
            board="MP Board / CBSE / ICSE",
            timings="Morning 11:00 AM - 12:30 PM | Evening 5:00 PM - 6:30 PM",
            batch_size="Strict 20 Students per batch",
            fee="₹800/- to ₹1,000/- (Monthly)",
            badge="Junior Foundation",
            badge_color="bg-blue-50 text-blue-700 border-blue-200",
            features=[
                "All Subjects Covered (Maths, Science, English, Hindi, Social Science)",
                "Weekly Assessment Tests with Parent Progress Reports",
                "Printed Comprehensive Study Material & Practice Worksheets",
                "Daily Dedicated Doubt Clearing & Homework Guidance",
                "Special focus on Handwriting, Reading & Basic Mathematical Speed",
            ],
            popular=True,
        ),
        CourseItem(
            id="high-school",
            category="board",
            title="Class 9th to 12th (Board & Entrance)",
            subtitle="Science (PCM / PCB) & Commerce Stream Mastery for Board Exams",
            target="Classes 9th, 10th, 11th & 12th",
            duration="1 Academic Year",
            board="MP Board / CBSE / ICSE",
            timings="Morning 11:00 AM - 1:00 PM | Evening 4:00 PM - 6:00 PM",
            batch_size="Small Batches (20 Students)",
            fee="Student-Friendly Affordable Fees",
            badge="Board Result Rankers",
            badge_color="bg-red-50 text-[#c22329] border-red-200",
            features=[
                "All Core Subjects: Physics, Chemistry, Maths, Biology, Commerce & Accounts",
                "Weekly Topic Tests + Monthly Full Board Model Examination Papers",
                "Previous 10 Years Board Papers analysis and Answer-Writing Drills",
                "Special NEET & JEE Mains Foundation Concepts covered by Expert Mentors",
                "Daily 1:1 Doubt Classes with Senior HODs (15+ to 30 Yrs Experience)",
            ],
            popular=True,
        ),
        CourseItem(
            id="college-degrees",
            category="college",
            title="College Degrees (B.Com, M.Com, BBA, MBA, B.Sc)",
            subtitle="Specialized Higher Education & Commerce/Management Coaching",
            target="Undergraduate & Postgraduate Students",
            duration="Semester / Academic Year",
            board="University Syllabus Aligned",
            timings="Flexible Morning & Evening College Batches",
            batch_size="Personalized Domain Batches",
            fee="Affordable Package Rates",
            badge="Higher Education",
            badge_color="bg-amber-50 text-amber-800 border-amber-200",
            features=[
                "Financial Accounting, Corporate Accounting, Taxation & Costing",
                "Business Studies, Economics, Statistics & Financial Management",
                "Taught by Veteran Commerce Head Mr. Jitendra Shindey (30 Yrs Experience)",
                "University Exam Pattern Model Question Banks & Solved Papers",
                "Concept clearing for Competitive Exams (Bank PO, CA Foundation, CAT)",
            ],
            popular=False,
        ),
    ]

    # 4. Featured Toppers
    featured_toppers = [
        TopperStudent(
            name="Prince",
            grade="Class 12th",
            board="MP Board",
            score="94%",
            marks="580 / 600",
            rank="Rank 1st",
            year="2023",
            subjects="Maths: 100/100 • Physics: 99/100",
            quote="Aarambh ne mujhe sahi direction diya aur regular practice sets ki wajah se board exam mein top rank mili.",
            initials="PR",
            badge_color="bg-amber-100 text-amber-900 border-amber-300",
        ),
        TopperStudent(
            name="Rohit Garg",
            grade="Class 10th",
            board="MP Board",
            score="91%",
            marks="Board Distinction",
            rank="Rank 2nd",
            year="2024",
            subjects="Maths & Physics Topper",
            quote="Proud to be an Aarambhian! The teachers personally cleared every doubt before the exams.",
            initials="RG",
            badge_color="bg-blue-100 text-blue-900 border-blue-300",
        ),
        TopperStudent(
            name="Payal Sharma",
            grade="Class 10th",
            board="MP Board",
            score="89%",
            marks="Board Distinction",
            rank="Rank 3rd",
            year="2024",
            subjects="Maths & Chemistry Distinction",
            quote="Aarambh didn't just teach me, it transformed me. Concepts were made crystal clear.",
            initials="PS",
            badge_color="bg-emerald-100 text-emerald-900 border-emerald-300",
        ),
    ]

    all_toppers = [
        StudentRollItem(name="Prince", class_name="12th", board="MP Board", score="94%", year="2023", highlight="Rank 1st (Maths 100/100)"),
        StudentRollItem(name="Rohit Garg", class_name="10th", board="MP Board", score="91%", year="2024", highlight="Rank 2nd"),
        StudentRollItem(name="Payal Sharma", class_name="10th", board="MP Board", score="89%", year="2024", highlight="Rank 3rd"),
        StudentRollItem(name="Neha Yadav", class_name="10th", board="MP Board", score="89%", year="2023", highlight="Distinction"),
        StudentRollItem(name="Nupur", class_name="10th", board="CBSE", score="89%", year="2023", highlight="Distinction"),
        StudentRollItem(name="Monika", class_name="12th", board="CBSE", score="85%", year="2024", highlight="Distinction"),
        StudentRollItem(name="Ritika Sarothiya", class_name="10th", board="CBSE", score="85%", year="2025", highlight="Distinction"),
        StudentRollItem(name="Nishtha Jain", class_name="10th", board="MP Board", score="83%", year="2025", highlight="First Division"),
        StudentRollItem(name="Shrishti Yadav", class_name="9th", board="MP Board", score="A Grade", year="2025", highlight="Class Topper"),
        StudentRollItem(name="Vanshika Yadav", class_name="7th", board="MP Board", score="A Grade", year="2025", highlight="Class Topper"),
        StudentRollItem(name="Atharva Choudhary", class_name="8th", board="CBSE", score="A Grade", year="2025", highlight="School Star"),
    ]

    testimonials = [
        TestimonialItem(
            name="Dhruvika",
            class_info="Class 6th",
            year="2023",
            role="Parent Review",
            review="Aarambh Institute ke teachers bahut dedicated hain. Mere bachche ke marks aur confidence dono mein kaafi improvement hua hai. Hum institute ki teaching aur guidance se bahut santusht hain.",
        ),
        TestimonialItem(
            name="Yashika",
            class_info="Class 7th",
            year="2024",
            role="Student Review",
            review="Aarambh Institute mein padhai ka environment bahut positive hai. Teachers har topic ko simple aur interesting tareeke se samjhate hain, jis se padhai aasan lagti hai.",
        ),
        TestimonialItem(
            name="Vaishnavi Patel",
            class_info="Class 10th (Boards)",
            year="2025",
            role="Student Review",
            review="Regular tests, personal attention aur progress updates ki wajah se humein performance ka poora pata rehta hai. Aarambh Institute sach mein students ke future ko lekar serious hai.",
        ),
        TestimonialItem(
            name="Rishabh Bhargav",
            class_info="Class 11th (Science)",
            year="2025",
            role="Student Review",
            review="Yahan mujhe padhai ke saath motivation bhi milta hai. Teachers hamesha support karte hain aur doubts ko turant solve karte hain.",
        ),
        TestimonialItem(
            name="Gourav Sarothiya",
            class_info="Class 10th (Boards)",
            year="2024",
            role="Student Review",
            review="Best guidance for academic success! Highly recommended for all board students in Indore.",
        ),
    ]

    usps = [
        UspFeature(number=1, title="Expert Faculty", description="Highly qualified and experienced teachers with up to 30 years of dedicated teaching legacy."),
        UspFeature(number=2, title="Personalised Attention", description="Strict small batch sizes of 20 students to ensure individual guidance and better interaction."),
        UspFeature(number=3, title="Result Oriented Approach", description="Consistent record of excellent results in board examinations (98.5% highest scorer)."),
        UspFeature(number=4, title="Comprehensive Study Material & Regular Tests", description="Notes, practice sets, and return modules designed for all levels with weekly feedback."),
        UspFeature(number=5, title="Supportive Learning Environment", description="Encouraging atmosphere that builds confidence, eliminates fear, and motivates students to excel."),
        UspFeature(number=6, title="Student-Friendly Fee Structure", description="Quality education at an affordable and transparent price starting from ₹800/mo."),
    ]

    notices = [
        NoticeItem(
            date="24 March 2026",
            title="Weekly Board Mock Test Series (Sunday Batch)",
            desc="Mandatory for Class 10th and 12th students. Timings: 11:00 AM to 1:00 PM. Answer sheet evaluation will be handed over to parents on Wednesday.",
            priority="High Priority",
            color="bg-red-50 text-[#c22329] border-red-200",
        ),
        NoticeItem(
            date="20 March 2026",
            title="New Academic Session (2026-27) Admissions Open",
            desc="Classes 4th to 12th & Degree programs. Limited 20 seats per batch. Avail early bird fee benefits at Hawa Bangla campus.",
            priority="Admission Alert",
            color="bg-blue-50 text-blue-700 border-blue-200",
        ),
        NoticeItem(
            date="15 March 2026",
            title="Doubt Clearing Clinic with HODs",
            desc="Special extra classes every evening from 6:00 PM to 7:00 PM for physics numericals and organic chemistry reactions.",
            priority="Academic",
            color="bg-amber-50 text-amber-800 border-amber-200",
        ),
    ]

    holidays = [
        HolidayItem(holiday="Mahavir Jayanti", date="April 2026", status="Holiday"),
        HolidayItem(holiday="Good Friday / Ambedkar Jayanti", date="April 2026", status="Holiday"),
        HolidayItem(holiday="Summer Break (Junior Batches Only)", date="May 15 - May 25, 2026", status="Special Timings"),
        HolidayItem(holiday="Independence Day & Raksha Bandhan", date="August 2026", status="Celebration"),
        HolidayItem(holiday="Ganesh Chaturthi / Anant Chaturdashi", date="September 2026", status="Holiday"),
        HolidayItem(holiday="Dussehra & Diwali Break", date="October / November 2026", status="Festival Break"),
    ]

    materials = [
        StudyMaterialItem(
            title="Class 10th Maths All Formulas Booklet",
            target_class="Class 10th (MP Board / CBSE)",
            pages="18 Pages",
            size="2.4 MB PDF",
            downloads="1,240+ Downloads",
            author="Mrs. Shobhna Vyas & Mr. Vishal Rathore",
            badge="Most Popular",
            badge_color="bg-red-50 text-[#c22329] border-red-200",
        ),
        StudyMaterialItem(
            title="Class 12th Physics Quick Revision & Derivations",
            target_class="Class 12th Science",
            pages="26 Pages",
            size="3.8 MB PDF",
            downloads="980+ Downloads",
            author="Mrs. Anita Holkar",
            badge="Board Essential",
            badge_color="bg-blue-50 text-blue-700 border-blue-200",
        ),
        StudyMaterialItem(
            title="Class 12th Biology Diagram Compendium & Labels",
            target_class="Class 12th & PMT/NEET",
            pages="32 Pages",
            size="5.1 MB PDF",
            downloads="1,450+ Downloads",
            author="Mr. Pankaj Dubey (30 Yrs Exp)",
            badge="NEET Ready",
            badge_color="bg-emerald-50 text-emerald-700 border-emerald-200",
        ),
        StudyMaterialItem(
            title="Class 11th & 12th Commerce Accounting Proformas",
            target_class="Commerce & B.Com",
            pages="22 Pages",
            size="2.9 MB PDF",
            downloads="890+ Downloads",
            author="Mr. Jitendra Shindey (30 Yrs Exp)",
            badge="Commerce Star",
            badge_color="bg-amber-50 text-amber-800 border-amber-200",
        ),
        StudyMaterialItem(
            title="Class 4th to 8th Vedic Maths & Mental Calculation Tricks",
            target_class="Junior Section",
            pages="14 Pages",
            size="1.8 MB PDF",
            downloads="620+ Downloads",
            author="Aarambh Junior Academic Cell",
            badge="Speed Maths",
            badge_color="bg-purple-50 text-purple-700 border-purple-200",
        ),
        StudyMaterialItem(
            title="MP Board & CBSE 2026 Model Solved Question Paper",
            target_class="All High School Batches",
            pages="40 Pages",
            size="4.5 MB PDF",
            downloads="2,100+ Downloads",
            author="Aarambh Faculty Panel",
            badge="Official Model",
            badge_color="bg-rose-50 text-rose-700 border-rose-200",
        ),
    ]

    # Dynamic CMS overrides
    contact_cms = cms_map.get("contact", {})
    home_stats = cms_map.get("home", {}).get("stats", {})
    about_cms = cms_map.get("about", {})
    results_cms = cms_map.get("results", {})
    sc_cms = cms_map.get("student_corner", {})

    if contact_cms:
        inst_name = contact_cms.get("institute_name", inst_name)
        inst_address = contact_cms.get("full_address", inst_address)
        inst_phone = contact_cms.get("primary_phone", inst_phone)

    if cms_map.get("courses", {}).get("courses_list"):
        try:
            courses_list = [CourseItem(**c) for c in cms_map["courses"]["courses_list"]]
        except Exception:
            pass

    if cms_map.get("faculty", {}).get("faculty_list"):
        try:
            teachers_list = [FacultyMember(**f) for f in cms_map["faculty"]["faculty_list"]]
        except Exception:
            pass

    if results_cms.get("featured_toppers"):
        try:
            featured_toppers = [TopperStudent(**t) for t in results_cms["featured_toppers"]]
        except Exception:
            pass
    if results_cms.get("all_toppers"):
        try:
            all_toppers = [StudentRollItem(**t) for t in results_cms["all_toppers"]]
        except Exception:
            pass
    if results_cms.get("testimonials"):
        try:
            testimonials = [TestimonialItem(**t) for t in results_cms["testimonials"]]
        except Exception:
            pass

    if sc_cms.get("notices"):
        try:
            notices = [NoticeItem(**n) for n in sc_cms["notices"]]
        except Exception:
            pass
    if sc_cms.get("holidays"):
        try:
            holidays = [HolidayItem(**h) for h in sc_cms["holidays"]]
        except Exception:
            pass
    if sc_cms.get("materials"):
        try:
            materials = [StudyMaterialItem(**m) for m in sc_cms["materials"]]
        except Exception:
            pass

    return LandingPageBundle(
        contact=InstituteContactInfo(
            name=inst_name,
            tagline=contact_cms.get("tagline", "Step Toward Success"),
            established_year=2015,
            city="Indore, Madhya Pradesh",
            full_address=inst_address,
            primary_phone=inst_phone,
            secondary_phone=contact_cms.get("secondary_phone", "79097-14081"),
            whatsapp_number=contact_cms.get("whatsapp_number", "88397-14081"),
            email=contact_cms.get("email", inst_email),
            website_domain="aarambhinstitute.com",
            google_maps_url=contact_cms.get("google_maps_url", "https://maps.app.goo.gl/T2m2g9b8tjVMCDqL9"),
            working_hours=contact_cms.get("working_hours", "10:00 AM to 8:00 PM (Monday to Saturday)"),
            boards_covered=["MP Board", "CBSE", "ICSE"],
            classes_taught="Class 4th to 12th, B.Com, M.Com, BBA, MBA, B.Sc",
            footer_tagline=contact_cms.get("footer_tagline", "Education with values. Learning with joy."),
        ),
        stats=HeroStats(
            years_experience=home_stats.get("years_experience", "15+ Yrs"),
            total_students=home_stats.get("total_students", "2,000+"),
            highest_board_score=home_stats.get("highest_board_score", "98.5%"),
            board_pass_rate=home_stats.get("board_pass_rate", "98%"),
            faculty_count=home_stats.get("faculty_count", "7 Educators"),
            batch_size_limit=home_stats.get("batch_size_limit", "20 Students"),
        ),
        about=AboutSectionData(
            title=about_cms.get("title", "Transforming Academic Journeys With The Right Guidance"),
            paragraphs=about_cms.get("paragraphs", [
                "At Aarambh Institute, we believe that the right guidance at the right time can transform a student's academic journey.",
                "Our experienced faculty, well-researched curriculum, and student-centric approach make learning both effective and engaging.",
            ]),
            director_name=about_cms.get("director_name", "Mrs. Shobhna Vyas"),
            director_designation=about_cms.get("director_designation", "Founder & Academic Director"),
            director_experience=about_cms.get("director_experience", "20 Years Experience"),
            director_quote=about_cms.get("director_quote", "As a parent myself, I know what you want: safety, learning, and happiness for your child. At Aarambh Institute, you will get all three. Let's grow together."),
            award_title=about_cms.get("award_title", "Best Coaching Institute Award, Indore 2023"),
            core_values=about_cms.get("core_values", [
                {"title": "Child Safety First", "desc": "Protected and encouraging learning environment"},
                {"title": "Effective Learning", "desc": "Proven concept-building and test techniques"},
                {"title": "Joyful Environment", "desc": "Education with happiness and zero fear"},
            ]),
        ),
        courses=courses_list,
        faculty=teachers_list,
        featured_toppers=featured_toppers,
        all_toppers=all_toppers,
        testimonials=testimonials,
        usps=usps,
        notices=notices,
        holidays=holidays,
        materials=materials,
    )


@router.post(
    "/enquiries",
    response_model=PublicEnquiryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit public enquiry / free demo booking from landing page",
)
async def submit_public_enquiry(
    body: PublicEnquiryCreate,
    db: AsyncSession = Depends(get_db),
) -> PublicEnquiryResponse:
    """
    Direct lead submission into the Neon PostgreSQL `enquiries` table.
    Enquiry is automatically assigned source=WEBSITE and stage=NEW.
    """
    # 1. Resolve Institute
    inst_stmt = select(Institute).where(Institute.code == "AARAMBH")
    res = await db.execute(inst_stmt)
    institute = res.scalar_one_or_none()

    if not institute:
        # Fallback to any active institute
        any_inst_stmt = select(Institute).limit(1)
        res = await db.execute(any_inst_stmt)
        institute = res.scalar_one_or_none()

    if not institute:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Institute tenant not configured",
        )

    # 2. Construct Enquiry Record
    combined_remarks = (
        f"Target: {body.target_class}"
        + (f" | Stream: {body.stream}" if body.stream else "")
        + (f" | Notes: {body.remarks}" if body.remarks else " | Free Demo Request")
    )

    enquiry = Enquiry(
        id=uuid.uuid4(),
        institute_id=institute.id,
        student_name=body.student_name,
        student_phone=body.phone,
        student_email=str(body.email) if body.email else None,
        parent_name=body.parent_name,
        parent_phone=body.phone,
        parent_email=str(body.email) if body.email else None,
        source=EnquirySource.WEBSITE,
        stage=EnquiryStage.NEW,
        remarks=combined_remarks,
    )

    db.add(enquiry)
    await db.commit()
    await db.refresh(enquiry)

    return PublicEnquiryResponse(
        id=enquiry.id,
        student_name=enquiry.student_name,
        parent_name=enquiry.parent_name,
        phone=enquiry.parent_phone,
        message="Thank you! Your free demo class and enquiry has been received. Our counselor will contact you shortly.",
    )
