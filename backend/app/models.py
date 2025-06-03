from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Expert(Base):
    __tablename__ = "experts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    biography = Column(String, nullable=True)
    biography_file_key = Column(String, nullable=True)
    location = Column(String, nullable=True)
    availability = Column(String, nullable=True)
    email = Column(String, nullable=False, unique=True)
    phone = Column(String, nullable=True)
    desired_work = Column(String, nullable=True)
    hourly_rate = Column(Float, nullable=True)
    cv_s3_key = Column(String, nullable=True)
    google_scholar_url = Column(String, nullable=True)

    publications = relationship("Publication", back_populates="expert", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    organization_name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    qualifications = Column(String, nullable=True)
    start_date = Column(String, nullable=True)
    end_date = Column(String, nullable=True)
    funding_min = Column(Float, nullable=True)
    funding_max = Column(Float, nullable=True)
    days_per_week = Column(String, nullable=True)


class Publication(Base):
    __tablename__ = "publications"

    id = Column(Integer, primary_key=True, index=True)
    expert_id = Column(Integer, ForeignKey("experts.id"), nullable=False)
    title = Column(String, nullable=False)
    year = Column(Integer, nullable=True)
    url = Column(String, nullable=True)

    expert = relationship("Expert", back_populates="publications")
