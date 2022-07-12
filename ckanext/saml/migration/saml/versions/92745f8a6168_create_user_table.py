"""empty message

Revision ID: 92745f8a6168
Revises:
Create Date: 2022-04-21 16:17:57.972546

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = "92745f8a6168"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    tables = inspector.get_table_names()
    if "saml2_user" in tables:
        return

    op.create_table(
        "saml2_user",
        sa.Column("id", sa.UnicodeText, primary_key=True),
        sa.Column("name_id", sa.UnicodeText, unique=True, nullable=False),
        sa.Column("allow_update", sa.Boolean),
    )


def downgrade():
    op.drop_table(
        "saml2_user",
    )
