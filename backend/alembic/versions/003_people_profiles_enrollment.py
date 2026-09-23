"""
003_people_profiles_enrollment — People profiles and enrollment engine.

Creates:
  - student_profiles
  - teacher_profiles
  - parent_profiles
  - staff_profiles
  - student_parents (join table)
  - enrollments
  - batch_transfer_history
Alters:
  - batches (adds FK constraint on teacher_id -> teacher_profiles.id)
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Enums ─────────────────────────────────────────────────────────────
    gender_enum = postgresql.ENUM("MALE", "FEMALE", "OTHER", name="gender_enum", create_type=False)
    gender_enum.create(op.get_bind(), checkfirst=True)

    blood_group_enum = postgresql.ENUM(
        "A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-",
        name="blood_group_enum", create_type=False,
    )
    blood_group_enum.create(op.get_bind(), checkfirst=True)

    enrollment_status_enum = postgresql.ENUM(
        "ACTIVE", "COMPLETED", "DROPPED", "TRANSFERRED", "CANCELLED",
        name="enrollment_status_enum", create_type=False,
    )
    enrollment_status_enum.create(op.get_bind(), checkfirst=True)

    # ── student_profiles ──────────────────────────────────────────────────
    op.create_table(
        "student_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institute_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("institutes.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("branches.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, unique=True),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("date_of_birth", sa.Date, nullable=True),
        sa.Column("gender", sa.Enum("MALE", "FEMALE", "OTHER", name="gender_enum"), nullable=True),
        sa.Column("blood_group", sa.Enum("A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-", name="blood_group_enum"), nullable=True),
        sa.Column("photo_url", sa.String(500), nullable=True),
        sa.Column("admission_number", sa.String(50), nullable=True),
        sa.Column("current_class_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("school_classes.id", ondelete="SET NULL"), nullable=True),
        sa.Column("joining_date", sa.Date, nullable=True),
        sa.Column("address_line1", sa.String(255), nullable=True),
        sa.Column("address_line2", sa.String(255), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("state", sa.String(100), nullable=True),
        sa.Column("pincode", sa.String(10), nullable=True),
        sa.Column("emergency_contact_name", sa.String(150), nullable=True),
        sa.Column("emergency_contact_phone", sa.String(20), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("institute_id", "admission_number", name="uq_student_profiles_institute_admission_number"),
    )
    op.create_index("ix_student_profiles_institute_id", "student_profiles", ["institute_id"])
    op.create_index("ix_student_profiles_user_id", "student_profiles", ["user_id"])
    op.create_index("ix_student_profiles_current_class_id", "student_profiles", ["current_class_id"])
    op.create_index("ix_student_profiles_admission_number", "student_profiles", ["admission_number"])
    op.create_index("ix_student_profiles_deleted_at", "student_profiles", ["deleted_at"])

    # ── teacher_profiles ──────────────────────────────────────────────────
    op.create_table(
        "teacher_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institute_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("institutes.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("branches.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, unique=True),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("date_of_birth", sa.Date, nullable=True),
        sa.Column("gender", sa.Enum("MALE", "FEMALE", "OTHER", name="gender_enum"), nullable=True),
        sa.Column("photo_url", sa.String(500), nullable=True),
        sa.Column("employee_code", sa.String(50), nullable=True),
        sa.Column("qualification", sa.String(255), nullable=True),
        sa.Column("experience_years", sa.Integer, nullable=True),
        sa.Column("joining_date", sa.Date, nullable=True),
        sa.Column("personal_email", sa.String(255), nullable=True),
        sa.Column("personal_phone", sa.String(20), nullable=True),
        sa.Column("address", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("institute_id", "employee_code", name="uq_teacher_profiles_institute_employee_code"),
    )
    op.create_index("ix_teacher_profiles_institute_id", "teacher_profiles", ["institute_id"])
    op.create_index("ix_teacher_profiles_user_id", "teacher_profiles", ["user_id"])
    op.create_index("ix_teacher_profiles_employee_code", "teacher_profiles", ["employee_code"])
    op.create_index("ix_teacher_profiles_deleted_at", "teacher_profiles", ["deleted_at"])

    # ── batches: add FK constraint to teacher_profiles ────────────────────
    op.create_foreign_key(
        "fk_batches_teacher_id_teacher_profiles",
        "batches", "teacher_profiles",
        ["teacher_id"], ["id"],
        ondelete="SET NULL",
    )

    # ── parent_profiles ───────────────────────────────────────────────────
    op.create_table(
        "parent_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institute_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("institutes.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("branches.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, unique=True),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("relation", sa.String(30), nullable=False, server_default="PARENT"),
        sa.Column("occupation", sa.String(150), nullable=True),
        sa.Column("annual_income", sa.String(50), nullable=True),
        sa.Column("photo_url", sa.String(500), nullable=True),
        sa.Column("address", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_parent_profiles_institute_id", "parent_profiles", ["institute_id"])
    op.create_index("ix_parent_profiles_user_id", "parent_profiles", ["user_id"])
    op.create_index("ix_parent_profiles_deleted_at", "parent_profiles", ["deleted_at"])

    # ── staff_profiles ────────────────────────────────────────────────────
    op.create_table(
        "staff_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("institute_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("institutes.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("branches.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, unique=True),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("designation", sa.String(100), nullable=True),
        sa.Column("department", sa.String(100), nullable=True),
        sa.Column("employee_code", sa.String(50), nullable=True),
        sa.Column("joining_date", sa.Date, nullable=True),
        sa.Column("photo_url", sa.String(500), nullable=True),
        sa.Column("address", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("institute_id", "employee_code", name="uq_staff_profiles_institute_employee_code"),
    )
    op.create_index("ix_staff_profiles_institute_id", "staff_profiles", ["institute_id"])
    op.create_index("ix_staff_profiles_user_id", "staff_profiles", ["user_id"])
    op.create_index("ix_staff_profiles_employee_code", "staff_profiles", ["employee_code"])
    op.create_index("ix_staff_profiles_deleted_at", "staff_profiles", ["deleted_at"])

    # ── student_parents ───────────────────────────────────────────────────
    op.create_table(
        "student_parents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("student_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("parent_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("is_primary", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("student_id", "parent_id", name="uq_student_parents"),
    )
    op.create_index("ix_student_parents_student_id", "student_parents", ["student_id"])
    op.create_index("ix_student_parents_parent_id", "student_parents", ["parent_id"])

    # ── enrollments ───────────────────────────────────────────────────────
    op.create_table(
        "enrollments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("student_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("student_profiles.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("batch_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("batches.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("institute_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("institutes.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("status", sa.Enum("ACTIVE", "COMPLETED", "DROPPED", "TRANSFERRED", "CANCELLED", name="enrollment_status_enum"),
                  nullable=False, server_default="ACTIVE"),
        sa.Column("enrollment_date", sa.Date, nullable=False),
        sa.Column("end_date", sa.Date, nullable=True),
        sa.Column("enrolled_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("remarks", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_enrollments_student_id", "enrollments", ["student_id"])
    op.create_index("ix_enrollments_batch_id", "enrollments", ["batch_id"])
    op.create_index("ix_enrollments_institute_id", "enrollments", ["institute_id"])
    op.create_index("ix_enrollments_status", "enrollments", ["status"])

    # ── batch_transfer_history ────────────────────────────────────────────
    op.create_table(
        "batch_transfer_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("enrollment_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("enrollments.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("student_profiles.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("from_batch_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("batches.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("to_batch_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("batches.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("reason", sa.Text, nullable=False),
        sa.Column("transferred_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("institute_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_batch_transfer_history_enrollment_id", "batch_transfer_history", ["enrollment_id"])
    op.create_index("ix_batch_transfer_history_student_id", "batch_transfer_history", ["student_id"])
    op.create_index("ix_batch_transfer_history_from_batch_id", "batch_transfer_history", ["from_batch_id"])
    op.create_index("ix_batch_transfer_history_to_batch_id", "batch_transfer_history", ["to_batch_id"])
    op.create_index("ix_batch_transfer_history_institute_id", "batch_transfer_history", ["institute_id"])
    op.create_index("ix_batch_transfer_history_created_at", "batch_transfer_history", ["created_at"])


def downgrade() -> None:
    op.drop_table("batch_transfer_history")
    op.drop_table("enrollments")
    op.drop_table("student_parents")
    op.drop_constraint("fk_batches_teacher_id_teacher_profiles", "batches", type_="foreignkey")
    op.drop_table("staff_profiles")
    op.drop_table("parent_profiles")
    op.drop_table("teacher_profiles")
    op.drop_table("student_profiles")

    op.execute("DROP TYPE IF EXISTS enrollment_status_enum")
    op.execute("DROP TYPE IF EXISTS blood_group_enum")
    op.execute("DROP TYPE IF EXISTS gender_enum")
