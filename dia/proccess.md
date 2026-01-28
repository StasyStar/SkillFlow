### Правильная последовательность процесса:
#### Этап 1: Регистрация/Авторизация
1. React App → API Gateway → User Service → PostgreSQL (пользователь входит в систему)

#### Этап 2: Загрузка резюме и парсинг
2. React App → API Gateway → Skill Parser (пользователь загружает резюме)
3. Skill Parser → PostgreSQL (store resume)
4. Skill Parser → Feature Store (store vectors)
5. Skill Parser → Kafka (resume_parsed event)

#### Этап 3: Анализ Gap (запускается асинхронно)
6. Kafka → Gap Analyzer (trigger - слушает событие resume_parsed)
7. Gap Analyzer → User Service → PostgreSQL (get_user_profile)
8. Gap Analyzer → Skill Parser (get_parsed_resume)
9. Gap Analyzer → Elasticsearch (read_job_data)
10. Gap Analyzer → Feature Store (read_vectors)
11. Gap Analyzer → PostgreSQL (store analysis results)
12. Gap Analyzer → Kafka (analysis_done event)

#### Этап 4: Генерация рекомендаций (запускается асинхронно)
13. Kafka → Recommendation (analysis_ready - слушает analysis_done)
14. Recommendation → PostgreSQL (read gaps)
15. Recommendation → Elasticsearch (search_courses)
16. Recommendation → Feature Store (read_vectors)
17. Recommendation → External (course data - если нужно свежие данные)

#### Этап 5: Показ результатов пользователю
18. Recommendation → PostgreSQL (cache recommendations)
19. React App ← API Gateway ← Recommendation (пользователь видит рекомендации)

#### Этап 6: Фоновые процессы (независимо)
20. Celery → Vacancy Scraper (scheduled - по расписанию)
21. Vacancy Scraper → External (scrape_jobs)
22. Vacancy Scraper → Elasticsearch (store_jobs)
23. Vacancy Scraper → Feature Store (job vectors)