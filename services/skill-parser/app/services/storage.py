from typing import Dict, Any, Optional

from app.models.database import ParsedResumeDB
from sqlalchemy.orm import Session


class ResumeStorage:
    @staticmethod
    def save_parsed_resume(
            db: Session,
            parsed_data: Dict[str, Any],
            original_filename: Optional[str] = None,
            user_id: Optional[str] = None,
            file_type: Optional[str] = None,
            processing_time: Optional[float] = None
    ) -> ParsedResumeDB:
        """Сохранение распарсенного резюме в БД"""

        resume = ParsedResumeDB(
            user_id=user_id,
            original_filename=original_filename,
            file_type=file_type,
            parsed_data=parsed_data,
            raw_text=parsed_data.get('raw_text', ''),
            skills=parsed_data.get('skills', []),
            experience_summary=parsed_data.get('experience', []),
            education_summary=parsed_data.get('education', []),
            processing_time=processing_time,
            is_successful=True,
            confidence_score=ResumeStorage._calculate_confidence(parsed_data)
        )

        db.add(resume)
        db.commit()
        db.refresh(resume)
        return resume

    @staticmethod
    def _calculate_confidence(parsed_data: Dict[str, Any]) -> float:
        """Расчет confidence score"""
        confidence = 0.5  # Базовый уровень

        # Учитываем количество извлеченных навыков
        skills_count = len(parsed_data.get('skills', []))
        if skills_count > 10:
            confidence += 0.2
        elif skills_count > 5:
            confidence += 0.1

        # Учитываем наличие опыта
        if parsed_data.get('experience'):
            confidence += 0.2

        # Учитываем наличие образования
        if parsed_data.get('education'):
            confidence += 0.1

        # Ограничиваем от 0 до 1
        return min(max(confidence, 0), 1)

    @staticmethod
    def get_resume_by_id(db: Session, resume_id: str) -> Optional[ParsedResumeDB]:
        """Получение резюме по ID"""
        return db.query(ParsedResumeDB).filter(ParsedResumeDB.id == resume_id).first()

    @staticmethod
    def get_user_resumes(db: Session, user_id: str, limit: int = 10) -> list:
        """Получение резюме пользователя"""
        return db.query(ParsedResumeDB) \
            .filter(ParsedResumeDB.user_id == user_id) \
            .order_by(ParsedResumeDB.created_at.desc()) \
            .limit(limit) \
            .all()