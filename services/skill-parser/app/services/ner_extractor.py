import re
from typing import List, Dict, Any

import spacy
from app.core.config import settings
from spacy.matcher import Matcher, PhraseMatcher


class SkillExtractor:
    def __init__(self):
        # Загружаем модель spaCy
        try:
            self.nlp = spacy.load(settings.SPACY_MODEL)
        except OSError:
            # Если модель не установлена, скачиваем
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", settings.SPACY_MODEL])
            self.nlp = spacy.load(settings.SPACY_MODEL)

        self._initialize_matchers()
        self._load_skill_patterns()

    def _initialize_matchers(self):
        """Инициализация матчеров spaCy"""
        self.matcher = Matcher(self.nlp.vocab)
        self.phrase_matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")

        # Паттерны для опыта работы
        experience_patterns = [
            [{"LOWER": {"IN": ["experience", "exp"]}}, {"LOWER": "in"}],
            [{"LOWER": "worked"}, {"LOWER": "as"}],
            [{"LOWER": {"IN": ["years", "yrs"]}}, {"LOWER": "of"}],
        ]

        for i, pattern in enumerate(experience_patterns):
            self.matcher.add(f"EXPERIENCE_{i}", [pattern])

    def _load_skill_patterns(self):
        """Загрузка паттернов для навыков"""
        # Технические навыки (можно расширять)
        self.tech_skills = {
            "programming": ["python", "java", "javascript", "c++", "c#", "go", "ruby", "php", "swift", "kotlin"],
            "web": ["html", "css", "react", "angular", "vue", "django", "flask", "fastapi", "spring"],
            "databases": ["sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch"],
            "devops": ["docker", "kubernetes", "aws", "azure", "gcp", "jenkins", "git", "ci/cd"],
            "data_science": ["pandas", "numpy", "tensorflow", "pytorch", "scikit-learn", "ml"],
            "tools": ["git", "jira", "confluence", "slack", "vs code", "intellij"]
        }

        # Создаем фразы для phrase matcher
        skill_phrases = []
        for category, skills in self.tech_skills.items():
            for skill in skills:
                skill_phrases.append(self.nlp.make_doc(skill))

        self.phrase_matcher.add("SKILLS", skill_phrases)

    def extract_skills(self, text: str) -> List[str]:
        """Извлечение навыков из текста"""
        doc = self.nlp(text.lower())
        skills = set()

        # Используем phrase matcher для поиска навыков
        matches = self.phrase_matcher(doc)
        for match_id, start, end in matches:
            span = doc[start:end]
            skills.add(span.text)

        # Дополнительный поиск по ключевым словам
        skill_keywords = ["skill", "proficient in", "experience with", "knowledge of"]
        for sent in doc.sents:
            for keyword in skill_keywords:
                if keyword in sent.text.lower():
                    # Ищем существительные после ключевых слов
                    for token in sent:
                        if token.pos_ in ["NOUN", "PROPN"] and token.text.lower() not in skills:
                            skills.add(token.text.lower())

        return list(skills)

    def extract_experience(self, text: str) -> List[Dict[str, Any]]:
        """Извлечение опыта работы"""
        experience_items = []

        # Паттерны для поиска опыта
        patterns = [
            # Формат: Должность в Компании (Годы)
            r'([A-Z][a-z\s]+(?:[A-Z][a-z\s]+)*)\s+(?:at|in|@)\s+([A-Z][a-zA-Z\s&]+?)\s+\((\d+(?:\.\d+)?)\s+years?\)',
            # Формат: Должность - Компания (Годы)
            r'([A-Z][a-z\s]+(?:[A-Z][a-z\s]+)*)\s*[-–]\s*([A-Z][a-zA-Z\s&]+?)\s+\((\d+(?:\.\d+)?)\s+years?\)',
            # Формат с датами
            r'([A-Z][a-z\s]+(?:[A-Z][a-z\s]+)*)\s+at\s+([A-Z][a-zA-Z\s&]+?)\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\s+[-–]\s+(?:present|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4})',
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) >= 2:
                    experience_items.append({
                        "title": match.group(1).strip(),
                        "company": match.group(2).strip() if len(match.groups()) > 1 else None,
                        "years": float(match.group(3)) if len(match.groups()) > 2 and match.group(3) else None,
                        "raw": match.group(0)
                    })

        # Альтернативный подход: поиск по ключевым словам
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ in ["ORG", "WORK_OF_ART"]:
                # Ищем должности рядом с названиями компаний
                pass

        return experience_items

    def extract_education(self, text: str) -> List[Dict[str, Any]]:
        """Извлечение образования"""
        education_items = []

        # Паттерны для образования
        patterns = [
            # Университет - Степень (Год)
            r'([A-Z][a-zA-Z\s&]+University|[A-Z][a-zA-Z\s&]+College|[A-Z][a-zA-Z\s&]+Institute)[,\s]+([A-Z][a-z\s]+(?:[A-Z][a-z\s]+)*)[,\s]+(\d{4})',
            # Степень in Специальность, Университет
            r'([A-Z][a-z\s]+(?:[A-Z][a-z\s]+)*)\s+in\s+([A-Z][a-z\s]+(?:[A-Z][a-z\s]+)*)[,\s]+([A-Z][a-zA-Z\s&]+(?:University|College|Institute))',
            # Бакалавр/Магистр etc.
            r'(Bachelor|Master|PhD|Doctorate|Diploma|Certificate)\s+(?:of|in)\s+([A-Z][a-z\s]+(?:[A-Z][a-z\s]+)*)[,\s]+([A-Z][a-zA-Z\s&]+)',
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) >= 2:
                    education_items.append({
                        "institution": match.group(1).strip(),
                        "degree": match.group(2).strip() if len(match.groups()) > 1 else None,
                        "graduation_year": int(match.group(3)) if len(match.groups()) > 2 and match.group(3) else None,
                        "raw": match.group(0)
                    })

        return education_items

    def parse_resume(self, text: str) -> Dict[str, Any]:
        """Полный парсинг резюме"""
        skills = self.extract_skills(text)
        experience = self.extract_experience(text)
        education = self.extract_education(text)

        # Извлечение языков
        languages = self._extract_languages(text)

        # Извлечение сертификаций
        certifications = self._extract_certifications(text)

        return {
            "skills": skills,
            "experience": experience,
            "education": education,
            "languages": languages,
            "certifications": certifications,
            "raw_text": text,
            "metadata": {
                "skills_count": len(skills),
                "experience_count": len(experience),
                "education_count": len(education)
            }
        }

    def _extract_languages(self, text: str) -> List[str]:
        """Извлечение языков"""
        languages = set()
        common_languages = ["english", "russian", "spanish", "french", "german",
                            "chinese", "japanese", "arabic", "portuguese", "italian"]

        text_lower = text.lower()
        for lang in common_languages:
            if lang in text_lower:
                languages.add(lang.capitalize())

        # Поиск паттернов "Language: ..."
        lang_pattern = r'(?:languages?|language\s+skills?)[:\s]+([^.\n]+)'
        match = re.search(lang_pattern, text, re.IGNORECASE)
        if match:
            lang_section = match.group(1)
            for lang in common_languages:
                if lang in lang_section.lower():
                    languages.add(lang.capitalize())

        return list(languages)

    def _extract_certifications(self, text: str) -> List[str]:
        """Извлечение сертификаций"""
        certifications = set()

        # Паттерны для сертификаций
        patterns = [
            r'(?:certification|certificate|certified)\s+in\s+([A-Z][a-zA-Z\s]+)',
            r'([A-Z][a-zA-Z\s]+)\s+(?:certification|certificate|certified)',
            r'(AWS|Azure|GCP|Google|Microsoft|Oracle|Cisco)\s+([A-Z][a-zA-Z\s]+)',
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                cert = match.group(1).strip()
                if cert and len(cert) > 3:  # Фильтр коротких совпадений
                    certifications.add(cert)

        return list(certifications)