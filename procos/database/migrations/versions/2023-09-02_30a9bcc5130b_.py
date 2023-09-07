"""empty message

Revision ID: 30a9bcc5130b
Revises:
Create Date: 2023-09-02 18:17:36.937162

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "30a9bcc5130b"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "projects",
        sa.Column("id_", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column(
            "created_date", sa.Date(), server_default=sa.text("CURRENT_DATE"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id_"),
    )
    op.create_table(
        "contracts",
        sa.Column("id_", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column(
            "created_date", sa.Date(), server_default=sa.text("CURRENT_DATE"), nullable=False
        ),
        sa.Column("signed_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("project_id_", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["project_id_"],
            ["projects.id_"],
        ),
        sa.PrimaryKeyConstraint("id_"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("contracts")
    op.drop_table("projects")
    # ### end Alembic commands ###
