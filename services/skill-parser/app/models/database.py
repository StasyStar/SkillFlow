from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


def generate_uuid():
    return str(uuid.uuid4())


class ParsedResumeDB(Base):
    __tablename__ = "parsed_resumes"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=True)  # Привязка к пользователю
    original_filename = Column(String)
    file_type = Column(String)
    parsed_data = Column(JSON)  # Структурированные данные
    raw_text = Column(Text)
    skills = Column(JSON)  # Массив навыков
    experience_summary = Column(JSON)
    education_summary = Column(JSON)
    confidence_score = Column(Float, default=0.0)
    processing_time = Column(Float)
    is_successful = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "original_filename": self.original_filename,
            "skills": self.skills,
            "experience": self.experience_summary,
            "education": self.education_summary,
            "confidence_score": self.confidence_score,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }