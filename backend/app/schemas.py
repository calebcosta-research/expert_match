from __future__ import annotations

from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List


class ExpertBase(BaseModel):
    name: str
    biography: Optional[str] = None
    biography_file_key: Optional[str] = None
    location: Optional[str] = None
    availability: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    desired_work: Optional[str] = None
    hourly_rate: Optional[float] = None
    cv_s3_key: Optional[str] = None
    google_scholar_url: Optional[str] = None

    @validator("email")
    def email_must_be_edu(cls, v):
        if v and not v.endswith(".edu"):
            raise ValueError("email must end with .edu")
        return v


class ExpertCreate(ExpertBase):
    pass


class Expert(ExpertBase):
    id: int
    publications: List['Publication'] = []

    class Config:
        orm_mode = True


class PublicationBase(BaseModel):
    title: str
    year: Optional[int] = None
    url: Optional[str] = None


class Publication(PublicationBase):
    id: int

    class Config:
        orm_mode = True


class ProjectBase(BaseModel):
    organization_name: str
    description: Optional[str] = None
    qualifications: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    funding_min: Optional[float] = None
    funding_max: Optional[float] = None
    days_per_week: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class Project(ProjectBase):
    id: int

    class Config:
        orm_mode = True
