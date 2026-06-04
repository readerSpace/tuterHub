# TutorHub

TutorHub is a tutoring operations portfolio project built around a Django core API and a separate FastAPI AI microservice. The Django application handles authentication, student management, lessons, reports, assignments, scores, and invoices. The FastAPI service adds lightweight student retrieval plus OpenAI-backed assistance for parent feedback, homework suggestions, and study planning.

This repository also includes a Vue 3 + Vite + TypeScript frontend for operating the tutoring workflow from the browser. The frontend provides login, dashboard metrics, student list/detail views, lesson record entry, and AI generation screens.

## Implemented features

- JWT authentication and role-based permissions in Django
- Student, lesson, lesson report, assignment, score, and invoice CRUD APIs
- Search, filtering, ordering, pagination, admin customization, and CSV export
- Celery and Redis integration for lesson report notifications
- FastAPI AI microservice with health, students, and AI generation endpoints
- OpenAI integration with local mock fallback for development and testing
- PostgreSQL-backed AI generation logging
- Vue 3 frontend with Pinia, Vue Router, and Axios
- Docker Compose setup for Django, FastAPI, PostgreSQL, Redis, Gunicorn, and Nginx
- Pytest coverage for both Django and FastAPI flows

## Services

### Django API

- `/api/auth/token/`
- `/api/auth/token/refresh/`
- `/api/auth/me/`
- `/api/students/`
- `/api/students/export_csv/`
- `/api/lessons/`
- `/api/reports/`
- `/api/assignments/`
- `/api/scores/`
- `/api/invoices/`
- `/api/schema/`
- `/api/docs/`

### FastAPI AI Service

- `GET /health`
- `GET /students`
- `POST /ai/lesson-feedback`
- `POST /ai/homework-suggestion`
- `POST /ai/study-plan`
- `GET /docs`

### Frontend

- `http://localhost:8000/login` (nginx-served production-style frontend)
- `http://localhost:8000/dashboard`
- `http://localhost:8000/students`
- `http://localhost:8000/lessons/new`
- `http://localhost:8000/studio/ai/lesson-feedback`
- `http://localhost:8000/studio/ai/homework-suggestion`
- `http://localhost:8000/studio/ai/study-plan`
- `http://localhost:5173/login` (Vite dev server, available only with the `dev-frontend` Compose profile)

## Local setup

1. Copy `.env.example` to `config/.env` when you want PostgreSQL, Redis, and the AI service to share one configuration. The project also accepts the legacy root `.env` as a fallback.
2. Install dependencies with `python -m pip install -r requirements.txt`.
3. Run Django migrations with `python manage.py migrate`.
4. Create an admin user with `python manage.py createsuperuser`.
5. Start Django with `python manage.py runserver`.
6. Start the AI service with `uvicorn ai_service.app.main:app --reload --port 8001`.
7. Start the frontend with `cd frontend && npm install && npm run dev`.

If both `config/.env` and the legacy root `.env` are absent, Django and the FastAPI service both fall back to local SQLite databases for quick development. The AI service also falls back to deterministic mock responses when `OPENAI_API_KEY` is missing or when `OPENAI_USE_MOCK=true`.

## Docker setup

1. Copy `.env.example` to `config/.env`.
2. Run `docker compose up --build`.
3. Open `http://localhost:8000/` for the nginx-served frontend.
4. Open `http://localhost:8000/api/docs/` for Django Swagger.
5. Open `http://localhost:8001/docs` for FastAPI docs.
6. If you want the Vite dev frontend as well, run `docker compose --profile dev-frontend up -d --build frontend` and open `http://localhost:5173/login`.

## Usage

After the services are running, the typical workflow is: sign in to Django, call protected tutoring APIs with a JWT access token, and use the FastAPI service for AI-assisted feedback and planning.

### 1. Open the API documentation

- Django Swagger: `http://localhost:8000/api/docs/`
- FastAPI Swagger: `http://localhost:8001/docs`
- Django admin: `http://localhost:8000/admin/`

These pages are the fastest way to inspect request and response formats while developing.

### 2. Create a user and obtain a JWT token

If you have not created a user yet, create one first.

```bash
python manage.py createsuperuser
```

Then request a token from Django.

```bash
curl -X POST http://localhost:8000/api/auth/token/ \
	-H "Content-Type: application/json" \
	-d '{
		"username": "admin",
		"password": "your-password"
	}'
```

The response includes `access` and `refresh` tokens. Use the `access` token in the `Authorization: Bearer ...` header for protected Django endpoints.

### 3. Confirm the authenticated user

```bash
curl http://localhost:8000/api/auth/me/ \
	-H "Authorization: Bearer <access-token>"
```

This is the simplest check that authentication is working correctly.

### 4. Use the tutoring management APIs

Most Django endpoints require authentication. A common first step is listing students.

```bash
curl http://localhost:8000/api/students/ \
	-H "Authorization: Bearer <access-token>"
```

Create a student record:

```bash
curl -X POST http://localhost:8000/api/students/ \
	-H "Authorization: Bearer <access-token>" \
	-H "Content-Type: application/json" \
	-d '{
		"full_name": "Taro Yamada",
		"grade": "中3",
		"school": "Oita Junior High",
		"target_school": "Oita Uenogaoka High School",
		"weak_subjects": "Mathematics, English",
		"teacher": 1,
		"parent": 2,
		"guardian_contact": "parent@example.com",
		"notes": "Needs weekly review."
	}'
```

From there, the same token can be used with `/api/lessons/`, `/api/reports/`, `/api/assignments/`, `/api/scores/`, and `/api/invoices/`.

### 5. Use the AI service endpoints

The FastAPI service is useful when you want generated parent comments, homework ideas, or short study plans.

Generate lesson feedback:

```bash
curl -X POST http://localhost:8001/ai/lesson-feedback \
	-H "Content-Type: application/json" \
	-d '{
		"student_name": "山田太郎",
		"subject": "英語",
		"lesson_content": "長文読解と要約",
		"understanding_level": 4,
		"teacher_note": "要点整理はよくできたが、接続詞の見落としがあった"
	}'
```

Generate homework suggestions:

```bash
curl -X POST http://localhost:8001/ai/homework-suggestion \
	-H "Content-Type: application/json" \
	-d '{
		"student_name": "山田太郎",
		"grade": "中2",
		"subject": "数学",
		"weak_points": ["一次関数", "連立方程式"],
		"available_minutes": 30
	}'
```

Generate a study plan:

```bash
curl -X POST http://localhost:8001/ai/study-plan \
	-H "Content-Type: application/json" \
	-d '{
		"student_name": "山田太郎",
		"grade": "中3",
		"target_school": "大分上野丘高校",
		"scores": [
			{"subject": "数学", "score": 58, "max_score": 100},
			{"subject": "英語", "score": 66, "max_score": 100},
			{"subject": "理科", "score": 72, "max_score": 100}
		],
		"weeks": 4
	}'
```

### 6. Understand mock versus real OpenAI responses

When `OPENAI_USE_MOCK=true`, or when `OPENAI_API_KEY` is missing or invalid, the AI service returns deterministic mock responses for local development.

When `OPENAI_USE_MOCK=false` and a valid API key is configured, the AI service calls OpenAI. If that call fails, the service still falls back to mock output, and the failure is written to the `ai_service` container logs so you can tell that the response was degraded.

## Django to FastAPI integration

The Django side includes an HTTP client in `tutoring.ai_client` and can optionally use the AI lesson feedback endpoint when lesson report emails are generated. Set `ENABLE_AI_PARENT_COMMENT=true` if you want Django to automatically fetch AI-generated parent comments when a lesson report does not already contain one.

## Testing

- Run `pytest` for both Django and FastAPI tests.
- Run `python manage.py check` for Django configuration validation.
