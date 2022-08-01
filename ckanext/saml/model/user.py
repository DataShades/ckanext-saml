from __future__ import annotations

import ckan.model as model
from sqlalchemy import Boolean, Column, UnicodeText
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB

Base = declarative_base(metadata=model.meta.metadata)


class User(Base):
    __tablename__ = "saml2_user"

    id = Column(UnicodeText, ForeignKey(model.User.id), primary_key=True)
    name_id = Column(UnicodeText, nullable=False, unique=True)
    allow_update = Column(Boolean, default=False)
    attributes = Column(JSONB, nullable=False, default=dict)

    user = relationship(model.User, backref=backref("saml2_user", uselist=False, cascade="all, delete-orphan"))
