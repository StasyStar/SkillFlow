from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field


class ExperienceItem(BaseModel):
    title: str
    company: Optional[str] = None
    years: float
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None


class EducationItem(BaseModel):
    degree: str
    institution: str
    field_of_study: Optional[str] = None
    graduation_year: Optional[int] = None


class ResumeParseRequest(BaseModel):
    text: Optional[str] = None
    # Файл передается через form-data


class ResumeParseResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None


class ParsedResume(BaseModel):
    skills: List[str] = Field(default_factory=list)
    experience: List[ExperienceItem] = Field(default_factory=list)
    education: List[EducationItem] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    raw_text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True
