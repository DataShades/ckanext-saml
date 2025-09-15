from __future__ import annotations

from sqlalchemy import Boolean, Column, UnicodeText
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql.schema import ForeignKey

import ckan.model as model

Base = declarative_base(metadata=model.meta.metadata)


class User(Base):
    __tablename__ = "saml2_user"

    id = Column(UnicodeText, ForeignKey(model.User.id), primary_key=True)
    name_id = Column(UnicodeText, nullable=False, unique=True)
    allow_update = Column(Boolean, default=False)
    attributes = Column(JSONB, nullable=False, default=dict)

    user = relationship(
        model.User,
        backref=backref("saml2_user", uselist=False, cascade="all, delete-orphan"),
    )
