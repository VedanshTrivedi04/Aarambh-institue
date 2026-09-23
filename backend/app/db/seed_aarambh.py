"""
app/db/seed_aarambh.py
-----------------------
Seed script for Aarambh Institute in Neon PostgreSQL.
Inserts tenant, branches, academic boards, classes, courses, and teacher profiles.
Idempotent: safe to run multiple times.
"""

import asyncio
import uuid
from datetime import date
from sqlalchemy import select, text
from app.db.session import AsyncSessionLocal
from app.models.institute import Institute, Branch
from app.models.academic_structure import AcademicYear, Board, SchoolClass, Course
from app.models.user import User, UserStatus
from app.models.people import TeacherProfile
from app.core.security import hash_password


async def seed():
    async with AsyncSessionLocal() as session:
        print("Starting Aarambh Institute database seeding...")

        # 1. Institute
        inst_stmt = select(Institute).where(Institute.code == "AARAMBH")
        res = await session.execute(inst_stmt)
        institute = res.scalar_one_or_none()

        if not institute:
            institute = Institute(
                id=uuid.uuid4(),
                name="Aarambh Institute",
                code="AARAMBH",
                address="8 Shantinath Puri, Hawa Bangla, Near Sai Mandir, Indore, Madhya Pradesh",
                contact_email="aarambhinstitute09@gmail.com",
                contact_phone="88397-14081",
                is_active=True,
            )
            session.add(institute)
            await session.flush()
            print(f"Created Institute: {institute.name} ({institute.id})")
        else:
            print(f"Institute already exists: {institute.name}")

        # 2. Branch
        branch_stmt = select(Branch).where(
            Branch.institute_id == institute.id, Branch.code == "HAWA_BANGLA"
        )
        res = await session.execute(branch_stmt)
        branch = res.scalar_one_or_none()

        if not branch:
            branch = Branch(
                id=uuid.uuid4(),
                institute_id=institute.id,
                name="Hawa Bangla Campus",
                code="HAWA_BANGLA",
                address="8 Shantinath Puri, Hawa Bangla, Near Sai Mandir, Indore, Madhya Pradesh",
                contact_number="88397-14081",
                is_main_branch=True,
                is_active=True,
            )
            session.add(branch)
            await session.flush()
            print(f"Created Branch: {branch.name}")
        else:
            print(f"Branch exists: {branch.name}")

        # 3. Academic Year
        ay_stmt = select(AcademicYear).where(
            AcademicYear.institute_id == institute.id, AcademicYear.name == "2026-27"
        )
        res = await session.execute(ay_stmt)
        academic_year = res.scalar_one_or_none()

        if not academic_year:
            academic_year = AcademicYear(
                id=uuid.uuid4(),
                institute_id=institute.id,
                name="2026-27",
                start_date=date(2026, 4, 1),
                end_date=date(2027, 3, 31),
                is_current=True,
            )
            session.add(academic_year)
            await session.flush()
            print(f"Created Academic Year: {academic_year.name}")
        else:
            print(f"Academic Year exists: {academic_year.name}")

        # 4. Boards
        boards_data = [
            ("MP Board", "MPBOARD"),
            ("CBSE", "CBSE"),
            ("ICSE", "ICSE"),
        ]
        boards_map = {}
        for b_name, b_code in boards_data:
            b_stmt = select(Board).where(
                Board.institute_id == institute.id, Board.code == b_code
            )
            res = await session.execute(b_stmt)
            board = res.scalar_one_or_none()
            if not board:
                board = Board(
                    id=uuid.uuid4(),
                    institute_id=institute.id,
                    name=b_name,
                    code=b_code,
                    is_active=True,
                )
                session.add(board)
                await session.flush()
                print(f"Created Board: {board.name}")
            boards_map[b_code] = board

        # 5. School Classes
        classes_data = [
            ("Class 4th", 4),
            ("Class 5th", 5),
            ("Class 6th", 6),
            ("Class 7th", 7),
            ("Class 8th", 8),
            ("Class 9th", 9),
            ("Class 10th", 10),
            ("Class 11th", 11),
            ("Class 12th", 12),
            ("B.Com", 13),
            ("M.Com", 14),
            ("BBA", 15),
            ("MBA", 16),
            ("B.Sc", 17),
        ]
        classes_map = {}
        for c_name, c_order in classes_data:
            c_stmt = select(SchoolClass).where(
                SchoolClass.institute_id == institute.id,
                SchoolClass.board_id == boards_map["MPBOARD"].id,
                SchoolClass.name == c_name,
            )
            res = await session.execute(c_stmt)
            sc = res.scalar_one_or_none()
            if not sc:
                sc = SchoolClass(
                    id=uuid.uuid4(),
                    institute_id=institute.id,
                    board_id=boards_map["MPBOARD"].id,
                    name=c_name,
                    display_order=c_order,
                    is_active=True,
                )
                session.add(sc)
                await session.flush()
                print(f"Created Class: {sc.name}")
            classes_map[c_name] = sc
        print("Seeded School Classes.")

        # 6. Courses
        courses_data = [
            (
                "Class 4th to 8th Foundation",
                "CRS_4_8",
                classes_map["Class 8th"].id,
                12,
            ),
            (
                "Class 9th to 12th Boards & Entrance",
                "CRS_9_12",
                classes_map["Class 10th"].id,
                12,
            ),
            (
                "College Degrees Coaching",
                "CRS_DEGREE",
                classes_map["B.Com"].id,
                12,
            ),
        ]
        for crs_name, crs_code, cid, dur in courses_data:
            crs_stmt = select(Course).where(
                Course.institute_id == institute.id,
                Course.academic_year_id == academic_year.id,
                Course.code == crs_code,
            )
            res = await session.execute(crs_stmt)
            crs = res.scalar_one_or_none()
            if not crs:
                crs = Course(
                    id=uuid.uuid4(),
                    institute_id=institute.id,
                    academic_year_id=academic_year.id,
                    class_id=cid,
                    name=crs_name,
                    code=crs_code,
                    duration_months=dur,
                    is_active=True,
                )
                session.add(crs)
                await session.flush()
                print(f"Created Course: {crs.name}")

        # 7. Teachers
        teachers_data = [
            ("Pankaj", "Dubey", "Biology", 30, "M.Sc, B.Ed", "EMP_PD"),
            ("Jitendra", "Shindey", "Commerce & Accounts", 30, "M.Com, Senior Commerce Expert", "EMP_JS"),
            ("Shobhna", "Vyas", "Mathematics & Science", 20, "M.Sc (Founder & Director)", "EMP_SV"),
            ("Vishal", "Rathore", "Mathematics", 15, "M.Sc Mathematics", "EMP_VR"),
            ("Anita", "Holkar", "Physics", 15, "M.Sc Physics", "EMP_AH"),
            ("Ansh", "Sir", "Chemistry, Biology, Physics", 5, "B.Tech / Science Specialist", "EMP_AS"),
            ("Darshna", "Panchal", "Business Studies & Economics", 2, "MBA, Institutional Management", "EMP_DP"),
        ]

        default_pwd = hash_password("AarambhTeacher@2026")
        for fn, ln, subj, exp, qual, emp_code in teachers_data:
            tp_stmt = select(TeacherProfile).where(
                TeacherProfile.institute_id == institute.id,
                TeacherProfile.employee_code == emp_code,
            )
            res = await session.execute(tp_stmt)
            tp = res.scalar_one_or_none()

            if not tp:
                # Create user first
                u_email = f"{fn.lower()}.{ln.lower()}@aarambhinstitute.com"
                user_stmt = select(User).where(User.email == u_email)
                ures = await session.execute(user_stmt)
                u = ures.scalar_one_or_none()
                if not u:
                    u = User(
                        id=uuid.uuid4(),
                        institute_id=institute.id,
                        email=u_email,
                        mobile=None,
                        password_hash=default_pwd,
                        role="TEACHER",
                        status=UserStatus.ACTIVE,
                    )
                    session.add(u)
                    await session.flush()

                tp = TeacherProfile(
                    id=uuid.uuid4(),
                    institute_id=institute.id,
                    user_id=u.id,
                    first_name=fn,
                    last_name=ln,
                    employee_code=emp_code,
                    qualification=f"{qual} ({subj})",
                    experience_years=exp,
                    personal_email=u_email,
                    is_active=True,
                )
                session.add(tp)
                await session.flush()
                print(f"Created Teacher: {fn} {ln} ({exp} yrs)")

        # 8. Admin User
        admin_email = "admin@aarambhinstitute.com"
        admin_stmt = select(User).where(User.email == admin_email)
        admin_res = await session.execute(admin_stmt)
        admin_user = admin_res.scalar_one_or_none()
        if not admin_user:
            admin_pwd = hash_password("AarambhAdmin@2026")
            admin_user = User(
                id=uuid.uuid4(),
                institute_id=institute.id,
                email=admin_email,
                mobile="8839714081",
                password_hash=admin_pwd,
                role="ADMIN",
                status=UserStatus.ACTIVE,
            )
            session.add(admin_user)
            await session.flush()
            print(f"Created Admin: {admin_user.email}")
        else:
            print(f"Admin user exists: {admin_user.email}")

        await session.commit()
        print("Successfully committed Aarambh Institute seed data to Neon PostgreSQL!")


if __name__ == "__main__":
    asyncio.run(seed())
