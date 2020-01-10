from sqlalchemy import Column, UnicodeText, Boolean
from sqlalchemy.ext.declarative import declarative_base
import ckan.model as model

Base = declarative_base()
metadata = Base.metadata


class SAML2User(Base):
    __tablename__ = 'saml2_user'

    id = Column(UnicodeText, primary_key=True)
    name_id = Column(UnicodeText, nullable=False, unique=True)
    allow_update = Column(Boolean, default=False)


def setupdb():

    metadata.create_all(model.meta.engine)


def dropdb():

    metadata.drop_all(model.meta.engine)
