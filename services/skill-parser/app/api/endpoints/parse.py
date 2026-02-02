import os
import time
from typing import Optional

from app.core.config import settings
from app.core.database import get_db
from app.models.schemas import ResumeParseRequest, ResumeParseResponse, ParsedResume
from app.services.ner_extractor import SkillExtractor
from app.services.parser import FileParser
from app.services.storage import ResumeStorage
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session

router = APIRouter()

# Инициализируем экстрактор навыков (можно кэшировать)
skill_extractor = SkillExtractor()


def validate_file_extension(filename: str) -> str:
    """Проверка расширения файла"""
    ext = os.path.splitext(filename)[1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Неподдерживаемый формат файла. Разрешены: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    return ext


@router.post("/parse", response_model=ResumeParseResponse)
async def parse_resume(
        background_tasks: BackgroundTasks,
        file: Optional[UploadFile] = File(None),
        text: Optional[str] = Form(None),
        user_id: Optional[str] = Form(None),
        db: Session = Depends(get_db)
):
    """
    Парсинг резюме из файла или текста

    Поддерживаемые форматы:
    - PDF (.pdf)
    - Word (.docx, .doc)
    - Текст (.txt)
    - Прямой текст в поле 'text'
    """
    start_time = time.time()

    try:
        parsed_text = ""
        file_type = None
        original_filename = None

        # Обработка файла
        if file:
            # Проверка размера файла
            if file.size > settings.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"Файл слишком большой. Максимальный размер: {settings.MAX_FILE_SIZE // 1024 // 1024}MB"
                )

            # Проверка расширения
            file_extension = validate_file_extension(file.filename)
            original_filename = file.filename

            # Чтение файла
            file_content = await file.read()

            # Парсинг файла
            parsed_text, file_type = FileParser.parse_file(file_content, file_extension)

        # Обработка текста
        elif text:
            parsed_text = text.strip()
            file_type = "text"

        else:
            raise HTTPException(
                status_code=400,
                detail="Необходимо предоставить файл или текст"
            )

        if not parsed_text or len(parsed_text) < 50:
            raise HTTPException(
                status_code=400,
                detail="Текст слишком короткий для анализа (минимум 50 символов)"
            )

        # Извлечение информации из текста
        parsed_data = skill_extractor.parse_resume(parsed_text)

        # Извлечение секций
        sections = FileParser.extract_sections(parsed_text)
        parsed_data["sections"] = sections

        processing_time = time.time() - start_time

        # Сохранение в БД
        resume_record = ResumeStorage.save_parsed_resume(
            db=db,
            parsed_data=parsed_data,
            original_filename=original_filename,
            user_id=user_id,
            file_type=file_type,
            processing_time=processing_time
        )

        # Добавляем ID записи в ответ
        parsed_data["resume_id"] = resume_record.id
        parsed_data["created_at"] = resume_record.created_at.isoformat()

        return ResumeParseResponse(
            success=True,
            data=parsed_data,
            processing_time=processing_time
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Логируем ошибку
        print(f"Error parsing resume: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обработке резюме: {str(e)}"
        )


@router.get("/parse/{resume_id}", response_model=ResumeParseResponse)
async def get_parsed_resume(
        resume_id: str,
        db: Session = Depends(get_db)
):
    """Получение ранее распарсенного резюме по ID"""
    resume = ResumeStorage.get_resume_by_id(db, resume_id)

    if not resume:
        raise HTTPException(status_code=404, detail="Резюме не найдено")

    if not resume.is_successful:
        return ResumeParseResponse(
            success=False,
            error=resume.error_message
        )

    return ResumeParseResponse(
        success=True,
        data={
            **resume.parsed_data,
            "resume_id": resume.id,
            "created_at": resume.created_at.isoformat() if resume.created_at else None,
            "confidence_score": resume.confidence_score
        },
        processing_time=resume.processing_time
    )


@router.get("/user/{user_id}/resumes")
async def get_user_resumes(
        user_id: str,
        limit: int = 10,
        db: Session = Depends(get_db)
):
    """Получение всех резюме пользователя"""
    resumes = ResumeStorage.get_user_resumes(db, user_id, limit)

    return {
        "success": True,
        "count": len(resumes),
        "resumes": [resume.to_dict() for resume in resumes]
    }