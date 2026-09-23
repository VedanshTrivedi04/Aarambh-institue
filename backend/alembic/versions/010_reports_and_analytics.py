"""
010_reports_and_analytics — Materialized Views for Batch & Performance Analytics.

Creates:
  - mv_batch_performance_summary (PostgreSQL Materialized View)
  - uq_mv_batch_perf_batch_id (Unique Index)
  - ix_mv_batch_perf_institute_id (Index)
"""

from __future__ import annotations

from alembic import op

revision = "010"
down_revision = "009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS mv_batch_performance_summary AS
        SELECT
            b.id AS batch_id,
            b.institute_id,
            b.name AS batch_name,
            COALESCE(e.total_enrolled, 0)::integer AS total_enrolled,
            COALESCE(cs.total_sessions_conducted, 0)::integer AS total_sessions_conducted,
            COALESCE(att.average_attendance_rate, 0.0)::float AS average_attendance_rate,
            COALESCE(t.tests_conducted, 0)::integer AS tests_conducted,
            COALESCE(t.average_test_score, 0.0)::float AS average_test_score
        FROM batches b
        LEFT JOIN (
            SELECT batch_id, COUNT(id) AS total_enrolled
            FROM enrollments
            WHERE status = 'ACTIVE'
            GROUP BY batch_id
        ) e ON e.batch_id = b.id
        LEFT JOIN (
            SELECT batch_id, COUNT(id) AS total_sessions_conducted
            FROM class_sessions
            WHERE status = 'HELD' AND deleted_at IS NULL
            GROUP BY batch_id
        ) cs ON cs.batch_id = b.id
        LEFT JOIN (
            SELECT cs.batch_id,
                   ROUND(AVG(CASE WHEN a.status = 'PRESENT' THEN 100.0 ELSE 0.0 END)::numeric, 2) AS average_attendance_rate
            FROM attendance a
            JOIN class_sessions cs ON cs.id = a.class_session_id
            WHERE cs.status = 'HELD'
            GROUP BY cs.batch_id
        ) att ON att.batch_id = b.id
        LEFT JOIN (
            SELECT t.batch_id,
                   COUNT(DISTINCT t.id) AS tests_conducted,
                   ROUND(AVG(tr.percentage)::numeric, 2) AS average_test_score
            FROM tests t
            LEFT JOIN test_results tr ON tr.test_id = t.id
            WHERE t.status = 'PUBLISHED' AND t.deleted_at IS NULL
            GROUP BY t.batch_id
        ) t ON t.batch_id = b.id
        WHERE b.deleted_at IS NULL;
        """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS uq_mv_batch_perf_batch_id
        ON mv_batch_performance_summary (batch_id);
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_mv_batch_perf_institute_id
        ON mv_batch_performance_summary (institute_id);
        """
    )


def downgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_batch_performance_summary CASCADE;")
