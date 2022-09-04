"""add attributes column to saml2_user table

Revision ID: e8e7ebedf90d
Revises: 25dc326c059e
Create Date: 2022-08-01 15:55:55.408354

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = "e8e7ebedf90d"
down_revision = "25dc326c059e"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "saml2_user",
        sa.Column("attributes", JSONB, nullable=False, server_default="{}"),
    )
    pass


def downgrade():
    op.drop_column("saml2_user", "attributes")
