"""add_foreign_key_constraint_on_user_id

Revision ID: 25dc326c059e
Revises: 92745f8a6168
Create Date: 2022-07-26 15:01:52.311445

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '25dc326c059e'
down_revision = '92745f8a6168'
branch_labels = None
depends_on = None


def upgrade():
    op.create_foreign_key(
        "saml2_user_id_fkey",
        "saml2_user",
        "user",
        ["id"],
        ["id"],
    )



def downgrade():
    op.drop_constraint(
        "saml2_user_id_fkey",
        "saml2_user",
        type_=u"foreignkey",
    )
