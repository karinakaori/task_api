"""Initial tasks table.

Revision ID: 20260501_0001
Revises:
Create Date: 2026-05-01
"""

from alembic import op
import sqlalchemy as sa


revision = "20260501_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = inspector.get_table_names()

    if "tasks" not in tables:
        op.create_table(
            "tasks",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("title", sa.String(length=100), nullable=False),
            sa.Column("description", sa.String(length=500), nullable=True),
            sa.Column("status", sa.String(length=16), nullable=False),
            sa.Column("owner_id", sa.String(length=64), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("due_date", sa.Date(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
    else:
        columns = {column["name"] for column in inspector.get_columns("tasks")}
        if "owner_id" not in columns:
            op.add_column("tasks", sa.Column("owner_id", sa.String(length=64), nullable=True))

    indexes = {index["name"] for index in inspector.get_indexes("tasks")}
    if "ix_tasks_id" not in indexes:
        op.create_index(op.f("ix_tasks_id"), "tasks", ["id"], unique=False)
    if "ix_tasks_owner_id" not in indexes:
        op.create_index(op.f("ix_tasks_owner_id"), "tasks", ["owner_id"], unique=False)
    if "ix_tasks_status" not in indexes:
        op.create_index(op.f("ix_tasks_status"), "tasks", ["status"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "tasks" not in inspector.get_table_names():
        return

    indexes = {index["name"] for index in inspector.get_indexes("tasks")}
    if "ix_tasks_status" in indexes:
        op.drop_index(op.f("ix_tasks_status"), table_name="tasks")
    if "ix_tasks_owner_id" in indexes:
        op.drop_index(op.f("ix_tasks_owner_id"), table_name="tasks")
    if "ix_tasks_id" in indexes:
        op.drop_index(op.f("ix_tasks_id"), table_name="tasks")

    columns = {column["name"] for column in inspector.get_columns("tasks")}
    if "owner_id" in columns:
        with op.batch_alter_table("tasks") as batch_op:
            batch_op.drop_column("owner_id")
